# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/openldap`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/_worktrees/patched`
- Patch ID: `f6ae8ef451f38e3f2f3ec6fc43cc8806ecfe125a`
- Base ref: `HEAD`
- Base commit: `595e7ea6f36d5352af5a60eccef64c5cb3357fb2`
- Patch apply status: `already_applied`
- Profile: `openldap`
- Effective profile: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 7
- Candidate hunks: 13
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 8660 |
| `patch_lines` | 269 |
| `raw_hunks` | 16 |
| `candidate_hunks` | 13 |
| `changed_files` | 7 |
| `churn` | 91 |
| `candidate_context_bytes` | 25771 |
| `candidates_json_bytes` | 76810 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/openldap show 595e7ea6f36d5352af5a60eccef64c5cb3357fb2:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis.json`.

## Candidate Hunks

- `HUNK-0004` `servers/lloadd/config.c` old `77-85` new `77-87` symbol `lload_features_t, lload_features, LLOAD_FEATURES_DEFAULT, features_requested, features_disabled` surface `proc_sys_consumers, config_keys, network_protocol, libldap_api, protocol_behavior, config_schema`
- `HUNK-0005` `servers/lloadd/config.c` old `158-163` new `160-167` symbol `CFG_FEATURE_ENABLE, CFG_FEATURE_DISABLE, fp_getline_init` surface `ioctl_netlink_consumers, config_keys, ioctl_netlink, protocol_behavior, config_schema`
- `HUNK-0006` `servers/lloadd/config.c` old `394-406` new `398-425` symbol `NULL, enable, name, ARG_MAGIC, CFG_FEATURE_ENABLE, config_feature, fp_getline_init` surface `config_keys, config_schema`
- `HUNK-0007` `servers/lloadd/config.c` old `818-824` new `837-844` symbol `MAY, olcBkLloadFeatureEnable, olcBkLloadFeatureDisable, olcBkLloadFeature, fp_getline_init` surface `config_keys, config_schema`
- `HUNK-0008` `servers/lloadd/config.c` old `2092-2102` new `2112-2135` symbol `config_feature, lload_features_t, fp, c, type, CFG_FEATURE, mask_to_verbs` surface `config_keys, network_protocol, libldap_api, config_schema`
- `HUNK-0009` `servers/lloadd/config.c` old `2109-2119` new `2142-2154` symbol `config_feature, fp, features, i, mask, lload_features, mask_to_verbs` surface `config_keys, user_visible_output, network_protocol, libldap_api, config_schema`
- `HUNK-0010` `servers/lloadd/config.c` old `2136-2142` new `2171-2193` symbol `config_feature, features_requested, features_disabled, lload_features_t, overlap, i, Debug` surface `cli_options, config_keys, user_visible_output, network_protocol, libldap_api, config_schema`
- `HUNK-0011` `servers/lloadd/lload.h` old `184-189` new `184-193` symbol `define, LLOAD_FEATURES_DEFAULT, LLOAD_FEATURE_PROXYAUTHZ, lload_cf_aux_table_parse_x` surface `public_headers, daemon_control, libldap_api`
- `HUNK-0012` `tests/data/lloadd-anon.conf` old `17-22` new `17-25` symbol `we, re, anonymous, and, want, to` surface `tests, config_files, config_keys, config, protocol_behavior, config_schema`
- `HUNK-0013` `tests/data/lloadd-empty.conf` old `17-23` new `17-23` symbol `enable, proxyauthz, feature` surface `tests, config_files, config_keys, config, protocol_behavior, config_schema`
- `HUNK-0014` `tests/data/lloadd-sasl.conf` old `17-23` new `17-23` symbol `enable, proxyauthz, feature` surface `tests, config_files, config_keys, config, protocol_behavior, config_schema`
- `HUNK-0015` `tests/data/lloadd-tls.conf` old `26-32` new `26-32` symbol `enable, proxyauthz, feature` surface `tests, config_files, config_keys, config, protocol_behavior, config_schema`
- `HUNK-0016` `tests/data/lloadd.conf` old `17-23` new `17-23` symbol `enable, proxyauthz, feature` surface `tests, config_files, config_keys, config, protocol_behavior, config_schema`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis.json`
