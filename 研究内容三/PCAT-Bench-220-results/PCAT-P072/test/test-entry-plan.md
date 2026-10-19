# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/lvm2`
- Analysis repo: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/591a1c/compatibility-testing`
- Patch ID: `591a1c9310506124685cacc75aa338e31a148a06`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `config_key` `_type (config integer parsing path)`
- Target: `libdm/libdm-config.c:734-741` `_type`
- Entry kind: `input_boundary_harness`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

