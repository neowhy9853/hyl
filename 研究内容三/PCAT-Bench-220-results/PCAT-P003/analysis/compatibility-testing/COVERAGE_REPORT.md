# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `828e0bb791b319cbbb6102978c639ecac0bc917a` |
| 仓库 | `/home/soong/pca_benchmark/_repos/kernel` |
| 基线 | `ffc253263a1375a65fa6c9f62a893e9767fbebfa` |
| Profile | `kernel_6_6` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：headers_install 和真实 QEMU RTM_GETLINK 均确认 struct/IFLA_STATS 从 96 增至 100 字节；type-aware exact contract 已 breach，且 before-header 旧消费者在 after kernel 上严格长度解析失败。按用户指定 benchmark 口径，唯一 UAPI patch target 已验证，覆盖率 1/1=100%；runtime gcov 对声明不适用。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 1 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `mixed` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `用户态布局/运行 probe: -O0；kernel: x86_64_defconfig 默认优化（补丁目标为非执行声明）` |
| 覆盖率工具 | `Benchmark patch-target coverage via headers/QEMU probes；gcov/gcov-dump 13.3.0 仅用于确认 runtime counter N/A` |
- before/after 均从 base_commit 创建完整 detached worktree；patch 只应用于 after，git diff --check 通过。
- 使用静态 /init probe、内置/外部 initramfs 和 QEMU 8.2.2 q35 TCG；/dev/kvm 不可用。
- before/after 各自执行 headers_install，probe 仅使用对应版本的安装 UAPI headers。
- after-oldheader 使用 before headers 编译的静态 probe 和 after bzImage，验证真实旧消费者交叉路径。
- 按用户指定 benchmark 口径，唯一 UAPI 声明目标已验证并按 1/1=100% 计入有效覆盖；runtime gcov 仍为 N/A。

## Finding 测试结果

### PCA-0001: IOCTL_NETLINK_ABI_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `include/uapi/linux/if_link.h:37-43 (struct rtnl_link_stats)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/runtime_netlink.sh` | `timeout 1800 bash test-entry-work/PCA-0001/runtime_netlink.sh` | before 96/96；after native 100/100；after-oldheader 96/100 且 strict_old_accept=0、prefix_old_accept=1 | 三次 QEMU 均输出 NETLINK_RUNTIME_RESULT 与 NETLINK_RUNTIME_DONE success=1，入口最终输出 PCAT_P003_ENTRY_OK |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0001-ioctl_netlink_abi_stability-1 | breached | exact canonical observation 从 before 的 size/stride/payload=96、nla_len=100、strict_old_accept=1，变化为 after 的 size/stride/payload=100、nla_len=104、strict_old_accept=0；两侧命令均 rc=0。 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I3/I4-rtnetlink-native | IOCTL_NETLINK_ABI_CHANGE | sizeof=96 align=4 stride=96；IFLA_STATS nla_len=100 payload=96；strict_old_accept=1 | sizeof=100 align=4 stride=100，新字段 offset=96；IFLA_STATS nla_len=104 payload=100；strict_old_accept=0 | runtime-netlink/results/layout.before.log; layout.after.log; before.console.log; after.console.log |
| I5-rtnetlink-after-oldheader | IOCTL_NETLINK_ABI_CHANGE | 旧头文件消费者 compiled_size=96，在 before kernel 对 96-byte payload 精确接受 | 同一旧布局消费者在 after kernel 收到 100-byte payload：strict_old_accept=0、prefix_old_accept=1、native_exact=0 | runtime-netlink/results/after-oldheader.console.log |
| I4/I5-uninitialized-tail-observation | IOCTL_NETLINK_ABI_CHANGE | IFLA_STATS 仅 96 字节，不存在 offset 96 尾字段 | 独立 after 启动在 offset 96 观测到不同非零 raw_xdp 值；serializer 的 copy_rtnl_link_stats() 未给新增字段赋值 | runtime-netlink/results/test-entry-verification.log; net/core/rtnetlink.c:910-944 |
- 既有字段 offset 保持不变，因此容忍尾部扩展且只解析 96-byte 前缀的旧消费者仍兼容。
- 精确长度/sizeof/数组步长消费者发生确定性破坏，符合已锁定的 IOCTL_NETLINK_ABI_CHANGE。
- 新增尾字段的非确定值是额外运行时风险，未用于变更 finding 类型。

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| input | I6-compat32-runtime | 已尝试 gcc -m32，但主机缺少 32-bit libc development header：bits/libc-header-start.h；因此未生成或运行 32-bit 用户态 probe。 | 在隔离环境提供 gcc multilib 与 32-bit libc development headers 后，使用相同 after UAPI probe 重跑 32-bit 编译/启动。 |
| coverage | PCA-0001-patch-line-gcov | runtime gcov 对结构体字段声明不适用；有效 patch-target coverage 已由 headers_install 和真实 RTM_GETLINK 验证为 1/1=100%。 | 无需补充 runtime gcov；保留编译期布局与真实 netlink payload 证据。 |
| input | PCA-0001-unknown-nested-request-attrs | 未执行未知/嵌套 RTM_GETLINK 请求属性矩阵，因为补丁只改变固定 reply IFLA_STATS 结构布局，不改变请求 nla_policy；该矩阵不能提高目标行可达性。 | 仅在扩展为无关的 RTM_GETLINK request-policy 回归测试时添加；不应计作本补丁声明覆盖率。 |

## 产物

| Artifact | Path |
|---|---|
| behavior_diff | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase4_execution/behavior_diff.json` |
| contract_summary | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase4_execution/coverage_iterations.json` |
| entry_verification | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/test-entry-work/test-entry-verification.json` |
| execution_results | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P003/analysis/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 若保留尾部扩展，要求/修复消费者按至少 96 字节解析兼容前缀而非精确等于 sizeof(old struct)。
- 在公开协议中明确版本化或尾部扩展规则，并添加 before-header/after-kernel 回归测试。
- 在发送 IFLA_STATS 前显式初始化新增 rx_dropped_by_xdp 字段；当前 serializer 未赋值且实测尾部值非确定。
- 具备 multilib 环境后补充 32-bit 用户态 consumer；netlink wire payload 本身不经过 compat struct translation，但应验证工具链/消费代码。
