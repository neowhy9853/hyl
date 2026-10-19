# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/_worktrees/patched`
- Patch ID: `8b68438b2e0b38909b5b2f76e22ceccd2fa48278`
- Base ref: `8b68438b2e0b38909b5b2f76e22ceccd2fa48278^`
- Base commit: `d7ec293abc89a0dde9cc730acfa7ba838601a197`
- Patch apply status: `applied`
- Profile: `httpd`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=275 >= 250; candidates_json_bytes=148993 >= 100000
- Changed files: 10
- Candidate hunks: 24
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 23612 |
| `patch_lines` | 578 |
| `raw_hunks` | 25 |
| `candidate_hunks` | 24 |
| `changed_files` | 10 |
| `churn` | 275 |
| `candidate_context_bytes` | 53874 |
| `candidates_json_bytes` | 148993 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/shards`
- Shard count: 10

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 1 | 1 | 3025 | `shards/shard-0001.json` |
| `SHARD-0002` | `cli_options` | 1 | 1 | 333 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 3 | 1 | 7966 | `shards/shard-0003.json` |
| `SHARD-0004` | `config_keys` | 4 | 1 | 9741 | `shards/shard-0004.json` |
| `SHARD-0005` | `network_protocol` | 1 | 1 | 290 | `shards/shard-0005.json` |
| `SHARD-0006` | `plugin_api` | 1 | 1 | 1642 | `shards/shard-0006.json` |
| `SHARD-0007` | `public_headers` | 5 | 3 | 9794 | `shards/shard-0007.json` |
| `SHARD-0008` | `tests` | 2 | 1 | 4069 | `shards/shard-0008.json` |
| `SHARD-0009` | `user_visible_output` | 3 | 3 | 6511 | `shards/shard-0009.json` |
| `SHARD-0010` | `user_visible_output` | 3 | 1 | 10503 | `shards/shard-0010.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd show d7ec293abc89a0dde9cc730acfa7ba838601a197:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `changes-entries/h2_header_strictness.txt` old `1-4` new `1-5` symbol `mod_http2, field, values, headers, and, trailers` surface `network_protocol`
- `HUNK-0003` `modules/http2/h2_c2_filter.c` old `495-501` new `495-501` symbol `make_table, h2_util_ignore_resp_header, hline, h2_util_ignore_header, ap_log_cerror` surface `user_visible_output, plugin_api, logging, network_protocol, persistence_state, module_api`
- `HUNK-0004` `modules/http2/h2_config.c` old `75-81` new `75-80` symbol `h2_config, header_strictness, which, rfc, to, follow, h2_config_seti64` surface `config_keys, plugin_api, module_api`
- `HUNK-0005` `modules/http2/h2_config.c` old `111-117` new `110-115` symbol `header, strictness, apr_time_from_sec` surface `config_keys, plugin_api, module_api`
- `HUNK-0006` `modules/http2/h2_config.c` old `155-161` new `153-158` symbol `h2_config_create_svr, conf, header_strictness, DEF_VAL, h2_config_init` surface `config_keys, plugin_api, module_api`
- `HUNK-0007` `modules/http2/h2_config.c` old `198-204` new `195-200` symbol `h2_config_merge, n, header_strictness, H2_CONFIG_GET, add, base, h2_config_init` surface `config_keys, plugin_api, module_api`
- `HUNK-0008` `modules/http2/h2_config.c` old `282-289` new `278-283` symbol `h2_srv_config_geti64, H2_CONF_HEADER_STRICTNESS, H2_CONFIG_GET, conf, defconf, header_strictness` surface `config_keys, plugin_api, module_api`
- `HUNK-0009` `modules/http2/h2_config.c` old `343-351` new `337-342` symbol `h2_srv_config_seti, H2_CONF_HEADER_STRICTNESS, H2_CONFIG_SET, conf, header_strictness, val` surface `config_keys, plugin_api, network_protocol, module_api, request_handling`
- `HUNK-0010` `modules/http2/h2_config.c` old `712-735` new `703-708` symbol `h2_conf_set_modern_tls_only, h2_conf_set_header_strictness, cmd_parms, cmd, dirconf, value, CONFIG_CMD_SET` surface `config_keys, plugin_api, module_api, config_directives`
- `HUNK-0011` `modules/http2/h2_config.c` old `964-971` new `937-942` symbol `AP_INIT_TAKE1, H2HeaderStrictness, h2_conf_set_header_strictness, NULL, RSRC_CONF, set` surface `cli_options, config_keys, cli, plugin_api, module_api, config_directives`
- `HUNK-0012` `modules/http2/h2_config.h` old `43-49` new `43-48` symbol `H2_CONF_HEADER_STRICTNESS` surface `public_headers, cli_options, config_keys, cli, plugin_api, network_protocol, module_api, config_directives, request_handling`
- `HUNK-0013` `modules/http2/h2_session.c` old `957-968` new `957-966` symbol `h2_session_create, whitespace, of, RFC, fields, But, nghttp2_option_set_no_closed_streams` surface `callbacks, config_keys, user_visible_output, plugin_api, logging, network_protocol, module_api, request_handling`
- `HUNK-0014` `modules/http2/h2_stream.c` old `654-660` new `654-660` symbol `add_trailer, h2_ignore_req_trailer, name, nlen, h2_req_ignore_trailer, ap_log_cerror` surface `user_visible_output, plugin_api, logging, network_protocol, module_api`
- `HUNK-0015` `modules/http2/h2_util.c` old `1390-1408` new `1390-1398` symbol `h2_brigade_mem_size, h2_util_ignore_resp_header, key, h2_util_ignore_header, name, never` surface `plugin_api, module_api`
- `HUNK-0016` `modules/http2/h2_util.c` old `1423-1428` new `1413-1429` symbol `inv_field_value_chr, strip_field_value_ws, nghttp2_nv, nv, valuelen, value, count_header` surface `user_visible_output, plugin_api, logging, network_protocol, module_api`
- `HUNK-0017` `modules/http2/h2_util.c` old `1455-1467` new `1456-1469` symbol `add_header, strip_field_value_ws, nv, h2_util_ignore_resp_header, key, h2_util_ignore_header, ap_log_perror` surface `user_visible_output, plugin_api, logging, network_protocol, module_api`
- `HUNK-0018` `modules/http2/h2_util.c` old `1620-1625` new `1622-1633` symbol `literal, IgnoredResponseHeaders, H2_DEF_LITERAL, upgrade, connection, keep` surface `user_visible_output, plugin_api, persistence_state, module_api`
- `HUNK-0019` `modules/http2/h2_util.c` old `1634-1722` new `1642-1767` symbol `contains_name, literal, lits, size_t, llen, nghttp2_nv, H2_DEF_LITERAL` surface `user_visible_output, plugin_api, persistence_state, module_api`
- `HUNK-0020` `modules/http2/h2_util.h` old `342-350` new `342-349` symbol `h2_util_table_bytes, h2_ignore_req_trailer, name, size_t, len, h2_ignore_resp_trailer` surface `public_headers, plugin_api, network_protocol, module_api`
- `HUNK-0021` `modules/http2/h2_util.h` old `375-399` new `374-380` symbol `h2_util_base64url_encode, h2_util_ignore_resp_header, name, define, H2_HD_MATCH_LIT_CS, l, h2_util_base64url_decode` surface `public_headers, plugin_api, network_protocol, module_api`
- `HUNK-0022` `modules/http2/h2_version.h` old `27-33` new `27-33` symbol `define, MOD_HTTP2_VERSION` surface `public_headers, plugin_api, persistence_state, module_api`
- `HUNK-0023` `modules/http2/h2_version.h` old `35-41` new `35-41` symbol `define, MOD_HTTP2_VERSION_NUM` surface `public_headers, plugin_api, persistence_state, module_api`
- `HUNK-0024` `test/modules/http2/test_203_rfc9113.py` old `11-18` new `11-17` symbol `_class_scope, by, default, we, accept, leading` surface `tests, network_protocol`
- `HUNK-0025` `test/modules/http2/test_203_rfc9113.py` old `22-42` new `21-52` symbol `test_h2_203_01_ws_ignore, response, header, are, also, handled` surface `tests, network_protocol`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P067/analysis.json`
