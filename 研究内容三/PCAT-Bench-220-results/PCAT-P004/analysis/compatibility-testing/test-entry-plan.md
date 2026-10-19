# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P004/analysis/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/kernel`
- Analysis repo: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P004/analysis/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P004/analysis/compatibility-testing`
- Patch ID: `c6d4181a1e8281b4e446ba83aa8eb06021cafdc7`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `macro` `CTL_MAXNAME`
- Target: `include/uapi/linux/sysctl.h:30-30` `CTL_MAXNAME`
- Entry kind: `input_boundary_harness`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

