# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/lvm2`
- Patched analysis worktree: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/_worktrees/patched`
- Patch ID: `48291d27ac20`
- Base ref: `fe5081ca9588a9c7ecfe75cff8c2260f6eb04554`
- Base commit: `fe5081ca9588a9c7ecfe75cff8c2260f6eb04554`
- Patch apply status: `applied`
- Profile: `lvm2`
- Effective profile: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 549 |
| `patch_lines` | 13 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 2 |
| `candidate_context_bytes` | 2254 |
| `candidates_json_bytes` | 6964 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/lvm2 show fe5081ca9588a9c7ecfe75cff8c2260f6eb04554:<path>`.
- Rebuild worktree: `/usr/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/usr/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tools/vgchange.c` old `1114-1120` new `1114-1120` symbol `cmd_context, yes_no_prompt, Change, clustered, property, of, log_error` surface `cli_options, user_visible_output, cli, logging, cli_tools`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis.json`
