# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/_worktrees/patched`
- Patch ID: `66d9658f5f557e0e525e5db5449ef94686df50d3`
- Base ref: `ca30c826476ba01ad1383f0fbb4e3d51fd998ea3`
- Base commit: `ca30c826476ba01ad1383f0fbb4e3d51fd998ea3`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1172 |
| `patch_lines` | 39 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 8 |
| `candidate_context_bytes` | 1656 |
| `candidates_json_bytes` | 5053 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show ca30c826476ba01ad1383f0fbb4e3d51fd998ea3:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/util.c` old `327-339` new `327-341` symbol `safe_malloc, Can, be, replaced, by, strlcpy, strcpy` surface `user_visible_output`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/66d965/analysis.json`
