# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Analysis repo: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing`
- Patch ID: `66dfb3c`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `daemon_handler` `supplicant_iface_wps_credentials_cb`
- Target: `src/core/devices/wifi/nm-device-wifi.c:2198-2213` `supplicant_iface_wps_credentials_cb`
- Entry kind: `input_boundary_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

