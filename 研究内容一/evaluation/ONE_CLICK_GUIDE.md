# 研究内容一：本次修改与一键测评说明

本说明覆盖研究内容一的完整补丁分类测评：五轮、每轮 250 条，共 1,250 个评测位置，涉及 14 个仓库、926 个不同提交。重复提交在不同位置独立分析。本次已在远端全新目录完成从零验收；源码修改与文档均保留在工作区，未因本次整理创建 Git commit 或推送 GitHub。

这套数据用于补丁意图的五分类兼容测评，不是补丁关联关系的人工金标测评，也不包含研究内容二、三的测评。

## 1. 本次修改

下表路径均相对于 `研究内容一/`。

| 文件或目录 | 修改内容 |
|---|---|
| `evaluation/scripts/run_evaluation.py` | 一条命令串联镜像构建、源码恢复、工作区预检、模型连通性检查、五轮独立执行、结果保存与计分；支持并发、续跑和运行失败重试 |
| `evaluation/scripts/benchmark.py` | 冻结数据读取、严格 JSON 契约、11 类到五类映射、准确率、分类别 precision/recall/F1、macro F1 和混淆矩阵 |
| `evaluation/scripts/prepare_sanitized_repo.py` | 为每例建立独立 Git 工作区，净化目标提交标题中的标签前缀，校验 tree 和 parents 不变；兼容共享对象、稀疏检出、纯删除和空树提交 |
| `evaluation/scripts/verify_run.py` | 从冻结输入和原始事件重新核验逐例结果、映射及汇总指标 |
| `evaluation/scripts/container-entrypoint.sh` | 在独立 HOME/XDG 下加载镜像内 Skill，启动 OpenCode |
| `evaluation/config/repositories.json` | 明确数据集仓库名到公开上游 URL 的映射，不依赖旧机器上的源码目录 |
| `evaluation/config/label_mapping.json` | 显式保存五分类兼容映射，避免隐含转换规则 |
| `evaluation/config/opencode.example.json` | 提供模型配置模板，支持通过环境变量提供端点和密钥 |
| `Dockerfile`、`.dockerignore` | 构建 Node 22.18.0、OpenCode 1.18.4、Ctags 等运行环境；补充 ripgrep、Python 命令兼容及新入口路径；构建上下文排除数据集和旧结果 |
| `patch-intent-analysis/scripts/install_ctags.py` | 补充下载超时与有限重试，保留版本和校验和检查 |
| 两个 Skill 的 `SKILL.md` | 调整 Python 调用等运行兼容说明；分类和证据标准继续保留 |
| 项目及 `evaluation/` 下的 README | 补全入口、配置、计分、隔离、续跑和结果核验说明，适配当前目录结构 |

### 源码恢复与从零运行修复

- 同一仓库的选中提交一起获取，避免分批 shallow fetch 令较早目标变成浅边界、导致 diff 被误判为根提交差异。
- 获取目标与父提交的完整源码树，检查 Git 对象连通性和真实父对象，不依赖旧缓存或特定机器目录。
- 在模型调用前，对全部 926 个目标工作区进行实际创建与检出检查。
- 修复纯删除补丁、空目标树、annotated tag、submodule gitlink 和旧 Git 的稀疏检出兼容问题。
- 适配 `evaluation/scripts/` 和 `evaluation/config/` 的新目录布局。

### OpenCode 的执行方式

每条样本使用独立容器和会话，调用 OpenCode 原生工具。Agent 可以读源码、执行 Git、补充获取历史和资料，需要时运行测试；源码视图不再限定为两个固定状态。初始缓存提供目标版本和父提交，工作区默认只检出变化文件，其他源码可通过 Git 读取或扩展检出。

继续保留 Skill 的评审标准、结构化输出契约及过程记录。每例保存任务、净化检查、OpenCode 原始事件、工具调用、最终答案、状态、耗时和尝试记录。数据集、gold 标签和其他样本结果不挂载给 Agent。

容器里的 `/workspace/repo`、`/source-objects`、`/opt/patch-analysis` 等是镜像和挂载约定，程序会自动准备，用户无需在宿主机创建同名目录。临时工作区使用共享对象缓存，不能只复制工作区就当作独立仓库使用。需要可独立搬迁的净化仓库时，使用 [仓库复制工具](scripts/README.md) 的 `--clone-mode full`；这不要求修改一键流程的内部挂载路径。

目标提交标题中的旧分类前缀仍通过 `git replace` 净化，任务禁止绕过替换或查询原始目标标题来获取标签。这是评测约定，Git 原始对象仍存在，不构成防恶意 Agent 的强安全隔离。

## 2. 运行前提

主机需准备：

- Python 3.10+、Git、已启动且当前用户可使用的 Docker 服务。
- 可访问依赖下载源、Git 上游和模型服务的网络；必要时提供自己的代理。
- 有效的 OpenAI-compatible Chat Completions 模型配置及凭据。
- 足够的磁盘与模型服务额度；源码下载、镜像和全部轨迹会占用空间，消耗取决于数据与模型行为。

无需在主机预装 OpenCode、Node、Ctags、Skill 或 Python 第三方包，也无需提前下载被测仓库。“从零”指不依赖旧评测环境、源码缓存或模型答案，不包含自动安装主机 Docker/Git/Python。

本次完整验收平台为 Linux x86_64。执行器使用 POSIX 文件锁和用户 ID 接口，适用于 Linux/macOS 主机，不支持原生 Windows Python。Windows 用户应在 WSL2 中准备 Python、Git 和可访问的 Docker 服务；该组合及 macOS/ARM 尚未完成本次全量验收。Docker Desktop 需允许访问项目、配置和输出所在目录，容器网络也须按所在平台配置。

## 3. 一键运行

### 路径约定与模型配置

以下命令均从本机的 `研究内容一/` 目录执行，项目可放在任意位置，包括包含空格或中文的路径。程序根据脚本位置查找数据和其他项目资源，不要求存在特定的服务器目录。

| 配置 | 默认值或来源 | 如何调整 |
|---|---|---|
| `EVAL_CONFIG` | `evaluation/config/opencode.example.json` | 设置为用户自己的配置文件路径，可用相对或绝对路径 |
| `EVAL_OUTPUT` | `../research1-runs/full` | 设置为项目源码目录之外的可写目录，首次验收选择尚不存在的目录 |
| `MODEL_BASE_URL`、`MODEL_API_KEY` | 当前终端环境 | 使用默认配置模板时必须设置，分别提供模型服务端点和密钥 |

相对的配置和输出路径按当前终端工作目录解析。换一个终端续跑或核验时，需重新设置相同的 `EVAL_CONFIG`、`EVAL_OUTPUT`；不要切换成另一个输出目录。含空格的路径需保留示例中的双引号。

使用已有配置时设置 `EVAL_CONFIG` 即可。没有配置时，使用 [config/opencode.example.json](config/opencode.example.json)；模型 ID、上下文和输出限额必须与实际服务一致。需要修改模板时，建议先复制到项目之外的个人配置目录，例如：

```bash
mkdir -p ../research1-config
cp -n evaluation/config/opencode.example.json ../research1-config/opencode.json
export EVAL_CONFIG="../research1-config/opencode.json"
# 编辑该文件，使模型 ID 和限额与自己的服务一致。
export MODEL_BASE_URL='https://your-model-service.example/v1'
# 在当前终端安全设置并导出 MODEL_API_KEY，勿将实际密钥写入仓库。
```

配置好模型后执行：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config "${EVAL_CONFIG:-evaluation/config/opencode.example.json}" \
  --output "${EVAL_OUTPUT:-../research1-runs/full}" \
  --workers 4
```

默认输出目录与 `研究内容一/` 同级，不会把结果写入源码目录。并发按主机资源和服务额度设置，默认评测并发为 4、下载并发为 3。该命令自动构建运行环境、下载并校验源码、预检工作区、运行五轮并生成结果。首次需要强制无缓存构建时追加 `--rebuild`，它会使用 `--pull --no-cache`；续跑时移除此参数。

上面的域名是占位符，须替换为实际服务。配置支持 `options.apiKey`、`options.baseURL` 的 `{env:NAME}`、`{file:/path}` 引用；相对凭据文件路径相对于配置文件目录解析。额外认证头、OAuth 和非兼容协议暂不支持。生成的专用配置不会继承原配置插件、自定义指令或会话。

旧模型名 `deepseek/deepseek-v4-flash` 显式解析为服务 ID `deepseek-flash`，两者均记录；不会因单例失败而切换模型。

### 代理和模型直连

无代理也能访问下载源和模型时，无需额外参数。若代理在 Linux 主机回环地址，向运行命令追加：

```text
--proxy http://127.0.0.1:YOUR_PROXY_PORT --network host
```

`YOUR_PROXY_PORT` 必须替换成当前可用代理端口。若下载走代理而模型直连，在运行前设置 `NO_PROXY`/`no_proxy`，将实际模型服务主机名和需要保留的原有例外包含进去；例如：

```bash
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}actual-model-host.example,localhost,127.0.0.1"
export no_proxy="$NO_PROXY"
```

`--proxy` 作用于依赖下载、Git 和容器流量；`--git-proxy` 只用于 Git 下载。默认容器使用 bridge 网络，Linux 回环代理才使用上述 host 配置。Docker Desktop 的网络行为需按实际平台配置。

代理地址由用户提供，不依赖维护者机器上的端口或 SSH 隧道。

## 4. 预检、续跑及失败处理

在上述完整命令后追加 `--prepare-only`，可仅构建镜像、恢复源码并预检全部工作区，不调用模型。随后使用相同输入和输出目录、移除 `--prepare-only` 继续运行。

中断后再次执行相同命令即可续跑。首次若用了 `--rebuild`，续跑时必须移除。程序检查输入、实现、映射、模型和实际镜像 ID 的一致性；这些内容变化时使用新输出目录。

| 情况 | 处理方式 |
|---|---|
| 下载、镜像或工作区预检失败 | 查看终端错误、`preparation.json`、`workspace-preflight.json`；修复网络或依赖后重跑 |
| 模型连通性失败 | 查看 `preflight/events.jsonl`、`preflight/stderr.log`，检查端点、凭据、容器网络 |
| 样本运行失败或超时 | 默认最多尝试 2 次；已保存的运行失败可追加 `--retry-errors` 重试 |
| 模型分类错误、未映射标签或无效 JSON | 保留原始结果并计错，不自动重采样 |
| 提示输入、代码、模型或镜像变化 | 使用新输出目录，不将不同协议的结果混合 |

单例超时默认 600 秒，`--timeout 0` 表示不限时；`--attempts` 调整运行失败尝试上限。这些参数属于冻结协议的一部分，续跑不能悄悄改变。`--rounds` 和 `--limit-per-round` 可做小规模烟测，但不能把烟测结果当成全量验收。

退出码：`0` 为所选样本全部完成且无最终运行错误；`1` 为完成但仍有运行错误；`2` 为配置或预检失败；`130` 为中断。退出 `0` 不表示所有分类正确。

## 5. 结果与独立核验

| 输出路径（相对于 `--output`） | 内容 |
|---|---|
| `summary.json` | 五轮汇总、完成状态、准确率、F1、状态计数和混淆矩阵 |
| `round_N/results.jsonl`、`round_N/metrics.json` | 每例结果与本轮指标 |
| `protocol.json`、`runtime.json` | 冻结输入、代码摘要、模型信息和实际镜像 ID |
| `preparation.json`、`workspace-preflight.json` | 源码与全部工作区预检结果 |
| `preflight/` | 模型连通性检查记录 |
| `round_N/traces/case_NNN/attempt-*/` | 每次尝试的任务、事件、工具调用、答案、命令及状态 |

执行器一键运行会计算指标；要独立重算并校验原始事件，执行：

```bash
python3 evaluation/scripts/verify_run.py \
  --output "${EVAL_OUTPUT:-../research1-runs/full}"
```

核验器退出 `0` 表示完整结果通过核验且无运行错误。该核验器用于新测评的输出目录；仓库中的历史交付结果 `evaluation/results/` 继续保留。

## 6. 本次从零验收结果

以下为维护者已完成的验收记录，用户运行时不需要访问原验收机器或其目录。

复制当前源码到全新 `source/`，排除旧结果与 Git 元数据；`run/` 初始不存在，没有复制旧源码缓存或模型答案。随后以 `--rebuild` 无缓存构建、重新下载全部源码、16 路评测并发和 4 路下载并发运行。

| 项目 | 实际结果 |
|---|---|
| 源码恢复 | 14/14 个仓库 |
| 工作区预检 | 926/926，通过；错误 0 |
| 全量执行 | 1,250/1,250；主程序退出码 0 |
| 独立核验 | 1,250 条通过；核验器退出码 0 |
| 正确数与准确率 | 1,068/1,250，85.44% |
| 输出状态 | 1,211 条有效且可映射、28 条未映射、11 条无效 JSON/契约输出 |
| 最终运行错误 | 0 |
| 尝试次数 | 1,254 次；1,246 条一次完成，4 条进行了第二次尝试；首次失败记录保留 |
| 最终会话 | 1,250 个不同会话 |
| 全量用时 | 约 89 分钟，含从零构建和准备；不保证其他环境相同耗时 |
| 实际续跑 | 退出码 0；结果与指标不变，尝试数仍为 1,254，无新增样本调用 |
| 实现一致性 | 验收冻结的 30 个运行文件与当时远端正式目录完全一致 |

| 轮次 | 正确/总数 | 准确率 |
|---|---:|---:|
| 1 | 216/250 | 86.40% |
| 2 | 212/250 | 84.80% |
| 3 | 216/250 | 86.40% |
| 4 | 211/250 | 84.40% |
| 5 | 213/250 | 85.20% |
| 总计 | 1,068/1,250 | 85.44% |

原始验收证据包括 `receipt.json`、`verification.log`、`resume-proof.json`、`run/summary.json` 与 `run/round_N/traces/`，由维护者另行保存。前三项由本次验收包装流程产生，不是一键执行器每次都会生成的文件；用户的新结果应查看自己指定的 `EVAL_OUTPUT`，并使用上一节命令核验。续跑会再次做连通性预检，但已完成的样本不重新调用模型。

### 评分口径

协议为 `opencode_patch_intent_legacy5_v1`：当前 11 类 Skill 输出按 [label_mapping.json](config/label_mapping.json) 转换为旧数据集五类。Feature→feat；BugFix/CVE/资源泄露&crash补丁→fix；Refactor/CleanUp→refactor；Doc/Typo修复→docs；TestCode→test；Optimize/其他无映射，计错。

所有无效、未映射和运行失败均保留在分母。本次 85.44% 不是 11 类人工金标准确率，也不表示复现历史评审程序的 82.4%；不同 harness、模型和输出协议的分数应分别报告。

更多参数和 Git 净化工具用法见 [scripts/README.md](scripts/README.md)。
