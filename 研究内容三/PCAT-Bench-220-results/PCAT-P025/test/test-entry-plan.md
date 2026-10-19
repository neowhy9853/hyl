# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/vim`
- Analysis repo: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/compatibility-testing`
- Patch ID: `5fdb44c438747d419a403110f3c2dd792f539497`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `term_start term_finish option`
- Target: `src/job.c:386-393` `get_job_options`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

