# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/62319b/_worktrees/patched`
- Patch ID: `62319b49bbe7e52df2cf90d8c4a5121112135784`
- Base ref: `62319b49bbe7e52df2cf90d8c4a5121112135784^`
- Base commit: `c9d708b7fce6f910d77f5cb499796712f3bdfd04`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/62319b/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/62319b/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/62319b`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1254 |
| `patch_lines` | 41 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 5 |
| `candidate_context_bytes` | 1897 |
| `candidates_json_bytes` | 4473 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/62319b/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show c9d708b7fce6f910d77f5cb499796712f3bdfd04:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/62319b/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/62319b/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `.gitlab-ci.yml` old `104-113` new `104-113` symbol `image, macos, xcode` surface `unknown`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/62319b/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/62319b/analysis.json`
