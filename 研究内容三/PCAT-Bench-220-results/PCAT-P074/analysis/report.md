# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/lvm2`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/_worktrees/patched`
- Patch ID: `19b79b4d9625b379848559ece3507a189c0b89b8`
- Base ref: `19b79b4d9625b379848559ece3507a189c0b89b8^`
- Base commit: `a83165b7d71e40d9ef2238b6775169200766554f`
- Patch apply status: `applied`
- Profile: `lvm2`
- Effective profile: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 479 |
| `patch_lines` | 13 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 2 |
| `candidate_context_bytes` | 1876 |
| `candidates_json_bytes` | 7762 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/lvm2 show a83165b7d71e40d9ef2238b6775169200766554f:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tools/dumpconfig.c` old `331-337` new `331-337` symbol `cmd_context, log_error, valuesonly, has, no, effect` surface `public_headers, cli_options, config_keys, user_visible_output, cli, logging, cli_tools, config_metadata`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/lvm2/pca-results/19b79b/analysis.json`
