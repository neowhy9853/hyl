# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P072/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P072/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P072/compatibility-testing`
- Patch ID: `21491b21577c68858b3cc02c21e3db88f0a30bb1`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `SSLVHostSNIPolicy`
- Target: `modules/ssl/mod_ssl.c:95-102` `ssl_config_cmds`
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
- API: `exported_function` `ssl_config_global_create`
- Target: `modules/ssl/ssl_engine_config.c:60-68` `snivh_policy`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `daemon_handler` `ssl_hook_ReadReq`
- Target: `modules/ssl/ssl_engine_kernel.c:195-250` `ssl_hook_ReadReq`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

