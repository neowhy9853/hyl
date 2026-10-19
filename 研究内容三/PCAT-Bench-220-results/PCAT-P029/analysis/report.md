# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/_worktrees/patched`
- Patch ID: `pca_2b8d07`
- Base ref: `5111520e2a140b80f60565c579b694b8d95eee01`
- Base commit: `5111520e2a140b80f60565c579b694b8d95eee01`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_2b`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 4
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 4980 |
| `patch_lines` | 156 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 4 |
| `changed_files` | 3 |
| `churn` | 105 |
| `candidate_context_bytes` | 10388 |
| `candidates_json_bytes` | 24029 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 5111520e2a140b80f60565c579b694b8d95eee01:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `path-walk.c` old `382-388` new `382-388` symbol `path_walk_context, ctx, info, strict_types, path_is_for_direct_objects, path, oid_array_append` surface `unknown`
- `HUNK-0003` `path-walk.c` old `608-613` new `608-624` symbol `path_walk_info, LOFC_OBJECT_TYPE, info, commits, options, object_type, list_objects_filter_release` surface `user_visible_output`
- `HUNK-0004` `path-walk.h` old `47-52` new `47-58` symbol `path_walk_info, If, strict_types, is, then, direct, int` surface `public_library_headers`
- `HUNK-0005` `t/t6601-path-walk.sh` old `643-648` new `643-732` symbol `test_expect_success, all, object, type, commit, filter` surface `tests`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/pca_2b/analysis.json`
