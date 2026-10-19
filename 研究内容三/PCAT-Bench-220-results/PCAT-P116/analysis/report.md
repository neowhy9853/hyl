# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/_worktrees/patched`
- Patch ID: `8e14f88e25192080ac237cb64be452c592c1e4fe`
- Base ref: `8e14f88e25192080ac237cb64be452c592c1e4fe^`
- Base commit: `902b38d33a9761eba12c6a53e13c6fb89a167b39`
- Patch apply status: `applied`
- Profile: `c_project`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=301 >= 250; candidate_hunks=28 >= 25; candidates_json_bytes=151976 >= 100000
- Changed files: 6
- Candidate hunks: 28
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 20227 |
| `patch_lines` | 576 |
| `raw_hunks` | 28 |
| `candidate_hunks` | 28 |
| `changed_files` | 6 |
| `churn` | 301 |
| `candidate_context_bytes` | 71107 |
| `candidates_json_bytes` | 151976 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/shards`
- Shard count: 11

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 3 | 2 | 11045 | `shards/shard-0001.json` |
| `SHARD-0002` | `callbacks` | 3 | 1 | 11011 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 1 | 1 | 1691 | `shards/shard-0003.json` |
| `SHARD-0004` | `internal_or_unknown` | 5 | 1 | 11169 | `shards/shard-0004.json` |
| `SHARD-0005` | `internal_or_unknown` | 4 | 1 | 8552 | `shards/shard-0005.json` |
| `SHARD-0006` | `internal_or_unknown` | 3 | 2 | 6264 | `shards/shard-0006.json` |
| `SHARD-0007` | `internal_or_unknown` | 1 | 1 | 4164 | `shards/shard-0007.json` |
| `SHARD-0008` | `logging` | 2 | 1 | 2538 | `shards/shard-0008.json` |
| `SHARD-0009` | `tests` | 3 | 1 | 8202 | `shards/shard-0009.json` |
| `SHARD-0010` | `tests` | 1 | 1 | 2280 | `shards/shard-0010.json` |
| `SHARD-0011` | `user_visible_output` | 2 | 1 | 4191 | `shards/shard-0011.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup show 902b38d33a9761eba12c6a53e13c6fb89a167b39:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `ChangeLog` old `1-3` new `1-18` symbol `Dan, Winship, danw, gnome, org, libsoup` surface `callbacks, plugin_api`
- `HUNK-0002` `libsoup/soup-auth-manager-ntlm.c` old `45-52` new `45-56` symbol `SoupAuthManagerNTLM, ntlm_request_queued, SoupSession, session, SoupMessage, msg, ntlm_request_unqueued, Copyright` surface `unknown`
- `HUNK-0003` `libsoup/soup-auth-manager-ntlm.c` old `67-74` new `71-82` symbol `soup_auth_manager_ntlm_new, g_signal_connect, session, request_queued, G_CALLBACK, ntlm_request_queued, ntlm_request_unqueued` surface `unknown`
- `HUNK-0004` `libsoup/soup-auth-manager-ntlm.c` old `96-103` new `104-115` symbol `soup_auth_manager_ntlm_free, g_signal_handlers_disconnect_by_func, ntlm, session, ntlm_request_queued, ntlm_request_unqueued` surface `unknown`
- `HUNK-0005` `libsoup/soup-auth-manager-ntlm.c` old `253-265` new `265-280` symbol `ntlm_authorize_post, ntlm_request_queued, SoupSession, session, SoupMessage, msg, G_CALLBACK, ntlm_authorize_pre, g_free` surface `unknown`
- `HUNK-0006` `libsoup/soup-auth-manager-ntlm.c` old `292-311` new `307-320` symbol `ntlm_request_started, ntlm_request_unqueued, SoupSession, session, SoupMessage, msg, ntlm_authorize_pre, ntlm_authorize_post, soup_message_headers_replace` surface `unknown`
- `HUNK-0007` `libsoup/soup-auth-manager.c` old `19-26` new `19-30` symbol `session_request_queued, SoupSession, session, SoupMessage, msg, gpointer, session_request_unqueued, Copyright` surface `config_keys`
- `HUNK-0008` `libsoup/soup-auth-manager.c` old `53-60` new `57-68` symbol `soup_auth_manager_new, g_signal_connect, session, request_queued, G_CALLBACK, session_request_queued, session_request_unqueued` surface `unknown`
- `HUNK-0009` `libsoup/soup-auth-manager.c` old `79-87` new `87-101` symbol `soup_auth_manager_free, g_signal_handlers_disconnect_by_func, manager, session, G_CALLBACK, session_request_queued, session_request_unqueued` surface `unknown`
- `HUNK-0010` `libsoup/soup-auth-manager.c` old `431-446` new `445-455` symbol `requeue_if_proxy_authenticated, session_request_queued, SoupSession, session, SoupMessage, msg, session_request_started, soup_session_requeue_message` surface `unknown`
- `HUNK-0011` `libsoup/soup-auth-manager.c` old `448-457` new `457-462` symbol `session_request_started, auth, manager, proxy_auth, authenticate_auth, msg, soup_message_add_status_code_handler` surface `unknown`
- `HUNK-0012` `libsoup/soup-auth-manager.c` old `459-461` new `464-494` symbol `session_request_started, SoupSession, session, SoupMessage, msg, SoupSocket, soup_message_add_status_code_handler` surface `unknown`
- `HUNK-0013` `libsoup/soup-logger.c` old `321-328` new `321-332` symbol `soup_logger_clear_id, request_queued, SoupSession, session, SoupMessage, msg, request_unqueued, g_object_set_qdata` surface `unknown`
- `HUNK-0014` `libsoup/soup-logger.c` old `348-355` new `352-363` symbol `soup_logger_attach, g_signal_connect, session, request_queued, G_CALLBACK, logger, request_unqueued` surface `unknown`
- `HUNK-0015` `libsoup/soup-logger.c` old `366-372` new `374-382` symbol `g_signal_handlers_disconnect_by_func, session, request_queued, logger, request_unqueued, soup_logger_detach` surface `user_visible_output, logging`
- `HUNK-0016` `libsoup/soup-logger.c` old `600-614` new `610-625` symbol `got_body, request_queued, SoupSession, session, SoupMessage, msg, g_signal_connect, G_CALLBACK, got_informational, g_mutex_unlock` surface `user_visible_output, logging`
- `HUNK-0017` `libsoup/soup-logger.c` old `623-640` new `634-641` symbol `request_started, soup_logger_set_id, logger, msg, msg_id, g_signal_connect, G_CALLBACK, got_informational, got_body` surface `logging`
- `HUNK-0018` `libsoup/soup-logger.c` old `643-645` new `644-657` symbol `request_started, request_unqueued, SoupSession, session, SoupMessage, msg, g_signal_handlers_disconnect_by_func, got_informational, got_body, print_request` surface `logging`
- `HUNK-0019` `libsoup/soup-session.c` old `121-127` new `121-129` symbol `soup_uri_copy_root, REQUEST_QUEUED, REQUEST_UNQUEUED, soup_uri_host_equal` surface `callbacks, plugin_api`
- `HUNK-0020` `libsoup/soup-session.c` old `254-266` new `256-321` symbol `soup_session_class_init, SoupSession, request, queued, session, the, g_type_class_add_private` surface `callbacks, plugin_api`
- `HUNK-0021` `libsoup/soup-session.c` old `273-278` new `328-353` symbol `soup_session_class_init, SoupSession, request, unqueued, session, the, G_STRUCT_OFFSET` surface `callbacks, plugin_api`
- `HUNK-0022` `libsoup/soup-session.c` old `716-721` new `791-802` symbol `connection_started_request, Kludge, to, deal, with, the, soup_message_headers_replace` surface `unknown`
- `HUNK-0023` `libsoup/soup-session.c` old `984-989` new `1065-1072` symbol `message_finished, g_signal_handlers_disconnect_by_func, msg, redirect_handler, session, g_signal_emit` surface `callbacks, ioctl_netlink_consumers, ioctl_netlink, plugin_api`
- `HUNK-0024` `libsoup/soup-session.c` old `1004-1009` new `1087-1094` symbol `queue_message, g_signal_emit, session, signals, REQUEST_QUEUED, msg, soup_message_set_io_status` surface `callbacks, ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api`
- `HUNK-0025` `tests/auth-test.c` old `397-402` new `397-420` symbol `async_finished, async_authenticate_522601, SoupSession, session, SoupMessage, msg, g_main_loop_quit` surface `tests, user_visible_output`
- `HUNK-0026` `tests/auth-test.c` old `406-411` new `424-430` symbol `do_async_auth_test, gboolean, been_there, FALSE` surface `tests, user_visible_output`
- `HUNK-0027` `tests/auth-test.c` old `457-462` new `476-482` symbol `do_async_auth_test, g_object_unref, auth, G_CALLBACK` surface `tests, user_visible_output`
- `HUNK-0028` `tests/auth-test.c` old `490-496` new `510-547` symbol `do_async_auth_test, Test, that, giving, the, wrong, password, authenticate, g_object_unref` surface `tests, user_visible_output`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis.json`
