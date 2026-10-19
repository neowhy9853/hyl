# Patch Compatibility Analyzer Report Draft

- Source repo: `/tmp/go-pcia-n029-shallow`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/_worktrees/patched`
- Patch ID: `ff4d4b349e71`
- Base ref: `e59fbed6bc5136c240d4ba6a67200d652736cd87~1`
- Base commit: `df98494a30bb8059fbf45b3d1ba0500721eacfcd`
- Patch apply status: `applied`
- Profile: `golang`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1936 |
| `patch_lines` | 58 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 1 |
| `churn` | 33 |
| `candidate_context_bytes` | 5006 |
| `candidates_json_bytes` | 17211 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/_worktrees/patched`.
- Pre-patch source read command: `git -C /tmp/go-pcia-n029-shallow show df98494a30bb8059fbf45b3d1ba0500721eacfcd:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/cmd/internal/script/engine_test.go` old `13-18` new `13-19` symbol `import, strings` surface `tests, go_commands`
- `HUNK-0002` `src/cmd/internal/script/engine_test.go` old `59-71` new `60-66` symbol `TestInterruptCmd, checkInterruptCmdError, t, err, expectedError, signal` surface `tests, go_errors, go_commands, user_visible_output, errors`
- `HUNK-0003` `src/cmd/internal/script/engine_test.go` old `76-81` new `71-100` symbol `TestInterruptCmd, checkInterruptCmdError, calls, t, Fatal, err` surface `tests, go_errors, go_commands, user_visible_output, errors`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N029/analysis.json`
