# Patch Compatibility Analyzer Report Draft

- Source repo: `/data7/wanghy/tmp/opencode/go-checkout`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/_worktrees/patched`
- Patch ID: `2a95a616e9da16f49dfc55b11d7ca9f079bbb430`
- Base ref: `f192b5be2ef8f82e627e923ea72507c38b9f5ea5`
- Base commit: `f192b5be2ef8f82e627e923ea72507c38b9f5ea5`
- Patch apply status: `applied`
- Profile: `golang`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2830 |
| `patch_lines` | 58 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 2 |
| `churn` | 6 |
| `candidate_context_bytes` | 4380 |
| `candidates_json_bytes` | 13313 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/_worktrees/patched`.
- Pre-patch source read command: `git -C /data7/wanghy/tmp/opencode/go-checkout show f192b5be2ef8f82e627e923ea72507c38b9f5ea5:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/net/http/csrf.go` old `65-72` new `65-72` symbol `func, u, User, nil, Path, RawQuery, AddTrustedOrigin` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0002` `src/net/http/csrf_test.go` old `235-240` new `235-242` symbol `TestCrossOriginProtectionAddTrustedOriginErrors, with, empty, userinfo, https, example` surface `tests, go_errors, user_visible_output, stdlib, errors`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P032/analysis.json`
