# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Analysis repo: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/e671f8/compatibility-testing`
- Patch ID: `e671f885037435884f070493be753eb021e26e79`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `exported_function` `sd_notify(READY=1) via main() in rsyslogd.c`
- Target: `tools/rsyslogd.c:2666-2682` `main`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

