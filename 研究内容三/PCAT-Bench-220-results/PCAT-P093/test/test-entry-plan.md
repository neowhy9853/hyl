# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P033/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P033/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P033/compatibility-testing`
- Patch ID: `16e8e067516c7c35f2affd8e9d58271707611575`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `public_method` `runtime.PanicNilError.Error()`
- Target: `src/runtime/panic.go:794-794` `PanicNilError.Error`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

