# 测试入口验证

- 入口：`PCA-TE-0001`
- 状态：`runnable_verified`
- 命令：`timeout 120 bash test-entry-work/PCA-0001/reproducer.sh phase2_environment/headers-before phase2_environment/headers-after`
- 退出码：0
- 可达信号：`reachability=headers_install output expanded include/uapi/linux/sysctl.h:30`
- 契约信号：`contract_breach=CTL_MAXNAME input boundary tightened from 10 to 8`
- 实测摘要：before 为 `CTL_MAXNAME=10 array_count=10 array_bytes=40`，after 为 `8/8/32`；`nlen=9` 和 `10` 从接受变为拒绝；旧消费者从编译成功变为静态断言失败。
