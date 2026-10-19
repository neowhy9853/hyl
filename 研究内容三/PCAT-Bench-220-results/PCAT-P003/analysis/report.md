# PCAT-P003 兼容性变更分析报告

- 仓库：`/home/soong/pca_benchmark/_repos/kernel`
- 基线：`ffc253263a1375a65fa6c9f62a893e9767fbebfa`
- Patch ID（内容标识，不是 commit）：`828e0bb791b319cbbb6102978c639ecac0bc917a`
- Profile：`kernel_6_6`
- 补丁应用状态：`applied`
- 隔离分析 worktree：`/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/_worktrees/patched`

## 概要

| 指标 | 数量 |
|---|---:|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 确认兼容性变更 | 1 |
| High | 1 |
| Medium | 0 |
| Low | 0 |

## PCA-0001：IFLA_STATS UAPI/netlink 布局变化

- 类型：`IOCTL_NETLINK_ABI_CHANGE`
- 优先级：`high`
- 置信度：`0.99`
- 位置：`include/uapi/linux/if_link.h:37-43`
- 符号：`struct rtnl_link_stats`

### 变更前行为

`struct rtnl_link_stats` 含 24 个 `__u32` 字段，x86_64 上 `sizeof`、`alignof` 和数组步长为 96、4、96 字节。`rtnl_fill_stats()` 使用 `sizeof(struct rtnl_link_stats)` 预留 `IFLA_STATS` 属性，因此旧载荷为 96 字节。

### 变更后行为

结构体尾部新增 `__u32 rx_dropped_by_xdp`，`sizeof` 和数组步长变为 100 字节，新字段偏移为 96；`IFLA_STATS` 属性载荷随之增长为 100 字节。既有字段偏移不变。

### 兼容性影响

该结构体位于稳定 `include/uapi`，并直接定义公开 rtnetlink 线协议载荷大小。按旧头文件构建、严格要求 96 字节、复制固定大小或以旧 `sizeof` 计算结构数组步长的消费者，面对新载荷可能拒绝、截断或错误迭代。只读取兼容前缀并容忍尾部扩展的消费者仍可继续工作，但精确长度和布局契约已经改变。

### 证据

```c
/* include/uapi/linux/if_link.h */
__u32 tx_compressed;

__u32 rx_nohandler;
+__u32 rx_dropped_by_xdp;
```

```c
/* net/core/rtnetlink.c:1263-1268 */
attr = nla_reserve(skb, IFLA_STATS,
                   sizeof(struct rtnl_link_stats));
copy_rtnl_link_stats(nla_data(attr), sp);
```

### 定向测试建议

对 before/after 分别执行 `headers_install`，用同一 C probe 比较 `sizeof`、`alignof`、关键 `offsetof` 和数组步长；再在匹配 QEMU 内核中发送 `NETLINK_ROUTE` `RTM_GETLINK`，比较 `IFLA_STATS` 的 `nla_len`/载荷布局，以旧头文件消费者验证严格长度失败与兼容前缀解析，并保留 native-header/native-size 控制路径。

