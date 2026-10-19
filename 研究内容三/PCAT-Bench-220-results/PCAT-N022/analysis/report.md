# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/vim`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/_worktrees/patched`
- Patch ID: `7b11d840c00d3807a7ac88e131fefd886fe2cfa4`
- Base ref: `HEAD`
- Base commit: `3cfdb634b1db2ed51d1147b720e0d9d67b7f5252`
- Patch apply status: `already_applied`
- Profile: `vim`
- Effective profile: `/home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 0
- Candidate hunks: 0
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1961 |
| `patch_lines` | 52 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 0 |
| `changed_files` | 0 |
| `churn` | 11 |
| `candidate_context_bytes` | 0 |
| `candidates_json_bytes` | 736 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/vim show 3cfdb634b1db2ed51d1147b720e0d9d67b7f5252:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/analysis.json`.

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/vim/pca-results/7b11d8/analysis.json`
