# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/_worktrees/patched`
- Patch ID: `96cab112a257`
- Base ref: `HEAD`
- Base commit: `4b63ae29a5c030c9a5cd199b546da3d7a1331827`
- Patch apply status: `already_applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5677 |
| `patch_lines` | 108 |
| `raw_hunks` | 7 |
| `candidate_hunks` | 7 |
| `changed_files` | 3 |
| `churn` | 41 |
| `candidate_context_bytes` | 16470 |
| `candidates_json_bytes` | 44233 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show 4b63ae29a5c030c9a5cd199b546da3d7a1331827:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/core/ndisc/nm-lndp-ndisc.c` old `487-493` new `487-494` symbol `send_ra, nm_auto_str_buf, NMStrBuf, sbuf, NM_STR_BUF_INIT, FALSE` surface `cli_options, user_visible_output, logging, dbus_api`
- `HUNK-0002` `src/core/ndisc/nm-lndp-ndisc.c` old `531-543` new `532-540` symbol `send_ra, htonl, _nm_ndisc_lifetime_from_expiry, now_msec, address, expiry_msec, _LOG_INVALID_RA` surface `cli_options, user_visible_output, logging, dbus_api`
- `HUNK-0003` `src/core/ndisc/nm-ndisc.c` old `1124-1130` new `1124-1131` symbol `nm_ndisc_set_config, gint64, now_msec, nm_utils_get_monotonic_timestamp_msec, gint32, now` surface `config_keys, config, dbus_api`
- `HUNK-0004` `src/core/ndisc/nm-ndisc.c` old `1147-1162` new `1148-1162` symbol `nm_ndisc_set_config, now, address, addr, expiry_msec, _nm_ndisc_lifetime_to_expiry, nm_l3_config_data_iter_obj_for_each` surface `config_keys, config, dbus_api`
- `HUNK-0005` `src/core/ndisc/nm-ndisc.c` old `1176-1183` new `1176-1182` symbol `nm_ndisc_set_config, expiry_msec, _nm_ndisc_lifetime_to_expiry, now_msec, NM_NDISC_ROUTER_LIFETIME, NM_NDISC_EXPIRY_BASE_TIMESTAMP, nm_l3_config_data_iter_obj_for_each` surface `cli_options, config_keys, cli, config, dbus_api`
- `HUNK-0006` `src/core/ndisc/nm-ndisc.c` old `1192-1199` new `1191-1197` symbol `nm_ndisc_set_config, expiry_msec, _nm_ndisc_lifetime_to_expiry, now_msec, NM_NDISC_ROUTER_LIFETIME, NM_NDISC_EXPIRY_BASE_TIMESTAMP, nm_l3_config_data_iter_obj_for_each` surface `cli_options, config_keys, cli, config, dbus_api`
- `HUNK-0007` `src/core/ndisc/nm-ndisc.h` old `50-67` new `50-55` symbol `nm_ndisc_dhcp_level_to_string, in, common, cases, the, expiry_msec, MIN` surface `public_headers, config_keys, config, dbus_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis.json`
