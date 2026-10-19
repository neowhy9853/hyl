# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnf`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/compatibility-testing`
- Patch ID: `017bbab0a253d84978f645cd358cdeb63e9ecb18`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `OptionParser._add_general_options`
- Target: `dnf/cli/option_parser.py:199-210` `OptionParser._add_general_options`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `Cli._read_conf_file`
- Target: `dnf/cli/cli.py:953-959` `Cli._read_conf_file`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `exported_function` `Cli._read_conf_file`
- Target: `dnf/cli/cli.py:981-1003` `Cli._read_conf_file`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

