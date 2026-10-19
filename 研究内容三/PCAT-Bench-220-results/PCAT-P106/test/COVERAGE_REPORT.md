# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `a23d8e124fbd` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux` |
| 基线 | `475b2384bb91576e7881bca8f17548a6bbee8ded` |
| Profile | `kernel_6_6` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Static analysis confirmed 2 compatibility changes: (1) HIGH: bond_option_xmit_hash_policy_set now rejects vlan+srcmac xmit_hash_policy when XDP is loaded on 802.3ad/balance-xor bonds via EOPNOTSUPP, affecting sysfs (/sys/class/net/<bond>/bonding/xmit_hash_policy) and netlink (IFLA_BOND_XMIT_HASH_POLICY) interfaces; (2) LOW: new __bond_xdp_check API symbol added to bonding.h (additive only). Dynamic testing was limited by kernel version mismatch - the analysis worktree uses v7.2-rc code that cannot be built against host kernel 6.8.0. Test entry scripts and contract probes have been generated and are ready for execution in a matching VM. Build was attempted 2 times with different strategies; both failed due to struct/API differences between kernel versions.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 6 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 6 |
| 已覆盖行 | 0 |
| 未覆盖行 | 6 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc-12 (attempted, failed due to kernel version mismatch)` |
| 优化级别 | `Og (attempted, build failed)` |
| 覆盖率工具 | `gcov (not usable - build blocked)` |
- Host kernel: 6.8.0-90-generic
- Analysis worktree kernel: v7.2-rc (requires kernel headers >= v7.0)
- Build attempted twice: (1) standard module build failed with net/netdev_lock.h missing, (2) extended include paths failed with struct bond_params field mismatches
- Kernel module build requires a VM running kernel >= v7.0 with matching headers
- GCOV_KERNEL=y and CONFIG_GCOV_PROFILE_ALL=y needed for coverage instrumentation

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `drivers/net/bonding/bond_options.c:1592-1599 (bond_option_xmit_hash_policy_set)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | generated | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | EOPNOTSUPP when XDP loaded + vlan+srcmac; success when XDP not loaded | sysfs write to /sys/class/net/<bond>/bonding/xmit_hash_policy triggers bond_option_xmit_hash_policy_set |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | skipped | Kernel bonding module from analysis worktree (v7.2-rc) cannot be built against host kernel 6.8.0. Requires VM with matching kernel version. |

- **覆盖率**: 0/6 (0.00%)
- **未覆盖行**: 1592, 1593, 1594, 1595, 1596, 1597
- Highest priority finding: sysfs/netlink xmit_hash_policy change rejection affects userspace tools
- Test script generated at test-entry-work/PCA-0001/reproducer.sh - ready for VM execution
- Build blocked: requires VM with kernel >= v7.0, CONFIG_BONDING=m, XDP support, and bpftool

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `include/net/bonding.h:697-703 (__bond_xdp_check)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_stability | skipped | Low priority additive-only change. __bond_xdp_check is a new symbol; bond_xdp_check signature preserved. |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: 700
- Additive-only API change: new __bond_xdp_check function declared in bonding.h
- Existing bond_xdp_check signature and callers unchanged
- Low priority: does not break existing consumers

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| build | kernel_version_mismatch | Analysis worktree code (kernel v7.2-rc) requires kernel headers >= v7.0. Host has 6.8.0-90-generic. Bonding module fails with: net/netdev_lock.h missing, struct bond_params field differences (broadcast_neighbor, lacp_strict), pernet_operations exit signature change. | Set up a VM running Linux >= v7.0 with kernel headers installed, CONFIG_BONDING=m, and GCOV_KERNEL=y for coverage instrumentation. |
| environment | xdp_environment | XDP program loading for bond device requires bpftool and a compiled XDP object file. Root privileges needed for bond device creation and XDP attach/detach. | Install bpftool, compile or use an XDP pass program (.o), run reproducer.sh as root in a VM with matching kernel. |
| coverage | gcov_kernel_missing | GCOV_KERNEL=y and CONFIG_GCOV_PROFILE_ALL=y required for line-level patch coverage. Host kernel not built with GCOV support. Debugfs must be mounted. | Rebuild kernel in VM with CONFIG_GCOV_KERNEL=y and CONFIG_GCOV_PROFILE_ALL=y, add GCOV_PROFILE_bonding.o := y to drivers/net/bonding/Makefile. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_iterations.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Set up a VM running Linux >= v7.0 with XDP and bonding support
- Build kernel with CONFIG_GCOV_KERNEL=y and CONFIG_GCOV_PROFILE_ALL=y for coverage
- Run test-entry-work/PCA-0001/reproducer.sh as root in the VM to verify the EOPNOTSUPP contract
- Execute contract verification for both PCA-0001 (config_cli_behavior_stability) and PCA-0002 (api_signature_stability)
- Collect gcov data from /sys/kernel/debug/gcov/ to measure patch line coverage
