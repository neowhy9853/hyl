# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/libsoup`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/_worktrees/patched`
- Patch ID: `39b6be1fb28fdbf0dfa80996b0a737827b080cb7`
- Base ref: `39b6be1fb28fdbf0dfa80996b0a737827b080cb7^`
- Base commit: `0cc386355df45ffd22cc89319a1fc7de1817f0fa`
- Patch apply status: `applied`
- Profile: `libsoup`
- Effective profile: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 7
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 4720 |
| `patch_lines` | 117 |
| `raw_hunks` | 7 |
| `candidate_hunks` | 7 |
| `changed_files` | 7 |
| `churn` | 17 |
| `candidate_context_bytes` | 14196 |
| `candidates_json_bytes` | 42370 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/libsoup show 0cc386355df45ffd22cc89319a1fc7de1817f0fa:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `examples/simple-proxy.c` old `352-358` new `352-358` symbol `server_callback, g_signal_connect, client_msg, got, headers, G_CALLBACK, send_headers, g_bytes_unref` surface `callbacks, plugin_api, network_protocol, http_semantics`
- `HUNK-0002` `libsoup/auth/soup-auth-negotiate.c` old `267-273` new `267-273` symbol `soup_auth_negotiate_update_connection, got, headers, got_headers, free_connection_state_data` surface `user_visible_output, network_protocol, persistence_state, http_semantics`
- `HUNK-0003` `tests/auth-test.c` old `313-319` new `313-319` symbol `do_pipelined_auth_test, g_signal_connect, msg, wrote, headers, wrote_headers, g_object_set_data` surface `tests, config_keys, user_visible_output, network_protocol, http_semantics`
- `HUNK-0004` `tests/multipart-test.c` old `433-439` new `433-439` symbol `test_multipart, g_signal_connect, msg, got, headers, got_headers` surface `tests, callbacks, network_protocol, http_semantics`
- `HUNK-0005` `tests/ntlm-test.c` old `341-349` new `341-349` symbol `do_message, g_signal_connect, msg, got, headers, got_headers` surface `tests, user_visible_output, network_protocol, persistence_state, http_semantics`
- `HUNK-0006` `tests/redirect-test.c` old `186-192` new `186-192` symbol `do_message_api_test, g_signal_connect, msg, got, headers, got_headers, g_bytes_unref` surface `tests, callbacks, user_visible_output, plugin_api, network_protocol, http_semantics`
- `HUNK-0007` `tests/server-auth-test.c` old `337-343` new `337-343` symbol `main, g_signal_connect, server, request, started, request_started, test_init` surface `tests, callbacks, plugin_api, network_protocol, http_semantics`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/libsoup/pca-results/39b6be/analysis.json`
