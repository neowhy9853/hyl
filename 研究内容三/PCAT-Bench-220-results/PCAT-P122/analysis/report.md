# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/grub2`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/_worktrees/patched`
- Patch ID: `56ccc5ed569869fd735074ccebeaa7aab058342d`
- Base ref: `01f064064c3146bd82e0c8db0da11d286bca31c6`
- Base commit: `01f064064c3146bd82e0c8db0da11d286bca31c6`
- Patch apply status: `applied`
- Profile: `grub2`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 4357 |
| `patch_lines` | 107 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 26 |
| `candidate_context_bytes` | 5736 |
| `candidates_json_bytes` | 14575 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/grub2 show 01f064064c3146bd82e0c8db0da11d286bca31c6:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `util/grub.d/30_os-prober.in` old `117-135` new `117-142` symbol `GRUB_OS_PROBER_SKIP_LIST, in, dD, eE, vV, grub_warn` surface `user_visible_output, config, boot_protocol`
- `HUNK-0003` `util/grub.d/30_os-prober.in` old `299-305` new `306-312` symbol `UUID, grub_probe, target, fs_uuid, device, DEVICE` surface `cli_options, user_visible_output, cli, config, boot_protocol`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P062/analysis.json`
