# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/glib`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/_worktrees/patched`
- Patch ID: `eaec725d99c166b8e2eabde04b131fc044ae9f1e`
- Base ref: `HEAD`
- Base commit: `6a7a743f75aaaa08227a06f7bd0b569e6a871371`
- Patch apply status: `already_applied`
- Profile: `glib2`
- Effective profile: `/home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/eaec72`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 0
- Candidate hunks: 0
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 941 |
| `patch_lines` | 28 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 0 |
| `changed_files` | 0 |
| `churn` | 4 |
| `candidate_context_bytes` | 0 |
| `candidates_json_bytes` | 737 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/glib show 6a7a743f75aaaa08227a06f7bd0b569e6a871371:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/analysis.json`.

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/glib/pca-results/eaec72/analysis.json`
