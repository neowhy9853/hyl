# 评测脚本

以下命令从 `研究内容一/` 目录执行。

本次修改、首次配置、代理示例和全量验收记录见 [一键测评说明](../ONE_CLICK_GUIDE.md)。

| 文件 | 用途 |
|---|---|
| `run_evaluation.py` | 构建运行环境、准备源码、执行分类评测并计算指标 |
| `benchmark.py` | 数据读取、模型输出解析、标签映射和计分公共逻辑 |
| `prepare_sanitized_repo.py` | 创建仓库副本并处理目标 commit message 的标签前缀 |
| `verify_run.py` | 从执行器保存的输入和轨迹重新核验逐条结果与指标 |
| `container-entrypoint.sh` | 容器内的 OpenCode 启动入口 |

## 批量运行分类评测

Linux/macOS 主机需 Python 3.10+、Git、可用的 Docker 服务和网络，以及调用者自己的 OpenAI-compatible 模型服务配置。无需安装 OpenCode、Python 第三方包、Skill 或 Ctags，也无需预先下载被测仓库。在 `研究内容一/` 目录运行：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config "${EVAL_CONFIG:-evaluation/config/opencode.example.json}" \
  --output "${EVAL_OUTPUT:-../research1-runs/full}" \
  --workers 4
```

运行前按 [一键测评说明](../ONE_CLICK_GUIDE.md) 设置模型端点和密钥。`EVAL_CONFIG` 可指定自己的配置，`EVAL_OUTPUT` 可指定项目外的输出目录；不设置时使用上述默认值。相对路径按当前工作目录解析，核验和续跑需保持相同配置。

本次完整验收平台为 Linux x86_64。执行器使用 POSIX 文件锁和用户 ID 接口，适用于 Linux/macOS 主机，不支持原生 Windows Python。Windows 用户应在 WSL2 中准备 Python、Git 和可访问的 Docker 服务；该组合及 macOS/ARM 尚未完成本次全量验收。Docker Desktop 需允许访问项目、配置和输出所在目录，容器网络也须按所在平台配置。

这一条命令会构建固定版本 Docker 镜像、从 `evaluation/config/repositories.json` 下载全部 14 个仓库中所需的 926 个不同 commit 及父提交、校验对象及目标版本和父提交的完整源码树、逐个验证全部独立工作区能正确检出，再检查模型服务、独立执行五轮共 1,250 个位置，保存完整工具轨迹并计算准确率、分类别 precision/recall/F1 和混淆矩阵。重复 commit 仍各自执行，不缓存模型答案。

`--output` 必须位于项目源码目录之外。模型配置示例见 `evaluation/config/opencode.example.json`，支持 `options.apiKey`、`options.baseURL` 的 `{env:NAME}` 和 `{file:/path}` 引用；相对凭据文件路径相对于配置文件目录解析。模型端点采用 OpenAI-compatible Chat Completions 协议。额外认证头、OAuth 或不兼容协议尚不支持。调用此命令即请求将评测所需的补丁和源码发送给指定模型服务。

配置中的 `deepseek/deepseek-v4-flash` 会解析为服务模型 ID `deepseek-flash`，请求名和最终 ID 均记录在协议中。也可用 `--model provider/model` 显式指定模型；不会在单个样本失败后切换模型。专用 provider 和会话独立创建，不继承原配置插件、自定义指令或旧会话，密钥不写入生成的配置和协议。

### 运行选项

- 默认运行全部五轮。`--rounds 1,3` 选择轮次；`--limit-per-round 1` 仅用于快速烟测，不代表完整评测。
- `--prepare-only` 只构建环境、准备全部源码对象并逐例检查工作区，不调用模型；随后使用相同参数并补上 `--config` 可继续执行。
- `--workers` 控制独立评测容器并发，`--fetch-workers` 控制仓库下载并发。默认分别为 4 和 3；结合 CPU、磁盘、网络及服务并发额度设置。
- `--rebuild` 强制无缓存构建并拉取基础镜像。用于从零验收时应同时选用全新的输出目录。
- `--timeout 600` 是单例总秒数，`0` 表示不设超时。默认基础设施失败最多尝试 2 次，可用 `--attempts` 调整。不会重试分类错误、未映射标签或无效模型 JSON 来提高分数。
- 除去首次验收用的 `--rebuild` 后，相同命令再次执行会续跑；续跑不要重建镜像，否则实际镜像 ID 变化会触发拒绝混跑。`--retry-errors` 重试已保存的基础设施错误。输入、代码、映射、模型或实际容器镜像变化时拒绝混跑，需新输出目录。
- `--proxy http://your-proxy:port` 将代理用于依赖下载、Git 和容器模型访问；也支持标准 HTTP_PROXY/HTTPS_PROXY/NO_PROXY 环境变量。代理位于 Linux 宿主机回环地址时，需加 `--network host`；默认使用 bridge 网络。代理地址由调用者提供，不写死在源码中。
- `--git-proxy http://your-proxy:port` 仅在需要 Git 下载代理时指定，无内置机器地址。模型服务需从容器网络可达；宿主机 `localhost` 服务需自行提供容器可访问的地址。
- `--repositories` 支持替换仓库清单；每个条目是数据中的仓库名到 `{"url":"..."}` 的映射。离线或私有镜像可以使用自建 Git 服务，预检仍严格校验原始 commit ID，不能用同名仓库或近似版本替代。

### 标签与计分

执行协议为 `opencode_patch_intent_legacy5_v1`，使用当前 OpenCode 和 `patch-intent-analysis` 的完整 11 类输出，按冻结的 `evaluation/config/label_mapping.json` 汇总为数据集的五类：

| 当前输出 | 兼容标签 |
|---|---|
| `Feature` | `feat` |
| `BugFix`、`CVE`、`资源泄露&crash补丁` | `fix` |
| `Refactor`、`CleanUp` | `refactor` |
| `Doc`、`Typo修复` | `docs` |
| `TestCode` | `test` |
| `Optimize`、`其他` | 未映射，计为错误 |

该映射用于五分类兼容评测，不能据此计算 11 类人工金标准确率。所有失败和无效输出保留在分母；不会筛掉困难样本。原始 11 类结论始终保留，可独立分析分类差异。

### 样本隔离与证据

每例以空 HOME/XDG 启动独立容器，只挂载自己的任务工作区、当前仓库的只读对象缓存和专用模型配置。数据集、gold 标签、其他样本答案、旧结果均不挂载给 Agent。缓存保存目标版本和父提交的完整源码树，历史按 depth=2 获取；Agent 需要更早历史时可自行 fetch。稀疏工作区只检出目标 commit 的变化文件以控制磁盘开销，其他文件仍可通过原生 Git 查询或扩展检出，任务明确提醒不能将工作区缺失当作源码不存在。

保留现有 `git replace` 的 message 前缀净化语义。任务明确禁止绕过替换或网上查询目标 commit 的原始标题；这仍是评测约定，不是防恶意 Agent 的强安全边界，Git 原始对象本身保留在对象库。不能把此协议描述为完全去除潜在标签线索。

每例保存原始 OpenCode 事件、工具输入输出、最终文本/JSON、净化检查、运行命令、状态和耗时。容器输出日志对已知服务密钥做字面脱敏。不承诺保存 provider 未暴露的内部推理或每次 HTTP 原始响应。工作区默认在完成后删除，`--keep-workspaces` 可保留；源码对象缓存与所有评测轨迹保留以便复核。

### 验收和退出状态

```bash
python3 evaluation/scripts/verify_run.py \
  --output "${EVAL_OUTPUT:-../research1-runs/full}"
```

`verify_run.py` 根据冻结输入、原始事件中的最终答案及映射重新计算每例结果和全部指标，检查样本重复/缺失、轨迹一致性和无效接受。它核验执行器输出目录，不适用于历史交付目录中的五轮结果。

执行器退出 `0` 表示所有选定样本完成且没有基础设施错误，不表示全部分类正确；`1` 表示样本完成但仍有基础设施错误；`2` 表示预检或批次配置失败。机器可读结果见输出目录的 `summary.json`、`round_N/results.jsonl`、`round_N/metrics.json`。`protocol.json` 绑定输入与实现，`preparation.json` 记录仓库校验结果，`workspace-preflight.json` 记录全部目标工作区预检，`preflight/` 记录真实模型连通性检查，`round_N/traces/case_NNN/attempt-*/` 保存每次尝试。

## 仓库复制与 commit message 替换

[`prepare_sanitized_repo.py`](prepare_sanitized_repo.py) 实现以下流程：

1. 从源 Git 仓库创建一个新的 clone，不修改源仓库。
2. 解析目标 commit 的完整 SHA 和原始 commit object。
3. 默认只移除 message 第一行开头的旧分类标签，例如 `feat:`、`fix(scope):`、`docs!:`。
4. 保留 commit object 的原始 headers，因此 tree、parents、author、committer 等信息不变。
5. 写入新的 commit object，并在 clone 中执行 `git replace <原始 commit> <新 commit>`。
6. 校验普通 Git 视图与原始对象的 tree、parents 完全一致。
7. detached checkout 到目标 commit，供 OpenCode 或其他评测程序分析。

以下三种创建示例择一使用；每次创建必须指定一个尚不存在的输出目录。先设置用户自己的源仓库和目标提交，`SANITIZED_REPO` 默认写到项目之外：

```bash
: "${SOURCE_REPO:?请先设置本机源 Git 仓库路径}"
: "${COMMIT_ID:?请先设置目标 commit ID}"
SANITIZED_REPO="${SANITIZED_REPO:-../research1-runs/sanitized-repo}"
```

创建快速共享 clone：

```bash
python3 evaluation/scripts/prepare_sanitized_repo.py \
  --source-repo "$SOURCE_REPO" \
  --commit "$COMMIT_ID" \
  --output-repo "$SANITIZED_REPO" \
  --clone-mode shared
```

创建不依赖源仓库对象目录的完整 clone：

```bash
python3 evaluation/scripts/prepare_sanitized_repo.py \
  --source-repo "$SOURCE_REPO" \
  --commit "$COMMIT_ID" \
  --output-repo "$SANITIZED_REPO" \
  --clone-mode full
```

使用自定义 message：

```bash
python3 evaluation/scripts/prepare_sanitized_repo.py \
  --source-repo "$SOURCE_REPO" \
  --commit "$COMMIT_ID" \
  --output-repo "$SANITIZED_REPO" \
  --message-file "${MESSAGE_FILE:?请设置替换 message 文件路径}"
```

输出目录必须尚不存在。`shared` 模式速度快，会引用当前源仓库的对象目录；移动或删除源目录后，共享副本可能无法使用。`full` 模式复制 Git 对象，适合独立保留或搬迁到其他机器；复制后如需继续 fetch，另行配置目标机器可达的 Git remote。原始审计记录中的绝对路径仅记录创建来源，不是要求新机器保留的目录。

普通 Git 命令会读取替换后的 message：

```bash
git -C "$SANITIZED_REPO" show -s --format=%B "$COMMIT_ID"
```

`git replace` 是评测视图隔离，不是安全边界。`--no-replace-objects`、`GIT_NO_REPLACE_OBJECTS` 或直接读取原始 object 都能绕过替换。运行评测 Agent 时必须禁止这些绕过方式，也不能把原始标签作为 prompt、文件名或其他元数据暴露给模型。
