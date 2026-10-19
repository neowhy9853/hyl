# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/_worktrees/patched`
- Patch ID: `21491b21577c68858b3cc02c21e3db88f0a30bb1`
- Base ref: `21491b21577c68858b3cc02c21e3db88f0a30bb1^`
- Base commit: `e54735bf82e02278dc70eb80d931a748a81e8ce8`
- Patch apply status: `applied`
- Profile: `httpd`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; churn=382 >= 250
- Changed files: 5
- Candidate hunks: 12
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 20624 |
| `patch_lines` | 546 |
| `raw_hunks` | 13 |
| `candidate_hunks` | 12 |
| `changed_files` | 5 |
| `churn` | 382 |
| `candidate_context_bytes` | 34167 |
| `candidates_json_bytes` | 99576 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/shards`
- Shard count: 6

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `cli_options` | 1 | 1 | 2760 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 3 | 2 | 10596 | `shards/shard-0002.json` |
| `SHARD-0003` | `environment_variables` | 1 | 1 | 5495 | `shards/shard-0003.json` |
| `SHARD-0004` | `plugin_api` | 1 | 1 | 0 | `shards/shard-0004.json` |
| `SHARD-0005` | `public_headers` | 4 | 1 | 12503 | `shards/shard-0005.json` |
| `SHARD-0006` | `user_visible_output` | 2 | 1 | 2813 | `shards/shard-0006.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd show e54735bf82e02278dc70eb80d931a748a81e8ce8:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `modules/ssl/mod_ssl.c` old `95-100` new `95-102` symbol `SSL_CMD_SRV, VHostSNIPolicy, TAKE1, SSL, VirtualHost, SNI` surface `cli_options, config_keys, cli, plugin_api, network_protocol, module_api, config_directives, request_handling`
- `HUNK-0003` `modules/ssl/ssl_engine_config.c` old `60-65` new `60-68` symbol `ssl_config_global_create, ifdef, HAVE_TLSEXT, mc, snivh_policy, MODSSL_SNIVH_SECURE, AP_DEBUG_ASSERT` surface `config_keys, plugin_api, persistence_state, module_api, request_handling`
- `HUNK-0004` `modules/ssl/ssl_engine_config.c` old `2038-2043` new `2041-2084` symbol `ssl_cmd_SSLStrictSNIVHostCheck, ssl_cmd_SSLVHostSNIPolicy, cmd_parms, cmd, dcfg, arg, apr_psprintf` surface `config_keys, user_visible_output, plugin_api, persistence_state, module_api, config_directives, request_handling`
- `HUNK-0005` `modules/ssl/ssl_engine_init.c` old `297-302` new `297-406` symbol `load_echkeys, ifdef, HAVE_TLSEXT, Helper, functions, to, the, ap_log_error` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, module_api, request_handling`
- `HUNK-0006` `modules/ssl/ssl_engine_init.c` old `563-568` new `667-674` symbol `ssl_init_Module, sc, sni_policy_hash, create_sni_policy_hash, p, ptemp, ap_log_error` surface `environment_variables, config_keys, user_visible_output, env_vars, plugin_api, logging, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0007` `modules/ssl/ssl_engine_kernel.c` old `105-216` new `105-132` symbol `fill_reneg_buffer, Check, whether, a, transition, from` surface `user_visible_output, plugin_api, network_protocol, module_api, request_handling`
- `HUNK-0008` `modules/ssl/ssl_engine_kernel.c` old `279-284` new `195-202` symbol `ssl_hook_ReadReq, AP_DEBUG_ASSERT, hssc, apr_table_setn` surface `plugin_api, network_protocol, module_api, request_handling`
- `HUNK-0009` `modules/ssl/ssl_engine_kernel.c` old `319-337` new `237-250` symbol `ssl_hook_ReadReq, Enforce, SSL, SNI, vhost, compatibility, ssl_check_vhost_sni_policy, apr_table_setn` surface `user_visible_output, plugin_api, logging, network_protocol, module_api, request_handling`
- `HUNK-0010` `modules/ssl/ssl_private.h` old `558-563` new `558-576` symbol `SNI, vhost, compatibility, policy, MODSSL_SNIVH_STRICT, MODSSL_SNIVH_SECURE, mask` surface `public_headers, config_keys, plugin_api, persistence_state, module_api, request_handling`
- `HUNK-0011` `modules/ssl/ssl_private.h` old `723-728` new `736-743` symbol `modssl_snivhpolicy_t, snivh_policy, startup` surface `public_headers, config_keys, user_visible_output, plugin_api, logging, persistence_state, module_api, request_handling`
- `HUNK-0012` `modules/ssl/ssl_private.h` old `876-881` new `891-897` symbol `SSLSrvConfigRec, sni_policy_hash, STACK_OF` surface `public_headers, config_keys, plugin_api, network_protocol, persistence_state, module_api, request_handling`
- `HUNK-0013` `modules/ssl/ssl_private.h` old `961-966` new `977-983` symbol `ssl_cmd_SSLRequire, ssl_cmd_SSLVHostSNIPolicy, cmd_parms, cmd, dcfg, arg, ssl_config_proxy_merge` surface `public_headers, config_keys, plugin_api, module_api, config_directives, request_handling`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P072/analysis.json`
