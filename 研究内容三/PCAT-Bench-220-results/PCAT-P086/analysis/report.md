# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/_worktrees/patched`
- Patch ID: `9770e32ce07110f0c8c7a381604ec9a490028eed`
- Base ref: `9770e32ce07110f0c8c7a381604ec9a490028eed^`
- Base commit: `9eb50a40b4186d665aa98c8dbea7cf60fb2aacca`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=268 >= 250
- Changed files: 5
- Candidate hunks: 8
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 19224 |
| `patch_lines` | 436 |
| `raw_hunks` | 16 |
| `candidate_hunks` | 8 |
| `changed_files` | 5 |
| `churn` | 268 |
| `candidate_context_bytes` | 30594 |
| `candidates_json_bytes` | 69884 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/shards`
- Shard count: 3

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `internal_or_unknown` | 1 | 1 | 280 | `shards/shard-0001.json` |
| `SHARD-0002` | `python_public_api` | 4 | 2 | 10119 | `shards/shard-0002.json` |
| `SHARD-0003` | `tests` | 3 | 2 | 20195 | `shards/shard-0003.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show 9eb50a40b4186d665aa98c8dbea7cf60fb2aacca:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/analysis.json`.

## Candidate Hunks

- `HUNK-0009` `Lib/os.py` old `219-232` new `219-235` symbol `_add, def, makedirs, name, mode, exist_ok` surface `python_public_api, python_exceptions, syscall_wrappers, user_visible_output, python_stdlib, exceptions`
- `HUNK-0010` `Lib/os.py` old `234-240` new `237-247` symbol `makedirs, parent_mode, is, not, None, head` surface `python_public_api, python_exceptions, user_visible_output, python_stdlib, exceptions`
- `HUNK-0011` `Lib/pathlib/__init__.py` old `1204-1210` new `1204-1210` symbol `touch, def, mkdir, self, mode, parents` surface `python_public_api, python_exceptions, user_visible_output, python_stdlib, exceptions`
- `HUNK-0012` `Lib/pathlib/__init__.py` old `1213-1219` new `1213-1223` symbol `mkdir, parent_mode, is, not, None, self, parent, parents` surface `python_public_api, python_exceptions, user_visible_output, python_stdlib, exceptions`
- `HUNK-0013` `Lib/test/test_os/test_os.py` old `2139-2144` new `2139-2232` symbol `test_mode, unittest, skipIf, support, is_emscripten, or` surface `tests, python_exceptions, exceptions`
- `HUNK-0014` `Lib/test/test_os/test_os.py` old `2212-2226` new `2300-2308` symbol `test_win32_mkdir_700, Remove, the, whole, tree, regardless` surface `tests, python_exceptions, exceptions`
- `HUNK-0015` `Lib/test/test_pathlib/test_pathlib.py` old `2492-2497` new `2492-2604` symbol `my_mkdir, unittest, skipIf, is_emscripten, or, is_wasi` surface `tests`
- `HUNK-0016` `Misc/NEWS.d/next/Library/2025-08-30-07-44-30.gh-issue-86533.pathlib.rst` old `0--1` new `1-4` symbol `The, func, os, makedirs, function, and` surface `unknown`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P026/analysis.json`
