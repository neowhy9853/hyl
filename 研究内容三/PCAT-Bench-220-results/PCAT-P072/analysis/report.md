# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/lvm2`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/_worktrees/patched`
- Patch ID: `591a1c9310506124685cacc75aa338e31a148a06`
- Base ref: `HEAD`
- Base commit: `d804677c7565bff40c87ed830473674119f23f6a`
- Patch apply status: `already_applied`
- Profile: `lvm2`
- Effective profile: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1245 |
| `patch_lines` | 35 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 5 |
| `candidate_context_bytes` | 3069 |
| `candidates_json_bytes` | 11784 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/lvm2 show d804677c7565bff40c87ed830473674119f23f6a:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `libdm/libdm-config.c` old `725-730` new `725-731` symbol `dm_config_value, endptr, log_error` surface `public_headers, config_keys, user_visible_output, logging, config_metadata`
- `HUNK-0002` `libdm/libdm-config.c` old `733-740` new `734-741` symbol `dm_config_value, v, i, strtoll, p, tb, log_error` surface `public_headers, config_keys, user_visible_output, logging, config_metadata`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis.json`
