# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/_worktrees/patched`
- Patch ID: `7ae248cc9872d9cb25d4b682fbd6c00efa54de5f`
- Base ref: `7ae248cc9872d9cb25d4b682fbd6c00efa54de5f^`
- Base commit: `b488c0f3d84eba2787635d6e00e5ac581677341e`
- Patch apply status: `applied`
- Profile: `httpd`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2750 |
| `patch_lines` | 66 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 17 |
| `candidate_context_bytes` | 8409 |
| `candidates_json_bytes` | 23816 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd show b488c0f3d84eba2787635d6e00e5ac581677341e:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `modules/http2/h2_c2.c` old `461-468` new `461-473` symbol `check_early_hints, ifdef, HTTP_EARLY_HINTS, r, status, status_line, apr_table_setn` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, module_api, request_handling`
- `HUNK-0002` `modules/http2/h2_proxy_session.c` old `293-298` new `293-306` symbol `on_frame_recv, ifndef, HTTP_EARLY_HINTS, workaround, until, we, ping_ev_frame_received` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, module_api`
- `HUNK-0003` `modules/http2/h2_stream.c` old `1709-1715` new `1709-1719` symbol `stream_do_response, ifdef, HTTP_EARLY_HINTS, resp, status, endif, h2_stream_submit_pushes` surface `callbacks, config_keys, user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P066/analysis.json`
