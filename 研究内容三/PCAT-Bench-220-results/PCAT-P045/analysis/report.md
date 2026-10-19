# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/_worktrees/patched`
- Patch ID: `f346fcf977c22f12b509fff3c674dbfb67490a38`
- Base ref: `f346fcf977c22f12b509fff3c674dbfb67490a38^`
- Base commit: `ec1522fa8c8997509624836b3625cdd237e23e69`
- Patch apply status: `applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; candidates_json_bytes=121242 >= 100000
- Changed files: 6
- Candidate hunks: 16
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 11256 |
| `patch_lines` | 244 |
| `raw_hunks` | 16 |
| `candidate_hunks` | 16 |
| `changed_files` | 6 |
| `churn` | 83 |
| `candidate_context_bytes` | 47352 |
| `candidates_json_bytes` | 121242 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/shards`
- Shard count: 6

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 3 | 1 | 10225 | `shards/shard-0001.json` |
| `SHARD-0002` | `callbacks` | 3 | 2 | 8438 | `shards/shard-0002.json` |
| `SHARD-0003` | `config` | 1 | 1 | 5061 | `shards/shard-0003.json` |
| `SHARD-0004` | `config_keys` | 5 | 3 | 13436 | `shards/shard-0004.json` |
| `SHARD-0005` | `public_headers` | 2 | 2 | 5690 | `shards/shard-0005.json` |
| `SHARD-0006` | `user_visible_output` | 2 | 2 | 4502 | `shards/shard-0006.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show ec1522fa8c8997509624836b3625cdd237e23e69:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `introspection/org.freedesktop.NetworkManager.Device.xml` old `396-402` new `396-402` symbol `managed, link, linkend, NMDeviceManaged, Whether, the` surface `config_keys, user_visible_output, config, persistence_state, dbus_api`
- `HUNK-0002` `introspection/org.freedesktop.NetworkManager.Device.xml` old `404-410` new `404-410` symbol `arg, name, managed, type, u, direction` surface `user_visible_output, config, persistence_state, dbus_api`
- `HUNK-0003` `src/core/devices/nm-device.c` old `14941-14947` new `14941-14947` symbol `impl_device_get_applied_connection, NMDeviceManaged, managed_state, gboolean, nm_active_connection_version_id_get` surface `user_visible_output, config, network_protocol, daemon_control, persistence_state, dbus_api`
- `HUNK-0004` `src/core/devices/nm-device.c` old `14959-14969` new `14959-14971` symbol `set_managed, NMDevice, self, NMDeviceManaged, managed, NMDeviceManagedFlags, nm_active_connection_version_id_get` surface `config_keys, user_visible_output, config, network_protocol, daemon_control, persistence_state, dbus_api`
- `HUNK-0005` `src/core/devices/nm-device.c` old `14975-14985` new `14977-14988` symbol `set_managed, managed_to_disk, managed, NM_DEVICE_MANAGED_RESET, NM_TERNARY_DEFAULT, g_set_error_literal` surface `config_keys, user_visible_output, config, persistence_state, dbus_api`
- `HUNK-0006` `src/core/devices/nm-device.c` old `14987-14993` new `14990-14997` symbol `set_managed, managed_to_disk, NM_TERNARY_DEFAULT, nm_device_get_unmanaged_flags, self, NM_UNMANAGED_USER_CONF, nm_config_get_device_managed` surface `config_keys, user_visible_output, config, persistence_state, dbus_api`
- `HUNK-0007` `src/core/devices/nm-device.c` old `15008-15014` new `15012-15025` symbol `set_managed, managed, NM_DEVICE_MANAGED_RESET, nm_device_set_unmanaged_by_flags, self, NM_UNMANAGED_USER_EXPLICIT, g_object_set, g_set_error` surface `callbacks, config_keys, user_visible_output, config, persistence_state, dbus_api`
- `HUNK-0008` `src/core/devices/nm-device.c` old `15022-15028` new `15033-15039` symbol `set_managed_cb, NMDeviceManaged, managed, gboolean` surface `callbacks, config_keys, user_visible_output, config, logging, daemon_control, persistence_state, dbus_api`
- `HUNK-0009` `src/core/devices/nm-device.c` old `15030-15040` new `15041-15060` symbol `set_managed_cb, error, NM_IN_SET, managed, NM_DEVICE_MANAGED_NO, NM_DEVICE_MANAGED_YES, g_set_error_literal` surface `callbacks, config_keys, user_visible_output, config, logging, daemon_control, persistence_state, dbus_api`
- `HUNK-0010` `src/core/devices/nm-device.c` old `15074-15088` new `15094-15110` symbol `impl_device_set_managed, guint32, managed_u, NMDeviceManaged, managed, g_variant_get, nm_assert` surface `callbacks, user_visible_output, config, logging, network_protocol, daemon_control, persistence_state, dbus_api`
- `HUNK-0011` `src/core/devices/nm-device.c` old `20066-20072` new `20088-20094` symbol `NM_DEFINE_GDBUS_ARG_INFO, managed, u, b, NM_DEFINE_DBUS_METHOD_INFO_EXTENDED` surface `config, network_protocol, daemon_control, persistence_state, dbus_api`
- `HUNK-0012` `src/libnm-client-impl/libnm.ver` old `2115-2120` new `2115-2121` symbol `nm_device_managed_get_type` surface `config_keys, config, plugin_api, network_protocol`
- `HUNK-0013` `src/libnm-client-impl/nm-device.c` old `1485-1491` new `1485-1491` symbol `nm_device_set_managed, NMDeviceManaged, managed, gboolean, _nm_object_get_path` surface `callbacks, user_visible_output, config, plugin_api, daemon_control, persistence_state, dbus_api`
- `HUNK-0014` `src/libnm-client-impl/nm-device.c` old `1503-1509` new `1503-1509` symbol `nm_device_set_managed_async, g_variant_new, uu, managed, flags, bu, _nm_object_get_path` surface `callbacks, user_visible_output, config, plugin_api, daemon_control, persistence_state, dbus_api`
- `HUNK-0015` `src/libnm-client-public/nm-device.h` old `152-158` new `152-158` symbol `NMDeviceManaged, managed, gboolean, nm_device_set_managed` surface `public_headers, callbacks, config_keys, user_visible_output, config, plugin_api, persistence_state, libnm_api`
- `HUNK-0016` `src/libnm-core-public/nm-dbus-interface.h` old `1248-1253` new `1248-1269` symbol `NMDeviceManaged, NM_DEVICE_MANAGED_NO, the, device, is, not, to, nm_device_reapply_async` surface `public_headers, config_keys, config, persistence_state, libnm_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis.json`
