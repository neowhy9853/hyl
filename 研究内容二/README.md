# 安全补丁合入与迁移

将参考安全修复迁移到指定 Git 版本，支持同仓库跨版本迁移和跨仓库语义适配。先尝试严格直接应用；成功即合入并返回，不调用迁移分析、语义评审或构建测试。需要适配时，Agent 再按分析、实施、验证三个阶段执行。

## 组件

| Skill | 功能 |
|---|---|
| `security-patch-port` | 编排迁移流程、检查阶段门禁并汇总结果 |
| `patch-port-analysis` | 分析修复语义、追踪代码变化并确定目标修改位置 |
| `patch-port-apply` | 在独立工作区实施修复并导出候选补丁 |
| `patch-port-validation` | 重放候选补丁，检查结构、安全语义及项目验证结果 |
| `patch-dependency-discovery` | 查找前置提交，核对目标所需能力与依赖关系 |

总控先运行 `security-patch-port/scripts/direct_apply.py`。严格应用成功后返回 `success`；失败才调用三个阶段 Skill，并按需发现依赖。适配分支仍要求分析、实施和独立验证门禁全部通过。

## 目录结构

| 路径 | 内容 | 用途 |
|---|---|---|
| `README.md` | 项目说明 | 介绍补丁迁移流程、Skill 职责、输入输出、安装方式和运行方式 |
| `Dockerfile` | 容器构建文件 | 构建预装 OpenCode、运行依赖和补丁迁移 Skill 的镜像 |
| `skills/security-patch-port/` | 补丁迁移总控 Skill | 编排分析、实施和独立验证，检查阶段门禁，按需调用依赖发现并汇总结果 |
| `skills/patch-port-analysis/` | 补丁迁移分析 Skill | 定义修复语义、历史追踪和跨仓库映射规则，提供代码检索脚本并输出迁移计划 |
| `skills/patch-port-apply/` | 补丁迁移实施 Skill | 按分析计划适配目标代码，提供独立工作区管理、补丁应用和候选补丁导出脚本 |
| `skills/patch-port-validation/` | 补丁迁移验证 Skill | 定义安全语义与目标兼容性验证规则，提供干净重放、结构检查和验证命令执行脚本 |
| `skills/patch-dependency-discovery/` | 补丁依赖发现 Skill | 定义参考仓库历史检索、候选前置提交和目标能力核验流程，输出依赖调查结果 |
| `evaluation/` | 补丁迁移评测材料 | 包含 Linux 与 openEuler 补丁配对数据、参考补丁与标准答案补丁、覆盖全部 496 条的一键评测脚本及使用说明 |

## 环境

- Git：支持 worktree、apply、blame 和历史查询。
- ripgrep：供 Agent 搜索源码；Docker 镜像已安装，随附 Python 检索脚本使用 Git。
- Python 3.10 或更新版本：运行辅助脚本和评测器，仅使用标准库。
- OpenCode 或兼容 Agent 运行环境：支持加载 Skill、读取源码和编辑文件。
- 目标项目的构建工具和测试依赖：按项目验证计划配置。

## 安装

在项目根目录执行：

```bash
mkdir -p ~/.opencode/skills
cp -r skills/* ~/.opencode/skills/
```

## 补丁迁移

向 Agent 提供仓库、参考补丁和目标版本：

```text
使用 $security-patch-port，将 <reference-patch> 的安全修复迁移到
<repo> 仓库的 <target-ref>。
参考修复提交为 <reference-fix>，阶段产物写入 <output-dir>。
先尝试严格直接应用；成功即返回，需要适配时执行分析、实施和验证门禁。保留未提交的候选修改。
```

| 输入 | 说明 |
|---|---|
| `repo` | 包含目标版本和必要历史的本地 Git 仓库 |
| `reference_patch` | unified diff 格式的参考补丁 |
| `target_ref` | 接收修复的目标版本 |
| `reference_fix`、`reference_parent` | 参考修复提交及其父提交 |
| `output_dir` | 分析、补丁和验证产物的输出目录 |
| 验证命令 | 目标项目的构建、测试或静态检查命令 |

跨仓库任务使用 `port_mode=cross_repo_semantic`，并提供 `reference_repo` 和 `target_repo`。分析过程按功能、接口和控制流建立对应关系，详见[跨仓库迁移](skills/patch-port-analysis/references/cross-repo-semantic.md)。

需要单独分析前置依赖时：

```text
使用 $patch-dependency-discovery，分析 <reference-fix> 所需的能力。
reference_repo=<参考仓库>，reference_patch=<补丁路径>，
target_repo=<目标仓库>，target_ref=<目标版本>，output_dir=<输出目录>。
结合失败日志和目标代码，输出候选依赖及迁移必要性。
```

## 输出

直接合入保存 `generated.patch`、`final.json`、`details/application.json` 和 `details/direct-apply.json`，不生成分析或验证报告；`completion_mode=direct_apply` 表示仅完成原补丁应用，未执行的分析和验证记为 `not_run`。

适配分支的产物根目录保留 `generated.patch`、`final.json`、`port-analysis.json` 和 `VALIDATION_REPORT.md`；查询证据、实施和验证记录统一放入 `details/`，候选源码放入 `candidate-worktree/`。默认不生成重复的验证证据 Markdown 摘要，保留必要历史映射、检查事实和未验证项。

| 最终状态 | 含义 |
|---|---|
| `success` | 原补丁严格直接合入成功，或适配分支的分析、实施和独立验证门禁均通过 |
| `no_change` | 分析已证明目标不受影响或已有等价修复 |
| `blocked` | 必要输入、证据、授权范围或关键验证条件不足，暂不能继续放行 |
| `failed` | 已确认候选存在错误、漏改或构建与测试失败 |

适配分支中，验证阶段的 `partial` 表示仍有关键验证未完成，总控汇总为 `blocked`，并保留具体缺项。脚本输出的 `structurally_ready`、`structurally_valid` 仅表示机械检查通过；Agent 还需完成阶段契约要求的语义审核。

## Docker

在项目根目录构建包含 OpenCode 和五个 Skill 的镜像：

```bash
docker build -t patch-port-opencode:2.1 .
```

挂载仓库、补丁、输出目录和模型配置：

```bash
docker run --rm -it \
  -v /path/to/repo:/workspace/repo \
  -v /path/to/reference.patch:/workspace/reference.patch:ro \
  -v /path/to/results:/workspace/results \
  -v /path/to/opencode.json:/home/node/.config/opencode/opencode.json:ro \
  patch-port-opencode:2.1
```

容器内使用 `$security-patch-port`，输入路径分别为 `/workspace/repo`、`/workspace/reference.patch` 和 `/workspace/results`。输出目录需允许容器用户写入。

镜像提供 Agent 和迁移脚本运行环境；目标项目的编译器、系统库和测试依赖需按验证计划另行配置。依赖发现可独立进行代码复核；需要关联分析 Skill 时另行安装 `patch-relation-analysis`。配置中的 `{file:...}` 凭据引用需按相同绝对路径挂载到容器。

## 评测

首次配置、从零运行、结果核验与续跑见 [一键运行指南](evaluation/ONE_CLICK_GUIDE.md)。在本目录执行：

```bash
python3 evaluation/scripts/run_evaluation.py \
  --config /absolute/path/to/opencode.json \
  --output /absolute/path/outside-repository/patch-port-evaluation \
  --workers 2
```

默认覆盖 Linux 404 条与重点项目 92 条，自动准备源码及目标基线，调用模型迁移并按 oracle 等价性判分。每个完成案例保存 `input.json`、`result.json`、`trace.jsonl`；新输出写入指定的项目外目录。

[评测目录说明](evaluation/README.md)介绍目录构成，[数据说明](evaluation/data/README.md)介绍输入字段，[脚本说明](evaluation/scripts/README.md)介绍执行与核验入口。
