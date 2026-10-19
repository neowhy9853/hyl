# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/glib`
- Analysis repo: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/compatibility-testing`
- Patch ID: `c9da977c`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `g_dbus_node_info_new_for_xml`
- Target: `gio/gdbusintrospection.c:1266-1272` `parser_start_element`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

