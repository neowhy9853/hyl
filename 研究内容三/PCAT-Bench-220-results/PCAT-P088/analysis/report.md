# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/_worktrees/patched`
- Patch ID: `681477de459bd12ab2429669aa6d52cbed83c018`
- Base ref: `681477de459bd12ab2429669aa6d52cbed83c018^`
- Base commit: `93beea7e5a3c5a03253e6812a06f2497505aeb30`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3105 |
| `patch_lines` | 79 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 37 |
| `candidate_context_bytes` | 5559 |
| `candidates_json_bytes` | 15981 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython show 93beea7e5a3c5a03253e6812a06f2497505aeb30:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `Lib/tarfile.py` old `2129-2135` new `2129-2135` symbol `zstopen, except, Exception` surface `python_public_api, python_exceptions, python_stdlib, exceptions`
- `HUNK-0002` `Lib/test/test_tarfile.py` old `1141-1146` new `1141-1178` symbol `LzmaDetectReadTest, support, requires_zstd, class, ZstdOpenTest, unittest, ZstdDetectReadTest` surface `tests, python_exceptions`
- `HUNK-0003` `Misc/NEWS.d/next/Library/2026-05-19-18-25-00.gh-issue-150077.zstopen-close.rst` old `0--1` new `1-3` symbol `Fix, tarfile, TarFile, zstopen, to, close` surface `python_exceptions`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P028/analysis.json`
