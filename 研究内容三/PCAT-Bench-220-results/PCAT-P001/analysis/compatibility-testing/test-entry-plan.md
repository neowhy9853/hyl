# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P001/analysis/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/linux`
- Analysis repo: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P001/analysis/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P001/analysis/compatibility-testing`
- Patch ID: `632ca5e16e3e3141e559b9b4a4e588d252d0df2a`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct input_event`
- Target: `include/uapi/linux/input.h:44-50` `struct input_event`
- Entry kind: `kernel_reachability_reproducer`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, and limitations.

## PCA-TE-0002 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct input_event`
- Target: `include/uapi/linux/input.h:44-50` `struct input_event`
- Entry kind: `kernel_qemu_syscall_harness`
- Preferred artifact: static initramfs probe booted against isolated before/after kernels
- Trigger surface: `write(/dev/uinput)` and `read(/dev/input/eventX)`

Expected agent output: real syscall return values for legacy and native record sizes, guest completion markers, and isolated VM logs.
