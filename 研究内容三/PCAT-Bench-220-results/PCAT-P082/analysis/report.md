# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/_worktrees/patched`
- Patch ID: `6ca5cdba185aeb3b7f72ae0dd61b6a9685d8c416`
- Base ref: `6ca5cdba185aeb3b7f72ae0dd61b6a9685d8c416^`
- Base commit: `5dd5c8b5a66af18904d4e015ce3120e2686ddb23`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=290 >= 250
- Changed files: 7
- Candidate hunks: 9
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 19102 |
| `patch_lines` | 500 |
| `raw_hunks` | 19 |
| `candidate_hunks` | 9 |
| `changed_files` | 7 |
| `churn` | 290 |
| `candidate_context_bytes` | 16790 |
| `candidates_json_bytes` | 49611 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/shards`
- Shard count: 4

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `internal_or_unknown` | 2 | 2 | 2373 | `shards/shard-0001.json` |
| `SHARD-0002` | `public_headers` | 4 | 2 | 8523 | `shards/shard-0002.json` |
| `SHARD-0003` | `python_exceptions` | 1 | 1 | 2222 | `shards/shard-0003.json` |
| `SHARD-0004` | `tests` | 2 | 2 | 3672 | `shards/shard-0004.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show 5dd5c8b5a66af18904d4e015ce3120e2686ddb23:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/analysis.json`.

## Candidate Hunks

- `HUNK-0011` `Include/cpython/critical_section.h` old `2-16` new `2-7` symbol `Python, critical, sections, Conceptually, are, a` surface `public_headers, user_visible_output, c_api`
- `HUNK-0012` `Include/cpython/critical_section.h` old `43-94` new `34-52` symbol `undef, Py_BEGIN_CRITICAL_SECTION, Py_END_CRITICAL_SECTION, Py_BEGIN_CRITICAL_SECTION2, Py_END_CRITICAL_SECTION2, NOTE` surface `public_headers, c_api`
- `HUNK-0013` `Include/cpython/critical_section.h` old `101-154` new `59-75` symbol `PyCriticalSection2_End, Py_GIL_DISABLED, endif, NOTE, the, contents` surface `public_headers, c_api`
- `HUNK-0014` `Include/critical_section.h` old `4-9` new `4-94` symbol `Python, critical, sections, Conceptually, are, a` surface `public_headers, c_api, stable_abi`
- `HUNK-0015` `Lib/test/test_cext/extension.c` old `99-104` new `99-108` symbol `_testcext_exec, Test, that, Py_BEGIN_CRITICAL_SECTION, is, available, Py_END_CRITICAL_SECTION, assert` surface `tests`
- `HUNK-0016` `Lib/test/test_stable_abi_ctypes.py` old `134-139` new `134-143` symbol `test_windows_feature_macros, PyCriticalSection2_Begin, PyCriticalSection2_End, PyCriticalSection_Begin, PyCriticalSection_End` surface `tests`
- `HUNK-0017` `Misc/NEWS.d/next/C_API/2026-05-01-14-49-09.gh-issue-149225.IdAYPZ.rst` old `0--1` new `1-2` symbol `c, type, PyCriticalSection, and, related, functions` surface `unknown`
- `HUNK-0018` `Misc/stable_abi.toml` old `2689-2694` new `2689-2716` symbol `function, PyCriticalSection_Begin, added, PyCriticalSection_End, PyCriticalSection, struct_abi_kind` surface `unknown`
- `HUNK-0019` `PC/python3dll.c` old `174-179` new `174-183` symbol `EXPORT_FUNC, PyCriticalSection2_Begin, PyCriticalSection2_End, PyCriticalSection_Begin, PyCriticalSection_End, __pragma` surface `python_exceptions, stable_abi`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P022/analysis.json`
