# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/libxml2`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/_worktrees/patched`
- Patch ID: `65b12d44a593075139849806fc2f18d98f482d47`
- Base ref: `13a3df99ffe2521a903f270abb33aa7092b34147`
- Base commit: `13a3df99ffe2521a903f270abb33aa7092b34147`
- Patch apply status: `applied`
- Profile: `libxml2`
- Effective profile: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 528 |
| `patch_lines` | 17 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 1 |
| `candidate_context_bytes` | 1586 |
| `candidates_json_bytes` | 4505 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/libxml2 show 13a3df99ffe2521a903f270abb33aa7092b34147:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `.gitlab-ci/Dockerfile` old `9-14` new `9-15` symbol `PCIA, seeded, CI, only, note, no` surface `config_keys`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/libxml2/pca-results/65b12d/analysis.json`
