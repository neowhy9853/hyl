# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/_worktrees/patched`
- Patch ID: `5235467b9183a8be8675aed17bd5b5a993975da7`
- Base ref: `5235467b9183a8be8675aed17bd5b5a993975da7~1`
- Base commit: `c3972f2795bf9270008d09dc6919b9735e20c606`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=372 >= 250
- Changed files: 3
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 21125 |
| `patch_lines` | 470 |
| `raw_hunks` | 8 |
| `candidate_hunks` | 7 |
| `changed_files` | 3 |
| `churn` | 372 |
| `candidate_context_bytes` | 43956 |
| `candidates_json_bytes` | 91886 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/shards`
- Shard count: 3

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `python_public_api` | 3 | 1 | 15960 | `shards/shard-0001.json` |
| `SHARD-0002` | `tests` | 3 | 1 | 27584 | `shards/shard-0002.json` |
| `SHARD-0003` | `user_visible_output` | 1 | 1 | 412 | `shards/shard-0003.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show c3972f2795bf9270008d09dc6919b9735e20c606:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `Lib/inspect.py` old `3351-3356` new `3351-3445` symbol `BufferFlags, def, _get_details_for_cli, module, nominal_target, resolved_target, name` surface `python_public_api, python_exceptions, python_cli, cli_options, user_visible_output, python_stdlib`
- `HUNK-0003` `Lib/inspect.py` old `3367-3372` new `3456-3463` symbol `_main, We, don, t, use, pkgutil` surface `python_public_api, python_exceptions, python_cli, cli_options, user_visible_output, python_stdlib`
- `HUNK-0004` `Lib/inspect.py` old `3384-3412` new `3475-3490` symbol `_main, details, _get_details_for_cli, module, target, obj, _render_details_for_cli` surface `python_public_api, python_exceptions, python_cli, cli_options, user_visible_output, python_stdlib`
- `HUNK-0005` `Lib/test/test_inspect/test_inspect.py` old `6493-6500` new `6493-6511` symbol `test_wrapped_descriptor, def, _clean_object_ids, text, Helper, to` surface `tests, python_exceptions, user_visible_output, exceptions`
- `HUNK-0006` `Lib/test/test_inspect/test_inspect.py` old `6522-6548` new `6533-6755` symbol `test_qualname_source, def, test_error_builtins, self, assertEqual, lines, test_error_extension` surface `tests, python_exceptions, user_visible_output, exceptions`
- `HUNK-0007` `Lib/test/test_inspect/test_inspect.py` old `6635-6641` new `6842-6846` symbol `f` surface `tests, python_exceptions, cli_options, user_visible_output, exceptions`
- `HUNK-0008` `Misc/NEWS.d/next/Library/2026-05-04-00-51-32.gh-issue-149010.BCp_8k.rst` old `0--1` new `1-6` symbol `The, inspect, module, CLI, now, reports` surface `user_visible_output`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P027/analysis.json`
