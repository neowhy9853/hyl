---
name: patch-compatibility-analysis
description: "静态分析补丁、diff、commit 或上游提交 URL 中的 API/ABI、系统接口、契约、错误、外部副作用、输出、配置/CLI 和语义兼容性变化，生成经过校验的 PCA 分析产物，不执行动态测试。当请求包含兼容性变更、兼容性影响、补丁分析、影响分析、接口变化、行为变化、API/ABI 变更、静态分析、compatibility change、compatibility impact、patch analysis、impact analysis、API change、ABI change 或 compatibility review 等词时使用。出现兼容性变更但没有明确的测试、验证、复现、契约或覆盖率动作时，默认使用本 Skill。"
---

# Patch Compatibility Analysis

只执行静态兼容性分析，不生成可运行测试入口，也不执行动态测试。分析完成后，如果用户尚未明确要求继续测试，必须询问是否将本次 `analysis.json` 交给同级 `../patch-compatibility-testing/SKILL.md` 进行定向动态测试。

## Deterministic Priority Calibration

After final compatibility `findings` are written and before handing the result
to testing, run the deterministic priority calibrator:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/priority_calibrator.py" \
  --analysis "<RESULT_DIR>/analysis.json" \
  --candidates "<RESULT_DIR>/candidates.json" \
  --profile "<PACKAGE_PROFILE>" \
  --repo "<REPO>" \
  --apply
```

The calibrator does not decide whether a candidate is a compatibility change,
and it does not own the final High/Medium/Low classification. It only computes
a deterministic `recommended_priority` for already-confirmed findings from the
effective profile's API-surface priority, matched candidate hunks, API kind, and
compatibility type. It records the agent's original/final priority,
recommended priority, matched surfaces, and trace in
`findings[].priority_decision`, then rewrites the summary counts from the
Agent-final `findings[].test_priority`.

Use `priority_decision.recommended_priority` as evidence when choosing the final
classification. The Agent keeps final authority over `findings[].test_priority`;
if the final classification differs from the recommendation, explain the reason
in `test_priority_reason` or `analysis_summary.notes` and set
`priority_decision.recommendation_disagreement_reasons` to one or more fixed
labels only:

- `opt_out_available`
- `additive_behavior_only`
- `internal_or_test_only`
- `narrow_surface`
- `no_external_observable_break`
- `profile_overmatched`

After reading the calibration report, perform a final priority pass over every
finding. If you edit any `test_priority` or disagreement reason after
calibration, rerun `priority_calibrator.py --apply` so
`priority_decision.final_priority` and the summary counts match the Agent-final
value.

## 2026 Heavy Mode And Composable Profile Update

This skill now has two deterministic front-end extensions:

1. **Heavy mode for large patches.** `orchestrator.py` computes
   `patch-metrics.json` after candidate extraction. In `--analysis-mode auto`,
   it switches to heavy mode when soft thresholds are exceeded and always
   switches to heavy mode when hard thresholds are exceeded. Heavy mode writes
   `shards.json` plus `shards/shard-*.json`; each shard is a bounded semantic
   analysis task grouped by API surface, file, and changed symbol. Analyze shard
   files independently, then merge shard result files with:

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/orchestrator.py" \
     --aggregate-shards "<RESULT_DIR>/analysis.json"
   ```

   Use subagents only when the current Codex environment exposes subagent tools
   and the user has allowed parallel/subagent work. If subagents are not
   available, process shard files sequentially. Do not give a heavy-mode worker
   the whole patch when the shard file is sufficient.

2. **Composable package profiles.** Package profiles may now use `extends` and
   `variants`. The loader resolves a deterministic `effective-profile.yaml` by
   merging reusable layers such as `base/default`, `languages/c_family`,
   `domains/cli_tool`, `domains/daemon_network`, and `domains/kernel_base`,
   then applying the package profile from `profiles/packages/` and
   any matching variant overlay. `diff_parser.py` uses this effective profile
   for API-surface matching; old hard-coded recognizers are only a fallback when
   no profile surface matches. Always consult `effective-profile.yaml` before
   deciding whether a candidate is public, ABI-stable, CLI/config-visible,
   protocol-visible, or only internal.

Heavy-mode thresholds currently are:

| level | trigger |
|---|---|
| soft | `patch_lines>=600`, `raw_hunks>=30`, `changed_files>=12`, `churn>=250`, `candidate_hunks>=25`, `candidate_context_bytes>=100000`, or `candidates_json_bytes>=100000` |
| hard | `patch_lines>=1000`, `raw_hunks>=45`, `changed_files>=25`, `candidate_hunks>=40`, `candidate_context_bytes>=180000`, or `candidates_json_bytes>=180000` |

Profiles are organized under `profiles/base`, `profiles/languages`,
`profiles/domains`, `profiles/platforms`, and `profiles/packages`. Initial
analysis artifacts include `effective-profile.yaml`, `patch-metrics.json`, and,
in heavy mode, `shards.json` plus `shards/`.

## 2026 Efficiency Update

This skill is the deliverable. Do not require or modify any external harness,
agent runner, BatchAgent implementation, or tool allowlist to make the workflow
work. All efficiency behavior must come from this Skill's instructions and
bundled scripts.

`orchestrator.py` now writes `analysis-context.json`, a bounded agent input
that summarizes changed files, candidate hunks, API surfaces, changed-line
snippets, and focused source excerpts with line numbers. Use it before opening
`candidates.json`, `report.md`, or source files.

Low-context analysis rules:

1. Run `check_dependencies.py` before expensive work. It also validates bundled
   package profiles and catches YAML/extends errors early.
2. Run `orchestrator.py` and then read, in this order:
   `analysis.json`, `analysis-context.json`, and `patch.diff`. For first-pass
   semantic judgment, treat `candidate_hunks[].source_excerpt` as the focused
   source window; do not reopen the same source file only to locate the changed
   function.
3. Do not scan repository roots, patch-list directories, output directories, or
   profile trees. Do not read the full `report.md` candidate section when
   `analysis-context.json` is sufficient.
4. Open `candidates.json` only when the compact context is insufficient for a
   specific finding. Never load it wholesale for ordinary small patches.
5. If a shell command is rejected by the environment or harness policy, do not
   spend turns trying equivalent `ls`, `rg`, `grep`, `head`, or `python -c`
   commands. Switch to bounded file reads or the deterministic scripts already
   provided by this Skill.
6. Default evidence budget is zero extra source reads per candidate after
   `analysis-context.json`. Use at most one bounded extra source read per
   candidate, and only for a missing public declaration or a disputed contract.
   Do not inspect unchanged callee implementations merely to restate an
   argument/data-flow change that is already visible in the hunk.
7. After `validate_analysis.py` passes, finish the analysis immediately. Do not
   generate runnable entries or re-read large artifacts just to restate metadata.

你是一个**补丁兼容性影响分析器**。你的任务是基于给定的目标仓库和补丁/diff 文件，
**不运行动态测试**，**不依赖经验性关键词匹配**，识别补丁中可能导致兼容性变更的代码。

## 核心原则

1. **确定性分析找证据，LLM 做语义判断** — 模式匹配只用于召回候选，最终判断由你在代码上下文、API surface、contract diff、behavior diff 和静态调用链证据约束下完成
2. **每条 finding 必须引用具体文件、行号、代码片段作为证据**
3. **区分 syntactic breaking changes 和 behavioral/semantic breaking changes**
4. **最终 findings 只保留确认的兼容性变化**；如果不是 public/exported/CLI/config/protocol/test-reachable，且无法说明外部可观察影响，则保留在 candidates 中，不写入 findings

---

## 输入

用户会提供以下参数：
- **repo**: 目标仓库路径或 URL，必需
- **patch_file**: patch/diff 文件路径，或 GitHub/GitLab commit/patch URL，必需
- **base_ref**: 补丁基线 commit/tag/branch，可选，默认使用当前 HEAD
- **package_profile**: `auto`, `kernel_6_6`, `openeuler_24_03`, `cpython`, `golang`, `ruby`, `dnf`, `libsoup`, `grub2`, `libxml2`, `httpd`, `vim`, `git`, `glib2`, `networkmanager`, `dnsmasq`, `haproxy`, `rsyslog`, `lvm2`, `openldap`, `procps-ng`, `util-linux`, `grep`, `systemd`, `openssh`, `gcc`, `c_project`；默认 `auto`
- **output_format**: `json` 或 `markdown`，默认 `json`
- **output_dir**: 分析产物存放目录，可选；用户指定时必须使用该目录作为本次 `RESULT_DIR`
- **report_language**: 最终分析报告语言，可选；默认跟随用户请求语言，无法判断时使用中文
- **include_call_chain**: 是否输出静态调用链，默认 `false`

最终 `report.md`、`analysis.json` 中的自然语言说明字段（如 `old_behavior`、`new_behavior`、`compatibility_reason`、`recommended_review`、`test_recommendation`）以及面向用户阅读的分析说明必须使用用户请求所用语言；若用户没有明确请求语言或请求主要由路径、URL、代码片段组成，则默认使用中文。代码标识符、CLI 选项、错误码、兼容性类型枚举和路径保持原文。

## 目标 Patch 与 openEuler 分析焦点

当前重点目标以 openEuler 社区 repo/分支为主。默认优先分析：

- 24.03-LTS-SP1 分支内的目标 patch 兼容性影响。
- 24.03 基线升级到较新版本时，上游目标 patch 对 CLI、配置、库头文件、系统接口和运行时副作用的影响。
- 上游 GitHub/GitLab commit URL 可直接作为 `--patch` 输入；orchestrator 会下载 `.patch` 并记录 `analysis.json.patch_source`。如果分析 openEuler 分支，请显式传入 `--base-ref <openEuler-branch-or-commit>`，不要让工具默认用上游 HEAD 推断兼容性。

正常 patch 兼容性分析必须是无 ground-truth 的无源分析。Skill 内不得内置、
读取或写入预期结论、验收规则、目标答案、历史修复结论等会影响语义判断的信息。
Agent 只能基于 diff、profile API surface、代码上下文、调用链和可观察 contract
证据判断兼容性变化。若用户提供外部回归样例或目标 patch 清单，只可把它当作
运行对象列表，不可把预期结果作为分析输入。

近期目标差异类型映射：

- `03 输入变更`：正则、CLI 参数、配置、路径、挂载拓扑、编译输入或 header 依赖的接受/拒绝范围变化。优先映射 `INPUT_CONTRACT_CHANGE`，若诊断/退出状态也变则附带 `ERROR_EXCEPTION_CHANGE` 或 `CONFIG_CLI_BEHAVIOR_CHANGE`。
- `05 异常变更`：上游 patch 引入、后续 patch 修复的用户可见异常行为，常见于 CLI 输出空值、截断、尾随空格、列宽、错误回显。不要因为它是“bug fix/regression fix”而丢弃；优先映射实际可观察面，例如 `OUTPUT_FORMAT_CHANGE`。
- `06 副作用变更`：默认协议、系统状态切换、文件/设备/服务状态、编译时 transitive include、资源生命周期等非返回值本身的外部影响。优先映射 `SIDE_EFFECT_CHANGE`，并按入口附带 `CONFIG_CLI_BEHAVIOR_CHANGE`、`INPUT_CONTRACT_CHANGE` 或 `ERROR_EXCEPTION_CHANGE`。

## 输出产物目录

如果用户明确指定分析产物存放目录，所有本次分析产物必须写入该目录，并将该目录作为 `RESULT_DIR`，不要再追加 `pca-results/<patch_id[:6]>` 子路径。目录已存在时可以覆盖本次分析生成的同名文件，但不要删除用户手工添加的其他文件。

如果用户没有指定产物目录，使用默认位置：

```text
<repo>/pca-results/<patch_id[:6]>/
```

其中：
- `repo` 是用户提供的本地仓库目录；如果用户给的是 URL，则先克隆到本地目录，再以该克隆目录作为 `repo`。
- `patch_id` 优先使用补丁对应的 git commit hash；如果 patch 文件中没有 commit hash，则使用 patch 文件名 stem；仍无法稳定命名时，使用 patch 文件内容的 SHA-256 前 12 位。
- `<patch_id[:6]>` 是 `patch_id` 的前 6 个字符。目录已存在时可以覆盖本次分析生成的同名文件，但不要删除用户手工添加的其他文件。

目录中至少包含：
- `patch.diff`：本次分析使用的补丁副本
- `candidates.json`：`diff_parser.py` 生成的结构化候选
- `callchains.json`：静态调用链聚合结果；未启用或失败时写入 `[]`
- `analysis.json`：符合 `schemas/output_schema.json` 的最终 JSON 结果
- `report.md`：当用户要求 markdown 或需要便于阅读的摘要时生成
- `_worktrees/patched/`：orchestrator 创建的临时隔离分析 worktree。语义分析期间用于读取补丁后源码上下文和构建 CallGraph；整个分析完成后默认应清理以节省空间。清理后可从 `analysis.json` 重新生成。

完成分析后的回复必须主动说明实际产物位置，例如：`产物已写入 <RESULT_DIR>/`。

---

## 执行流程

### Skill 资源

- `${CLAUDE_SKILL_DIR}/scripts/diff_parser.py`：解析 unified diff，提取 hunk、符号、上下文和 API surface 候选。
- `${CLAUDE_SKILL_DIR}/scripts/callgraph.py`：AST-only、尽力而为的静态调用链构建器。
- `${CLAUDE_SKILL_DIR}/scripts/orchestrator.py`：统一执行仓库准备、`patch_id` 生成、产物目录创建、隔离 patched worktree 创建、候选提取、报告草稿生成，并在最终 findings 确认后附加调用链。
- `${CLAUDE_SKILL_DIR}/scripts/check_dependencies.py`：依赖检查器；在运行分析脚本前检查 Python 版本、git、脚本语法和调用链 AST 依赖。
- `${CLAUDE_SKILL_DIR}/scripts/validate_analysis.py`：最终产物校验器；检查 `analysis.json` 是否包含标准 finding 字段、代码行位置和证据行号。
- `${CLAUDE_SKILL_DIR}/scripts/profile_loader.py`：递归加载、合成和自动识别 package profile。
- `${CLAUDE_SKILL_DIR}/scripts/profile_generator.py`：根据 repo 生成 reviewable package profile 草案。
- `${CLAUDE_SKILL_DIR}/package-profile-generator/SKILL.md`：PCA 子 skill；按 repo 生成或更新 package profile。
- `${CLAUDE_SKILL_DIR}/profiles/base/*.yaml`：通用兼容性分类、证据策略和兜底 surface。
- `${CLAUDE_SKILL_DIR}/profiles/languages/*.yaml`：语言层 profile，例如 C/C++、Python、Go、Ruby。
- `${CLAUDE_SKILL_DIR}/profiles/domains/*.yaml`：领域层 profile，例如 CLI、daemon/network、kernel surface。
- `${CLAUDE_SKILL_DIR}/profiles/platforms/*.yaml`：平台/发行版级 overlay profile。
- `${CLAUDE_SKILL_DIR}/profiles/packages/*.yaml`：重点软件包 API surface 和兼容性类型定义。
- `${CLAUDE_SKILL_DIR}/schemas/output_schema.json`：最终 JSON 输出结构。

### Phase 0: 依赖检查

运行任何分析脚本前，先执行基础依赖检查：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check_dependencies.py"
```

如果用户要求调用链或 `include_call_chain=true`，在确认最终 findings 后按实际语言检查 AST 依赖，例如：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check_dependencies.py" \
  --include-callgraph \
  --languages "c,python"
```

如果检查失败，停止当前脚本执行，并询问用户是否安装或配置缺失依赖。不要自动降级到正则/grep 调用链扫描。

### Phase 1: 环境准备与补丁解析

优先运行统一 orchestrator，减少不同 agent 执行流程差异：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/orchestrator.py" \
  --repo "<repo-or-url>" \
  --patch "<patch_file-or-commit-url>" \
  --profile "<auto|profile>" \
  [--output-dir "<user-specified-result-dir>"] \
  [--base-ref "<base_ref>"]
```

orchestrator 会自动完成：
- 如果 `repo` 是 URL，克隆到本地工作目录；否则使用用户提供的 `repo` 目录
- 如果 `patch` 是 GitHub/GitLab commit URL 或 `.patch/.diff` URL，下载为本地 patch 并在 `analysis.json.patch_source` 记录原始 URL、下载 URL、缓存 patch 和 commit
- 计算 `patch_id`；若用户指定 `output_dir`，则 `RESULT_DIR=<output_dir>`，否则 `RESULT_DIR=<repo>/pca-results/<patch_id[:6]>`，创建该目录
- 将输入 patch 复制为 `${RESULT_DIR}/patch.diff`
- 从 `base_ref`（未提供时为 `HEAD`）创建 `${RESULT_DIR}/_worktrees/patched/` 隔离 worktree；不要修改用户传入 repo 的当前 checkout
- 在该隔离 worktree 中执行 `git apply`。如果补丁已经存在，则记录 `patch_apply_status=already_applied`；如果既不能正向 apply，也不能 reverse-check，停止并要求用户提供正确 `base_ref`
- 运行 `diff_parser.py` 时，`--repo` 必须指向 `${RESULT_DIR}/_worktrees/patched/`，不能指向原始 repo
- 在候选阶段写入空的 `${RESULT_DIR}/callchains.json`；调用链必须等最终 findings 确认后再按 finding 目标构建，避免对非兼容候选浪费时间
- 生成 `${RESULT_DIR}/analysis.json` 草稿和 `${RESULT_DIR}/report.md`，并写入 `analysis_repo`、`base_ref`、`base_commit`、`patch_apply_status`、`analysis_worktree_status=available`

**代码状态强约束**：后续读取补丁后完整函数、运行 AST CallGraph、定位新增符号时，只能使用 `analysis.json` 中的 `analysis_repo`。`repo` 只表示源仓库和产物落盘位置，不代表补丁已经应用后的代码状态。

**worktree 生命周期**：初始 orchestrator 运行后不要立刻删除 `_worktrees/patched/`，因为语义判定和后续测试子 skill 可能需要补丁后源码。默认保留该 worktree。只有用户明确要求释放空间，或确认不会继续测试时，才清理：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/orchestrator.py" \
  --cleanup-worktree "${RESULT_DIR}/analysis.json"
```

如果 `analysis_worktree_status=cleaned` 或 `analysis_repo` 目录不存在，但仍需复核源码或附加调用链，先重建；测试阶段也可通过同一命令重建：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/orchestrator.py" \
  --ensure-worktree "${RESULT_DIR}/analysis.json"
```

**检索目录强约束**：所有补丁后源码检索、`rg`、`grep`、`find`、`sed`、`git grep`、编辑器打开文件路径，都必须以 `analysis_repo` 为根目录。不要对 `analysis.json.repo` 或用户原始输入 repo 执行源码检索，因为那里可能仍停在补丁前、集成分支 HEAD 或其它无关状态。

运行 orchestrator 后，先读取并固定以下路径：

```bash
ANALYSIS_JSON="${RESULT_DIR}/analysis.json"
ANALYSIS_REPO="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8-sig"))["analysis_repo"])' "$ANALYSIS_JSON")"
SOURCE_REPO="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8-sig"))["repo"])' "$ANALYSIS_JSON")"
BASE_COMMIT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8-sig"))["base_commit"])' "$ANALYSIS_JSON")"
```

示例：如果要查 `kernel/sched` 下的 `.pick_task =`，应当执行：

```bash
rg "\.pick_task\s*=" "${ANALYSIS_REPO}/kernel/sched"
```

不要执行：

```bash
rg "\.pick_task\s*=" "${SOURCE_REPO}/kernel/sched"
```

读取补丁前旧文件时，使用源 repo 的 git 对象，而不是 checkout 源 repo：

```bash
git -C "${SOURCE_REPO}" show "${BASE_COMMIT}:kernel/sched/idle.c"
```

如果 orchestrator 不可用，再手动执行以下步骤：

1. 使用 `git diff` 或 `git apply --stat` 解析补丁文件，获取：
   - 所有 changed files
   - 每个文件的 hunks（old/new line mapping）
   - 变更所在的函数/类/结构体名称

2. 对每个 hunk 构建 PatchHunk 结构：

```json
{
  "file": "<文件路径>",
  "old_start": <起始行>,
  "old_end": <结束行>,
  "new_start": <起始行>,
  "new_end": <结束行>,
  "added_lines": ["<新增行>", ...],
  "deleted_lines": ["<删除行>", ...],
  "context_lines": ["<上下文行>", ...],
  "changed_symbols": ["<符号名>", ...],
  "in_header": <true|false>,
  "in_exported_api": <true|false>,
  "in_syscall": <true|false>,
  "in_ioctl": <true|false>,
  "in_netlink": <true|false>,
  "in_procfs": <true|false>,
  "in_sysfs": <true|false>,
  "in_sysctl": <true|false>,
  "in_test": <true|false>,
  "in_config": <true|false>,
  "in_doc": <true|false>
}
```

### Phase 2: Package Profile 识别

如果 `package_profile` 为 `auto`，根据仓库文件结构自动识别：

| Profile | 识别特征 |
|---------|---------|
| kernel_6_6 | Makefile + Kconfig + include/uapi/ + arch/ |
| openeuler_24_03 | openEuler 24.03 系统接口分析范围；当分析 distro 补丁、C/C++ 库 ABI、syscall、ioctl、netlink、proc/sys/sysfs 差异且没有更具体 profile 时手动选择 |
| cpython | Python/ + Include/ + Lib/ + setup.py (Python 解释器) |
| golang | src/runtime/ + src/cmd/go/ + go.mod (Go 工具链) |
| ruby | ruby.c + lib/ + ext/ + common.mk |
| dnf | dnf/ + setup.py + dnf.spec (Python 包管理) |
| libsoup | libsoup/ + meson.build + libsoup-3.0.pc.in |
| grub2 | grub-core/ + util/ + configure.ac |
| libxml2 | parser.c + tree.c + include/libxml/ |
| httpd | modules/ + server/ + include/httpd.h |
| vim | src/vim.h + src/eval.c + runtime/ |
| git | git.c + builtin/ + Documentation/ |
| glib2 | glib/ + gobject/ + gio/ + meson.build |
| networkmanager | src/core/ + src/libnm/ + clients/cli/ |
| dnsmasq | src/dnsmasq.c + src/dnsmasq.h |
| haproxy | src/haproxy.c + include/haproxy/ |
| rsyslog | runtime/ + plugins/ + configure.ac |
| lvm2 | lib/ + tools/ + daemons/ |
| openldap | servers/slapd/ + libraries/libldap/ + include/ |
| procps-ng | src/ps/sortformat.c 或 ps/sortformat.c + src/ 或 proc/ |
| util-linux | libsmartcols/ + sys-utils/ 或 misc-utils/ |
| grep | src/grep.c + lib/ 或 tests/ |
| systemd | src/systemctl/ + src/core/ + meson.build |
| openssh | scp.c + sftp.c + ssh.c |
| gcc | gcc/ + libstdc++-v3/ |

通过 `profile_loader.py --show <profile> --repo <repo>` 生成并读取 `effective-profile.yaml`，获取继承、variant overlay 后该软件包本次分析实际使用的 API surface 定义。

如果无法识别，使用 `c_project` 通用 profile。

### Phase 3: 变更函数/符号定位

使用 Bash 工具执行 `${CLAUDE_SKILL_DIR}/scripts/diff_parser.py`（或等价命令）：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/diff_parser.py" \
  --repo "<analysis_repo>" \
  --patch "<patch_file>" \
  --profile "$PROFILE" \
  --output "${RESULT_DIR}/candidates.json"
```

如果脚本不可用，使用以下工具手动完成：
1. `git diff` 获取变更
2. 在 `analysis_repo` 下用 `rg` / `grep` 定位补丁后符号定义；不要在源 repo 当前 checkout 下定位
3. 读取变更函数的完整代码。补丁后代码必须从 `analysis_repo` 读取；补丁前代码优先从 `base_commit` 对应的 git 对象读取，或从 `patch.diff` 的删除行与上下文还原。

对每个变更，提取：
- 函数/方法的完整签名
- 变更前后的完整函数体
- 所在文件是否为公共头文件
- 符号是否为导出符号

### Phase 4: API Surface 判定

根据 profile 判断每个变更是否处于公共 API 边界：

**C/C++ 项目**：
- `EXPORT_SYMBOL` / `EXPORT_SYMBOL_GPL`（Kernel）
- `include/uapi/**`、`include/linux/**`（Kernel UAPI）
- `PyAPI_FUNC` / `PyAPI_DATA`（CPython C API）
- `Include/*.h`（CPython）
- public headers（`include/`、`*.h` 被 `pkg-config` 暴露）
- export map / version script（`.map`、`.symver`）
- shared library ABI 元数据（`.symbols`、`.def`、`.exports`、symbol version node）
- CLI 参数解析（`getopt_long`、`argparse`）
- 配置文件解析逻辑

**openEuler 24.03 系统接口补充面**：
- C/C++ 开发包接口：devel 包暴露的 public header、导出符号、symbol version、pkg-config/CMake target、结构体布局、枚举值、宏常量。
- 系统调用：`SYSCALL_DEFINE*`、`COMPAT_SYSCALL_DEFINE*`、`__SYSCALL`、`__NR_*`、syscall table、`copy_to_user`/`copy_from_user` 路径；重点比较参数合法性、flag 语义、返回值、`errno`、compat 处理、阻塞/超时语义。
- ioctl/netlink：`_IO*` 命令号、uapi struct、`unlocked_ioctl`/`compat_ioctl`、`nla_policy`、generic netlink family/operation/attribute；重点比较命令号、属性必选性、长度、默认值和错误码。
- `/proc`、`/proc/sys`、`/sys` 输出差异：`proc_create*`、`seq_printf`/`seq_puts`、`proc_ops`、`register_sysctl`、`ctl_table`、`DEVICE_ATTR*`、`sysfs_emit*`、show/store 函数；字段增删、顺序、分隔符、单位、精度、默认值、权限、缺失文件和错误路径变化都应作为候选。
- 对 `debugfs`、trace/debug-only 输出保持谨慎：除非文档、工具或测试显示外部依赖，否则只保留在 candidates，不写入最终 findings。

**Python**：
- `__all__` 列表中的符号
- 不带 `_` 前缀的模块级函数/类
- stdlib 模块中的公共 API
- `Lib/` 下的公共模块

**Go**：
- 大写字母开头的 exported identifiers
- `go doc` 可见的 API
- `cmd/go` 行为变更

**Ruby**：
- public methods（非 private/protected）
- C extension API（`rb_*` 函数）
- 标准库公共 API

### Phase 5: 兼容性变更候选生成

对每个变更，构建三类候选：

#### 5.1 签名差异 (SIGNATURE_DIFF)

比较 old/new 的：
- 函数名、可见性
- 参数个数、类型、顺序、默认值
- 返回值类型
- 结构体/枚举/宏/常量
- 导出符号表

```json
{
  "candidate_type": "SIGNATURE_DIFF",
  "symbol": "<函数名>",
  "file": "<文件路径>",
  "old_signature": "<旧签名>",
  "new_signature": "<新签名>",
  "evidence": ["<变更项>", ...]
}
```

#### 5.2 契约差异 (CONTRACT_DIFF)

抽取：
- 新增/删除 guard 条件
- 输入校验变化（NULL 接受性、范围检查、类型检查）
- 错误路径变化（errno、异常类型、return code）
- 资源生命周期变化（acquire/release 模式）
- 文档注释中 @param/@return/@raises 变化

```json
{
  "symbol": "<函数名>",
  "old_contract": {
    "accepts_null": <true|false>,
    "input_range": "<描述>",
    "on_invalid": "<描述>",
    "return": "<描述>",
    "errors": ["<错误>", ...]
  },
  "new_contract": {
    "accepts_null": <true|false>,
    "input_range": "<描述>",
    "on_invalid": "<描述>",
    "return": "<描述>",
    "errors": ["<错误>", ...]
  }
}
```

#### 5.3 行为差异 (BEHAVIOR_DIFF)

构建轻量语义摘要：
- 控制流差异（新增/删除条件分支、循环）
- 数据流差异（变量赋值、状态变更）
- 可观察效果（输出、状态、资源、时间、错误路径）
- 系统接口输出差异（syscall/ioctl/netlink 返回、`/proc`、`/proc/sys`、`/sys` 文本字段、权限、单位、默认值）

```json
{
  "old_behavior_summary": "<旧行为一句话描述>",
  "new_behavior_summary": "<新行为一句话描述>",
  "observable_effect": "<外部可观察的效果>"
}
```

### Phase 6: LLM 语义判定

**对每个候选变更，你必须基于以下证据做出判断：**

**你收到的上下文必须包含：**
1. 变更 hunk（diff 片段）
2. 变更前函数的完整代码
3. 变更后函数的完整代码
4. 函数签名对比
5. 调用方摘要（至少 3-5 个典型调用方）
6. API surface 判断结果
7. 相关注释/文档/测试名
8. contract diff / behavior diff 摘要
9. 目标项目 profile 的 API 边界定义

**判定分类体系：**

| 类型 | 说明 |
|------|------|
| API_SIGNATURE_CHANGE | 函数签名/ABI 变更 |
| ABI_CHANGE | 结构体布局/枚举值/导出符号/二进制接口变更 |
| INPUT_CONTRACT_CHANGE | 输入合法性检查变化（收紧/放宽） |
| RETURN_CONTRACT_CHANGE | 返回值约定变化 |
| ERROR_EXCEPTION_CHANGE | 错误码/异常类型/异常消息变化 |
| SIDE_EFFECT_CHANGE | 副作用变化（状态、资源、并发） |
| OUTPUT_FORMAT_CHANGE | 输出格式化行为变化 |
| PROC_SYS_OUTPUT_CHANGE | `/proc`、`/proc/sys`、`/sys` 条目、属性或文本输出差异 |
| SYSCALL_SEMANTIC_CHANGE | 系统调用号、参数、flag、`errno`、compat、阻塞/超时语义差异 |
| IOCTL_NETLINK_ABI_CHANGE | ioctl 命令、uapi struct、netlink family/attribute/policy 差异 |
| CONFIG_CLI_BEHAVIOR_CHANGE | 配置/CLI/环境变量行为变化 |
| RESOURCE_LIFETIME_CHANGE | 资源生命周期变化（内存、fd、锁） |
| PERFORMANCE_RESOURCE_SEMANTIC_CHANGE | 性能/超时/重试语义变化 |

最终 `findings` 只输出确认存在兼容性变化、并可作为后续回归测试、已有断言复核或 fuzzing 种子目标的项。纯内部变更、无法说明外部可观察影响的候选应留在 `candidates.json`，不要写入最终 `findings`。

**代码行位置是强制输出项**：每条最终 finding 必须包含 `location.file`、`location.old_lines`、`location.new_lines`、`location.symbol`，并且至少有一条 `evidence[]` 包含 `file`、`lines`、`snippet`。不要用 `affected_file`、`affected_symbols`、自然语言描述或报告标题替代 `location`；缺少行号的 finding 不合格。行号优先来自 `candidates.json` 的 `old_start/old_end/new_start/new_end`，必要时回到 `patch.diff` 的 hunk header 校正。

**对每个候选，你必须回答：**

1. 是否为兼容性变更？ (is_compatibility_change: bool)
2. 兼容性变更类型？ (compatibility_type: string)
3. 影响什么接口/API？ (affected_api)
4. 变更前行为？ (old_behavior)
5. 变更后行为？ (new_behavior)
6. 为什么客户端可能受影响？ (compatibility_reason)
7. 代码行位置？ (location)
8. 置信度？ (confidence: 0.0-1.0)
9. 推荐测试优先级？ (test_priority: high|medium|low)
10. 是否需要人工复核？ (manual_review_required: bool)

**测试优先级判定：**

```
HIGH (高优先级测试):
  - 最有价值优先测试，最可能导致既有回归测试、脚本断言、用户可见输出断言或协议/API 断言发生变化
  - 公共接口签名/ABI 变化
  - 错误码/异常/返回值语义变化
  - 输入契约收紧（新增拒绝合法输入的逻辑）
  - UAPI / syscall / ioctl / netlink / procfs / sysfs / sysctl / CLI / 配置文件 / 协议解析不兼容
  - 结构体布局变化影响 ABI
  - 导出符号删除/重命名
  - `/proc`、`/proc/sys`、`/sys` 的稳定或广泛消费输出发生字段、单位、权限、默认值或错误码变化
  - 命令行输出、配置默认值、协议字段、日志/诊断信息或测试夹具中已有断言依赖的行为发生变化
  - 长度检查、边界检查、资源生命周期、状态机路径发生变化并可由外部输入触发

MEDIUM (中优先级测试):
  - 明确属于兼容性变化，但触发条件较具体或影响面较窄
  - 输出格式变化（可能影响解析方）
  - 默认行为变化
  - 资源生命周期变化
  - 性能/超时语义变化
  - 行为变化影响已文档化的行为，或可能影响少量既有回归断言

LOW (低优先级测试):
  - 确认属于兼容性变化，但测试价值或潜在缺陷触发概率较低
  - 内部行为变化，但只有间接外部可观察影响
  - 文档/测试显示可能有兼容性含义
  - 新增可选参数/放宽输入
```

`test_priority` 不是普通 bug 风险概率，也不是兼容性变化是否成立的判据，更不是安全风险等级。所有最终 findings 都必须已经是兼容性变化；该字段只表达后续回归测试、已有断言复核、测试入口生成和可选 fuzzing 的推荐优先级。安全相关变化可以是高优先级来源之一，但不是唯一来源。

**质量控制：**

对每条 finding 实施三层校验：
1. **证据校验** — 必须引用具体文件、行号、代码片段
2. **表面校验** — 不是 public/exported/CLI/config/protocol/test-reachable 且无法说明外部影响的候选，不写入最终 findings
3. **测试价值校验** — 说明为什么该兼容性变化值得按当前优先级进入回归测试、已有断言复核、测试入口生成或 fuzzing

写完 `analysis.json` 后必须运行：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_analysis.py" "${RESULT_DIR}/analysis.json"
```

如果校验失败，必须修正 `analysis.json` 和 `report.md` 后重新运行，直到通过。不能把未通过校验的结果作为最终产物汇报。

### Phase 7: 静态调用链（可选）

如果 `include_call_chain` 为 `true`，只对最终确认的 `findings` 构建调用链，不要对全部 candidates 构建调用链。正确顺序是：先完成语义判定并写入通过校验的 `analysis.json`，再按每条 finding 的 `location.symbol` 和 `location.file` 运行调用链。

**测试入口程序定义**：

测试入口程序是指能触发变更代码路径的具体测试用例，必须尽量包含测试文件名、测试类名（如有）、测试方法/函数名，并用 `::` 分隔。例如 `Lib/test/test_urlparse.py::UrlParseTestCase::test_invalid_port`、`builtin/log.c::test_commit_log`。

**尽力而为声明**：

调用链构建是辅助证据，不是 finding 成立的前置条件。受限于静态分析工具可用性、语言动态特性、回调、函数指针、宏展开和跨语言绑定，可能无法为所有 finding 找到入口。找不到入口不视为分析失败；如果 `include_call_chain` 未开启或构建失败，`static_call_chains` 输出空数组 `[]`。

**入口类型分类**：

| entry_kind | 说明 | 模式示例 |
|------------|------|----------|
| test_entry | 测试框架中的测试用例 | `test_*.py`, `*_test.go`, `*Test.java`, `t/test_*.c` |
| cli_entry | CLI 主入口 | `main()`, `handle_main()`, `cmd_main()` |
| http_handler | HTTP 请求处理器 | `*_handler()`, `serve_*()`, route handlers |
| config_parser | 配置解析入口 | `*_config_parse()`, `*_read_config()` |
| plugin_callback | 插件/模块回调 | `module_init()`, `plugin_*()`, hook functions |
| exported_api | 库导出 API | `EXPORT_SYMBOL`, `PyAPI_FUNC`, exported Go identifiers |
| syscall | 系统调用入口 | `SYSCALL_DEFINE*`, `COMPAT_SYSCALL_DEFINE*`, syscall table |
| ioctl | ioctl 入口 | `unlocked_ioctl`, `compat_ioctl`, `_IO*` command |
| netlink | netlink 协议入口 | `genl_family`, `genl_ops`, `nla_policy` |
| procfs | procfs 输出入口 | `proc_create*`, `seq_printf`, `proc_ops` |
| sysfs | sysfs 属性入口 | `DEVICE_ATTR*`, `sysfs_emit`, show/store |
| sysctl | `/proc/sys` 入口 | `register_sysctl`, `ctl_table`, `proc_dointvec` |
| daemon_handler | 守护进程命令处理器 | dbus handler, signal handler, admin socket |

**调用链构建原则**：

1. 只使用 AST 级分析。Python 使用标准库 `ast`；C/C++、Go、Ruby 使用 `tree_sitter` 语法树。
2. 不允许回退到正则、grep、ctags、cscope 或全仓词法扫描构建调用链。AST 依赖缺失时调用链输出 `[]`，并在最终回复中说明依赖缺失或未配置。
3. 对每个最终 finding 的变更符号调用 `${CLAUDE_SKILL_DIR}/scripts/callgraph.py`：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/callgraph.py" \
  --repo "<analysis_repo>" \
  --target "<changed_symbol>" \
  --file "<changed_file>" \
  --language "<c|python|go|ruby>" \
  --output "${RESULT_DIR}/callchains-<changed_symbol>.json"
```

4. 推荐直接使用 orchestrator 的附加调用链模式，它会从最终 `analysis.json` 读取 findings、构建调用链、回写每条 finding 的 `static_call_chains` 并更新 `${RESULT_DIR}/callchains.json`：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/orchestrator.py" \
  --attach-call-chains "${RESULT_DIR}/analysis.json"
```

该模式会读取 `analysis.json.analysis_repo`，只在已应用补丁的隔离 worktree 上构建调用链。若 `analysis_repo` 缺失或目录不存在，orchestrator 会根据 `repo + base_commit + patch.diff` 先重建 worktree；不要退回到源 repo 当前 checkout。`--attach-call-chains` 不负责清理 worktree；清理是可选动作，只有用户要求释放空间且后续不需要测试/fuzzing 时才运行 `--cleanup-worktree`。

5. 如果脚本不存在、AST 依赖缺失、超时或返回空数组，不要中断兼容性分析，写入空数组 `[]`，并说明调用链是尽力而为证据。

输出格式：
```json
"static_call_chains": [
  {
    "entry_kind": "test_entry",
    "entry": "<文件>::<符号>",
    "chain": ["<符号1>", "<符号2>", ..., "<变更符号>"]
  }
]
```

### Phase 8: 测试交接

完成并校验 `analysis.json` 后停止分析。不要写入 `test-entry-tasks.json`、
`test-entry-work/` 或 finding 级 `test_entries[]`。如果用户要求继续测试，
将 `RESULT_DIR/analysis.json` 交给同级 `patch-compatibility-testing`；测试入口
规划、生成、执行和覆盖率证据全部由测试子 skill 写入其独立结果目录。

### Phase 9: 格式化输出

#### JSON 输出格式

最终 JSON 写入 `${RESULT_DIR}/analysis.json`。

```json
{
  "repo": "<源仓库路径，产物落盘位置>",
  "analysis_repo": "<已应用补丁的隔离 worktree 路径>",
  "artifact_dir": "<用户指定的 output_dir，或默认 <repo>/pca-results/<patch_id[:6]>>",
  "base_ref": "<基线 ref>",
  "base_commit": "<基线 commit>",
  "patch_apply_status": "applied|already_applied|applied_3way",
  "patch_apply_message": "<补丁应用状态说明>",
  "analysis_worktree_status": "available|cleaned",
  "patch_id": "<补丁标识>",
  "package_profile": "<profile 名>",
  "summary": {
    "total_changed_files": <N>,
    "total_candidates": <N>,
    "compatibility_changes": <N>,
    "high_priority": <N>,
    "medium_priority": <N>,
    "low_priority": <N>
  },
  "findings": [
    {
      "id": "PCA-0001",
      "compatibility_type": "<类型>",
      "test_priority": "high|medium|low",
      "confidence": <0.0-1.0>,
      "package_profile": "<profile>",
      "affected_surface": "<API surface 描述>",
      "affected_api": {
        "name": "<API 名称>",
        "kind": "exported_function|public_method|syscall|ioctl|netlink_family|procfs_entry|sysfs_attribute|sysctl_entry|cli_command|config_key|...",
        "language": "c|cpp|python|go|ruby|..."
      },
      "location": {
        "file": "<文件路径>",
        "old_lines": [<旧文件开始行>, <旧文件结束行>],
        "new_lines": [<新文件开始行>, <新文件结束行>],
        "symbol": "<符号名>"
      },
      "old_behavior": "<变更前行为>",
      "new_behavior": "<变更后行为>",
      "compatibility_reason": "<兼容性影响说明>",
      "evidence": [
        {
          "file": "<文件路径>",
          "lines": [<开始>, <结束>],
          "snippet": "<代码片段>"
        }
      ],
      "static_call_chains": [],
      "why_not_internal_only": "<解释为何不是纯内部变更>",
      "uncertainty": "<不确定因素>",
      "manual_review_required": true|false,
      "recommended_review": "<建议的人工复核点>",
      "test_recommendation": "<建议的回归测试/已有断言复核/fuzzing 方向>"
    }
  ]
}
```

#### Markdown 输出格式

当用户要求 Markdown 或需要可读摘要时，写入 `${RESULT_DIR}/report.md`。报告语言必须跟随用户请求语言；无法判断时使用中文。下方是中文模板，如果用户用英文或其他语言请求，则把标题、字段标签和自然语言说明等价翻译成对应语言，代码块、路径、CLI 选项和枚举值保持原文。

```markdown
# PCA 兼容性变更分析报告

**仓库**: {repo}
**基线**: {base_ref}
**补丁**: {patch_id}
**Profile**: {package_profile}

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | {total_changed_files} |
| 候选变更 | {total_candidates} |
| 兼容性变更 | {compatibility_changes} |
| 高优先级测试 | {high_priority} |
| 中优先级测试 | {medium_priority} |
| 低优先级测试 | {low_priority} |

---

## PCA-{序号}: {兼容性变更类型中文名}

- **测试优先级**: HIGH / MEDIUM / LOW
- **置信度**: {confidence}
- **影响接口**: {affected_api.name}
- **旧代码位置**: {location.file}:{location.old_lines[0]}-{location.old_lines[1]}
- **新代码位置**: {location.file}:{location.new_lines[0]}-{location.new_lines[1]}
- **类型**: {compatibility_type}

### 变更前行为
{old_behavior}

### 变更后行为
{new_behavior}

### 兼容性影响
{compatibility_reason}

### 证据
```{language}
{snippet}
```

### 静态调用链
{call_chain 内容}

### 复核建议
{recommended_review}

### 测试建议
{test_recommendation}

---
```

---

## 关键注意事项

1. **不要只给 diff** — 必须读取变更前后的完整函数代码，因为语义差异需要上下文
2. **不要臆测** — 每条结论必须有代码证据支撑
3. **不要混用代码状态** — 补丁后上下文和 CallGraph 只能来自 `analysis_repo`；源 repo 当前 checkout 可能是补丁前、补丁后或无关集成分支，不能作为语义判断的隐式依据。所有 `rg`/`grep`/文件读取路径都必须指向 `analysis_repo`。
4. **区分内部和外部** — 内部 static 函数、private 方法等默认不是兼容性问题
5. **考虑调用方** — 如果一个"内部"函数被广泛的外部模块使用，它实际是公共 API
6. **Kernel 特殊处理** — UAPI 变更任何细节通常都是高优先级测试目标；内部 kernel 函数通常不视为 API
7. **Python 特殊处理** — `_` 前缀的函数/类默认不是公共 API；`__all__` 列表中的符号是公共 API
8. **Go 特殊处理** — 小写字母开头的一定不是 exported；大写字母开头的是 exported
9. **对于不确定的判定，宁可标记为需要人工复核，也不要把非兼容性变化写入最终 findings**

---

## 执行模板

当你被调用时，按以下步骤执行：

```
1. [Bash] 运行 check_dependencies.py；失败则询问用户是否配置依赖
2. [Bash] 运行 orchestrator.py，完成仓库准备、patch_id、产物目录、隔离 patched worktree、候选和报告草稿生成；若用户指定产物目录，传入 `--output-dir <用户目录>`；此阶段不对全部 candidates 跑调用链
3. [Read] 读取 `RESULT_DIR/candidates.json`、`report.md`
4. [Read] 从 `analysis.json.analysis_repo` 读取补丁后完整上下文；从 `base_commit` 或 `patch.diff` 读取补丁前上下文。不要从源 repo 当前 checkout 读取补丁后代码；所有 `rg`/`grep`/文件打开路径都应以 `analysis_repo` 为根目录。
5. [Read] 读取对应 package profile 配置
6. [分析] 对每个候选执行 Phase 5-6 的判定，只把确认的兼容性变化写入最终 findings
7. [Write] 更新 `analysis.json`，按需更新 `report.md`；`report.md` 和用户可读分析说明使用用户请求语言，默认中文
8. [Bash] 运行 `validate_analysis.py RESULT_DIR/analysis.json`；失败时回到第 7 步修正
9. [Bash] 如果 include_call_chain=true，运行 check_dependencies.py --include-callgraph，然后运行 orchestrator.py --attach-call-chains RESULT_DIR/analysis.json
10. [Skip by default] 不自动运行 cleanup。若用户明确要求释放空间且不会继续测试，再运行 orchestrator.py --cleanup-worktree RESULT_DIR/analysis.json
11. [输出] 向用户展示兼容性变化摘要、代码行位置和推荐测试优先级，并明确说明分析产物目录和 worktree 状态
12. [Ask/Handoff] 如果用户尚未明确要求测试，最后询问：`补丁兼容性分析已完成，是否继续基于该分析结果进行定向测试？` 用户同意后读取并执行 `../patch-compatibility-testing/SKILL.md`，传入本次 `RESULT_DIR/analysis.json`。如果用户一开始已经明确要求分析后继续测试，则直接交接，不重复询问。
```
