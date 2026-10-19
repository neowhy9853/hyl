# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/_worktrees/patched`
- Patch ID: `4b5d8a0163fe4e9a4ac074f407e0599ba27acf68`
- Base ref: `42d960748efa79a31e72cc36d983aca244dc167e`
- Base commit: `42d960748efa79a31e72cc36d983aca244dc167e`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 4946 |
| `patch_lines` | 128 |
| `raw_hunks` | 4 |
| `candidate_hunks` | 3 |
| `changed_files` | 2 |
| `churn` | 63 |
| `candidate_context_bytes` | 8049 |
| `candidates_json_bytes` | 18472 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 42d960748efa79a31e72cc36d983aca244dc167e:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `revision.c` old `3181-3187` new `3181-3189` symbol `rev_info, DIFF_FORMAT_PATCH, DIFF_FORMAT_NO_OUTPUT, DIFF_FORMAT_RAW, DIFF_FORMAT_NAME, DIFF_FORMAT_NAME_STATUS, die` surface `user_visible_output, logging`
- `HUNK-0003` `t/t4211-line-log.sh` old `155-162` new `155-199` symbol `test_expect_success, raw, shows, mode, oid, status` surface `tests, user_visible_output`
- `HUNK-0004` `t/t4211-line-log.sh` old `738-741` new `775-784` symbol `test_expect_success, summary, shows, new, file, on` surface `tests`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/analysis.json`
