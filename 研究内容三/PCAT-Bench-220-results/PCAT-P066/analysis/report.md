# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/_worktrees/patched`
- Patch ID: `9c0f64303f61a7ce5247831afe546146073046f3`
- Base ref: `4fcd4f771ee356f05139a190d63899a98d47a530`
- Base commit: `4fcd4f771ee356f05139a190d63899a98d47a530`
- Patch apply status: `applied`
- Profile: `rsyslog`
- Effective profile: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; patch_lines=1190 >= 1000; raw_hunks=56 >= 45; candidate_hunks=52 >= 40; candidate_context_bytes=242788 >= 180000; candidates_json_bytes=485513 >= 180000
- Changed files: 15
- Candidate hunks: 52
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 51448 |
| `patch_lines` | 1190 |
| `raw_hunks` | 56 |
| `candidate_hunks` | 52 |
| `changed_files` | 15 |
| `churn` | 688 |
| `candidate_context_bytes` | 242788 |
| `candidates_json_bytes` | 485513 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/shards`
- Shard count: 14

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 1 | 1 | 6037 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 3 | 1 | 9044 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 4 | 1 | 23690 | `shards/shard-0003.json` |
| `SHARD-0004` | `config_keys` | 3 | 2 | 17490 | `shards/shard-0004.json` |
| `SHARD-0005` | `config_keys` | 3 | 1 | 30929 | `shards/shard-0005.json` |
| `SHARD-0006` | `config_keys` | 4 | 2 | 26738 | `shards/shard-0006.json` |
| `SHARD-0007` | `logging` | 4 | 1 | 30935 | `shards/shard-0007.json` |
| `SHARD-0008` | `persistence_state` | 6 | 2 | 25494 | `shards/shard-0008.json` |
| `SHARD-0009` | `public_headers` | 4 | 2 | 13462 | `shards/shard-0009.json` |
| `SHARD-0010` | `public_headers` | 3 | 1 | 10006 | `shards/shard-0010.json` |
| `SHARD-0011` | `tests` | 5 | 5 | 8399 | `shards/shard-0011.json` |
| `SHARD-0012` | `tests` | 7 | 5 | 9614 | `shards/shard-0012.json` |
| `SHARD-0013` | `user_visible_output` | 2 | 1 | 10344 | `shards/shard-0013.json` |
| `SHARD-0014` | `user_visible_output` | 3 | 1 | 20606 | `shards/shard-0014.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/rsyslog show 4fcd4f771ee356f05139a190d63899a98d47a530:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis.json`.

## Candidate Hunks

- `HUNK-0005` `runtime/action.c` old `90-95` new `90-96` symbol `include, ratelimit, h, processMsgMain` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0006` `runtime/action.c` old `175-180` new `176-182` symbol `cnfparamdescr, action, ratelimit, name, eCmdHdlrString, ATTR_NONNULL` surface `config_keys, user_visible_output, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0007` `runtime/action.c` old `317-328` new `319-332` symbol `actionDestruct, pThis, ratelimiter, NULL, ratelimitDestruct, free, qqueueDestruct` surface `config_keys, user_visible_output, logging, module_api, config_language, daemon_interfaces`
- `HUNK-0008` `runtime/action.c` old `371-376` new `375-382` symbol `actionConstruct, pThis, pszRatelimitName, NULL, ratelimiter, CHKmalloc` surface `config_keys, user_visible_output, logging, module_api, config_language, daemon_interfaces`
- `HUNK-0009` `runtime/action.c` old `500-505` new `506-524` symbol `nvls, STATSCOUNTER_INIT, pThis, ctrRateLimitAllowed, mutCtrRateLimitAllowed, CHKiRet` surface `user_visible_output, network_protocol, module_api, daemon_interfaces`
- `HUNK-0010` `runtime/action.c` old `582-587` new `601-624` symbol `nvls, pThis, pszRatelimitName, NULL, CHKiRet, ratelimitNewFromConfigForScope, action, ratelimitSetNoTimeCache, ratelimitSetThreadSafe, qqueueApplyCnfParam` surface `config_keys, user_visible_output, logging, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0011` `runtime/action.c` old `705-710` new `742-786` symbol `actionCommitted, rsRetVal, ATTR_NONNULL, actionCheckOutputRatelimit, action_t, pAction, actionSetState` surface `config_keys, user_visible_output, persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0012` `runtime/action.c` old `1906-1911` new `1982-1994` symbol `processMsgMain, iRet, actionCheckOutputRatelimit, pAction, pWti, RS_RET_DISCARDMSG, CHKiRet, ABORT_FINALIZE` surface `user_visible_output, logging, persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0013` `runtime/action.c` old `1918-1927` new `2001-2011` symbol `processMsgMain, finalize_it, CHKiRet` surface `callbacks, user_visible_output, plugin_api, logging, persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0014` `runtime/action.c` old `2336-2341` new `2420-2426` symbol `doSubmitToActionQNotAllMark, DEFiRet, DBGPRINTF` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0015` `runtime/action.c` old `2373-2378` new `2458-2465` symbol `cnfparamvals, strcmp, pblk, descr, i, name, action, CHKmalloc, actionApplyCnfParam` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0016` `runtime/action.c` old `2380-2386` new `2467-2475` symbol `cnfparamvals, finalize_it, RETiRet, RS_RET_OK, dbgprintf` surface `config_keys, user_visible_output, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0017` `runtime/action.h` old `40-45` new `40-47` symbol `ratelimit_s, ratelimit_t` surface `public_headers, config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0018` `runtime/action.h` old `95-100` new `97-104` symbol `action_s, uchar, pszRatelimitName, optional, output, ratelimit, rsRetVal` surface `public_headers, config_keys, user_visible_output, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0019` `runtime/action.h` old `117-122` new `121-130` symbol `action_s, STATSCOUNTER_DEF, ctrRateLimitAllowed, mutCtrRateLimitAllowed, ctrRateLimitDropped, mutCtrRateLimitDropped` surface `public_headers, config_keys, user_visible_output, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0020` `runtime/ratelimit.c` old `266-274` new `266-278` symbol `ratelimit_ps_policy_s, sbool, has_scope, has_output_mode, ratelimit_scope_t, scope, pthread_rwlock_destroy` surface `persistence_state, module_api, daemon_interfaces`
- `HUNK-0021` `runtime/ratelimit.c` old `456-461` new `460-497` symbol `rsRetVal, parsePolicyScopeValue, value, ratelimit_scope_t, out, DEFiRet, ABORT_FINALIZE` surface `user_visible_output, logging, module_api, daemon_interfaces`
- `HUNK-0022` `runtime/ratelimit.c` old `620-626` new `656-676` symbol `parsePolicyFile, last_key, NULL, strcmp, scope, parsePolicyScopeValue, LogError, CHKmalloc` surface `user_visible_output, module_api, daemon_interfaces`
- `HUNK-0023` `runtime/ratelimit.c` old `1311-1316` new `1361-1368` symbol `ratelimitReloadPolicyFile, ratelimit_scope_t, scope, ratelimit_output_mode_t, output_mode` surface `persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0024` `runtime/ratelimit.c` old `1321-1331` new `1373-1440` symbol `ratelimitReloadPolicyFile, pthread_mutex_lock, shared, mut, output_mode, pthread_mutex_unlock, LogError` surface `logging, persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0025` `runtime/ratelimit.c` old `1335-1340` new `1444-1452` symbol `ratelimitReloadPolicyFile, pthread_mutex_lock, shared, mut, output_mode, pthread_mutex_unlock, ratelimitSharedStoreUInt` surface `logging, persistence_state, module_api, daemon_interfaces`
- `HUNK-0026` `runtime/ratelimit.c` old `1498-1504` new `1610-1618` symbol `ratelimitAddConfig, per_source_topn, sbool, has_inline_policy_params, has_legacy_per_source_params` surface `logging, persistence_state, module_api, daemon_interfaces`
- `HUNK-0027` `runtime/ratelimit.c` old `1508-1513` new `1622-1629` symbol `ratelimitAddConfig, ratelimit_scope_t, scope, RATELIMIT_SCOPE_INPUT, ratelimit_output_mode_t, output_mode` surface `logging, persistence_state, module_api, daemon_interfaces`
- `HUNK-0028` `runtime/ratelimit.c` old `1520-1525` new `1636-1643` symbol `ratelimitAddConfig, file_policy, has_scope, scope, has_output_mode, output_mode, CHKiRet` surface `persistence_state, module_api, daemon_interfaces`
- `HUNK-0029` `runtime/ratelimit.c` old `1546-1551` new `1664-1704` symbol `ratelimitAddConfig, scope, RATELIMIT_SCOPE_OUTPUT, policy_file, NULL, LogError, ABORT_FINALIZE` surface `config_keys, persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0030` `runtime/ratelimit.c` old `1580-1585` new `1733-1740` symbol `ratelimitAddConfig, shared, scope, output_mode, CHKmalloc` surface `config_keys, logging, persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0031` `runtime/ratelimit.c` old `1671-1678` new `1826-1837` symbol `rsRetVal, ratelimitNewFromConfigForScope, ratelimit_t, ppThis, rsconf_t, conf, ratelimitNewFromConfig, ratelimitPolicyFileDestruct` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0032` `runtime/ratelimit.c` old `1687-1692` new `1846-1856` symbol `ratelimitNewFromConfig, shared, scope, pthread_rwlock_unlock, conf, ratelimit_cfgs, LogError` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0033` `runtime/ratelimit.c` old `1706-1711` new `1870-1880` symbol `rsRetVal, ratelimitNewFromConfig, ratelimit_t, ppThis, rsconf_t, conf, ratelimitNewFromConfigForScope, free` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0034` `runtime/ratelimit.c` old `1867-1872` new `2036-2113` symbol `rsRetVal, ratelimitMsgCountWait, ratelimit_t, __restrict__, ratelimit, time_t, ABORT_FINALIZE` surface `config_keys, user_visible_output, logging, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0035` `runtime/ratelimit.c` old `2163-2168` new `2404-2411` symbol `ratelimitNew, pThis, pShared, scope, RATELIMIT_SCOPE_INPUT, output_mode, snprintf` surface `user_visible_output, module_api, output_format, daemon_interfaces`
- `HUNK-0036` `runtime/ratelimit.h` old `31-38` new `31-48` symbol `ratelimit_ps_state_s, ratelimit_scope_e, RATELIMIT_SCOPE_INPUT, RATELIMIT_SCOPE_OUTPUT, ratelimit_scope_t, ratelimit_output_mode_e` surface `public_headers, user_visible_output, logging, persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0037` `runtime/ratelimit.h` old `102-107` new `112-123` symbol `rsconf_s, rsRetVal, ratelimitNewFromConfigForScope, ratelimit_t, ppThis, rsconf_t, ratelimitNew` surface `public_headers, config_keys, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0038` `runtime/ratelimit.h` old `114-120` new `130-138` symbol `ratelimitAddConfig, per_source_topn, sbool, has_inline_policy_params, has_legacy_per_source_params` surface `public_headers, config_keys, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0039` `runtime/ratelimit.h` old `122-127` new `140-152` symbol `ratelimitSetLinuxLike, rsRetVal, ratelimitMsgCountWait, ratelimit_t, ratelimit, time_t, ratelimitGetScope, ratelimitGetOutputMode, ratelimitSetNoTimeCache` surface `public_headers, config_keys, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0040` `runtime/rsconf.c` old `382-390` new `382-390` symbol `BEGINobjDestruct, ratelimit_cfgsDestruct, pThis, ratelimit_cfgs, free` surface `config_keys, user_visible_output, logging, module_api, config_language, daemon_interfaces`
- `HUNK-0041` `runtime/rsconf.c` old `524-529` new `524-531` symbol `cnfobj, sbool, has_inline_policy_params, has_legacy_per_source_params, initFunc_ratelimit` surface `persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0042` `runtime/rsconf.c` old `537-546` new `539-551` symbol `cnfobj, has_inline_policy_params, CHKmalloc` surface `persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0043` `runtime/rsconf.c` old `549-562` new `554-572` symbol `cnfobj, has_legacy_per_source_params, CHKmalloc` surface `persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0044` `runtime/rsconf.c` old `580-586` new `590-596` symbol `cnfobj, per_source_topn, has_inline_policy_params, has_legacy_per_source_params, CHKiRet` surface `config_keys, user_visible_output, logging, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0045` `tests/Makefile.am` old `653-658` new `653-662` symbol `action, ratelimit, drop, sh, pace, reload` surface `tests, config_keys, user_visible_output, persistence_state, config_language, output_format, daemon_interfaces`
- `HUNK-0046` `tests/action-ratelimit-drop.sh` old `0--1` new `1-31` symbol `bin, bash, Verify, generic, action, level` surface `tests, logging, output_format, daemon_interfaces`
- `HUNK-0047` `tests/action-ratelimit-pace.sh` old `0--1` new `1-40` symbol `bin, bash, Verify, generic, action, level` surface `tests, user_visible_output, logging, output_format, daemon_interfaces`
- `HUNK-0048` `tests/action-ratelimit-reload.sh` old `0--1` new `1-57` symbol `bin, bash, Verify, reload, behavior, output` surface `tests, logging, output_format, daemon_interfaces`
- `HUNK-0049` `tests/action-ratelimit-validation.sh` old `0--1` new `1-86` symbol `bin, bash, Validate, generic, output, rate` surface `tests, config_keys, user_visible_output, logging, config_language, daemon_interfaces`
- `HUNK-0050` `tests/stats-cee-vg.sh` old `3-9` new `3-9` symbol `uname, FreeBSD, then` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0051` `tests/stats-cee-vg.sh` old `32-36` new `32-36` symbol `custom_content_check, cee, name, an_action_that_is_never_called, origin, core` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0052` `tests/stats-cee.sh` old `24-28` new `24-28` symbol `custom_content_check, cee, name, an_action_that_is_never_called, origin, core` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0053` `tests/stats-json-es.sh` old `24-29` new `24-29` symbol `custom_content_check, name, an_action_that_is_never_called, origin, core, action` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0054` `tests/stats-json-vg.sh` old `3-9` new `3-9` symbol `uname, FreeBSD, then` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0055` `tests/stats-json-vg.sh` old `32-37` new `32-37` symbol `custom_content_check, name, an_action_that_is_never_called, origin, core, action` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0056` `tests/stats-json.sh` old `23-28` new `23-28` symbol `custom_content_check, name, an_action_that_is_never_called, origin, core, action` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis.json`
