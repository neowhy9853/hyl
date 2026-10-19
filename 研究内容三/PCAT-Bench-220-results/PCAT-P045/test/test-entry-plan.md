# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Analysis repo: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/compatibility-testing`
- Patch ID: `f346fcf977c22f12b509fff3c674dbfb67490a38`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `daemon_handler` `org.freedesktop.NetworkManager.Device.SetManaged`
- Target: `introspection/org.freedesktop.NetworkManager.Device.xml:404-410` `SetManaged`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `nm_device_set_managed_async`
- Target: `src/libnm-client-public/nm-device.h:152-158` `nm_device_set_managed_async`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

