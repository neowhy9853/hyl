# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/_worktrees/patched`
- Patch ID: `3fbef193c7e49e8edb5a4421c465df67de944da6`
- Base ref: `7c7c7ba4cea2f0063efa2a2a0d7c3d05ed8766fb`
- Base commit: `7c7c7ba4cea2f0063efa2a2a0d7c3d05ed8766fb`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 7150 |
| `patch_lines` | 228 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 128 |
| `candidate_context_bytes` | 3618 |
| `candidates_json_bytes` | 13640 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 7c7c7ba4cea2f0063efa2a2a0d7c3d05ed8766fb:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `git-gui.sh` old `2999-3099` new `2999-3103` symbol `proc, show_parse_err, err, tk, windowingsystem, eq` surface `cli_options, user_visible_output, cli`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis.json`
