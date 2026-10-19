# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/linux`
- Analysis repo: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/compatibility-testing`
- Patch ID: `3310153e66dddd35668e409c053cb72e3ae224ce`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `macro` `UINPUT_VERSION`
- Target: `include/uapi/linux/uinput.h:46-46` `UINPUT_VERSION`
- Entry kind: `kernel_reachability_reproducer`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, and limitations.

