# 测试入口验证

- `PCA-TE-0001`: `runnable_verified`
- 命令：`timeout 1800 bash test-entry-work/PCA-0001/runtime_netlink.sh`
- 退出码：`0`
- 证据：before、after、after-oldheader 三个 QEMU TCG 启动均输出 `NETLINK_RUNTIME_DONE ... success=1`，最终输出 `PCAT_P003_ENTRY_OK finding=PCA-0001`。
- 日志：`runtime-netlink/results/test-entry-verification.log`
