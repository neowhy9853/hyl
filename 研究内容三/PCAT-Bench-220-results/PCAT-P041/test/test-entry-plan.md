# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/glib/pca-results/407349/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/glib`
- Analysis repo: `/home/soong/pca_benchmark/_repos/glib/pca-results/407349/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/407349/compatibility-testing`
- Patch ID: `407349aa255a5c2b49caa52847aca1b8311c98b2`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `_g_dbus_auth_run_server (reachable via GDBusServer/GDBusConnection public API)`
- Target: `gio/gdbusauth.c:344-365` `_my_g_input_stream_read_line_safe`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

