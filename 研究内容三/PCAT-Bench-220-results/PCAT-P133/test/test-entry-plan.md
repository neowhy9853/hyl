# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P073/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P073/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P073/compatibility-testing`
- Patch ID: `f02c7a9b8ac443daafac8e7be5828b4010fb46d8`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `DAVLockDiscovery`
- Target: `modules/dav/main/mod_dav.c:306-329` `dav_cmd_davlockdiscovery`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

