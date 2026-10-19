# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/openldap`
- Analysis repo: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/compatibility-testing`
- Patch ID: `pca_openldap_60458c`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `olcDbPageSize`
- Target: `servers/slapd/back-mdb/config.c:71-88` `mdbcfg`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `exported_function` `mdb_db_open`
- Target: `servers/slapd/back-mdb/init.c:126-142` `mdb_db_open`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

