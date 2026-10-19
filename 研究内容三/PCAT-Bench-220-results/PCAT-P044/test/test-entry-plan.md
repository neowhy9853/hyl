# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/glib`
- Analysis repo: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing`
- Patch ID: `5f3b17`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `ABI_CHANGE`
- API: `exported_function` `GUserDirectory / G_USER_N_DIRECTORIES`
- Target: `glib/gutils.h:248-262` `G_USER_DIRECTORY_PROJECTS`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `get_icon_name (internal) -> g_file_query_info (public)`
- Target: `gio/glocalfileinfo.c:1840-1849` `get_icon_name`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

