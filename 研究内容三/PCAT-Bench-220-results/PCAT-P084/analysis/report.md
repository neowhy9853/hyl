# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/_worktrees/patched`
- Patch ID: `7f8fc07e850d7b27a220c815db8c8abd545286c3`
- Base ref: `7f8fc07e850d7b27a220c815db8c8abd545286c3^`
- Base commit: `2df69de5b36347d430aed0a959fa01e17b237331`
- Patch apply status: `applied`
- Profile: `c_project`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1836 |
| `patch_lines` | 41 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 2 |
| `churn` | 5 |
| `candidate_context_bytes` | 4708 |
| `candidates_json_bytes` | 15240 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show 2df69de5b36347d430aed0a959fa01e17b237331:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `Lib/asyncio/__main__.py` old `99-105` new `99-105` symbol `run, not, sys, flags, ignore_environment, and` surface `callbacks, environment_variables, cli_options, cli, env_vars, plugin_api`
- `HUNK-0002` `Lib/asyncio/__main__.py` old `200-206` new `200-206` symbol `interrupt, not, sys, flags, ignore_environment, and` surface `environment_variables, cli_options, user_visible_output, cli, env_vars, plugin_api`
- `HUNK-0003` `Misc/NEWS.d/next/Library/2026-05-06-23-13-40.gh-issue-149319.PLM93t.rst` old `0--1` new `1-1` symbol `The, mod, asyncio, REPL, now, ignores` surface `unknown`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P024/analysis.json`
