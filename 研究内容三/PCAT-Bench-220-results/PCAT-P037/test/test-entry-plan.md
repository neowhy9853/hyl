# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/ruby`
- Analysis repo: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing`
- Patch ID: `0d7e50a1746bfa3db2a50478d3680cd7c36ea383`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `rb_ec_exec_end_proc / rb_ec_teardown / error_handle (via rb_error_write path)`
- Target: `eval.c:147-172` `rb_ec_teardown`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `exported_function` `rb_ec_exec_end_proc / error_handle / rb_error_write / rb_ec_error_print`
- Target: `eval_jump.c:113-136` `rb_ec_exec_end_proc`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

