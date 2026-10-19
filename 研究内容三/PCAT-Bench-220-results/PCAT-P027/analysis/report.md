# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/_worktrees/patched`
- Patch ID: `e2164742`
- Base ref: `22b2f3d2a`
- Base commit: `22b2f3d2a319af32e9f3add0b3cc7732cbf4733b`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; candidates_json_bytes=215668 >= 180000
- Changed files: 7
- Candidate hunks: 32
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 20493 |
| `patch_lines` | 544 |
| `raw_hunks` | 33 |
| `candidate_hunks` | 32 |
| `changed_files` | 7 |
| `churn` | 251 |
| `candidate_context_bytes` | 96026 |
| `candidates_json_bytes` | 215668 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/shards`
- Shard count: 11

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 3 | 2 | 7387 | `shards/shard-0001.json` |
| `SHARD-0002` | `cli_options` | 5 | 1 | 14481 | `shards/shard-0002.json` |
| `SHARD-0003` | `cli_options` | 4 | 1 | 13359 | `shards/shard-0003.json` |
| `SHARD-0004` | `cli_options` | 4 | 1 | 15025 | `shards/shard-0004.json` |
| `SHARD-0005` | `config_keys` | 4 | 2 | 13865 | `shards/shard-0005.json` |
| `SHARD-0006` | `environment_variables` | 1 | 1 | 2393 | `shards/shard-0006.json` |
| `SHARD-0007` | `public_library_headers` | 1 | 1 | 1977 | `shards/shard-0007.json` |
| `SHARD-0008` | `tests` | 2 | 1 | 7790 | `shards/shard-0008.json` |
| `SHARD-0009` | `user_visible_output` | 4 | 1 | 11755 | `shards/shard-0009.json` |
| `SHARD-0010` | `user_visible_output` | 2 | 1 | 4414 | `shards/shard-0010.json` |
| `SHARD-0011` | `wire_protocol` | 2 | 2 | 3580 | `shards/shard-0011.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 22b2f3d2a319af32e9f3add0b3cc7732cbf4733b:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `builtin/fetch.c` old `99-104` new `99-105` symbol `transport, string_list, negotiation_include, STRING_LIST_INIT_NODUP` surface `cli_options, config_keys, config, commands`
- `HUNK-0003` `builtin/fetch.c` old `1534-1556` new `1535-1563` symbol `reference, add_negotiation_tips, string_list, input_list, oid_array, output_list, oid_array_append` surface `callbacks, cli_options, user_visible_output, config, commands`
- `HUNK-0004` `builtin/fetch.c` old `1559-1567` new `1566-1574` symbol `git_transport_options, argname, s, output_list, oids, negotiation, refs_for_each_ref_ext` surface `callbacks, cli_options, user_visible_output, config, commands`
- `HUNK-0005` `builtin/fetch.c` old `1597-1603` new `1604-1612` symbol `transport, add_negotiation_tips, negotiation_restrict, smart_options, negotiation_restrict_tips, negotiation, set_option` surface `cli_options, config_keys, user_visible_output, config, commands, wire_protocol`
- `HUNK-0006` `builtin/fetch.c` old `1606-1612` new `1615-1623` symbol `transport, add_negotiation_tips, negotiation_restrict, smart_options, negotiation_restrict_tips, negotiation, for_each_string_list_item` surface `cli_options, config_keys, user_visible_output, config, commands, wire_protocol`
- `HUNK-0007` `builtin/fetch.c` old `1615-1620` new `1626-1640` symbol `transport, negotiation_include, nr, smart_options, add_negotiation_tips, negotiation_include_tips, warning, _, strbuf_release` surface `cli_options, config_keys, user_visible_output, config, commands, wire_protocol`
- `HUNK-0008` `builtin/fetch.c` old `2582-2587` new `2602-2609` symbol `cmd_fetch, OPT_STRING_LIST, negotiation, include, negotiation_include, N_` surface `cli_options, config_keys, cli, config, commands, wire_protocol`
- `HUNK-0009` `builtin/pull.c` old `1000-1005` new `1000-1008` symbol `cmd_pull, OPT_PASSTHRU_ARGV, negotiation, include, opt_fetch, N_` surface `environment_variables, cli_options, config_keys, user_visible_output, cli, config, env_vars, logging, commands`
- `HUNK-0010` `fetch-pack.c` old `25-30` new `25-31` symbol `include, object, name, h` surface `cli_options, config_keys, cli, wire_protocol`
- `HUNK-0011` `fetch-pack.c` old `332-337` new `333-353` symbol `fetch_pack_args, add_oids_to_set, oid_array, array, oidset, set, trace2_data_string` surface `user_visible_output, wire_protocol`
- `HUNK-0012` `fetch-pack.c` old `347-352` new `363-369` symbol `fetch_negotiator, oidset, negotiation_include_oids, OIDSET_INIT, find_common` surface `user_visible_output, wire_protocol`
- `HUNK-0013` `fetch-pack.c` old `474-479` new `491-517` symbol `fetch_negotiator, Send, unconditional, haves, from, negotiation, add_oids_to_set, trace2_region_enter` surface `user_visible_output, wire_protocol`
- `HUNK-0014` `fetch-pack.c` old `584-589` new `622-628` symbol `fetch_negotiator, oidset_clear, negotiation_include_oids, send_request` surface `callbacks, user_visible_output, wire_protocol`
- `HUNK-0015` `fetch-pack.c` old `1305-1315` new `1344-1370` symbol `strbuf, haves_to_send, oidset, negotiation_include_oids, Send, unconditional, oidset_iter_init, add_haves` surface `cli_options, cli, wire_protocol`
- `HUNK-0016` `fetch-pack.c` old `1358-1364` new `1413-1420` symbol `fetch_negotiator, sideband_all, seen_ack, oidset, negotiation_include_oids, send_fetch_request` surface `cli_options, user_visible_output, cli, wire_protocol`
- `HUNK-0017` `fetch-pack.c` old `1413-1419` new `1469-1476` symbol `fetch_negotiator, haves_added, add_haves, negotiator, req_buf, haves_to_send, strbuf_release` surface `cli_options, user_visible_output, cli, wire_protocol`
- `HUNK-0018` `fetch-pack.c` old `1657-1662` new `1714-1720` symbol `ref, oidset, negotiation_include_oids, OIDSET_INIT, _` surface `config_keys, user_visible_output, wire_protocol`
- `HUNK-0019` `fetch-pack.c` old `1729-1734` new `1787-1794` symbol `ref, add_oids_to_set, args, negotiation_include_tips, negotiation_include_oids, filter_refs` surface `config_keys, user_visible_output, wire_protocol`
- `HUNK-0020` `fetch-pack.c` old `1747-1753` new `1807-1814` symbol `ref, seen_ack, negotiation_include_oids, trace2_region_enter_printf` surface `config_keys, user_visible_output, wire_protocol`
- `HUNK-0021` `fetch-pack.c` old `1883-1888` new `1944-1950` symbol `ref, oidset_clear, negotiation_include_oids, die` surface `cli_options, config_keys, user_visible_output, cli, config, wire_protocol`
- `HUNK-0022` `fetch-pack.c` old `2181-2192` new `2243-2256` symbol `oid_array, oidset, acked_commits, negotiation_include_tips, negotiation_include_oids, OIDSET_INIT, negotiate_using_fetch` surface `user_visible_output, wire_protocol`
- `HUNK-0023` `fetch-pack.c` old `2197-2202` new `2261-2269` symbol `oid_array, add_oids_to_set, negotiation_include_tips, negotiation_include_oids, fetch_negotiator_init` surface `cli_options, user_visible_output, cli, wire_protocol`
- `HUNK-0024` `fetch-pack.c` old `2221-2227` new `2288-2295` symbol `oid_array, haves_added, add_haves, negotiator, req_buf, haves_to_send, packet_buf_write` surface `cli_options, user_visible_output, cli, wire_protocol`
- `HUNK-0025` `fetch-pack.c` old `2273-2278` new `2341-2347` symbol `oid_array, oidset_clear, negotiation_include_oids, clear_common_flag` surface `cli_options, user_visible_output, cli, wire_protocol`
- `HUNK-0026` `fetch-pack.h` old `19-27` new `19-28` symbol `fetch_pack_args, lines, all, _include_, tips, and` surface `wire_protocol, public_library_headers`
- `HUNK-0027` `fetch-pack.h` old `93-99` new `94-101` symbol `oid_array, oidset, acked_commits, negotiation_include_tips, negotiate_using_fetch` surface `config_keys, user_visible_output, wire_protocol, public_library_headers`
- `HUNK-0028` `t/t5510-fetch.sh` old `1460-1465` new `1460-1475` symbol `test_expect_success, negotiation, tip, ignores, missing, refs` surface `tests, config_keys`
- `HUNK-0029` `t/t5510-fetch.sh` old `1511-1516` new `1521-1607` symbol `test_expect_success, negotiation, include, includes, configured, refs` surface `tests, config_keys, plugin_api, wire_protocol`
- `HUNK-0030` `transport.c` old `464-469` new `464-470` symbol `transport, args, negotiation_include_tips, data, options, memset` surface `user_visible_output, wire_protocol`
- `HUNK-0031` `transport.c` old `495-501` new `496-503` symbol `transport, data, options, acked_commits, negotiation_include_tips, negotiate_using_fetch` surface `user_visible_output, wire_protocol`
- `HUNK-0032` `transport.c` old `983-988` new `985-994` symbol `transport, data, options, negotiation_include_tips, oid_array_clear, free` surface `wire_protocol`
- `HUNK-0033` `transport.h` old `40-52` new `40-53` symbol `git_transport_options, these, member, names, in, fetch_pack_args` surface `public_library_headers`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis.json`
