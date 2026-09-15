---
name: patch-port-apply
description: 根据 patch-port-analysis 生成的结构化迁移计划，在独立 Git worktree 中实施参考安全修复，选择经过批准的 direct apply 或按 change unit 适配目标版本，跟踪耦合修改覆盖率并生成候选 patch 与实施记录。用于补丁迁移实施；必须提供 port-analysis.json。
---

# 补丁迁移实施

严格消费分析产物，把计划变成可验证候选补丁。不要重新发明映射关系，也不要把实施阶段的自检当作独立验证。

## 输入与前置门禁

必须提供 `repo`、`reference_patch`、`target_ref`、`port-analysis.json` 和 `output_dir`。

output_dir 始终为整次迁移的产物根目录。补丁放在根目录，实施记录放入 details/，候选源码放在 candidate-worktree/；所有跨文件引用使用实际绝对路径。

`cross_repo_semantic` 时 `repo=inputs.target_repo`，参考仓库只读。检查每个 mandatory unit 的 semantic_mapping 已确认且目标仓库、SHA、路径一致；使用 `strategy=semantic-adaptation` 执行下述 Strategy B，不要求跨仓库历史链。

只接受 `analysis_status=ready` 或 `direct_apply_ready`。确认：

- target SHA 与分析产物一致；
- mandatory change units 无 `unresolved`；
- coupled groups 具有完整实施决策；
- 没有未解决 critical 风险。
- 必要证据缺口均已解决，target location 在目标 SHA 有直接代码证据。复制历史文件、重建已迁移路径不能替代最终定位。

否则输出 `blocked`，不得修改代码。

## 隔离工作树

从精确 target SHA 创建独立 detached worktree。记录路径和基线状态，不修改调用者现有 checkout。禁止提交、推送、改写历史和使用 `git checkout <历史提交> -- <path>`。

使用随 Skill 附带的工作树脚本创建候选环境。`prepare` 必须提供 `--analysis`，两种迁移模式均检查分析状态、必要映射、上下文缺口和目标 SHA，通过后才创建工作树：

```bash
python3 <apply-skill-dir>/scripts/candidate_workspace.py prepare \
  --repo <repo> \
  --target-ref <target-commit> \
  --analysis <output-dir>/port-analysis.json \
  --worktree <output-dir>/candidate-worktree \
  --metadata-output <output-dir>/details/worktree.json
```

## Strategy A：批准的 direct apply

仅当分析产物为 `direct_apply_ready` 时使用其推荐策略。先执行相同参数的 `--check`，成功后实际应用。

对经批准的策略执行：

```bash
python3 <apply-skill-dir>/scripts/candidate_workspace.py apply-direct \
  --worktree <output-dir>/candidate-worktree \
  --patch <reference-patch> \
  --strategy <approved-strategy>
```

应用后逐项确认：

- changed paths 与分析范围一致；
- 没有新增已经迁移走的旧文件；
- 每个 change unit 和 coupled group 都被覆盖；
- API、控制流、锁、cleanup 和错误返回适配目标版本。

任何一项不成立，恢复隔离基线并进入 `blocked`；不得擅自切换到未经分析的策略。

## Strategy B：按 change unit 适配

按分析产物中的依赖拓扑实施：

1. 加载当前 unit 指定的 target location 和 required context。
2. 复述该 unit 的局部意图及所属安全不变量。
3. 使用目标版本已有 API、数据结构和代码风格实现最小修改。
4. 更新实施 ledger：`implemented`、`not_applicable` 或 `blocked`。
5. 完成整个 coupled group 后整体复查；组内任何 mandatory unit 失败都回退该组，不保留部分实施。
6. 完成所有 units 后进行跨组检查，确认声明、初始化、调用点和验证逻辑一致。

禁止：按最高文本相似度猜位置、复制旧版本整文件、绕过 unresolved unit、无关重构或只实现多文件修复的一部分。

## 实施自检

至少运行：

```bash
git status --short
git diff HEAD --check
git diff HEAD --stat
git diff HEAD
```

检查 conflict marker、`.rej`、重复代码、意外二进制变化、mode change、错误路径新增和无关格式化。验证所有新增 symbol、macro、include 和 API 在目标版本存在。

在另一个干净临时 target 环境中执行 `git apply --check generated.patch`，证明候选 patch 可重放。

完成编辑后运行确定性收尾：

```bash
python3 <apply-skill-dir>/scripts/candidate_workspace.py finalize \
  --worktree <output-dir>/candidate-worktree \
  --analysis <output-dir>/port-analysis.json \
  --patch-output <output-dir>/generated.patch \
  --evidence-output <output-dir>/details/application-evidence.json
```

读取 `details/application-evidence.json`，再补充 unit ledger、coupled-group 覆盖和实施语义，生成 `details/application.json`。只记录各 unit 的落点、完成状态、适配差异和证据引用，不复制完整补丁或分析原文。脚本的 `structurally_ready` 不等于 `candidate_ready`；只有 ledger 和组覆盖门禁也通过后才能升级。

## 产物

写出：

- `<output_dir>/generated.patch`：相对精确 target SHA 的候选 diff；
- `<output_dir>/details/application.json`：实施 ledger 和自检事实。
- `<output_dir>/details/application-evidence.json`：脚本生成的 diff、路径、conflict marker 和干净重放证据。

`application.json` 契约见 [实施产物契约](references/application-contract.md)。最终只返回相同 JSON。

`candidate_ready` 只表示可以进入独立验证，不表示补丁最终正确。
