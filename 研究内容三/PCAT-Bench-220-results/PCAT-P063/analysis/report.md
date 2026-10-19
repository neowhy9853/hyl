# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/_worktrees/patched`
- Patch ID: `98b1fd4ff9a719f34131fa04cbd93f92c0c362f7`
- Base ref: `HEAD`
- Base commit: `0748799ad18db4eeb72b33b30c5e0c420a8216ea`
- Patch apply status: `already_applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1369 |
| `patch_lines` | 34 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 6 |
| `candidate_context_bytes` | 1972 |
| `candidates_json_bytes` | 5943 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show 0748799ad18db4eeb72b33b30c5e0c420a8216ea:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/h3.c` old `2074-2081` new `2074-2082` symbol `qcs, TRACE_ERROR, Received, unexpected, PUSH_PROMISE, frame, qcc_set_error, BUG_ON` surface `user_visible_output, protocol_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis.json`
