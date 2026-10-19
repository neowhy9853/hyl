# PCAT-P099 测试入口验证

- `PCA-TE-0001`：真实 QEMU TCG + RXE/uverbs 入口已运行，但 `librxe` provider 对 `ibv_rereg_mr` 返回 `EOPNOTSUPP`，未到达 `rxe_rereg_user_mr`；状态为 `ran_expected_signal_mismatch`。
- `PCA-TE-0002`：Mock errno 契约入口通过，观察到 after `-EACCES` 和 `CONFIG_INFINIBAND_USER_MEM=n` 的 `-EOPNOTSUPP`。
- `PCA-TE-0003`：五驱动副作用顺序 Mock 通过；after 的拒绝路径在任何硬件/PD/MR 状态修改前返回。

Mock 验证只证明 helper 与 driver wrapper 单元契约，不代表真实硬件覆盖。
