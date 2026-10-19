# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/d33525/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/libxml2`
- Analysis repo: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/d33525/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/d33525/compatibility-testing`
- Patch ID: `d3352554e4c1f052b914cda7b415d06b7eab5dfa`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `xmllintMain --maxmem`
- Target: `xmllint.c:3075-3083` `xmllintMain`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

