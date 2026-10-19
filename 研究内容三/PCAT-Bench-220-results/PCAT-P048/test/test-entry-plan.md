# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Analysis repo: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing`
- Patch ID: `921fe6ec68a1cffc18a81752f996578831702ad7`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `NMSettingBond:arp_missed_max default`
- Target: `src/libnm-core-impl/nm-setting-bond.c:200-200` `arp_missed_max`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `_bond_get_option_normalized: arp_missed_max zero-to-default mapping`
- Target: `src/libnm-core-impl/nm-setting-bond.c:364-373` `_bond_get_option_normalized`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `config_key` `verify(): arp_missed_max mode compatibility check`
- Target: `src/libnm-core-impl/nm-setting-bond.c:957-974` `verify`
- Entry kind: `input_boundary_harness`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

