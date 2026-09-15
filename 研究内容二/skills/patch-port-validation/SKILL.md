---
name: patch-port-validation
description: 独立验证安全补丁迁移候选结果，重新检查 reference 语义、change unit 和耦合修改覆盖率，验证候选 patch 的结构、目标 API、错误路径、并发与资源生命周期，并运行适用的构建和测试，输出结构化 validation.json 与报告。用于补丁合入验收和候选 patch 审查。
---

# 补丁迁移独立验证

把候选实现视为待审查对象，不继承实施阶段的成功假设。验证失败时记录证据，不直接修改候选补丁。

## 输入

必须提供：

- `port-analysis.json`；
- `details/application.json`；
- `generated.patch`，以及可选的候选 `worktree_path` 供复核；
- 原始 `reference_patch` 和精确 `target_ref`；
- `output_dir`。

输入 SHA、路径和 artifact hash 不一致时立即 `blocked`。脚本在重放和执行命令前核对分析/实施状态、目标 SHA、补丁路径与哈希、分析及实施证据哈希；缺项或不一致时写出阻塞证据，后续检查记为 `not_run`。哈希均以文件原始字节计算。

`cross_repo_semantic` 时从分析中读取两仓库身份，`--repo` 必须是 target_repo；参考仓库只读。独立比较两侧输入、危险操作、guard、生命周期和错误路径，检查 semantic_mapping 的对应及差异，不要求跨仓库 map_chain 或相同补丁文本。检索账本中被截断、未核对的候选不能算已排除；候选定位及目标依赖未确认时不得放行。

## Layer 1：结构完整性

1. 先运行随 Skill 附带的独立验证脚本，从干净 target 重放候选 patch。
2. 执行 `git apply --check`、`git diff --check` 和 conflict marker 检查。
3. 对比计划路径与实际 changed paths、mode、rename、binary 和整文件新增。
4. 检查是否修改 `.patch-port`、分析产物或无关文件。

确定性验证命令：

```bash
python3 <validation-skill-dir>/scripts/validate_candidate.py \
  --repo <repo> \
  --target-ref <target-commit> \
  --patch <output-dir>/generated.patch \
  --analysis <output-dir>/port-analysis.json \
  --application <output-dir>/details/application.json \
  --output <output-dir>/details/validation-evidence.json \
  --command '<project-specific-test-command>'
```

`--command` 可重复；无可运行测试时省略并记录原因。默认不传 `--report`，避免重复生成 Markdown 证据摘要；仅用户明确需要该摘要时指定 details/ 下的路径。命令使用 argv 执行而不经 shell；管道、重定向和 shell 内建需改写为项目脚本后传入。

`validation-evidence.json` 只证明输入 hash、干净重放、diff 结构和已运行命令的事实。结构检查通过且已运行命令无失败时可输出 `structurally_valid`；未运行命令单列保存，在 Layer 2–6 完成前最多建议 `partial`。

## Layer 2：Change-unit 覆盖

逐个核对 analysis 中的 mandatory units：

- 是否在正确 target location 实施；
- diff 是否真正产生预期行为；
- coupled group 是否完整；
- 是否漏掉声明、调用点、初始化、cleanup 或测试侧修改。

不能只依赖 application ledger，必须从实际 diff 重新取证。

重新核对精确目标 SHA 的实际实现及路径演化。`analysis-evidence.json` 应有实际查询及可访问输出，核对其哈希、版本和 map_chain 引用；重读关键变化两侧及目标代码。`planned == actual` 只证明遵循计划，不能证明计划定位正确。未解决上下文、未覆盖的拆分分支、重建历史整文件或缺少目标入口证据时不得通过位置检查。

## Layer 3：安全语义

围绕每个安全不变量验证：

- guard 是否覆盖所有危险路径且位于危险操作之前；
- 边界、长度、权限、状态或引用检查是否使用正确变量和单位；
- 错误返回和部分成功语义是否保持；
- 锁、内存屏障和并发顺序是否等价；
- 分配、引用、释放和 cleanup 是否成对；
- 是否引入绕过路径、重复检查或新的拒绝服务风险。

至少构造一个正向路径和一个触发原漏洞条件的负向路径进行推演；能执行时转化为测试。

## Layer 4：目标版本兼容性

检查新增 include、macro、symbol、结构体字段、函数签名、配置条件和编译单元在 target 中存在。确认修改符合目标分支的 API、控制流和代码风格。

缺失声明、签名或有效 include 的证据时记录未验证，不能用“标准 API”或其他源文件能调用作为通过依据；同样不能用“补丁包含预期字符串”的自测证明 API 可用。

## Layer 5：构建与测试

按 analysis 的 validation plan 从小到大执行：

1. 语法或单文件检查；
2. 受影响模块构建；
3. 相关单元/回归测试；
4. 原漏洞触发或等价负向测试；
5. 必要时执行更大范围测试。

记录每条命令、退出码、关键输出和未运行原因。脚本的 `commands[].status` 为 `passed`、`failed` 或 `not_run`；可执行程序缺失或无法启动时为 `not_run`，退出码为 null，实际执行失败或超时为 `failed`。关键测试未运行时，静态与语义检查通过后的阶段结论为 `partial`。

## Layer 6：过度修改与回归风险

检查无关格式化、重构、删除、旧文件新增和大块低相似内容。评估候选是否改变正常行为、ABI/API、性能关键路径或错误码。

详细检查矩阵见 [验证矩阵](references/validation-matrix.md)。

## 判定规则

- `passed`：结构、unit 覆盖、安全语义和目标兼容性均通过，所有已运行测试通过，且没有阻塞性未运行验证。
- `partial`：静态与语义检查通过，但关键构建/测试因环境原因未完成。
- `failed`：发现语义错误、漏改、错误位置、构建/测试失败或回归。
- `blocked`：输入不一致、目标不可重建或证据不足以验证。

## 输出

写出 `<output_dir>/details/validation.json` 和 `<output_dir>/VALIDATION_REPORT.md`。JSON 契约见 [验证产物契约](references/validation-contract.md)。最终返回与 JSON 相同的单个对象。

保留 `<output_dir>/details/validation-evidence.json` 作为确定性运行证据，补充查询放入 `details/validation-observations/`。引用已有分析证据时使用实际绝对路径，不复制同一源码片段。

验证报告以 500 字以内说明修改、已验证项、未验证项和风险，详细检查使用证据路径/ID 引用。JSON 保留所有必要验证结论、失败与未运行项，不用报告的篇幅要求截断这些记录。

不得为了得到 `passed` 而修改候选补丁；修复应回到实施阶段形成新候选，再重新完整验证。
