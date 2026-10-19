# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P070/compatibility-testing`
- Patch ID: `0d71da4bdfff4c18abcea77ffa76227f70be0f73`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `callback_type` `process_connection hook callback contract (Event MPM)`
- Target: `server/mpm/event/event.c:1114-1192` `process_socket`
- Entry kind: `return_value_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `exported_function` `h2_c1_run / h2_c1_hook_process_connection`
- Target: `modules/http2/h2_c1.c:117-308` `h2_c1_run`
- Entry kind: `return_value_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

