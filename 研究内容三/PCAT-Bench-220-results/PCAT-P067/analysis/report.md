# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/_worktrees/patched`
- Patch ID: `8aa55fd776d35f6d475a2fd5b5d9dcf8864c9f8a`
- Base ref: `7491a61090ec7e78fb2910ca9a104c96fae468ee`
- Base commit: `7491a61090ec7e78fb2910ca9a104c96fae468ee`
- Patch apply status: `applied`
- Profile: `rsyslog`
- Effective profile: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; patch_lines=1367 >= 1000; raw_hunks=75 >= 45; candidate_hunks=60 >= 40; candidate_context_bytes=232301 >= 180000; candidates_json_bytes=514629 >= 180000
- Changed files: 10
- Candidate hunks: 60
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 60663 |
| `patch_lines` | 1367 |
| `raw_hunks` | 75 |
| `candidate_hunks` | 60 |
| `changed_files` | 10 |
| `churn` | 724 |
| `candidate_context_bytes` | 232301 |
| `candidates_json_bytes` | 514629 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/shards`
- Shard count: 20

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 1 | 1 | 3070 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 5 | 1 | 21704 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 3 | 1 | 16826 | `shards/shard-0003.json` |
| `SHARD-0004` | `config_keys` | 3 | 2 | 10923 | `shards/shard-0004.json` |
| `SHARD-0005` | `config_keys` | 4 | 1 | 16068 | `shards/shard-0005.json` |
| `SHARD-0006` | `config_keys` | 3 | 1 | 11430 | `shards/shard-0006.json` |
| `SHARD-0007` | `config_keys` | 3 | 1 | 11985 | `shards/shard-0007.json` |
| `SHARD-0008` | `config_keys` | 3 | 1 | 12823 | `shards/shard-0008.json` |
| `SHARD-0009` | `ioctl_netlink_consumers` | 4 | 1 | 12756 | `shards/shard-0009.json` |
| `SHARD-0010` | `network_protocol` | 1 | 1 | 4457 | `shards/shard-0010.json` |
| `SHARD-0011` | `plugin_api` | 1 | 1 | 3363 | `shards/shard-0011.json` |
| `SHARD-0012` | `public_headers` | 3 | 1 | 10529 | `shards/shard-0012.json` |
| `SHARD-0013` | `public_headers` | 1 | 1 | 2802 | `shards/shard-0013.json` |
| `SHARD-0014` | `syscall_wrappers` | 1 | 1 | 5035 | `shards/shard-0014.json` |
| `SHARD-0015` | `tests` | 8 | 4 | 21090 | `shards/shard-0015.json` |
| `SHARD-0016` | `user_visible_output` | 4 | 1 | 8574 | `shards/shard-0016.json` |
| `SHARD-0017` | `user_visible_output` | 6 | 2 | 31362 | `shards/shard-0017.json` |
| `SHARD-0018` | `user_visible_output` | 2 | 2 | 9389 | `shards/shard-0018.json` |
| `SHARD-0019` | `user_visible_output` | 2 | 1 | 9965 | `shards/shard-0019.json` |
| `SHARD-0020` | `user_visible_output` | 2 | 1 | 8150 | `shards/shard-0020.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/rsyslog show 7491a61090ec7e78fb2910ca9a104c96fae468ee:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/analysis.json`.

## Candidate Hunks

- `HUNK-0016` `grammar/rainerscript.c` old `4179-4184` new `4179-4187` symbol `cnfexpr, ar, NULL, cnfarrayContentDestruct` surface `user_visible_output, logging, config_language, output_format`
- `HUNK-0017` `grammar/rainerscript.c` old `4664-4669` new `4667-4677` symbol `cnfarray, ar, NULL, doIndent, indent, dbgprintf, cnfarrayPrint` surface `user_visible_output, logging, config_language`
- `HUNK-0018` `grammar/rainerscript.c` old `4966-4971` new `4974-4984` symbol `cnfarray, ar, nmemb, arr, NULL, val, cnfstmtPrintOnly` surface `user_visible_output, config_language`
- `HUNK-0019` `grammar/rainerscript.c` old `4996-5001` new `5009-5017` symbol `old, NULL, nmemb, cnfarrayNew, DBGPRINTF` surface `user_visible_output, config_language, output_format, daemon_interfaces`
- `HUNK-0020` `plugins/imtcp/imtcp.c` old `162-167` new `162-170` symbol `instanceConf_s, AllowedSenders, pAllowedSendersRoot, pAllowedSendersLast, sbool, bAllowedSendersSet, DEFobjCurrIf` surface `config_keys, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0021` `plugins/imtcp/imtcp.c` old `214-219` new `217-225` symbol `modConfData_s, AllowedSenders, pAllowedSendersRoot, pAllowedSendersLast, sbool, bAllowedSendersSet, DEFobjCurrIf` surface `config_keys, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0022` `plugins/imtcp/imtcp.c` old `252-257` new `258-264` symbol `cnfparamdescr, allowedsender, eCmdHdlrArray, DEFobjCurrIf` surface `config_keys, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0023` `plugins/imtcp/imtcp.c` old `297-302` new `304-310` symbol `cnfparamdescr, allowedsender, eCmdHdlrArray, DEFobjCurrIf` surface `config_keys, plugin_api, daemon_control, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0024` `plugins/imtcp/imtcp.c` old `507-514` new `515-527` symbol `setLegacyStrmDrvrMode, pUsrSrv, tcpLstnParams_t, cnf_params, NULL, bUseLegacyAllowedSender` surface `callbacks, user_visible_output, plugin_api, daemon_control, module_api, config_language, daemon_interfaces`
- `HUNK-0025` `plugins/imtcp/imtcp.c` old `619-624` new `632-640` symbol `createInstance, inst, pAllowedSendersRoot, NULL, pAllowedSendersLast, bAllowedSendersSet, CHKmalloc` surface `config_keys, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0026` `plugins/imtcp/imtcp.c` old `804-811` new `820-839` symbol `addListner, inst, bAllowedSendersSet, cnf_params, pAllowedSenderRoot, pAllowedSendersRoot, CHKiRet, free` surface `config_keys, user_visible_output, plugin_api, logging, daemon_control, module_api, config_language, daemon_interfaces`
- `HUNK-0027` `plugins/imtcp/imtcp.c` old `818-823` new `846-852` symbol `tcpsrv, SetUsrP, pOurTcpsrv, NULL, CHKmalloc` surface `config_keys, user_visible_output, plugin_api, logging, daemon_control, module_api, config_language, daemon_interfaces`
- `HUNK-0028` `plugins/imtcp/imtcp.c` old `900-905` new `929-948` symbol `strcmp, inppblk, descr, i, name, allowedsender, CHKiRet` surface `user_visible_output, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0029` `plugins/imtcp/imtcp.c` old `1025-1030` new `1068-1076` symbol `loadModConf, pAllowedSendersRoot, NULL, pAllowedSendersLast, bAllowedSendersSet, cnfparamvalsDestruct` surface `config_keys, user_visible_output, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0030` `plugins/imtcp/imtcp.c` old `1130-1135` new `1176-1195` symbol `strcmp, modpblk, descr, i, name, allowedsender, CHKiRet` surface `config_keys, user_visible_output, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0031` `plugins/imtcp/imtcp.c` old `1281-1286` new `1341-1349` symbol `pModConf, pAllowedSendersRoot, NULL, net, DestructAllowedSenders, free` surface `user_visible_output, plugin_api, network_protocol, module_api, config_language, daemon_interfaces`
- `HUNK-0032` `plugins/imtcp/imtcp.c` old `1311-1316` new `1374-1382` symbol `inst, pAllowedSendersRoot, NULL, net, DestructAllowedSenders, free` surface `user_visible_output, plugin_api, logging, persistence_state, module_api, config_language, daemon_interfaces`
- `HUNK-0033` `plugins/imudp/imudp.c` old `83-88` new `83-90` symbol `DEFobjCurrIf, AllowedSenders, pAllowedSenderRoot, sbool, bUseLegacyAllowedSender` surface `config_keys, plugin_api, network_protocol, daemon_control, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0034` `plugins/imudp/imudp.c` old `125-130` new `127-135` symbol `instanceConf_s, AllowedSenders, pAllowedSendersRoot, pAllowedSendersLast, sbool, bAllowedSendersSet, STATSCOUNTER_DEF` surface `config_keys, user_visible_output, plugin_api, network_protocol, daemon_control, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0035` `plugins/imudp/imudp.c` old `160-165` new `165-173` symbol `modConfData_s, AllowedSenders, pAllowedSendersRoot, pAllowedSendersLast, sbool, bAllowedSendersSet, STATSCOUNTER_DEF` surface `config_keys, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0036` `plugins/imudp/imudp.c` old `170-176` new `178-185` symbol `cnfparamdescr, preservecase, eCmdHdlrBinary, allowedsender, eCmdHdlrArray, STATSCOUNTER_DEF` surface `config_keys, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0037` `plugins/imudp/imudp.c` old `188-194` new `197-204` symbol `cnfparamdescr, ruleset, eCmdHdlrString, allowedsender, eCmdHdlrArray, STATSCOUNTER_DEF` surface `config_keys, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0038` `plugins/imudp/imudp.c` old `217-222` new `227-235` symbol `createInstance, inst, pAllowedSendersRoot, NULL, pAllowedSendersLast, bAllowedSendersSet, CHKmalloc` surface `config_keys, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0039` `plugins/imudp/imudp.c` old `399-404` new `412-427` symbol `addListner, inst, bAllowedSendersSet, newlcnfinfo, pAllowedSenderRoot, pAllowedSendersRoot, CHKmalloc` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, daemon_control, module_api, config_language, daemon_interfaces`
- `HUNK-0040` `plugins/imudp/imudp.c` old `515-520` new `538-544` symbol `std_checkRuleset_genErrMsg, lstn_s, ppLstnPrev, recvmmsg` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0041` `plugins/imudp/imudp.c` old `532-539` new `556-564` symbol `lstn_s, ppLstnPrev, lstn, net, CmpHost, frominet, processPacket` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0042` `plugins/imudp/imudp.c` old `541-547` new `566-576` symbol `lstn_s, lstn, bUseLegacyAllowedSender, pbIsPermitted, net, isAllowedSender2, warning` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0043` `plugins/imudp/imudp.c` old `596-601` new `625-631` symbol `lstn_s, ppLstnPrev, processSocket` surface `user_visible_output, plugin_api, logging, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0044` `plugins/imudp/imudp.c` old `655-663` new `685-693` symbol `wrkrInfo_s, processPacket, lstn, frominetPrev, ppLstnPrev, pbIsPermitted, ABORT_FINALIZE` surface `user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0045` `plugins/imudp/imudp.c` old `683-688` new `713-719` symbol `lstn_s, ppLstnPrev, processSocket` surface `user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0046` `plugins/imudp/imudp.c` old `728-735` new `759-766` symbol `wrkrInfo_s, CHKiRet, processPacket, lstn, frominetPrev, ppLstnPrev, ABORT_FINALIZE` surface `config_keys, user_visible_output, plugin_api, logging, network_protocol, daemon_control, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0047` `plugins/imudp/imudp.c` old `859-864` new `890-896` symbol `wrkrInfo_s, lstn_s, lstnPrev, rcvMainLoop` surface `config_keys, user_visible_output, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0048` `plugins/imudp/imudp.c` old `870-875` new `902-908` symbol `wrkrInfo_s, lstnPrev, NULL, rcvMainLoop` surface `ioctl_netlink_consumers, config_keys, user_visible_output, ioctl_netlink, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0049` `plugins/imudp/imudp.c` old `923-929` new `956-962` symbol `wrkrInfo_s, processSocket, pWrkr, currEvt, i, data, DBGPRINTF` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0050` `plugins/imudp/imudp.c` old `939-944` new `972-978` symbol `wrkrInfo_s, lstn_s, lstnPrev, ATTR_NONNULL` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0051` `plugins/imudp/imudp.c` old `947-952` new `981-987` symbol `wrkrInfo_s, lstnPrev, NULL, DBGPRINTF` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0052` `plugins/imudp/imudp.c` old `993-999` new `1028-1034` symbol `wrkrInfo_s, processSocket, pWrkr, lstn, frominetPrev, lstnPrev, assert` surface `plugin_api, logging, module_api, config_language, daemon_interfaces`
- `HUNK-0053` `plugins/imudp/imudp.c` old `1087-1092` new `1122-1141` symbol `cnfparamvals, strcmp, inppblk, descr, i, name, LogError` surface `user_visible_output, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0054` `plugins/imudp/imudp.c` old `1163-1168` new `1212-1220` symbol `loadModConf, pAllowedSendersRoot, NULL, pAllowedSendersLast, bAllowedSendersSet, cnfparamvalsDestruct` surface `config_keys, user_visible_output, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0055` `plugins/imudp/imudp.c` old `1215-1220` new `1267-1286` symbol `strcmp, modpblk, descr, i, name, allowedsender, LogError` surface `config_keys, user_visible_output, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0056` `plugins/imudp/imudp.c` old `1325-1334` new `1391-1406` symbol `inst, pAllowedSendersRoot, NULL, net, DestructAllowedSenders, pModConf, free` surface `config_keys, user_visible_output, plugin_api, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0057` `plugins/imudp/imudp.c` old `1420-1428` new `1492-1507` symbol `instanceConf_t, inst, bDoACLCheck, runModConf, bAllowedSendersSet, root, pthread_join` surface `syscall_wrappers, user_visible_output, plugin_api, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0058` `runtime/net.c` old `570-575` new `570-596` symbol `clearAllowedSenders, DestructAllowedSenders, AllowedSenders, ppRoot, pPrev, pCurr, assert, reinitAllowRoot` surface `user_visible_output, module_api, daemon_interfaces`
- `HUNK-0059` `runtime/net.c` old `879-884` new `900-936` symbol `addAllowedSenderLine, rsRetVal, addAllowedSenderEntry, AllowedSenders, ppRoot, ppLast, rsParsDestruct` surface `user_visible_output, network_protocol, module_api, daemon_interfaces`
- `HUNK-0060` `runtime/net.c` old `962-978` new `1014-1029` symbol `NetAddr, isAllowedSenderList, AllowedSenders, pAllowRoot, sockaddr, pFrom, isAllowedSender2, setAllowRoot, memcpy` surface `user_visible_output, persistence_state, module_api, daemon_interfaces`
- `HUNK-0061` `runtime/net.c` old `992-997` new `1043-1060` symbol `sockaddr, isAllowedSender2, uchar, pszType, pFrom, pszFromHost, assert, setAllowRoot` surface `user_visible_output, logging, persistence_state, module_api, output_format, daemon_interfaces`
- `HUNK-0062` `runtime/net.c` old `1610-1615` new `1673-1680` symbol `BEGINobjQueryInterface, pIf, addAllowedSenderEntry, DestructAllowedSenders, here` surface `user_visible_output, logging, network_protocol, daemon_control, persistence_state, module_api, daemon_interfaces`
- `HUNK-0063` `runtime/net.c` old `1624-1629` new `1689-1695` symbol `BEGINobjQueryInterface, pIf, isAllowedSenderList, here` surface `network_protocol, daemon_control, persistence_state, module_api, daemon_interfaces`
- `HUNK-0064` `runtime/net.h` old `148-153` new `148-156` symbol `BEGINinterface, rsRetVal, addAllowedSenderEntry, AllowedSenders, ppRoot, ppLast` surface `public_headers, daemon_control, module_api, config_language, daemon_interfaces`
- `HUNK-0065` `runtime/net.h` old `165-170` new `168-175` symbol `BEGINinterface, isAllowedSenderList, AllowedSenders, pAllowRoot, sockaddr, pFrom, int` surface `public_headers, user_visible_output, network_protocol, daemon_control, module_api, daemon_interfaces`
- `HUNK-0066` `runtime/net.h` old `229-235` new `234-240` symbol `BEGINinterface, define, netCURR_IF_VERSION, increment, whenever, you, rsRetVal` surface `public_headers, user_visible_output, module_api`
- `HUNK-0067` `runtime/tcpsrv.h` old `64-69` new `64-71` symbol `tcpLstnParams_s, AllowedSenders, pAllowedSenderRoot, source, address, ACL` surface `public_headers, config_keys, user_visible_output, logging, network_protocol, module_api, config_language, daemon_interfaces`
- `HUNK-0068` `tests/Makefile.am` old `258-263` new `258-265` symbol `allowed, sender, modern, sh, empty, array` surface `tests, environment_variables, user_visible_output, env_vars, output_format, daemon_interfaces`
- `HUNK-0069` `tests/Makefile.am` old `670-675` new `672-678` symbol `yaml, allowed, sender, modern, sh` surface `tests, config_keys, user_visible_output, persistence_state, config_language, output_format, daemon_interfaces`
- `HUNK-0070` `tests/Makefile.am` old `692-697` new `695-702` symbol `allowed, sender, modern, sh, empty, array` surface `tests, user_visible_output, persistence_state, output_format, daemon_interfaces`
- `HUNK-0071` `tests/Makefile.am` old `771-776` new `776-782` symbol `yaml, allowed, sender, modern, sh` surface `tests, user_visible_output, logging, output_format, daemon_interfaces`
- `HUNK-0072` `tests/Makefile.am` old `1999-2005` new `2005-2013` symbol `allowed, sender, modern, log, tcp, zero` surface `tests, config_keys, persistence_state, config_language, output_format, daemon_interfaces`
- `HUNK-0073` `tests/allowed-sender-empty-array.sh` old `0--1` new `1-58` symbol `bin, bash, Verify, that, modern, YAML` surface `tests, config_keys, user_visible_output, plugin_api, logging, persistence_state, config_language, daemon_interfaces`
- `HUNK-0074` `tests/allowed-sender-modern.sh` old `0--1` new `1-78` symbol `bin, bash, Verify, modern, allowedSender, ACLs` surface `tests, user_visible_output, plugin_api, logging, network_protocol, persistence_state, output_format, daemon_interfaces`
- `HUNK-0075` `tests/yaml-allowed-sender-modern.sh` old `0--1` new `1-87` symbol `bin, bash, Verify, YAML, parsing, modern` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/analysis.json`
