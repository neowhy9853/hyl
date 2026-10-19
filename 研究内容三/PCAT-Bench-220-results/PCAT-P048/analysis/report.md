# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/_worktrees/patched`
- Patch ID: `921fe6ec68a1cffc18a81752f996578831702ad7`
- Base ref: `HEAD`
- Base commit: `4b63ae29a5c030c9a5cd199b546da3d7a1331827`
- Patch apply status: `already_applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; candidates_json_bytes=101492 >= 100000
- Changed files: 6
- Candidate hunks: 16
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 11343 |
| `patch_lines` | 212 |
| `raw_hunks` | 16 |
| `candidate_hunks` | 16 |
| `changed_files` | 6 |
| `churn` | 56 |
| `candidate_context_bytes` | 48518 |
| `candidates_json_bytes` | 101492 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/shards`
- Shard count: 8

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 1 | 1 | 3508 | `shards/shard-0001.json` |
| `SHARD-0002` | `internal_or_unknown` | 1 | 1 | 2723 | `shards/shard-0002.json` |
| `SHARD-0003` | `network_protocol` | 3 | 1 | 7832 | `shards/shard-0003.json` |
| `SHARD-0004` | `public_headers` | 1 | 1 | 2060 | `shards/shard-0004.json` |
| `SHARD-0005` | `syscall_wrappers` | 4 | 4 | 14593 | `shards/shard-0005.json` |
| `SHARD-0006` | `syscall_wrappers` | 1 | 1 | 3136 | `shards/shard-0006.json` |
| `SHARD-0007` | `user_visible_output` | 3 | 2 | 8889 | `shards/shard-0007.json` |
| `SHARD-0008` | `user_visible_output` | 2 | 1 | 5777 | `shards/shard-0008.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show 4b63ae29a5c030c9a5cd199b546da3d7a1331827:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/core/devices/nm-device-bond.c` old `52-62` new `52-63` symbol `NM_SETTING_BOND_OPTION_PEER_NOTIF_DELAY, define, OPTIONS_REAPPLY_FULL, OPTIONS_REAPPLY_SUBSET, NM_SETTING_BOND_OPTION_ACTIVE_SLAVE, NM_SETTING_BOND_OPTION_ARP_IP_TARGET, Copyright` surface `syscall_wrappers, user_visible_output, config, logging, dbus_api`
- `HUNK-0002` `src/core/devices/nm-device-bond.c` old `501-506` new `502-509` symbol `_platform_lnk_bond_init_from_setting, props, arp_missed_max_has, NM_IN_SET, mode, NM_BOND_MODE_TLB, _bond_ns_ip6_target_to_platform` surface `callbacks, config_keys, config, persistence_state, dbus_api`
- `HUNK-0003` `src/core/devices/nm-device-bond.c` old `907-912` new `910-917` symbol `reapply_connection, NM_IN_SET, mode, NM_BOND_MODE_TLB, NM_BOND_MODE_ALB, NM_BOND_MODE_8023AD, set_bond_attr_or_default, set_bond_arp_ip_targets` surface `user_visible_output, config, dbus_api`
- `HUNK-0004` `src/libnm-core-impl/nm-setting-bond.c` old `197-203` new `197-203` symbol `NM_UTILS_STRING_TABLE_LOOKUP_STRUCT_DEFINE, NM_SETTING_BOND_OPTION_ARP_MISSED_MAX, NM_BOND_OPTION_TYPE_INT, nm_assert` surface `syscall_wrappers`
- `HUNK-0005` `src/libnm-core-impl/nm-setting-bond.c` old `364-369` new `364-373` symbol `_bond_get_option_normalized, nm_streq, option, NM_SETTING_BOND_OPTION_ARP_MISSED_MAX, value, _bond_get_option, _bond_get_option_default, _nm_utils_ascii_str_to_int64` surface `unknown`
- `HUNK-0006` `src/libnm-core-impl/nm-setting-bond.c` old `894-906` new `898-913` symbol `verify, is, an, invalid, value, in, g_prefix_error` surface `user_visible_output, config, persistence_state`
- `HUNK-0007` `src/libnm-core-impl/nm-setting-bond.c` old `950-955` new `957-965` symbol `verify, NM_IN_SET, bond_mode, NM_BOND_MODE_TLB, NM_BOND_MODE_ALB, NM_BOND_MODE_8023AD, g_prefix_error` surface `user_visible_output, config`
- `HUNK-0008` `src/libnm-core-impl/tests/test-setting.c` old `5533-5539` new `5533-5539` symbol `test_bond_meta, _A, _nm_setting_bond_opt_value_as_u8, set, NM_SETTING_BOND_OPTION_ARP_MISSED_MAX` surface `syscall_wrappers, user_visible_output, config`
- `HUNK-0009` `src/libnm-platform/nm-linux-platform.c` old `1766-1773` new `1766-1777` symbol `nlattr, tb, IFLA_BOND_MISSED_MAX, props, arp_missed_max, nla_get_u8, nla_for_each_nested` surface `syscall_wrappers, ioctl_netlink_consumers, ioctl_netlink, network_protocol`
- `HUNK-0010` `src/libnm-platform/nm-linux-platform.c` old `5126-5132` new `5130-5136` symbol `nl_msg, props, arp_missed_max_has, arp_missed_max, NLA_PUT` surface `syscall_wrappers, network_protocol`
- `HUNK-0011` `src/libnm-platform/nm-platform.c` old `6373-6378` new `6373-6379` symbol `nm_platform_lnk_bond_to_string, sbuf_arp_missed_max` surface `network_protocol`
- `HUNK-0012` `src/libnm-platform/nm-platform.c` old `6403-6409` new `6404-6410` symbol `nm_platform_lnk_bond_to_string, s, arp_missed_max, u, nm_strbuf_append` surface `user_visible_output, network_protocol`
- `HUNK-0013` `src/libnm-platform/nm-platform.c` old `6455-6461` new `6456-6467` symbol `nm_platform_lnk_bond_to_string, lnk, arp_missed_max_has, arp_missed_max, nm_sprintf_buf, sbuf_arp_missed_max, NM_ETHER_ADDR_FORMAT_VAL` surface `user_visible_output, network_protocol`
- `HUNK-0014` `src/libnm-platform/nm-platform.c` old `8388-8394` new `8394-8401` symbol `nm_platform_lnk_bond_hash_update, obj, use_carrier, arp_missed_max_has, nm_hash_update_vals` surface `network_protocol`
- `HUNK-0015` `src/libnm-platform/nm-platform.c` old `8466-8471` new `8473-8479` symbol `nm_platform_lnk_bond_cmp, NM_CMP_FIELD_BOOL, a, b, arp_missed_max_has` surface `network_protocol, persistence_state`
- `HUNK-0016` `src/libnm-platform/nm-platform.h` old `840-845` new `840-846` symbol `arp_missed_max_has, int` surface `public_headers, network_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis.json`
