# 华为胡杨林——研究内容一：补丁意图与关联关系分析

## 项目概述

研究内容一面向开源软件补丁的语义理解，提供两个可独立使用的 OpenCode Skill：

| Skill | 核心能力 | 主要输出 |
|---|---|---|
| `patch-intent-analysis` | 分析单个 commit 的修改意图和问题级别 | 补丁类型、问题级别、修改概述、详细分析及证据 |
| `patch-relation-analysis` | 分析两个或多个 commit 的关联关系和依赖方向 | 关系类型、关系分数、依赖方向、聚类结果及证据 |

仅依据 commit 标题中的 `fix`、`feat`、`docs` 等关键词，难以准确识别补丁的真实意图、问题级别及潜在影响。`patch-intent-analysis` 综合 commit message、变更文件、完整 patch 和源码上下文进行判断，并给出结构化分析结论。

`patch-relation-analysis` 根据 CVE、issue、`Fixes:`、upstream、backport、cherry-pick、代码符号和语义证据，判断调用者给出的 commit 是否相关，以及候选 commit 相对于目标 commit 的依赖方向。

两个 Skill 职责独立，不会自动互相调用。关联分析只处理调用者提供的 commit，不负责从仓库中自动发现候选 commit。

## 目录结构

| 路径 | 内容 | 用途 |
|---|---|---|
| `README.md` | 项目说明 | 介绍两个 Skill 的能力、输入输出、安装方式和运行方式 |
| `Dockerfile` | 容器构建文件 | 构建预装 OpenCode、运行依赖和两个 Skill 的镜像 |
| `.dockerignore` | Docker 构建过滤规则 | 只将 Dockerfile 和两个 Skill 加入构建上下文 |
| `patch-intent-analysis/` | 补丁意图分析 Skill | 定义单个 commit 的补丁类型、问题级别、证据规则和 JSON 输出契约，并提供依赖检查与静态分析脚本 |
| `patch-relation-analysis/` | 补丁关联分析 Skill | 定义 commit 之间的关系类型、分数、依赖方向和 JSON 输出契约，并提供关联证据提取脚本 |
| `evaluation/` | 补丁分类评测材料 | 包含基础 commit 数据、多轮均衡评测样本、commit message 净化工具及使用说明 |

## 完整分类测评

本次修改清单、从零运行、续跑与完整验收结果见 [一键测评说明](evaluation/ONE_CLICK_GUIDE.md)。

主机安装 Python 3.10+、Git 和 Docker，并按 [一键测评说明](evaluation/ONE_CLICK_GUIDE.md) 配置模型后，在本目录执行以下一条命令。它会自动构建运行环境、下载并校验评测源码、运行五轮 1,250 个位置并输出成绩与轨迹：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config "${EVAL_CONFIG:-evaluation/config/opencode.example.json}" \
  --output "${EVAL_OUTPUT:-../research1-runs/full}" \
  --workers 4
```

`EVAL_CONFIG` 和 `EVAL_OUTPUT` 分别覆盖配置与输出路径；默认使用仓库模型配置模板，并把结果写到项目之外的 `../research1-runs/full`。模板需提供 `MODEL_BASE_URL` 和 `MODEL_API_KEY`，模型 ID 须与服务匹配。执行器支持 POSIX 主机，不支持原生 Windows Python；平台限制见一键测评说明。

无需预装 OpenCode 或手工安装 Skill/Ctags。调用者仍需提供有效模型服务及其凭据，并具备下载公开源码所需的网络。新测评采用当前 11 类 Skill 与公开兼容映射，和历史五分类成绩分开保存。配置示例、首次准备、续跑、失败处理及核验命令详见 [evaluation/scripts/README.md](evaluation/scripts/README.md)。

## 安装

在本 README 所在目录执行：

```bash
mkdir -p ~/.opencode/skills

cp -r \
  patch-intent-analysis \
  patch-relation-analysis \
  ~/.opencode/skills/
```

运行依赖如下：

| 依赖 | 要求 | 用途 |
|---|---|---|
| Python | 3.10+ | 运行随 Skill 提供的分析脚本 |
| Git | 可用版本 | 读取 commit 和源码 |
| Universal Ctags | 可选 | 提升多语言符号定位精度 |

## 补丁意图分析

### 能力

`patch-intent-analysis` 分析一个 Git commit，给出唯一的主要补丁类型、补丁自身的问题级别、修改内容及判断依据。

完整规则和 JSON 输出契约见 [`patch-intent-analysis/SKILL.md`](patch-intent-analysis/SKILL.md)。

### 输入

| 参数 | 必填 | 说明 |
|---|---|---|
| `repo` | 是 | 包含目标 commit 的本地 Git 仓库路径 |
| `commit` | 是 | 目标 commit 的完整 SHA 或可唯一解析的 revision |

Skill 仅支持 `repo + commit` 输入。它会从指定仓库读取 commit message、变更文件、完整 patch 和必要的源码上下文。

### 调用示例

```text
使用 $patch-intent-analysis 分析 <repo-path> 仓库中的 commit <commit-id>。
返回补丁类型、问题级别、修改概述、详细分析和直接证据，
并严格按照 Skill 的输出契约返回单个 JSON 对象。
```

### 输出

| 字段 | 说明 |
|---|---|
| `patch_type` | commit 的唯一主要补丁类型 |
| `severity` | 补丁自身的问题级别 |
| `full_feature` | 一句话概括补丁的实际修改 |
| `confidence` | 当前分析结论的置信度 |
| `reason` | 补丁类型的判定依据 |
| `severity_reason` | 问题级别的判定依据 |
| `severity_factors` | 失败模式、触发条件、运行时暴露面和影响范围 |
| `detailed_analysis` | 补丁描述、潜在影响、风险和触发条件 |
| `intent_items` | 修改对象、具体变化、效果及直接证据 |

`patch_type` 的允许值：

```text
BugFix
CVE
Optimize
Feature
Refactor
CleanUp
Doc
Typo修复
TestCode
资源泄露&crash补丁
其他
```

`severity` 的允许值：

```text
致命
严重
一般
提示
```

## 补丁关联关系分析

### 能力

`patch-relation-analysis` 支持两种分析模式：

| 模式 | 输入 | 用途 |
|---|---|---|
| Pairwise | Git 仓库、`commit_a`、`commit_b` | 判断两个 commit 的关系及依赖方向 |
| Cluster | Git 仓库、两个或以上 commit | 根据两两关系形成 commit 聚类 |

Pairwise 模式始终以 `commit_a` 为当前目标补丁，以 `commit_b` 为候选补丁。依赖方向描述的是 `commit_b` 相对于 `commit_a` 的位置：

```text
commit_a = 当前目标补丁
commit_b = 候选补丁
```

调用时可以附带两个 commit 的 `patch-intent-analysis` 输出，作为补充语义证据。精确的 CVE、issue、backport 或 commit 标识仍优先于一般性的语义相似。

完整规则和 JSON 输出契约见 [`patch-relation-analysis/SKILL.md`](patch-relation-analysis/SKILL.md)。

### Pairwise 调用示例

```text
使用 $patch-relation-analysis 分析 <repo-path> 仓库中的目标 commit <commit-a>
和候选 commit <commit-b>，判断二者的关联关系，以及 commit-b 相对于
commit-a 的依赖方向，并严格按照 Skill 的 Pairwise 输出契约返回 JSON。
```

Pairwise 模式的主要输出：

| 字段 | 说明 |
|---|---|
| `relation_type` | `same_issue`、`backport`、`related`、`unrelated` 或 `uncertain` |
| `issue_cve_score` | issue 或 CVE 关系分数 |
| `backport_score` | backport 关系分数 |
| `overall_score` | 综合关系分数 |
| `confidence` | 当前关系结论的置信度 |
| `dependency_direction` | `commit_b` 相对于 `commit_a` 的依赖方向 |
| `dependency_type` | fixes、API/符号、series、follow-up、backport 或 revert 等依赖类型 |
| `prerequisite_dependencies` | `commit_a` 的前置依赖 |
| `subsequent_dependencies` | `commit_a` 的后置依赖 |
| `evidence` | 支撑关系和依赖判断的直接证据 |

`dependency_direction` 的允许值：

| 值 | 含义 |
|---|---|
| `commit_b_is_prerequisite` | `commit_b` 是 `commit_a` 的前置依赖 |
| `commit_b_is_subsequent` | `commit_b` 是 `commit_a` 的后置依赖 |
| `mutual_or_series` | 两者属于同一系列，但无法确定单一方向 |
| `none` | 存在关联，但没有依赖关系证据 |
| `unknown` | 证据不足，无法判断 |

### Cluster 调用示例

```text
使用 $patch-relation-analysis 对 <repo-path> 仓库中的
<commit-a>、<commit-b>、<commit-c> 进行聚类，
并严格按照 Skill 的 Cluster 输出契约返回 JSON。
```

Cluster 模式的主要输出：

| 字段 | 说明 |
|---|---|
| `cluster_threshold` | 形成关联边所使用的分数阈值 |
| `clusters` | 由相关 commit 组成的聚类 |
| `singletons` | 未与其他 commit 形成关联的独立项 |
| `pairwise_edges` | 支撑聚类结果的两两关系 |

## 运行方式

补丁意图分析可以在 Docker 容器中运行，也可以直接调用本机 OpenCode。两种方式都需要提供包含目标 commit 的本地 Git 仓库和可唯一解析的 commit ID。

### Docker 模式

Docker 模式在隔离容器中完成一个 commit 分析并直接输出结果。

运行前需要满足：

- 已安装 Docker，且 Docker 服务正常运行。
- 已使用本目录的 `Dockerfile` 构建镜像。
- 镜像内已安装 OpenCode、`patch-intent-analysis` 和 `patch-relation-analysis`。
- 宿主机存在有效的 OpenCode 配置文件，其中已配置可用的模型服务和访问凭据。
- 待分析目录是完整的 Git 仓库，且目标 commit 可以在该仓库中解析。
- 运行环境能够访问配置的模型服务。

以下命令均从本 README 所在的 `研究内容一/` 目录执行。先构建镜像：

```bash
RESEARCH_DIR="$(pwd)"
IMAGE_NAME=patch-analysis-opencode:1.0

docker build \
--tag "$IMAGE_NAME" \
"$RESEARCH_DIR"
```

设置待分析仓库、OpenCode 配置文件和 commit ID，然后运行：

```bash
: "${HOST_REPO:?请设置待分析仓库的本机绝对路径}"
: "${HOST_OPENCODE_CONFIG:?请设置 OpenCode 配置文件的本机绝对路径}"
IMAGE_NAME=patch-analysis-opencode:1.0
COMMIT_ID=replace-with-commit-id

docker run --rm \
--volume "$HOST_REPO:/workspace/repo:ro" \
--volume "$HOST_OPENCODE_CONFIG:/home/node/.config/opencode/opencode.json:ro" \
--workdir /workspace/repo \
--entrypoint opencode \
"$IMAGE_NAME" \
run \
"使用 \$patch-intent-analysis 分析 /workspace/repo 仓库中的 commit ${COMMIT_ID}。只返回符合 Skill 输出契约的单个 JSON 对象，不要添加 Markdown 代码围栏或说明文字。"
```

如果 OpenCode 配置通过 `{file:...}` 引用外部凭据文件，还需要将该文件挂载到容器中的相同绝对路径。

### 本机 OpenCode 模式

本机模式直接使用本机运行时和本机安装的 Skill 分析 commit。

运行前需要满足：

- 本机已安装 OpenCode，且可执行文件可以正常运行。
- OpenCode 已加载有效配置，其中已配置可用的模型服务和访问凭据。
- `patch-intent-analysis` 和 `patch-relation-analysis` 已安装到当前 OpenCode 实例能够发现的 Skill 目录。
- 本机已安装 Git 和 Python 3.10 或更高版本。
- 待分析目录是完整的 Git 仓库，且目标 commit 可以在该仓库中解析。
- 运行环境能够访问配置的模型服务。

设置 OpenCode 可执行文件、待分析仓库和 commit ID，然后运行：

```bash
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
: "${REPO_PATH:?请设置待分析的本机 Git 仓库路径}"
COMMIT_ID=replace-with-commit-id

"$OPENCODE_BIN" \
run \
--dir "$REPO_PATH" \
"使用 \$patch-intent-analysis 分析 ${REPO_PATH} 仓库中的 commit ${COMMIT_ID}。只返回符合 Skill 输出契约的单个 JSON 对象，不要添加 Markdown 代码围栏或说明文字。"
```

默认通过 `PATH` 查找 `opencode`；若未加入 `PATH`，将 `OPENCODE_BIN` 设置为本机可执行文件路径。Universal Ctags 可以提升源码符号定位精度；缺少时，Skill 会使用内置降级分析能力。
