# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/cpython`
- Patched analysis worktree: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/_worktrees/patched`
- Patch ID: `07ae6f133ad7a4e7ed506f6a511809b1fc3d1465`
- Base ref: `71cf3130c6e5dd903837b6871af99156c799fd1e`
- Base commit: `71cf3130c6e5dd903837b6871af99156c799fd1e`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 4
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2771 |
| `patch_lines` | 64 |
| `raw_hunks` | 4 |
| `candidate_hunks` | 4 |
| `changed_files` | 3 |
| `churn` | 12 |
| `candidate_context_bytes` | 7282 |
| `candidates_json_bytes` | 21136 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/cpython show 71cf3130c6e5dd903837b6871af99156c799fd1e:<path>`.
- Rebuild worktree: `/home/soong/miniconda3/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/miniconda3/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `Lib/sysconfig/__init__.py` old `437-442` new `437-443` symbol `parse_config_h, quoted_re, re, compile` surface `python_public_api, python_exceptions, config_keys, python_stdlib, exceptions`
- `HUNK-0002` `Lib/sysconfig/__init__.py` old `445-450` new `446-453` symbol `parse_config_h, mq, quoted_re, match, v, group` surface `python_public_api, python_exceptions, config_keys, python_stdlib, exceptions`
- `HUNK-0003` `Lib/test/test_sysconfig.py` old `576-581` new `576-587` symbol `test_linux_ext_suffix, unittest, skipIf, sysconfig, get_config_var, PY_BUILTIN_HASHLIB_HASHES, test_PY_BUILTIN_HASHLIB_HASHES_in_vars` surface `tests, config_keys`
- `HUNK-0004` `Misc/NEWS.d/next/Core_and_Builtins/2026-05-21-21-04-43.gh-issue-150208.VOkxRG.rst` old `0--1` new `1-2` symbol `Avoid, quoting, string, values, from, pyconfig` surface `config_keys`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis.json`
