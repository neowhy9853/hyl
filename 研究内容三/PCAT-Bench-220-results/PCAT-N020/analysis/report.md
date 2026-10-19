# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/_worktrees/patched`
- Patch ID: `92206fb02f179e3c8c690ac055ac9a7d31064a80`
- Base ref: `92206fb02f179e3c8c690ac055ac9a7d31064a80~1`
- Base commit: `d2c9bf70e5c481658a7d561b58ce94de8b76a212`
- Patch apply status: `applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 0
- Candidate hunks: 0
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2030 |
| `patch_lines` | 40 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 0 |
| `changed_files` | 0 |
| `churn` | 9 |
| `candidate_context_bytes` | 0 |
| `candidates_json_bytes` | 747 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show d2c9bf70e5c481658a7d561b58ce94de8b76a212:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/analysis.json`.

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/92206f/analysis.json`
