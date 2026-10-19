# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P068/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P068/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P068/compatibility-testing`
- Patch ID: `2d8a447551125cb0f1efb4781a58afa9ab77c392`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `RewriteRule directive, cmd_rewriterule`
- Target: `modules/mappers/mod_rewrite.c:3909-3920` `cmd_rewriterule`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

