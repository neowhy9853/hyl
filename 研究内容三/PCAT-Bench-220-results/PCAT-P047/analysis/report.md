# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/_worktrees/patched`
- Patch ID: `66dfb3c`
- Base ref: `66dfb3c728f33dc087a368ca5bded4f46c2275b3~1`
- Base commit: `c0691de32218bded6ca3e2279c484575da8cbf31`
- Patch apply status: `applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 4
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5770 |
| `patch_lines` | 143 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 4 |
| `churn` | 91 |
| `candidate_context_bytes` | 15641 |
| `candidates_json_bytes` | 37590 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show c0691de32218bded6ca3e2279c484575da8cbf31:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/core/devices/wifi/nm-device-wifi.c` old `2198-2218` new `2198-2213` symbol `supplicant_iface_wps_credentials_cb, psk, nm_wifi_utils_wps_key_to_psk, guint8, array, psk_len, g_variant_ref_sink, g_return_if_fail` surface `callbacks, user_visible_output, config, network_protocol, persistence_state, dbus_api`
- `HUNK-0002` `src/core/devices/wifi/nm-wifi-utils.c` old `890-895` new `890-917` symbol `nm_wifi_utils_is_manf_default_ssid, Convert, a, WPS, Key, credential` surface `config, dbus_api`
- `HUNK-0003` `src/core/devices/wifi/nm-wifi-utils.h` old `42-47` new `42-49` symbol `nm_wifi_utils_complete_connection, gboolean, nm_wifi_utils_wps_key_to_psk, guint8, key, gsize, nm_wifi_utils_is_manf_default_ssid` surface `public_headers, config_keys, user_visible_output, config, dbus_api`
- `HUNK-0004` `src/core/devices/wifi/tests/test-devices-wifi.c` old `1459-1464` new `1459-1508` symbol `test_ssids_options_to_ptrarray, test_wps_key_to_psk, key, gsize, key_len, gboolean, do_test_ssids_options_to_ptrarray` surface `user_visible_output, config, dbus_api`
- `HUNK-0005` `src/core/devices/wifi/tests/test-devices-wifi.c` old `1605-1609` new `1649-1655` symbol `main, g_test_add_func, wifi, wps_key_to_psk, test_wps_key_to_psk` surface `user_visible_output, config, dbus_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis.json`
