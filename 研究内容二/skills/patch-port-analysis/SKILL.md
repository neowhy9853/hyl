---
name: patch-port-analysis
description: 模型主导补丁迁移分析，提取漏洞行为与安全不变量，通过历史追踪或跨仓库分层检索建立目标对应，识别耦合修改、依赖和风险，输出实施与验证计划。用于 backport 定位和无共同历史的跨仓库语义迁移。
---

# 补丁迁移分析

由模型主导只读分析，逐步查询代码和 Git 历史、判断映射、选择下一步上下文，产生可审计迁移计划。

## 输入与输出

输入：`repo`、`reference_patch`、`target_ref`，以及可选的 `reference_fix`、`reference_parent`、验证命令和 `output_dir`。

模式路由：`port_mode=history` 使用同仓库正向、反向或双侧历史追踪；`port_mode=cross_repo_semantic` 另提供 `reference_repo`、`target_repo`，`repo=target_repo`。跨仓库先阅读 [分层语义检索](references/cross-repo-semantic.md)，以该流程替换下面 A 中的共同祖先检查及 D/E 的历史定位；B/C/F/G/H 的语义、依赖、暴露面和风险检查继续适用。两侧仓库和 revision 分别绑定，证据须标注所属仓库。

输出 `<output_dir>/details/analysis-evidence.json` 和 `<output_dir>/port-analysis.json`。前者记录实际查询及其结果引用，后者记录语义判断和迁移计划。查询输出放入 `<output_dir>/details/observations/`；同一输出保存一份并用证据 ID 引用，不在多个 JSON 中重复抄录源码。保留完整的必要 map_chain 和未解决项，不以精简输出为由缩减调查。见 [分析产物契约](references/analysis-contract.md)；仅 history 模式需阅读 [模型主导的历史追踪](references/history-tracing.md)。

若存在 `.patch-port/repository-scope.json`，读取其中的仓库范围和版本信息；缺少元数据时通过实际查询核实可见范围。模型在授权仓库内自行检索路径、函数、历史和依赖，不把参考补丁未涉及的文件当作不可读。确实无法取得必要证据时，记录缺口并返回 `blocked`。

## 执行方式

模型从读取参考修复开始负责分析循环：提出当前问题 → 调用 Git/读取/搜索工具 → 判断代码变化 → 记录证据与新状态 → 选择下一步查询。工具只执行查询或机械检查，不替模型选择整条历史链或决定语义对应关系。

直接使用 `git show`、`git diff`、`git log`、`git blame`、`git ls-tree`、`git grep` 等操作；命令示例见历史追踪参考。每次读取绑定具体提交和路径，关键输出保存在 `output_dir/details/observations/` 或引用可访问的工具日志。事实记录和模型判断分开保存。

`reference_fix` 存在时可查询其父提交作为参考基线；merge fix 必须确认所选 parent。两者都缺失时先请求参考基线，不能编造历史起点。

## 阶段 A：输入完整性与版本关系

1. 解析所有 revision 的完整 SHA，验证 reference patch 格式和 changed paths。
2. 检查 shallow repository、缺失对象、submodule、二进制 patch、rename/copy 和 mode change。
3. history 模式计算 reference parent、target 和 merge-base 的 ancestry 关系；cross_repo_semantic 分别检查两侧基线，不以找不到共同祖先判定失败。
4. 记录证据缺口；缺少关键历史时不得伪造连续 map chain。

## 阶段 B：参考修复语义建模

从完整 patch 和 reference pre-fix/fixed 代码提取：

- 漏洞行为、触发条件和危险操作；
- 修复建立的安全不变量；
- 输入来源、数据流、控制流、锁和资源生命周期；
- 错误返回、部分成功语义及兼容性约束。

把 patch 拆成 `change_units`。每个 unit 对应一个可独立追踪的安全语义修改，可包含多个相关 hunk。

## 阶段 C：Patch Dependency Graph

为 change unit 建图：

- `requires`：声明、宏、API 或初始化前置依赖；
- `coupled_with`：必须同时迁移的多文件或多 hunk 修改；
- `guards`：某 unit 为另一个危险操作提供 guard；
- `validates`：测试或断言验证某个安全不变量。

将连通且不可拆分的 units 归入同一 `coupled_group`。不能只迁移组内一部分。

若某项 requires 在目标找不到等价能力，使用 `$patch-dependency-discovery` 从参考使用点追踪提供该能力的提交，消费 `dependency-discovery.json`。它补充跨提交来源，不替代本阶段对目标暴露面和迁移必要性的判断。环境工具缺失、纯文本冲突及原候选漏改不直接视为前置源码依赖。候选涉及新增功能时先核对授权；证据不足保留 unresolved。依赖或目标基线变化后重新分析，不沿用旧计划。

## 阶段 D：Direct-apply 可行性探测

此节用于 history 模式。跨仓库先确定语义对应，不以同名路径或 apply 成功作为定位依据；默认 `strategy=semantic-adaptation`，原参考补丁的直接应用记为 not_run/not_applicable。

模型在临时隔离环境中先执行 strict `git apply --check`。失败后根据错误决定是否需要 `--recount`、whitespace tolerant 或 `--3way` 等检查；不必穷举不相关策略。记录未运行项及原因，不保留检查产生的修改。

记录每种策略的命令、退出状态和失败原因。检查成功只表示文本或三方合并可行，仍需执行目标语义检查：

- patch path 是否仍是目标实现位置；
- API 和控制流是否兼容；
- 是否会新增已经迁移走的旧文件；
- coupled group 是否全部覆盖。

只有结构和语义均可接受时输出 `direct_apply_ready`。

## 阶段 E：连续历史映射

此节用于 history 模式；cross_repo_semantic 使用候选检索和 `semantic_mapping`，没有跨仓库的连续 Git 链要求。

对不能安全 direct apply 的每个 change unit，阅读 [历史与语义映射](references/history-tracing.md) 并执行：

1. 读取参考 patch 及修复前代码，模型确定需追踪的代码元素和初始锚点。
2. 查询 ancestry，模型选择正向、反向或经 merge-base 的双侧路线；明确 merge 的 parent 选择。
3. 查询下一条相关变化及两侧代码，模型判断保留、移动、重写、拆分或合并。记录判断依据后更新当前状态。
4. 锚点失效时就在当前边扩大上下文并确认新锚点；确认后模型继续查询下一条变化，不跳到最终目标、不交给整段脚本续跑。拆分时保留多个待追踪状态，覆盖全部相关安全行为。
5. 对略过的无关区间记录范围、路径演化及无相关变化的查询证据。到达 target 后重新读取实际实现，至少使用两类证据确认落点。

无法连续解释最终位置时将该 unit 标记为 `unresolved`，总体状态不得为 `ready`。

## 阶段 F：目标暴露面判断

对每个 change unit 判断：

- `affected`：目标仍存在等价漏洞行为；
- `not_affected`：目标不存在危险操作或已具备同等安全不变量；
- `uncertain`：证据不足。

路径过滤或范围未知时，搜索无结果只证明当前输入没有该代码，不支持 `not_affected`。证明不受影响必须有目标实际实现及相关入口的直接证据；找不到实现时先检查目标全仓路径、符号和历史，仍缺少关键证据则 `blocked`。

必须说明目标中的危险输入、危险操作、安全检查现状和证据。不能仅凭版本号或 patch 能否应用判断受影响状态。

## 阶段 G：动态 Context 计划

由模型根据当前问题选择局部行、完整函数、数据结构和宏、helper、调用者、cleanup、锁及错误约定。每轮说明缺少什么事实、为什么读取这些位置、得到哪些证据以及是否足够，在每一步调查中更新上下文。为新增 API 检查目标声明及有效 include，不能仅凭记忆确认兼容性。

## 阶段 H：风险与迁移计划

评估：

- 路径/模块迁移风险；
- 大规模重构风险；
- 多文件耦合遗漏风险；
- API/ABI 和构建风险；
- 并发、内存屏障、错误路径及资源生命周期风险；
- 可用验证不足风险。

生成按依赖拓扑排序的 `implementation_plan` 和 `validation_plan`。存在 unresolved unit、critical 风险或目标暴露面不确定时输出 `blocked`。

## 约束

- 只读；不得编辑目标文件、提交或恢复历史文件到工作树。
- 使用输入的参考修复及授权仓库中的源码和历史建立迁移依据。
- 所有结论必须关联到 commit、path、symbol、diff 或代码证据。
- 最终只返回与 `port-analysis.json` 相同的合法 JSON。
