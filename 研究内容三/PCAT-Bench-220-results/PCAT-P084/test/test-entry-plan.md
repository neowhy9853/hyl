# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P024/compatibility-testing`
- Patch ID: `7f8fc07e850d7b27a220c815db8c8abd545286c3`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `asyncio REPL PYTHONSTARTUP handling`
- Target: `Lib/asyncio/__main__.py:99-105` `REPLThread.run`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `cli_command` `asyncio REPL PYTHON_BASIC_REPL handling`
- Target: `Lib/asyncio/__main__.py:200-206` `main`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

