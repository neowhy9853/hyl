# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/cpython`
- Patched analysis worktree: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/_worktrees/patched`
- Patch ID: `671d44f859bc597da9c27e4462b66d3b4ecc5644`
- Base ref: `1d4e965829eef4cdb089a984fda21ca465a1f534`
- Base commit: `1d4e965829eef4cdb089a984fda21ca465a1f534`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 0
- Candidate hunks: 0
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 552 |
| `patch_lines` | 15 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 0 |
| `changed_files` | 0 |
| `churn` | 2 |
| `candidate_context_bytes` | 0 |
| `candidates_json_bytes` | 801 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/cpython show 1d4e965829eef4cdb089a984fda21ca465a1f534:<path>`.
- Rebuild worktree: `/home/soong/miniconda3/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/miniconda3/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/analysis.json`.

## Candidate Hunks


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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-N014/analysis.json`
