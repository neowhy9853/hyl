# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/linux`
- Analysis repo: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing`
- Patch ID: `09dc18894148381d3bfc550083b1236043870dce`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `public_function` `ibv_rereg_mr / IB_USER_VERBS_CMD_REREG_MR`
- Target: `drivers/infiniband/core/umem.c:334-342` `ib_umem_check_rereg`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `public_function` `ibv_rereg_mr / IB_USER_VERBS_CMD_REREG_MR`
- Target: `drivers/infiniband/core/umem.c:339-341` `ib_umem_check_rereg`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `low`
- Type: `SIDE_EFFECT_CHANGE`
- API: `callback_type` `rereg_user_mr driver callbacks`
- Target: `drivers/infiniband/sw/rxe/rxe_verbs.c:1329-1344` `rxe_rereg_user_mr`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

