# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/git`
- Analysis repo: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing`
- Patch ID: `42d960748efa79a31e72cc36d983aca244dc167e`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `git log -L`
- Target: `line-log.c:1003-1020` `line_log_queue_pairs`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `git log -L --full-diff`
- Target: `revision.c:3179-3188` `setup_revisions`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `git log -L with -S/-G/--find-object/--diff-filter`
- Target: `log-tree.c:1185-1190` `log_tree_commit`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

