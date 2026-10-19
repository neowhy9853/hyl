# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnf`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing`
- Patch ID: `aeb975e5486fa3bb5cd7db9d35af1eebd4bc8e64`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `config_key` `usr_drift_protected_paths`
- Target: `dnf/cli/cli.py:255-257` `BaseCli.do_transaction`
- Entry kind: `input_boundary_harness`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

