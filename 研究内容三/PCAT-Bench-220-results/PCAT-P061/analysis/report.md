# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/_worktrees/patched`
- Patch ID: `0748799ad18db4eeb72b33b30c5e0c420a8216ea`
- Base ref: `HEAD`
- Base commit: `0748799ad18db4eeb72b33b30c5e0c420a8216ea`
- Patch apply status: `already_applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/074879`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 10
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 8165 |
| `patch_lines` | 227 |
| `raw_hunks` | 12 |
| `candidate_hunks` | 10 |
| `changed_files` | 3 |
| `churn` | 70 |
| `candidate_context_bytes` | 18797 |
| `candidates_json_bytes` | 57826 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show 0748799ad18db4eeb72b33b30c5e0c420a8216ea:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/analysis.json`.

## Candidate Hunks

- `HUNK-0003` `include/haproxy/hlua-t.h` old `47-52` new `47-53` symbol `define, CLASS_HTTPCLIENT_REQ, HTTPClientRequest, Copyright` surface `public_headers, config, struct_layout, protocol_behavior`
- `HUNK-0004` `reg-tests/lua/lua_httpclient.lua` old `18-23` new `18-25` symbol `register_service, local, httpclient, core` surface `config, network_protocol, runtime_api`
- `HUNK-0005` `reg-tests/lua/lua_httpclient.lua` old `30-48` new `32-47` symbol `cron, local, response2, httpclient, post, url` surface `config, network_protocol, runtime_api`
- `HUNK-0006` `src/http_client.c` old `47-52` new `47-53` symbol `class_httpclient_request_ref, httpclient, request, LUA, class, Copyright` surface `config_keys, user_visible_output, config, protocol, network_protocol, protocol_behavior`
- `HUNK-0007` `src/http_client.c` old `1536-1542` new `1537-1543` symbol `hlua, MAY_LJMP, hlua_checkudata, L, ud, class_httpclient_request_ref, httpclient_stop_and_destroy` surface `protocol, network_protocol, protocol_behavior`
- `HUNK-0008` `src/http_client.c` old `1554-1564` new `1555-1574` symbol `hlua_httpclient_gc, __LJMP, hlua_httpclient_factory_new, lua_State, L, lua_newtable, httpclient_stop_and_destroy` surface `user_visible_output, protocol, network_protocol, persistence_state, protocol_behavior`
- `HUNK-0009` `src/http_client.c` old `1580-1593` new `1590-1600` symbol `hlua_httpclient_new, lua_rawgeti, L, LUA_REGISTRYINDEX, class_httpclient_request_ref, hlua_hc, hlua_pusherror` surface `callbacks, user_visible_output, plugin_api, protocol, network_protocol, persistence_state, protocol_behavior`
- `HUNK-0010` `src/http_client.c` old `1869-1881` new `1876-1890` symbol `http_meth_t, Create, the, internal, httpclient, request, hlua_httpclient_new, hlua_httpclient_send` surface `user_visible_output, protocol, network_protocol, protocol_behavior`
- `HUNK-0011` `src/http_client.c` old `2013-2019` new `2022-2037` symbol `hlua_httpclient_delete, Register, HTTPClientRequest, lua_newtable, L, the, lua_pushstring, hlua_httpclient_gc, hlua_init_state` surface `protocol, network_protocol, persistence_state, protocol_behavior`
- `HUNK-0012` `src/http_client.c` old `2023-2039` new `2041-2051` symbol `hlua_http_client_init_state, hlua_class_function, L, httpclient, hlua_httpclient_factory_new, Register, lua_pushstring` surface `protocol, network_protocol, persistence_state, protocol_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/074879/analysis.json`
