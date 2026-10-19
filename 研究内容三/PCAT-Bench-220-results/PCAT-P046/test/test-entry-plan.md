# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Analysis repo: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing`
- Patch ID: `ff1d43509608cfe41a7c4c4dc8285a1de5bb1824`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `nmc_fields_dev_show_controller_prop / nmc_fields_dev_show_team_prop`
- Target: `src/nmcli/devices.c:766-784` `print_bond_bridge_info`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `_metagen_con_active_general_get_fcn`
- Target: `src/nmcli/connections.c:920-926` `_metagen_con_active_general_get_fcn`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

