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

```text
研究内容一/
├── README.md
├── Dockerfile
├── .dockerignore
├── patch-intent-analysis/
└── patch-relation-analysis/
```

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

## Docker

本目录的 `Dockerfile` 提供预装 OpenCode、运行依赖和两个 Skill 的容器环境。

### 构建镜像

在本 README 所在目录执行：

```bash
docker build -t patch-analysis-opencode:1.0 .
```

### 启动 OpenCode

将待分析仓库挂载到容器中的 `/workspace/repo`：

```bash
HOST_REPOSITORY=/absolute/path/to/repository
HOST_OPENCODE_CONFIG=/absolute/path/to/opencode.json

docker run --rm -it \
  -v "$HOST_REPOSITORY:/workspace/repo" \
  -v "$HOST_OPENCODE_CONFIG:/home/node/.config/opencode/opencode.json:ro" \
  patch-analysis-opencode:1.0
```

### 容器内 Prompt

启动 OpenCode 后，分析单个补丁意图可直接输入：

```text
使用 $patch-intent-analysis 分析 /workspace/repo 仓库中的 commit <commit-id>，
返回补丁类型、问题级别、修改概述、详细分析和直接证据，
并严格按照 Skill 的输出契约返回单个 JSON 对象。
```

分析两个补丁的关联关系和依赖方向可直接输入：

```text
使用 $patch-relation-analysis 分析 /workspace/repo 仓库中的目标 commit <commit-a>
和候选 commit <commit-b>，判断二者的关联关系，以及 commit-b 相对于
commit-a 的依赖方向，并严格按照 Skill 的 Pairwise 输出契约返回 JSON。
```

将 `<commit-id>`、`<commit-a>` 和 `<commit-b>` 替换为容器内仓库可解析的 commit SHA 或 revision。
