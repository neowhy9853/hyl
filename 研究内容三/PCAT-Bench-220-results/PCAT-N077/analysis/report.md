# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/_worktrees/patched`
- Patch ID: `f155b8f1c95762e6855557207e498238fc1a73e5`
- Base ref: `f155b8f1c95762e6855557207e498238fc1a73e5^`
- Base commit: `8e655dbef4c9e56f125dc3545e52d5cf703751ca`
- Patch apply status: `applied`
- Profile: `kernel_6_6`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2240 |
| `patch_lines` | 43 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 4 |
| `candidate_context_bytes` | 4045 |
| `candidates_json_bytes` | 9619 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux show 8e655dbef4c9e56f125dc3545e52d5cf703751ca:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tools/testing/selftests/bpf/progs/verifier_spill_fill.c` old `392-398` new `392-398` symbol `spill_32bit_of_64bit_fail, Compare, r2, with, another, to, volatile` surface `unknown`
- `HUNK-0002` `tools/testing/selftests/bpf/progs/verifier_spill_fill.c` old `431-437` new `431-437` symbol `spill_16bit_of_32bit_fail, Compare, r2, with, another, to, volatile` surface `unknown`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N037/analysis.json`
