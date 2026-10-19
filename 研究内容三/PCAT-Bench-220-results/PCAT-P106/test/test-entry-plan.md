# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P046/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P046/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P046/compatibility-testing`
- Patch ID: `a23d8e124fbd`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `sysfs_attribute` `bond_option_xmit_hash_policy_set`
- Target: `drivers/net/bonding/bond_options.c:1592-1599` `bond_option_xmit_hash_policy_set`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: shell command sequence or kselftest shell script
- Trigger surface: read/write the procfs/sysfs/sysctl node and assert output, errno, permission, or state transition
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

