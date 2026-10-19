# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/linux`
- Patched analysis worktree: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/_worktrees/patched`
- Patch ID: `cc8d0b2cf297563c219fe1b55a8307dd8a3408b8`
- Base ref: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`
- Base commit: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`
- Patch apply status: `applied`
- Profile: `kernel_6_6`
- Effective profile: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-N002`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 486 |
| `patch_lines` | 17 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 1 |
| `candidate_context_bytes` | 1136 |
| `candidates_json_bytes` | 4749 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/linux show ffc253263a1375a65fa6c9f62a893e9767fbebfa:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `kernel/sched/core.c` old `3-8` new `3-9` symbol `PCIA, seeded, internal, comment, only, note` surface `syscall_wrappers, syscall`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/output_dir_rerun/PCAT-N002/analysis.json`
