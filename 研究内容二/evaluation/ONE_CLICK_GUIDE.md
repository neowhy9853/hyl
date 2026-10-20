# 补丁迁移评测：一键运行指南

本指南说明如何从仓库中的数据和公开源码启动研究内容二评测。统一入口为 `evaluation/scripts/run_evaluation.py`，默认覆盖 Linux 404 条和重点开源项目 92 条，共 496 条。所有命令均在 `研究内容二/` 目录执行。

## 1. 目录与运行前提

| 路径 | 用途 |
|---|---|
| `evaluation/data/` | 数据集、参考补丁、oracle 补丁和固定目标基线补充包 |
| `evaluation/config/` | 公开源码清单与模型配置模板 |
| `evaluation/scripts/` | 统一运行入口、源码准备、容器运行、轨迹导出及结果核验 |
| `evaluation/results/` | 随仓库交付的逐条结果和轨迹 |

主机需要 Python 3.10+、Git、可访问的 Docker 服务，以及能够下载公开源码、镜像依赖并访问模型服务的网络。模型服务须兼容 OpenAI Chat Completions，并支持工具调用。OpenCode、迁移 Skill 和常用编译工具由 Docker 镜像安装，不需要在主机预装。

执行器使用 POSIX 文件锁和用户 ID 接口；Linux 可直接运行，Windows 应使用 WSL2 和可访问的 Docker 服务。macOS 使用 Docker Desktop 时需允许挂载源码、配置及输出目录；不能将 Linux 小样本运行视为其他平台或全部 496 条的验收。完整 Git 历史和多个工作区会占用较多磁盘，运行前应预留空间，并按主机资源与模型并发额度设置并发数。

检查主机依赖：

```bash
python3 --version
git --version
docker version
```

`docker version` 应同时能读取客户端和服务端。仅装有 Docker 命令但服务未启动，不能运行评测。

## 2. 配置模型与输出位置

如果已有可用的 OpenCode JSON 配置，设置其绝对路径即可：

```bash
export EVAL_CONFIG='/absolute/path/to/opencode.json'
export EVAL_OUTPUT="$HOME/research2-runs/full"
```

没有配置时，可复制模板到仓库之外，然后编辑：

```bash
mkdir -p "$HOME/.config/patch-port-evaluation"
cp -n evaluation/config/opencode.example.json "$HOME/.config/patch-port-evaluation/opencode.json"
export EVAL_CONFIG="$HOME/.config/patch-port-evaluation/opencode.json"
export EVAL_OUTPUT="$HOME/research2-runs/full"
```

模板中的 `model` 使用 `provider/model-name` 格式，前半部分对应 `provider` 对象的键，后半部分对应该服务下 `models` 的键。将模型名称、上下文和输出限额改成服务实际支持的值。模板的 `options.baseURL` 和 `options.apiKey` 分别引用 `MODEL_BASE_URL`、`MODEL_API_KEY`；以下命令在 Bash 中交互设置，不把密钥写进仓库：

```bash
read -r -p '模型服务的 Chat Completions 基地址: ' MODEL_BASE_URL
export MODEL_BASE_URL
read -r -s -p '模型 API Key: ' MODEL_API_KEY
export MODEL_API_KEY
printf '\n'
```

也支持 `{file:/absolute/path}` 凭据引用；相对凭据文件路径按配置文件所在目录解析。模型选项可通过 `--model provider/model`、`--judge-model provider/model` 覆盖，评审默认与生成使用同一模型，但采用独立容器和会话。当前兼容映射会将 `deepseek/deepseek-v4-flash` 解析为服务 ID `deepseek-flash`，实际请求模型记录在运行协议中。

`--output` 必须位于研究内容二源码目录之外，且不能是它的上级目录。首次运行使用一个新目录，不要指向仓库内的 `evaluation/results/`。模型调用会将本案例所需的提示词、补丁和源码上下文发送到所配置的服务，并产生该服务的调用费用。

## 3. 一键运行全部 496 条

完成上面的路径和模型配置后，执行：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config "$EVAL_CONFIG" \
  --output "$EVAL_OUTPUT" \
  --workers 2 \
  --fetch-workers 3
```

一条命令依次完成以下步骤：

1. 检查 Docker，构建或复用与当前 Skill 和构建文件对应的镜像，检查 OpenCode 运行参数。
2. 读取并固定全部 496 条输入、实现哈希、镜像 ID 和模型参数，保存 `protocol.json`。
3. 下载所需公开 Git 历史，导入目标基线补充包，核对提交、补丁及完整文件树。源码准备阶段结束后才开始模型任务；Linux 历史下载较慢时，模型阶段也会等待。
4. 检查模型连通性。为每例导出独立源码仓库，只提供参考修复与目标版本的允许历史，排除 oracle 提交和其他案例。
5. 向 OpenCode 提交总控 Skill 任务，由 Agent 按 Skill 契约执行分析、按需依赖调查、实施和验证，生成候选补丁。
6. 在固定目标基线上应用候选，并按结果树或独立语义审查判分。
7. 保存每例 `input.json`、`result.json`、`trace.jsonl`，更新分组指标和总统计，默认清理该例的临时工作区。

阶段 Skill 由 Agent 根据任务执行，外层执行器并不把每个 Skill 的阶段门禁实现为强制状态机。评测得分依据下面的 oracle 等价性规则；是否调用具体 Skill、运行哪些编译或测试，以逐条 trace 和阶段证据为准。

## 4. 小样本、准备检查与首次重建

先运行四个不同项目的案例，输出使用另一个新目录：

```bash
export EVAL_SMOKE_OUTPUT="$HOME/research2-runs/smoke"
python3 evaluation/scripts/run_evaluation.py \
  --config "$EVAL_CONFIG" \
  --output "$EVAL_SMOKE_OUTPUT" \
  --case-ids oe-01-libxml2,oe-22-python3,oe-50-git,oe-70-dnsmasq \
  --workers 2 \
  --fetch-workers 3
```

`--case-ids` 只选择指定记录，不代表全量覆盖。`--datasets linux` 或 `--datasets projects` 可只运行一组。小样本与全量运行必须使用不同输出目录，因为案例集合属于固定协议。

只检查全部源码准备，不调用模型：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --output "$EVAL_OUTPUT" \
  --prepare-only \
  --fetch-workers 3
```

随后使用第 3 节相同输出目录及相同案例选择运行，可继续模型阶段。准备检查仍会构建镜像和下载源码。需要从空缓存验收时，选择全新的输出目录；还需完全重建镜像时，在首次命令后追加 `--rebuild`。续跑时不要再次加 `--rebuild`，以免新镜像 ID 与固定协议不一致。

## 5. 判分与结果含义

方法标识为 `patch_port_oracle_equivalence_v1`：

| 情况 | 判定 |
|---|---|
| 有效候选无法应用到固定目标基线 | `incorrect` |
| 应用候选得到的完整代码树与 oracle 完全一致 | `correct`，依据为 `result_tree_identical` |
| 代码树不同，但独立审查确认所有功能修复义务等价且没有有害额外改动 | `correct`，依据为 `agent_semantic_review` |
| 独立审查发现漏改或错误 | `incorrect` |
| 独立审查的重要证据不足 | `uncertain` |
| 生成过程正常结束但没有非空候选补丁 | `generation_failed` |
| 源码准备、生成进程或评审过程出错 | `preparation_error`、`generation_error`、`judge_error` |

纯说明文字或无行为影响的格式差异可以通过语义等价审查。评审必须调查源码并给出修复义务与证据，不能仅因补丁可应用就判正确。正确率为正确数除以全部选定案例数，失败与不确定项不会从分母删除。

该分数表示 oracle 修复等价性，不等于所有构建和测试通过，也不保证重新执行得到与交付结果相同的分数。独立审查仍是模型判断。小样本通过不能证明全部 496 条、Linux 源码下载、复杂依赖迁移或长时间运行均无异常。

## 6. 输出位置与核验

```text
<output>/
├── protocol.json
├── preparation.json
├── summary.json
├── cache/
├── preparation/
├── preflight/
├── work/
└── results/
    ├── README.md
    ├── linux/
    │   ├── results.jsonl
    │   ├── metrics.json
    │   └── cases/<case_id>/
    │       ├── input.json
    │       ├── result.json
    │       └── trace.jsonl
    └── projects/                 # 相同结构
```

运行根目录还包含模型运行配置、文件锁和按需生成的构建日志，属于执行辅助文件；每个已完成案例目录恰好包含上述三个文件。`input.json` 中的 `task_input` 是生成输入，`evaluation_reference` 是评分参考；这个汇总文件不挂载给生成模型。`result.json` 保存实际候选补丁、判定、依据及哈希。

新运行的 trace 为 schema 2：第一行是 `manifest`，`event` 通过 `stage` 区分生成和评审并保留阶段内顺序，`artifact` 保存运行日志、查询和验证产物。相同内容通过 `content_ref` 引用，二进制证据采用 base64。Trace 保存 OpenCode 可见的模型文本、工具调用和返回，不补写服务未公开的内部推理，也不重复打包整个源码工作区。

核验全量新输出：

```bash
python3 evaluation/scripts/verify_run.py --output "$EVAL_OUTPUT"
```

核验上面的小样本输出：

```bash
python3 evaluation/scripts/verify_run.py --output "$EVAL_SMOKE_OUTPUT"
```

核验器检查逐条三文件结构、输入和 trace 哈希、嵌入证据、候选补丁及统计一致性。运行进度和计分见 `<output>/summary.json`，组内指标见 `<output>/results/<dataset>/metrics.json`。核验通过不替代对具体测试证据的阅读。

核验仓库中随附的固定 496 条结果使用另一个入口：

```bash
python3 evaluation/scripts/verify_saved_results.py
```

该脚本核对当前交付快照的 schema 1 轨迹和固定统计，不能用来核验新模型运行。交付目录说明见 [results/README.md](results/README.md)。

## 7. 续跑、网络与失败处理

重复执行同一命令会先核对固定协议，然后验证并跳过已完成案例。案例选择、数据、实现、模型参数、超时或实际镜像 ID 改变时，应改用新的输出目录，不能与已有结果混跑。

对已保存的基础设施错误显式重试：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config "$EVAL_CONFIG" \
  --output "$EVAL_OUTPUT" \
  --workers 2 \
  --fetch-workers 3 \
  --retry-errors
```

前次错误轨迹保留在新 trace 中。该选项不会为了提高分数重试 `incorrect`、`uncertain` 或 `generation_failed`。若原运行选择了小样本或单一数据集，续跑也必须带回相同选择参数。

| 现象 | 检查与处理 |
|---|---|
| Docker 不可用或挂载失败 | 启动 Docker，确认当前用户能访问服务，以及源码、配置和输出路径可挂载 |
| 镜像构建失败 | 查看输出根目录的 `build.log`，检查基础镜像和依赖下载网络 |
| 源码准备长时间无完成记录 | 查看控制台 `fetch/source_ready` 进度和 `preparation/`；完整 Linux 历史可能很大，不应误判为模型已运行 |
| Git 下载超时或源不可达 | 修复网络后使用相同配置续跑；必要时明确配置代理或镜像。当前 Git 命令超时上限为两小时，没有自动挑选备用镜像，也不承诺未完成传输可按字节续传 |
| 模型连通性检查失败 | 查看 `preflight/` 的事件、错误日志和结果，检查服务地址、模型名、凭据及容器网络 |
| 单例失败或不确定 | 查看该例 `result.json` 和 `trace.jsonl`，区分进程错误、补丁错误与证据不足 |
| 提示 `resume protocol changed` | 恢复原有配置和实现，或使用全新输出目录；不要手工修改协议文件绕过核对 |

`--proxy http://your-proxy:port` 将调用者指定的代理用于依赖下载、Git 和容器请求。Linux 宿主回环代理可配合 `--network host`，默认网络为 `bridge`。主机能访问模型不代表容器也能访问。

需要源码镜像时，复制 `evaluation/config/sources.json` 并仅替换对应仓库地址，通过 `--sources /absolute/path/to/sources.json` 指定，仍须满足固定提交、基线和补丁校验。变更源码清单应使用新输出目录。生成容器默认可联网访问模型；oracle 隔离通过仓库导出和挂载控制实现，任务也禁止外部答案查询，但没有把容器网络限制为仅能访问模型服务。

## 8. 常用选项

| 参数 | 用途 |
|---|---|
| `--workers 2` | 并行案例数 |
| `--fetch-workers 3` | 并行源码准备数 |
| `--timeout 1800` | 每例生成超时，单位秒；`0` 表示不设超时 |
| `--review-timeout 1800` | 每例独立审查超时，单位秒；`0` 表示不设超时 |
| `--keep-workspaces` | 保留案例临时工作区供调试，额外占用磁盘 |
| `--data /path` | 自定义数据目录，仍按当前数据集契约校验 |
| `--sources /path/to/sources.json` | 自定义源码来源清单 |
| `--rebuild` | 首次运行时无缓存重建镜像并拉取基础镜像 |

更多参数可执行 `python3 evaluation/scripts/run_evaluation.py --help`。退出码 `0` 表示全部所选案例完成且无基础设施错误，并不表示全部正确；`1` 表示存在基础设施错误；`2` 表示启动配置或批次预检失败。
