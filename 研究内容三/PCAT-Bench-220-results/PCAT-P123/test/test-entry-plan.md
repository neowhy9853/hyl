# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P063/analysis.json`
- Repo: `/data7/wanghy/tmp/opencode/grub2`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P063/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P063/compatibility-testing`
- Patch ID: `8811797b13b31605fd02155e44c7299bfee2ab4a`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `cli_command` `grub_script_function_create`
- Target: `grub-core/script/function.c:61-79` `grub_script_function_create`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `exported_function` `grub_script_function_create`
- Target: `grub-core/script/function.c:61-79` `grub_script_function_create`
- Entry kind: `return_value_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

