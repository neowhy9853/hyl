# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/_worktrees/patched`
- Patch ID: `ff1d43509608cfe41a7c4c4dc8285a1de5bb1824`
- Base ref: `ff1d43509608cfe41a7c4c4dc8285a1de5bb1824^1`
- Base commit: `1a2fec62f038beab768a3929abcfcb63dd52bc34`
- Patch apply status: `applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; patch_lines=5184 >= 1000; raw_hunks=330 >= 45; candidate_hunks=330 >= 40; candidate_context_bytes=2157413 >= 180000; candidates_json_bytes=3370928 >= 180000
- Changed files: 5
- Candidate hunks: 330
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 282330 |
| `patch_lines` | 5184 |
| `raw_hunks` | 330 |
| `candidate_hunks` | 330 |
| `changed_files` | 5 |
| `churn` | 1392 |
| `candidate_context_bytes` | 2157413 |
| `candidates_json_bytes` | 3370928 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/shards`
- Shard count: 37

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `config` | 2 | 1 | 7107 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 3 | 1 | 8777 | `shards/shard-0002.json` |
| `SHARD-0003` | `public_headers` | 1 | 1 | 3096 | `shards/shard-0003.json` |
| `SHARD-0004` | `tests` | 12 | 1 | 46648 | `shards/shard-0004.json` |
| `SHARD-0005` | `tests` | 12 | 1 | 43047 | `shards/shard-0005.json` |
| `SHARD-0006` | `tests` | 12 | 1 | 65289 | `shards/shard-0006.json` |
| `SHARD-0007` | `tests` | 12 | 1 | 67814 | `shards/shard-0007.json` |
| `SHARD-0008` | `tests` | 12 | 1 | 54538 | `shards/shard-0008.json` |
| `SHARD-0009` | `tests` | 12 | 1 | 46238 | `shards/shard-0009.json` |
| `SHARD-0010` | `tests` | 12 | 1 | 74652 | `shards/shard-0010.json` |
| `SHARD-0011` | `tests` | 12 | 1 | 78951 | `shards/shard-0011.json` |
| `SHARD-0012` | `tests` | 8 | 1 | 71121 | `shards/shard-0012.json` |
| `SHARD-0013` | `tests` | 4 | 1 | 70608 | `shards/shard-0013.json` |
| `SHARD-0014` | `tests` | 4 | 1 | 78214 | `shards/shard-0014.json` |
| `SHARD-0015` | `tests` | 3 | 1 | 57622 | `shards/shard-0015.json` |
| `SHARD-0016` | `tests` | 4 | 1 | 78310 | `shards/shard-0016.json` |
| `SHARD-0017` | `tests` | 10 | 1 | 74678 | `shards/shard-0017.json` |
| `SHARD-0018` | `tests` | 7 | 1 | 73827 | `shards/shard-0018.json` |
| `SHARD-0019` | `tests` | 10 | 1 | 77761 | `shards/shard-0019.json` |
| `SHARD-0020` | `tests` | 9 | 1 | 76992 | `shards/shard-0020.json` |
| `SHARD-0021` | `tests` | 10 | 2 | 79247 | `shards/shard-0021.json` |
| `SHARD-0022` | `tests` | 12 | 1 | 42673 | `shards/shard-0022.json` |
| `SHARD-0023` | `tests` | 12 | 1 | 37369 | `shards/shard-0023.json` |
| `SHARD-0024` | `tests` | 12 | 1 | 52108 | `shards/shard-0024.json` |
| `SHARD-0025` | `tests` | 12 | 1 | 67213 | `shards/shard-0025.json` |
| `SHARD-0026` | `tests` | 12 | 1 | 38202 | `shards/shard-0026.json` |
| `SHARD-0027` | `tests` | 11 | 1 | 66033 | `shards/shard-0027.json` |
| `SHARD-0028` | `tests` | 4 | 1 | 62418 | `shards/shard-0028.json` |
| `SHARD-0029` | `tests` | 4 | 1 | 71866 | `shards/shard-0029.json` |
| `SHARD-0030` | `tests` | 4 | 1 | 78323 | `shards/shard-0030.json` |
| `SHARD-0031` | `tests` | 12 | 1 | 76689 | `shards/shard-0031.json` |
| `SHARD-0032` | `tests` | 12 | 1 | 51016 | `shards/shard-0032.json` |
| `SHARD-0033` | `tests` | 12 | 1 | 43349 | `shards/shard-0033.json` |
| `SHARD-0034` | `tests` | 12 | 1 | 67837 | `shards/shard-0034.json` |
| `SHARD-0035` | `tests` | 12 | 1 | 72057 | `shards/shard-0035.json` |
| `SHARD-0036` | `tests` | 12 | 1 | 51537 | `shards/shard-0036.json` |
| `SHARD-0037` | `tests` | 4 | 1 | 44186 | `shards/shard-0037.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show 1a2fec62f038beab768a3929abcfcb63dd52bc34:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/nmcli/connections.c` old `920-925` new `920-926` symbol `_metagen_con_active_general_get_fcn, NMC_GENERIC_INFO_TYPE_CON_ACTIVE_GENERAL_MASTER_PATH, nm_object_get_path` surface `config, persistence_state, nmcli`
- `HUNK-0002` `src/nmcli/connections.c` old `949-954` new `950-957` symbol `CONTROLLER, PATH, _METAGEN_CON_ACTIVE_GENERAL, NMC_GENERIC_INFO_TYPE_CON_ACTIVE_GENERAL_MASTER_PATH` surface `config, persistence_state`
- `HUNK-0003` `src/nmcli/devices.c` old `766-782` new `766-784` symbol `NMC_META_GENERIC, PORTS, define, NMC_FIELDS_DEV_SHOW_CONTROLLER_PROP_COMMON, NAME, SLAVES` surface `config_keys, config, nmcli`
- `HUNK-0004` `src/nmcli/devices.c` old `1537-1543` new `1539-1546` symbol `print_bond_bridge_info, set_val_str, arr, g_strdup, ports_str, str, g_ptr_array_add` surface `config_keys, config, nmcli`
- `HUNK-0005` `src/nmcli/devices.c` old `1600-1607` new `1603-1611` symbol `print_team_info, set_val_str, arr, g_strdup, ports_str, str, sanitize_team_config, g_ptr_array_add` surface `config_keys, user_visible_output, config, persistence_state, nmcli`
- `HUNK-0006` `src/nmcli/utils.h` old `157-162` new `157-163` symbol `NMC_GENERIC_INFO_TYPE_CON_ACTIVE_GENERAL_MASTER_PATH, nmc_warn_if_version_mismatch` surface `public_headers`
- `HUNK-0007` `src/tests/client/test-client.check-on-disk/test_003.expected` old `1608-1619` new `1608-1619` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0008` `src/tests/client/test-client.check-on-disk/test_003.expected` old `1753-1767` new `1753-1768` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0009` `src/tests/client/test-client.check-on-disk/test_003.expected` old `1901-1906` new `1902-1908` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0010` `src/tests/client/test-client.check-on-disk/test_003.expected` old `2696-2707` new `2698-2709` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0011` `src/tests/client/test-client.check-on-disk/test_003.expected` old `2841-2846` new `2843-2849` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0012` `src/tests/client/test-client.check-on-disk/test_003.expected` old `2855-2869` new `2858-2873` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0013` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3003-3008` new `3007-3013` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0014` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3017-3022` new `3022-3028` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0015` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3540-3551` new `3546-3557` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0016` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3685-3690` new `3691-3697` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0017` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3699-3713` new `3706-3721` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0018` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3847-3852` new `3855-3861` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0019` `src/tests/client/test-client.check-on-disk/test_003.expected` old `3861-3875` new `3870-3885` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0020` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4009-4023` new `4019-4034` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0021` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4157-4162` new `4168-4174` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0022` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4376-4387` new `4388-4399` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0023` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4521-4526` new `4533-4539` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0024` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4535-4549` new `4548-4563` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0025` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4683-4688` new `4697-4703` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0026` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4697-4711` new `4712-4727` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0027` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4845-4859` new `4861-4876` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0028` `src/tests/client/test-client.check-on-disk/test_003.expected` old `4993-4998` new `5010-5016` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0029` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5228-5239` new `5246-5257` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0030` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5384-5389` new `5402-5408` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0031` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5402-5417` new `5421-5437` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0032` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5562-5567` new `5582-5588` symbol `GENERAL, CONTROLLER, PATH` surface `tests, persistence_state, dbus_api`
- `HUNK-0033` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5580-5595` new `5601-5617` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0034` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5740-5755` new `5762-5778` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0035` `src/tests/client/test-client.check-on-disk/test_003.expected` old `5900-5905` new `5923-5929` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0036` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6160-6171` new `6184-6195` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0037` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6316-6321` new `6340-6346` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0038` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6334-6349` new `6359-6375` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0039` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6494-6499` new `6520-6526` symbol `GENERAL, CONTROLLER, PATH` surface `tests, persistence_state, dbus_api`
- `HUNK-0040` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6512-6527` new `6539-6555` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0041` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6672-6687` new `6700-6716` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0042` `src/tests/client/test-client.check-on-disk/test_003.expected` old `6832-6837` new `6861-6867` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0043` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7072-7083` new `7102-7113` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0044` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7217-7222` new `7247-7253` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0045` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7231-7245` new `7262-7277` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0046` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7379-7384` new `7411-7417` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0047` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7393-7407` new `7426-7441` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0048` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7541-7555` new `7575-7590` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0049` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7689-7694` new `7724-7730` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0050` `src/tests/client/test-client.check-on-disk/test_003.expected` old `7904-7915` new `7940-7951` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0051` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8049-8054` new `8085-8091` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0052` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8063-8077` new `8100-8115` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0053` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8211-8216` new `8249-8255` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0054` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8225-8239` new `8264-8279` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0055` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8373-8387` new `8413-8428` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0056` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8521-8526` new `8562-8568` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0057` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8740-8751` new `8782-8793` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0058` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8762-8782` new `8804-8824` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0059` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8793-8813` new `8835-8855` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0060` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8824-8840` new `8866-8882` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0061` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8851-8858` new `8893-8900` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0062` `src/tests/client/test-client.check-on-disk/test_003.expected` old `8992-9003` new `9034-9045` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0063` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9014-9034` new `9056-9076` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0064` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9045-9065` new `9087-9107` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0065` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9076-9092` new `9118-9134` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0066` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9103-9110` new `9145-9152` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0067` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9260-9271` new `9302-9313` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0068` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9293-9318` new `9335-9360` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0069` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9340-9365` new `9382-9407` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0070` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9387-9404` new `9429-9446` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0071` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9426-9434` new `9468-9476` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0072` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9608-9619` new `9650-9661` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0073` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9641-9666` new `9683-9708` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0074` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9688-9713` new `9730-9755` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0075` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9735-9752` new `9777-9794` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0076` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9774-9782` new `9816-9824` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0077` `src/tests/client/test-client.check-on-disk/test_003.expected` old `9936-10003` new `9978-10045` symbol `size, stdout, bytes, GENERAL, ethernet, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0078` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10098-10165` new `10140-10207` symbol `size, stdout, bytes, GENERAL, ethernet, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0079` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10468-10479` new `10510-10521` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0080` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10613-10618` new `10655-10661` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0081` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10627-10641` new `10670-10685` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0082` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10775-10780` new `10819-10825` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0083` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10789-10803` new `10834-10849` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0084` `src/tests/client/test-client.check-on-disk/test_003.expected` old `10937-10951` new `10983-10998` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0085` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11085-11090` new `11132-11138` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0086` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11508-11519` new `11556-11567` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0087` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11653-11658` new `11701-11707` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0088` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11667-11681` new `11716-11731` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0089` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11815-11820` new `11865-11871` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0090` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11829-11843` new `11880-11895` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0091` `src/tests/client/test-client.check-on-disk/test_003.expected` old `11977-11991` new `12029-12044` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0092` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12125-12130` new `12178-12184` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0093` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12586-12597` new `12640-12651` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0094` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12742-12747` new `12796-12802` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0095` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12760-12775` new `12815-12831` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0096` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12920-12925` new `12976-12982` symbol `GENERAL, CONTROLLER, PATH` surface `tests, persistence_state, dbus_api`
- `HUNK-0097` `src/tests/client/test-client.check-on-disk/test_003.expected` old `12938-12953` new `12995-13011` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0098` `src/tests/client/test-client.check-on-disk/test_003.expected` old `13098-13113` new `13156-13172` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0099` `src/tests/client/test-client.check-on-disk/test_003.expected` old `13258-13263` new `13317-13323` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0100` `src/tests/client/test-client.check-on-disk/test_003.expected` old `13744-13755` new `13804-13815` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0101` `src/tests/client/test-client.check-on-disk/test_003.expected` old `13900-13905` new `13960-13966` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0102` `src/tests/client/test-client.check-on-disk/test_003.expected` old `13918-13933` new `13979-13995` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0103` `src/tests/client/test-client.check-on-disk/test_003.expected` old `14078-14083` new `14140-14146` symbol `GENERAL, CONTROLLER, PATH` surface `tests, persistence_state, dbus_api`
- `HUNK-0104` `src/tests/client/test-client.check-on-disk/test_003.expected` old `14096-14111` new `14159-14175` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0105` `src/tests/client/test-client.check-on-disk/test_003.expected` old `14256-14271` new `14320-14336` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0106` `src/tests/client/test-client.check-on-disk/test_003.expected` old `14416-14421` new `14481-14487` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0107` `src/tests/client/test-client.check-on-disk/test_003.expected` old `14864-14875` new `14930-14941` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0108` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15009-15014` new `15075-15081` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0109` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15023-15037` new `15090-15105` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0110` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15171-15176` new `15239-15245` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0111` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15185-15199` new `15254-15269` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0112` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15333-15347` new `15403-15418` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0113` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15481-15486` new `15552-15558` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, persistence_state, dbus_api`
- `HUNK-0114` `src/tests/client/test-client.check-on-disk/test_003.expected` old `15904-15915` new `15976-15987` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0115` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16049-16054` new `16121-16127` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0116` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16063-16077` new `16136-16151` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0117` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16211-16216` new `16285-16291` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0118` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16225-16239` new `16300-16315` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0119` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16373-16387` new `16449-16464` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0120` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16521-16526` new `16598-16604` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, persistence_state, dbus_api`
- `HUNK-0121` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16758-16769` new `16836-16847` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0122` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16777-16791` new `16855-16870` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0123` `src/tests/client/test-client.check-on-disk/test_003.expected` old `16799-16804` new `16878-16884` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0124` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17036-17047` new `17116-17127` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0125` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17055-17069` new `17135-17150` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0126` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17077-17082` new `17158-17164` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0127` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17330-17341` new `17412-17423` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0128` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17355-17370` new `17437-17453` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0129` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17384-17389` new `17467-17473` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0130` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17662-17673` new `17746-17757` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0131` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17687-17702` new `17771-17787` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0132` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17716-17721` new `17801-17807` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0133` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17974-17985` new `18060-18071` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0134` `src/tests/client/test-client.check-on-disk/test_003.expected` old `17993-18007` new `18079-18094` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0135` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18015-18020` new `18102-18108` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0136` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18248-18259` new `18336-18347` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0137` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18267-18281` new `18355-18370` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0138` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18289-18294` new `18378-18384` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0139` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18526-18552` new `18616-18642` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0140` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18704-18730` new `18794-18820` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0141` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18898-18909` new `18988-18999` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0142` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18911-18928` new `19001-19018` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0143` `src/tests/client/test-client.check-on-disk/test_003.expected` old `18930-18938` new `19020-19028` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0144` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19130-19141` new `19220-19231` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0145` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19143-19160` new `19233-19250` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0146` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19162-19170` new `19252-19260` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0147` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19342-19365` new `19432-19455` symbol `size, stdout, bytes, GENERAL, ethernet, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0148` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19478-19501` new `19568-19591` symbol `size, stdout, bytes, GENERAL, ethernet, UUID` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0149` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19820-19831` new `19910-19921` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0150` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19839-19853` new `19929-19944` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0151` `src/tests/client/test-client.check-on-disk/test_003.expected` old `19861-19866` new `19952-19958` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0152` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20300-20311` new `20392-20403` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0153` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20319-20333` new `20411-20426` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0154` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20341-20346` new `20434-20440` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0155` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20816-20827` new `20910-20921` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0156` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20841-20856` new `20935-20951` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0157` `src/tests/client/test-client.check-on-disk/test_003.expected` old `20870-20875` new `20965-20971` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0158` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21370-21381` new `21466-21477` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0159` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21395-21410` new `21491-21507` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0160` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21424-21429` new `21521-21527` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0161` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21888-21899` new `21986-21997` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0162` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21907-21921` new `22005-22020` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0163` `src/tests/client/test-client.check-on-disk/test_003.expected` old `21929-21934` new `22028-22034` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0164` `src/tests/client/test-client.check-on-disk/test_003.expected` old `22368-22379` new `22468-22479` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0165` `src/tests/client/test-client.check-on-disk/test_003.expected` old `22387-22401` new `22487-22502` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0166` `src/tests/client/test-client.check-on-disk/test_003.expected` old `22409-22414` new `22510-22516` symbol `GENERAL, CONTROLLER, PATH` surface `tests, proc_sys_consumers, config, dbus_api`
- `HUNK-0167` `src/tests/client/test-client.check-on-disk/test_004.expected` old `694-705` new `694-705` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0168` `src/tests/client/test-client.check-on-disk/test_004.expected` old `830-835` new `830-836` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0169` `src/tests/client/test-client.check-on-disk/test_004.expected` old `841-852` new `842-853` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0170` `src/tests/client/test-client.check-on-disk/test_004.expected` old `977-982` new `978-984` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0171` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1104-1115` new `1106-1117` symbol `size, stdout, bytes` surface `tests, config, dbus_api, nmcli`
- `HUNK-0172` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1240-1245` new `1242-1248` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0173` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1251-1262` new `1254-1265` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0174` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1387-1392` new `1390-1396` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0175` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1398-1409` new `1402-1413` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0176` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1534-1539` new `1538-1544` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0177` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1545-1556` new `1550-1561` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0178` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1681-1686` new `1686-1692` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0179` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1974-1985` new `1980-1991` symbol `size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0180` `src/tests/client/test-client.check-on-disk/test_004.expected` old `1993-2007` new `1999-2014` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0181` `src/tests/client/test-client.check-on-disk/test_004.expected` old `2015-2020` new `2022-2028` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0182` `src/tests/client/test-client.check-on-disk/test_004.expected` old `4580-4591` new `4588-4599` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0183` `src/tests/client/test-client.check-on-disk/test_004.expected` old `4716-4721` new `4724-4730` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0184` `src/tests/client/test-client.check-on-disk/test_004.expected` old `4727-4738` new `4736-4747` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0185` `src/tests/client/test-client.check-on-disk/test_004.expected` old `4863-4868` new `4872-4878` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0186` `src/tests/client/test-client.check-on-disk/test_004.expected` old `4874-4885` new `4884-4895` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0187` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5010-5015` new `5020-5026` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0188` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5021-5032` new `5032-5043` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0189` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5157-5162` new `5168-5174` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0190` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5450-5461` new `5462-5473` symbol `size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0191` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5469-5483` new `5481-5496` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0192` `src/tests/client/test-client.check-on-disk/test_004.expected` old `5491-5496` new `5504-5510` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0193` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8056-8067` new `8070-8081` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0194` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8203-8208` new `8217-8223` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0195` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8216-8227` new `8231-8242` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0196` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8363-8368` new `8378-8384` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0197` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8376-8387` new `8392-8403` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0198` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8523-8528` new `8539-8545` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0199` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8536-8547` new `8553-8564` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0200` `src/tests/client/test-client.check-on-disk/test_004.expected` old `8683-8688` new `8700-8706` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0201` `src/tests/client/test-client.check-on-disk/test_004.expected` old `9002-9013` new `9020-9031` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0202` `src/tests/client/test-client.check-on-disk/test_004.expected` old `9024-9039` new `9042-9058` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0203` `src/tests/client/test-client.check-on-disk/test_004.expected` old `9050-9055` new `9069-9075` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0204` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12204-12215` new `12224-12235` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0205` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12351-12356` new `12371-12377` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0206` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12364-12375` new `12385-12396` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0207` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12511-12516` new `12532-12538` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0208` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12524-12535` new `12546-12557` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0209` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12671-12676` new `12693-12699` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0210` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12684-12695` new `12707-12718` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0211` `src/tests/client/test-client.check-on-disk/test_004.expected` old `12831-12836` new `12854-12860` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0212` `src/tests/client/test-client.check-on-disk/test_004.expected` old `13150-13161` new `13174-13185` symbol `size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0213` `src/tests/client/test-client.check-on-disk/test_004.expected` old `13172-13187` new `13196-13212` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0214` `src/tests/client/test-client.check-on-disk/test_004.expected` old `13198-13203` new `13223-13229` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0215` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16352-16363` new `16378-16389` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0216` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16488-16493` new `16514-16520` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0217` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16499-16510` new `16526-16537` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0218` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16635-16640` new `16662-16668` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0219` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16646-16657` new `16674-16685` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0220` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16782-16787` new `16810-16816` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0221` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16793-16804` new `16822-16833` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0222` `src/tests/client/test-client.check-on-disk/test_004.expected` old `16929-16934` new `16958-16964` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0223` `src/tests/client/test-client.check-on-disk/test_004.expected` old `17222-17233` new `17252-17263` symbol `size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0224` `src/tests/client/test-client.check-on-disk/test_004.expected` old `17241-17255` new `17271-17286` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0225` `src/tests/client/test-client.check-on-disk/test_004.expected` old `17263-17268` new `17294-17300` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0226` `src/tests/client/test-client.check-on-disk/test_004.expected` old `19798-19809` new `19830-19841` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0227` `src/tests/client/test-client.check-on-disk/test_004.expected` old `19934-19939` new `19966-19972` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0228` `src/tests/client/test-client.check-on-disk/test_004.expected` old `19945-19956` new `19978-19989` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0229` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20081-20086` new `20114-20120` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0230` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20092-20103` new `20126-20137` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0231` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20228-20233` new `20262-20268` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0232` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20239-20250` new `20274-20285` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0233` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20375-20380` new `20410-20416` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0234` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20668-20679` new `20704-20715` symbol `size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0235` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20687-20701` new `20723-20738` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0236` `src/tests/client/test-client.check-on-disk/test_004.expected` old `20709-20714` new `20746-20752` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0237` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23244-23255` new `23282-23293` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0238` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23266-23284` new `23304-23322` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0239` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23295-23313` new `23333-23351` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0240` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23324-23342` new `23362-23380` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0241` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23353-23360` new `23391-23398` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0242` `src/tests/client/test-client.check-on-disk/test_004.expected` old `23430-23455` new `23468-23493` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0243` `src/tests/client/test-client.check-on-disk/test_004.expected` old `24898-24909` new `24936-24947` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0244` `src/tests/client/test-client.check-on-disk/test_004.expected` old `24920-24938` new `24958-24976` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0245` `src/tests/client/test-client.check-on-disk/test_004.expected` old `24949-24967` new `24987-25005` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0246` `src/tests/client/test-client.check-on-disk/test_004.expected` old `24978-24996` new `25016-25034` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0247` `src/tests/client/test-client.check-on-disk/test_004.expected` old `25007-25014` new `25045-25052` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0248` `src/tests/client/test-client.check-on-disk/test_004.expected` old `25084-25109` new `25122-25147` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0249` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26552-26563` new `26590-26601` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0250` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26585-26605` new `26623-26643` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0251` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26627-26647` new `26665-26685` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0252` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26669-26689` new `26707-26727` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0253` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26711-26719` new `26749-26757` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0254` `src/tests/client/test-client.check-on-disk/test_004.expected` old `26814-26847` new `26852-26885` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0255` `src/tests/client/test-client.check-on-disk/test_004.expected` old `28860-28871` new `28898-28909` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0256` `src/tests/client/test-client.check-on-disk/test_004.expected` old `28893-28913` new `28931-28951` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0257` `src/tests/client/test-client.check-on-disk/test_004.expected` old `28935-28955` new `28973-28993` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0258` `src/tests/client/test-client.check-on-disk/test_004.expected` old `28977-28997` new `29015-29035` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0259` `src/tests/client/test-client.check-on-disk/test_004.expected` old `29019-29027` new `29057-29065` symbol `GROUP, NAME, UUID, DEVICES, IP, IFACE` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0260` `src/tests/client/test-client.check-on-disk/test_004.expected` old `29122-29155` new `29160-29193` symbol `size, stdout, bytes, GROUP, NAME, UUID` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0261` `src/tests/client/test-client.check-on-disk/test_004.expected` old `31168-31234` new `31206-31272` symbol `size, stdout, bytes, GENERAL, con, vpn` surface `tests, config, dbus_api`
- `HUNK-0262` `src/tests/client/test-client.check-on-disk/test_004.expected` old `31280-31303` new `31318-31341` symbol `size, stdout, bytes, GENERAL, con, vpn` surface `tests, config, dbus_api`
- `HUNK-0263` `src/tests/client/test-client.check-on-disk/test_004.expected` old `32106-32172` new `32144-32210` symbol `size, stdout, bytes, GENERAL, con, vpn` surface `tests, config, dbus_api`
- `HUNK-0264` `src/tests/client/test-client.check-on-disk/test_004.expected` old `32218-32241` new `32256-32279` symbol `size, stdout, bytes, GENERAL, con, vpn` surface `tests, config, dbus_api`
- `HUNK-0265` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33044-33055` new `33082-33093` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0266` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33180-33185` new `33218-33224` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0267` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33191-33202` new `33230-33241` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0268` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33327-33332` new `33366-33372` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0269` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33338-33349` new `33378-33389` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0270` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33474-33479` new `33514-33520` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0271` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33485-33496` new `33526-33537` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0272` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33621-33626` new `33662-33668` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0273` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33914-33925` new `33956-33967` symbol `size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0274` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33933-33947` new `33975-33990` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0275` `src/tests/client/test-client.check-on-disk/test_004.expected` old `33955-33960` new `33998-34004` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0276` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37050-37061` new `37094-37105` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0277` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37186-37191` new `37230-37236` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0278` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37197-37208` new `37242-37253` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0279` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37333-37338` new `37378-37384` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0280` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37344-37355` new `37390-37401` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0281` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37480-37485` new `37526-37532` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0282` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37491-37502` new `37538-37549` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0283` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37627-37632` new `37674-37680` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0284` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37920-37931` new `37968-37979` symbol `size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0285` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37939-37953` new `37987-38002` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, dbus_api`
- `HUNK-0286` `src/tests/client/test-client.check-on-disk/test_004.expected` old `37961-37966` new `38010-38016` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0287` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41056-41067` new `41106-41117` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0288` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41203-41208` new `41253-41259` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0289` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41216-41227` new `41267-41278` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0290` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41363-41368` new `41414-41420` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0291` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41376-41387` new `41428-41439` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0292` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41523-41528` new `41575-41581` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0293` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41536-41547` new `41589-41600` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0294` `src/tests/client/test-client.check-on-disk/test_004.expected` old `41683-41688` new `41736-41742` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0295` `src/tests/client/test-client.check-on-disk/test_004.expected` old `42002-42013` new `42056-42067` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0296` `src/tests/client/test-client.check-on-disk/test_004.expected` old `42024-42039` new `42078-42094` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0297` `src/tests/client/test-client.check-on-disk/test_004.expected` old `42050-42055` new `42105-42111` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0298` `src/tests/client/test-client.check-on-disk/test_004.expected` old `45764-45775` new `45820-45831` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0299` `src/tests/client/test-client.check-on-disk/test_004.expected` old `45911-45916` new `45967-45973` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0300` `src/tests/client/test-client.check-on-disk/test_004.expected` old `45924-45935` new `45981-45992` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0301` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46071-46076` new `46128-46134` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0302` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46084-46095` new `46142-46153` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0303` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46231-46236` new `46289-46295` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0304` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46244-46255` new `46303-46314` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0305` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46391-46396` new `46450-46456` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0306` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46710-46721` new `46770-46781` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0307` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46732-46747` new `46792-46808` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, config, dbus_api`
- `HUNK-0308` `src/tests/client/test-client.check-on-disk/test_004.expected` old `46758-46763` new `46819-46825` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, dbus_api`
- `HUNK-0309` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50472-50483` new `50534-50545` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0310` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50608-50613` new `50670-50676` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0311` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50619-50630` new `50682-50693` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0312` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50755-50760` new `50818-50824` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0313` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50766-50777` new `50830-50841` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0314` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50902-50907` new `50966-50972` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0315` `src/tests/client/test-client.check-on-disk/test_004.expected` old `50913-50924` new `50978-50989` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0316` `src/tests/client/test-client.check-on-disk/test_004.expected` old `51049-51054` new `51114-51120` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0317` `src/tests/client/test-client.check-on-disk/test_004.expected` old `51342-51353` new `51408-51419` symbol `size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0318` `src/tests/client/test-client.check-on-disk/test_004.expected` old `51361-51375` new `51427-51442` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0319` `src/tests/client/test-client.check-on-disk/test_004.expected` old `51383-51388` new `51450-51456` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`
- `HUNK-0320` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54478-54489` new `54546-54557` symbol `size, stdout, bytes` surface `tests, config`
- `HUNK-0321` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54614-54619` new `54682-54688` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0322` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54625-54636` new `54694-54705` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0323` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54761-54766` new `54830-54836` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0324` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54772-54783` new `54842-54853` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0325` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54908-54913` new `54978-54984` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0326` `src/tests/client/test-client.check-on-disk/test_004.expected` old `54919-54930` new `54990-55001` symbol `size, stdout, bytes` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0327` `src/tests/client/test-client.check-on-disk/test_004.expected` old `55055-55060` new `55126-55132` symbol `GENERAL, CONTROLLER, PATH` surface `tests, config, persistence_state, dbus_api`
- `HUNK-0328` `src/tests/client/test-client.check-on-disk/test_004.expected` old `55348-55359` new `55420-55431` symbol `size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0329` `src/tests/client/test-client.check-on-disk/test_004.expected` old `55367-55381` new `55439-55454` symbol `GENERAL, CONTROLLER, PATH, size, stdout, bytes` surface `tests, persistence_state, dbus_api`
- `HUNK-0330` `src/tests/client/test-client.check-on-disk/test_004.expected` old `55389-55394` new `55462-55468` symbol `GENERAL, CONTROLLER, PATH` surface `tests, dbus_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis.json`
