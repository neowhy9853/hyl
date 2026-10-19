# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/grub2`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/_worktrees/patched`
- Patch ID: `5f8e091b6a668f89de4f40b15b0712bafa053cbe`
- Base ref: `HEAD`
- Base commit: `fe274638bb01104f56fce0caebe0a238ac5fc6a4`
- Patch apply status: `already_applied`
- Profile: `grub2`
- Effective profile: `/home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1210 |
| `patch_lines` | 27 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 3 |
| `candidate_context_bytes` | 2796 |
| `candidates_json_bytes` | 6842 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/grub2 show fe274638bb01104f56fce0caebe0a238ac5fc6a4:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `grub-core/kern/ieee1275/init.c` old `472-478` new `472-478` symbol `grub_regions_claim, Take, the, bigger, chunk, from, grub_dprintf` surface `user_visible_output, module_api, boot_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/grub2/pca-results/5f8e09/analysis.json`
