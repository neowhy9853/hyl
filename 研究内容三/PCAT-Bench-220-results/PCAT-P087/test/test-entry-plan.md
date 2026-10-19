# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P027/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P027/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P027/compatibility-testing`
- Patch ID: `5235467b9183a8be8675aed17bd5b5a993975da7`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `inspect module CLI --details output`
- Target: `Lib/inspect.py:3475-3490` `_main`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `inspect module CLI --details flag behavior`
- Target: `Lib/inspect.py:3478-3485` `_main`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

