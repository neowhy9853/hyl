# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/_worktrees/patched`
- Patch ID: `6cd9ea8dcb5bf68a195e90578c7f05e12eba5468`
- Base ref: `6cd9ea8dcb5bf68a195e90578c7f05e12eba5468^`
- Base commit: `ad449e35a46f2d9f08dd4b5ca3ec0e6ad18192a5`
- Patch apply status: `applied`
- Profile: `httpd`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2360 |
| `patch_lines` | 67 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 2 |
| `churn` | 12 |
| `candidate_context_bytes` | 4019 |
| `candidates_json_bytes` | 11341 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd show ad449e35a46f2d9f08dd4b5ca3ec0e6ad18192a5:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `CHANGES` old `1-6` new `1-8` symbol `mod_md, OpenSSL, compatibility` surface `config_keys, network_protocol`
- `HUNK-0002` `modules/md/md_ocsp.c` old `533-545` new `533-555` symbol `certid_summary, OPENSSL_VERSION_NUMBER, data, len, apr_size_t, ASN1_STRING_length, md_data_clear` surface `user_visible_output, plugin_api, module_api`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P065/analysis.json`
