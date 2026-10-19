# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/kernel`
- Analysis repo: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing`
- Patch ID: `828e0bb791b319cbbb6102978c639ecac0bc917a`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `IOCTL_NETLINK_ABI_CHANGE`
- API: `struct_type` `struct rtnl_link_stats / IFLA_STATS`
- Target: `include/uapi/linux/if_link.h:37-43` `struct rtnl_link_stats`
- Entry kind: `ioctl_or_netlink_uapi_reproducer`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line
- Contract: `ioctl_netlink_abi_stability` / `exact`
- Observation: command/family availability, UAPI layout, attributes, policy, reply, and errno
- Input axes: command/operation, struct size, known attributes, unknown attributes, nested policy, compat mode

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

