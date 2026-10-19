# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/_worktrees/patched`
- Patch ID: `0d71da4bdfff4c18abcea77ffa76227f70be0f73`
- Base ref: `0d71da4bdfff4c18abcea77ffa76227f70be0f73^`
- Base commit: `3934667f36d0775928ee1368b4784b3419cf45d8`
- Patch apply status: `applied`
- Profile: `httpd`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; candidates_json_bytes=204598 >= 180000
- Changed files: 7
- Candidate hunks: 25
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 25483 |
| `patch_lines` | 599 |
| `raw_hunks` | 25 |
| `candidate_hunks` | 25 |
| `changed_files` | 7 |
| `churn` | 283 |
| `candidate_context_bytes` | 76711 |
| `candidates_json_bytes` | 204598 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/shards`
- Shard count: 8

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 2 | 1 | 9866 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 4 | 1 | 11522 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 2 | 1 | 5461 | `shards/shard-0003.json` |
| `SHARD-0004` | `public_headers` | 4 | 3 | 11496 | `shards/shard-0004.json` |
| `SHARD-0005` | `public_headers` | 2 | 2 | 4694 | `shards/shard-0005.json` |
| `SHARD-0006` | `user_visible_output` | 4 | 2 | 11560 | `shards/shard-0006.json` |
| `SHARD-0007` | `user_visible_output` | 5 | 1 | 15215 | `shards/shard-0007.json` |
| `SHARD-0008` | `user_visible_output` | 2 | 1 | 6897 | `shards/shard-0008.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd show 3934667f36d0775928ee1368b4784b3419cf45d8:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `include/ap_mmn.h` old `725-730` new `725-731` symbol `dev, Add, AGAIN, AP_MPMQ_CAN_AGAIN, ap_assign_request_line` surface `public_headers, plugin_api, struct_layout, network_protocol, module_api, config_directives, request_handling`
- `HUNK-0002` `include/ap_mmn.h` old `732-738` new `733-739` symbol `define, MODULE_MAGIC_NUMBER_MINOR, n, ap_assign_request_line` surface `public_headers, plugin_api, struct_layout, network_protocol, module_api, config_directives, request_handling`
- `HUNK-0003` `include/ap_mpm.h` old `182-187` new `182-189` symbol `AP_DECLARE, MPM, reacts, to, AGAIN, response, use` surface `public_headers, callbacks, config_keys, plugin_api, struct_layout, network_protocol, daemon_control, module_api`
- `HUNK-0004` `include/httpd.h` old `458-470` new `458-473` symbol `AP_DECLARE, define, OK, Module, has, handled, request` surface `public_headers, user_visible_output, plugin_api, struct_layout, network_protocol, module_api`
- `HUNK-0005` `include/httpd.h` old `1319-1326` new `1322-1332` symbol `conn_slave_rec, CONN_STATE_PROCESSING, Processed, by, process_connection, hooks, the, get_remote_logname` surface `public_headers, config_keys, plugin_api, struct_layout, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0006` `modules/http2/h2.h` old `49-60` new `49-54` symbol `h2_stream, AP_MODULE_MAGIC_AT_LEAST, define, H2_USE_STATE_PROCESSING, endif, descriptors` surface `public_headers, plugin_api, network_protocol, module_api`
- `HUNK-0007` `modules/http2/h2_c1.c` old `47-69` new `47-71` symbol `async_mpm, mpm_can_again, ap_mpm_query, AP_MPMQ_IS_ASYNC, ifdef, AP_MPMQ_CAN_AGAIN` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, module_api, request_handling`
- `HUNK-0008` `modules/http2/h2_c1.c` old `113-135` new `115-137` symbol `h2_c1_setup, h2_c1_run, conn_rec, c, rc, OK, ap_remove_input_filter_byhandle` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0009` `modules/http2/h2_c1.c` old `153-172` new `155-193` symbol `h2_c1_run, Flush, then, keep, alive, c, ap_log_cerror` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`
- `HUNK-0010` `modules/http2/h2_c1.c` old `178-184` new `199-205` symbol `h2_c1_run, rc, APR_SUCCESS, process_connection` surface `config_keys, plugin_api, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0011` `modules/http2/h2_c1.c` old `284-291` new `305-311` symbol `h2_c1_hook_process_connection, h2_c1_run, c, OK, h2_conn_ctx_detach` surface `user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`
- `HUNK-0012` `modules/http2/h2_session.c` old `1762-1768` new `1762-1767` symbol `unblock_c1_out, H2_USE_STATE_PROCESSING, nghttp2_session_resume_data` surface `user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`
- `HUNK-0013` `modules/http2/h2_session.c` old `1770-1776` new `1769-1774` symbol `h2_send_flow_blocked, endif` surface `user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`
- `HUNK-0014` `modules/http2/h2_session.c` old `1954-1972` new `1952-1966` symbol `h2_session_process, By, returning, to, the, MPM, h2_session_dispatch_event` surface `user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api`
- `HUNK-0015` `server/mpm/event/event.c` old `734-739` new `734-742` symbol `event_query, AP_MPMQ_CAN_AGAIN, result, break` surface `user_visible_output, logging, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0016` `server/mpm/event/event.c` old `1082-1087` new `1085-1092` symbol `process_socket, close_connection, cs, ap_update_vhost_given_ip` surface `config_keys, user_visible_output, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0017` `server/mpm/event/event.c` old `1099-1105` new `1104-1109` symbol `process_socket, rc, OK, accept` surface `config_keys, user_visible_output, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0018` `server/mpm/event/event.c` old `1110-1185` new `1114-1201` symbol `process_socket, cs, pub, state, CONN_STATE_LINGER, goto, have, notify_resume` surface `callbacks, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0019` `server/mpm/event/event.c` old `1236-1241` new `1252-1258` symbol `process_socket, cs, pub, sense, CONN_SENSE_DEFAULT, notify_suspend` surface `user_visible_output, logging, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0020` `server/mpm/event/event.c` old `1257-1273` new `1274-1291` symbol `process_socket, goto, lingering_close, ap_run_input_pending, c, OK, apr_thread_mutex_unlock` surface `user_visible_output, logging, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0021` `server/mpm/event/event.c` old `1285-1290` new `1303-1309` symbol `process_socket, cs, pub, sense, CONN_SENSE_DEFAULT, notify_suspend` surface `user_visible_output, logging, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0022` `server/mpm/event/event.c` old `1312-1317` new `1331-1337` symbol `process_socket, lingering_close, notify_suspend` surface `user_visible_output, logging, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0023` `server/mpm/event/event.c` old `1336-1341` new `1356-1362` symbol `event_resume_suspended, cs, pub, sense, CONN_SENSE_DEFAULT, apr_atomic_dec32` surface `user_visible_output, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0024` `server/mpm/event/event.c` old `1765-1776` new `1786-1796` symbol `process_lingering_close, All, nonblocking, from, now, no, either, apr_socket_timeout_set, close_connection` surface `callbacks, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`
- `HUNK-0025` `server/mpm/event/event.c` old `1784-1792` new `1804-1820` symbol `process_lingering_close, One, timestamp, duration, the, whole, 2s` surface `user_visible_output, logging, network_protocol, daemon_control, persistence_state, module_api, request_handling`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis.json`
