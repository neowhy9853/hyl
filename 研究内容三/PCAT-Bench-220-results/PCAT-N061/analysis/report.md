# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/_worktrees/patched`
- Patch ID: `63a2709b700d5532b8925caca5bc8b9437e7a1f3`
- Base ref: `63a2709b700d5532b8925caca5bc8b9437e7a1f3^`
- Base commit: `70f7c6c0f2ddfd3b447946f1b926776b2a344703`
- Patch apply status: `applied`
- Profile: `c_project`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1504 |
| `patch_lines` | 39 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 7 |
| `candidate_context_bytes` | 3870 |
| `candidates_json_bytes` | 10577 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show 70f7c6c0f2ddfd3b447946f1b926776b2a344703:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `Lib/test/test_zipfile/test_core.py` old `1-6` new `1-7` symbol `import, errno` surface `tests, user_visible_output`
- `HUNK-0002` `Lib/test/test_zipfile/test_core.py` old `655-660` new `656-667` symbol `test_add_file_after_2107, except, OSError, as, exc, Some` surface `tests, syscall_wrappers, user_visible_output`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## Agent Adjudication Requirements

- This report is deterministic evidence, not the final compatibility decision.
- Start from analysis-context.json. It is the bounded context for agent adjudication and includes focused source excerpts.
- Do not reopen large source files to locate a changed function already present in analysis-context.json.
- Do not scan repo roots, patch-list directories, output directories, or profile trees.
- Final findings must include only confirmed compatibility changes.
- Every finding must include code line locations and at least one evidence snippet.
- In heavy mode, analyze each shard independently, then aggregate shard results with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N021/analysis.json`
