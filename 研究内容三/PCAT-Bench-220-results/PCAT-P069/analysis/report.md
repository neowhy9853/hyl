# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/_worktrees/patched`
- Patch ID: `e671f885037435884f070493be753eb021e26e79`
- Base ref: `HEAD`
- Base commit: `f9f5b3ca41d64d8e48a5c7e6b98c72339a7f7547`
- Patch apply status: `already_applied`
- Profile: `rsyslog`
- Effective profile: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; candidates_json_bytes=112341 >= 100000
- Changed files: 8
- Candidate hunks: 14
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 14740 |
| `patch_lines` | 362 |
| `raw_hunks` | 15 |
| `candidate_hunks` | 14 |
| `changed_files` | 8 |
| `churn` | 191 |
| `candidate_context_bytes` | 41613 |
| `candidates_json_bytes` | 112341 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/shards`
- Shard count: 7

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `cli_options` | 1 | 1 | 1863 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 2 | 1 | 6335 | `shards/shard-0002.json` |
| `SHARD-0003` | `environment_variables` | 1 | 1 | 5083 | `shards/shard-0003.json` |
| `SHARD-0004` | `ioctl_netlink_consumers` | 1 | 1 | 2095 | `shards/shard-0004.json` |
| `SHARD-0005` | `public_headers` | 2 | 1 | 5526 | `shards/shard-0005.json` |
| `SHARD-0006` | `syscall_wrappers` | 3 | 1 | 15246 | `shards/shard-0006.json` |
| `SHARD-0007` | `tests` | 4 | 3 | 5465 | `shards/shard-0007.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/rsyslog show f9f5b3ca41d64d8e48a5c7e6b98c72339a7f7547:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `plugins/imfile/imfile.c` old `2909-2915` new `2909-2918` symbol `do_inotify, ino_fd, close, in_processEvent` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api, module_api, config_language, daemon_interfaces`
- `HUNK-0003` `runtime/glbl.c` old `173-178` new `173-179` symbol `cnfparamdescr, systemd, notifyreadydelay, eCmdHdlrBinary` surface `config_keys, user_visible_output, logging, network_protocol, persistence_state, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0004` `runtime/glbl.c` old `1175-1180` new `1176-1182` symbol `resetConfigVariables, loadConf, globals, systemdNotifyReadyDelay, free` surface `config_keys, module_api, config_language, daemon_interfaces`
- `HUNK-0005` `runtime/glbl.c` old `1553-1558` new `1555-1562` symbol `glblDoneLoadCnf, strcmp, paramblk, descr, i, name, SetOptionDisallowWarning` surface `environment_variables, config_keys, user_visible_output, env_vars, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0006` `runtime/rsconf.c` old `90-111` new `90-153` symbol `loaded, then, rsconfSignalReady, once, initialised, When, rsconfWaitForModulesReady, DEFobjCurrIf` surface `syscall_wrappers, config_keys, user_visible_output, logging, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0007` `runtime/rsconf.c` old `114-120` new `156-175` symbol `rsconfSignalReady, pthread_once, onceModulesReadyCond, initModulesReadyCond, pthread_mutex_lock, mutModulesReady, pthread_mutex_unlock, LogError` surface `syscall_wrappers, config_keys, user_visible_output, logging, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0008` `runtime/rsconf.c` old `132-137` new `187-200` symbol `rsconfWaitForModulesReady, bModulesReadyWaitActive, pthread_mutex_unlock, mutModulesReady, rsconfReadyNotifySent, pthread_once, initModulesReadyCond, pthread_mutex_lock, LogError` surface `syscall_wrappers, user_visible_output, logging, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0009` `runtime/rsconf.h` old `113-118` new `113-119` symbol `globals_s, systemdNotifyReadyDelay, delay, sd_notify, READY, until, once` surface `public_headers, config_keys, user_visible_output, logging, network_protocol, module_api, config_language, output_format, daemon_interfaces`
- `HUNK-0010` `runtime/rsconf.h` old `320-325` new `321-328` symbol `rsconfNeedDropPriv, rsconfReadyNotifySent, rsconfShouldDelayReadyNotify, rsconf_t, cnf, rsconfRegisterReadiness` surface `public_headers, config_keys, user_visible_output, logging, module_api, config_language, daemon_interfaces`
- `HUNK-0011` `tests/Makefile.am` old `328-333` new `328-334` symbol `global, systemd, notifyreadydelay, rainerscript, sh` surface `tests, config_keys, user_visible_output, config_language, output_format, daemon_interfaces`
- `HUNK-0012` `tests/Makefile.am` old `654-659` new `655-661` symbol `global, systemd, notifyreadydelay, yaml, sh` surface `tests, config_keys, persistence_state, config_language, output_format, daemon_interfaces`
- `HUNK-0013` `tests/global-systemd-notifyreadydelay-rainerscript.sh` old `0--1` new `1-34` symbol `bin, bash, Validate, the, global, systemd` surface `tests, config_keys, user_visible_output, logging, config_language, daemon_interfaces`
- `HUNK-0014` `tests/global-systemd-notifyreadydelay-yaml.sh` old `0--1` new `1-44` symbol `bin, bash, Validate, YAML, parity, global` surface `tests, config_keys, user_visible_output, logging, config_language, daemon_interfaces`
- `HUNK-0015` `tools/rsyslogd.c` old `2666-2677` new `2666-2682` symbol `main, rsconfShouldDelayReadyNotify, runConf, rsconfWaitForModulesReady, rsconfReadyNotifySent, initAll` surface `cli_options, user_visible_output, cli, logging, daemon_interfaces`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis.json`
