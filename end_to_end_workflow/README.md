# 补丁端到端处理流程（End-to-End Patch Workflow）

统一入口为 `end_to_end_workflow/run_case.py`。默认从仓库 URL 下载源码、恢复目标版本、自动构建 Docker 环境，然后依次执行意图分析、补丁迁移与验证、兼容性分析与定向测试。新案例直接传入参数，无需新增 `case.json` 或 `run.sh`。

## 目录说明

| 文件 | 职责 |
|---|---|
| `run_case.py` | 统一入口，编排意图分析、补丁迁移与验证、兼容性分析与定向测试 |
| `bootstrap.py` | 下载源码、恢复目标基线、准备模型配置及 Docker 环境，再启动工作流 |
| `Dockerfile` | 定义工作流的通用运行环境 |
| `opencode.example.json` | 模型服务配置模板 |
| `libxml2-cve-2024-34459/` | 已有真实案例的参数、运行说明和历史结果 |

新案例直接调用 `end_to_end_workflow/run_case.py`，无需新增专用脚本。`bootstrap.py` 由入口自动调用；已有原生环境时使用 `--local`。

## 1. 主机需要准备什么

- Python 3.10+、Git，以及正在运行且当前用户可访问的 Docker 服务。
- Docker Buildx；镜像构建使用 BuildKit 的缓存挂载。已有匹配镜像时不会要求重新构建。
- 可访问源码、镜像和依赖下载源、模型服务的网络，以及足够保存完整 Git 历史和构建工作区的磁盘空间。
- 支持工具调用的 OpenAI Chat Completions 兼容模型服务配置。
- 上游仓库 URL、修复提交，以及下游仓库/目标版本信息。仅有一个 SHA 无法凭空恢复不存在于公开仓库中的私有下游源码。

默认模式不要求主机安装 OpenCode、Node.js 或项目编译工具。Dockerfile 安装 OpenCode、Python、C/C++ 编译器、常用构建工具及基础库。特殊项目依赖可用 `--dockerfile` 指定自定义 Dockerfile；它应保留 `/usr/local/bin/opencode`、`/usr/bin/rg`、Python 3 和运行所需工具。构建上下文仅含该 Dockerfile，应在 Dockerfile 中下载安装依赖，而不是 COPY 主机私有文件。

Linux 可直接运行；Windows 使用 WSL2 和可访问的 Docker 服务。macOS Docker Desktop 需允许挂载输入和输出目录；真实验收在 Linux 上进行，不代表所有平台已验收。

```bash
python3 --version
git --version
docker version
docker buildx version
```

## 2. 模型配置

已有 OpenCode JSON 配置时设置其路径即可：

```bash
export EVAL_CONFIG='/absolute/path/to/opencode.json'
export WORKFLOW_OUTPUT="$HOME/hyl-runs/new-case"
```

也可以复制 [opencode.example.json](opencode.example.json) 到仓库外，设置实际 `provider/model`、API 模型 ID、上下文及输出限额，再提供模板引用的环境变量：

```bash
mkdir -p "$HOME/.config/hyl-workflow"
cp -n end_to_end_workflow/opencode.example.json "$HOME/.config/hyl-workflow/opencode.json"
export EVAL_CONFIG="$HOME/.config/hyl-workflow/opencode.json"
read -r -p '模型 API 基地址: ' MODEL_BASE_URL
export MODEL_BASE_URL
read -r -s -p '模型 API Key: ' MODEL_API_KEY
export MODEL_API_KEY
printf '\n'
```

以上交互命令使用 Bash。支持 `options.baseURL`、`options.apiKey` 的字面值、`{env:NAME}` 和 `{file:path}`；相对文件路径按配置文件所在目录解析。运行器在主机解析所选模型的连接信息，将凭据通过环境变量传入容器；输出配置只保存环境变量引用，不复制原配置中的插件、自定义指令或凭据。OAuth、额外认证头及非 OpenAI-compatible 协议不在此入口支持范围内。

模型会接收任务所需的补丁、源码和提示词，并产生服务费用。可以用 `--model provider/model` 覆盖默认模型，或用 `--intent-model`、`--port-model`、`--compatibility-model` 分别设置三个阶段。旧名称 `deepseek/deepseek-v4-flash` 显式映射到服务 ID `deepseek-flash`，实际模型记录在 `bootstrap.json`。

## 3. 从 URL 一键运行新 case

在工具仓库根目录执行，将示例参数替换成实际值：

```bash
python3 end_to_end_workflow/run_case.py \
  --source-url https://github.com/OWNER/PROJECT.git \
  --commit UPSTREAM_FIX_COMMIT \
  --target-ref DOWNSTREAM_BASE_COMMIT \
  --config "$EVAL_CONFIG" \
  --output "$WORKFLOW_OUTPUT"
```

目标版本默认从同一个上游仓库获取。默认完整保留所选提交的祖先历史，不使用浅克隆；支持提交 SHA、远端可获取的分支或 tag，固定实验建议使用完整 SHA。

目标在另一个仓库时增加 `--target-url https://...`。两个仓库没有共同历史时增加 `--port-mode cross_repo_semantic`；共享历史则使用默认 `history`。也支持 `--source-repo`、`--target-repo` 读取已有本地仓库，此时仍默认自动准备 Docker 环境，并将输入复制到独立对象库，不修改原仓库。

运行器自动完成：

1. 检查参数和 Docker；解析模型连接信息。
2. 下载源码与参考提交，获取下游目标版本；下载失败默认重试三次并保存日志。
3. 必要时导入目标基线包，校验其 SHA-256、目标提交和源码树。
4. 构建或复用与 Dockerfile 哈希对应的运行镜像；需要构建时先检查 Docker Buildx，并显式启用 BuildKit。随后将本次实际 Skill 和入口复制到隔离运行目录。
5. 启动隔离容器，执行内容一。只有分类为 `CVE` 才继续，这是现有流程门槛。
6. 内容二先严格检查原补丁能否应用；成功则直接合入，不调用内容二模型、语义评审或构建测试。失败才进入分析、实施和独立验证。两条分支成功后，编排层均重放实际补丁确认基线一致。
7. 将实际候选补丁和指定下游基线交给内容三，执行兼容性分析与定向测试，保存总状态及阶段证据。

容器不挂载宿主 Docker 套接字；输入对象库只读，源码变更、编译及测试在本次输出目录内完成。流程不会提交或推送原仓库。

### 构建与测试命令

`--validation-command` 显式指定内容二的项目构建/测试命令，可重复传入。例如：

```text
--validation-command './configure --without-python && make -j2'
--validation-command 'make check'
```

这些命令仅在内容二需要适配的分支中执行，结果及退出码写入验证证据。严格直接合入分支跳过这些命令。省略时，编排器不自动补充项目专属构建/测试命令；Agent 仍可按 Skill 调查和执行检查，但不能据此保证已完成项目测试。它不控制内容三的定向测试。缺少重要依赖或证据时应输出 blocked/partial，不能将未执行测试当成通过。

### 目标基线不在上游仓库时

已交付的项目基线通过 `研究内容二/evaluation/config/sources.json` 按上游 URL、修复提交和目标提交精确匹配；运行器自动导入对应 `data/baselines/` 包并校验哈希和目标树。它不读取历史结果或 oracle 补丁，也不生成评分答案。

新案例可以提供下游仓库 URL，或额外指定：

```text
--target-bundle /absolute/path/to/downstream.bundle
--target-bundle-ref refs/heads/downstream-base
--target-tree EXPECTED_TREE_SHA
```

基线包也可为 HTTP(S) URL，此时必须同时提供 `--target-bundle-sha256`。本地基线包也建议提供哈希。增量包的前置提交必须包含在下载的仓库历史中，否则 `git bundle verify` 会报错。`--target-ref` 始终是补丁合入前的目标版本；基线包 ref 不能用不同提交替代它。

## 4. 可直接运行的 libxml2 案例

无需先 clone 仓库、手动导入 bundle 或预先构建镜像：

```bash
python3 end_to_end_workflow/run_case.py \
  --source-url https://github.com/GNOME/libxml2.git \
  --commit 2876ac5392a4e891b81e40e592c3ac6cb46016ce \
  --target-ref 196920f60f41dd72db57afd88b4d1b25017ba80f \
  --config "$EVAL_CONFIG" \
  --profile libxml2 \
  --validation-command './configure --without-python && make -j2' \
  --validation-command 'make check' \
  --output "$WORKFLOW_OUTPUT"
```

该目标提交属于下游发行版基线，入口会自动导入随交付数据提供的包。案例说明见 [libxml2 README](libxml2-cve-2024-34459/README.md)。不要将此案例的构建命令用于任意其他项目。

## 5. 预检、重试和网络

- `--dry-run`：只显示计划，不联网、不创建输出、不调用模型，也不证明远程提交可获取。
- `--prepare-only`：下载源码、恢复基线并构建镜像，不调用模型，不要求 `--config`。使用相同输入和输出目录移除该参数可继续运行。
- `--rebuild`：刷新基础镜像并禁用镜像层缓存；APT 依赖下载缓存仍保留，用于恢复短暂下载失败。普通运行会自动复用匹配镜像，无需此参数。
- `--download-attempts 3`、`--download-timeout 7200`：控制 Git 下载重试次数和每次超时。
- `--timeout 3600`：每个研究内容的模型阶段超时。

首次构建及使用 `--rebuild` 时需要 `docker buildx version` 成功。入口会在构建前检查，并设置 `DOCKER_BUILDKIT=1`；缺少 Buildx 时会直接给出安装或启用提示，不会等到 Dockerfile 执行中途才失败。

若准备阶段失败，相同命令可以继续使用本次已经下载的对象。输入参数变化请使用新输出目录。若已经存在 `run/`，入口拒绝重跑以保护阶段证据；目前不支持模型阶段断点续跑，重新执行应使用另一个新目录。

默认 bridge 网络。Linux 宿主回环代理可增加：

```text
--proxy http://127.0.0.1:YOUR_PROXY_PORT --network host
```

代理用于 Git 下载、Docker build 以及运行容器；host 网络同时用于镜像构建和运行。无需代理时不要添加上述参数。模型需直连时，在启动前将其实际主机名加入 `NO_PROXY`/`no_proxy`。Docker Desktop 的 host 网络行为需按本机设置确认。

## 6. 输出是什么

所有内容保存在 `--output` 指定的新目录：

```text
<output>/
├── bootstrap.json               # 准备/启动总状态、输入、镜像及实际模型
├── preparation.json             # 已解析的源提交、目标提交、源码树和基线包哈希
├── command.json                 # 容器启动参数，不含凭据值
├── build.log                    # 需要构建镜像时生成
├── pipeline.log                 # 三阶段入口日志
├── preparation/                 # 各次源码下载日志
├── inputs/                      # 本次独立下载的 Git 对象库及目标基线包
├── runtime/                     # 工具/Skill 快照、无密钥模型配置和运行环境
└── run/
    ├── pipeline-result.json     # 三阶段总状态、停止原因和阶段结果
    ├── reference.patch          # 上游修复提交的真实 diff
    ├── intent/                  # result.json、prompt.txt、events.jsonl 等
    ├── port/
    │   ├── final.json
    │   ├── generated.patch
    │   ├── port-analysis.json    # 仅适配分支生成
    │   └── details/             # 分析、实施、验证及其证据
    ├── compatibility/
    │   ├── analysis.json
    │   ├── patch.diff
    │   └── compatibility-testing/
    │       ├── test-summary.json
    │       └── COVERAGE_REPORT.md
    ├── source-repo/             # 上游修复版本的隔离工作区
    ├── target-repo/             # 下游基线的隔离工作区
    ├── replay-check/            # 编排层独立补丁重放
    └── agent-workspace/
```

内容二严格直接合入时，`port/final.json` 记录 `completion_mode=direct_apply`，分析与独立验证门禁为 `not_run`；`port/details/direct-apply.json` 保存目标、补丁哈希和应用记录。此分支成功后仍进入内容三。

先看 `bootstrap.json` 是否完成准备及启动，再看 `run/pipeline-result.json`。`success` 表示三个阶段门禁均通过；`skipped_non_cve` 表示分类后按规则停止；`blocked` 表示证据或环境不足；`failed` 表示迁移或兼容性检查失败；`error` 表示输入、运行或产物契约错误。退出码 0 也可能是正常筛出或 no_change，不能代替检查最终状态。

产物中的 `/pipeline-work/...` 和 `/opt/hyl/...` 是统一的容器路径，不依赖维护者服务器。保留 `inputs/` 才能继续使用依赖它的隔离 Git 工作区。整个目录可归档；在另一处重新执行请使用同一命令创建新输出。

## 7. 已准备好原生环境时

兼容已有本地运行方式，显式使用 `--local`：

```bash
python3 end_to_end_workflow/run_case.py --local \
  --source-repo /absolute/path/to/repository \
  --commit UPSTREAM_FIX_COMMIT \
  --target-ref DOWNSTREAM_BASE_COMMIT \
  --config "$EVAL_CONFIG" \
  --opencode "$(command -v opencode)" \
  --output /absolute/path/to/new-local-run
```

此模式需要主机已具备 OpenCode、项目依赖和所需 Git 对象，不下载源码或构建镜像；其 `pipeline-result.json` 直接位于 `--output` 根目录。`--dry-run` 在此模式会解析已有提交并写入执行计划。
