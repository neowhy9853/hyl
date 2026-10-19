# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `ba760c38b38b4fc5377f30bea492deba5f17df60` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux` |
| 基线 | `1229e2e57a5c2980ccd457b9b53ea0eed5a22ab3` |
| Profile | `kernel_6_6` |
| 执行状态 | `blocked` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80.0%` |
| 是否达标 | `False` |

**结论依据**：静态分析确认存在 1 个 INPUT_CONTRACT_CHANGE (HIGH priority)。补丁将 MGMT_OP_ADD_EXT_ADV_DATA 的长度校验从精确匹配 (!=) 放宽为上限检查 (>)，恢复与旧版 bluetoothd 的向后兼容性。测试入口 C 程序和 shell 包装已生成并通过语法编译验证。由于当前环境缺少带 Bluetooth MGMT 支持的运行内核和 GCOV 插桩构建，动态测试尚未执行。补丁逻辑简单明确（单条件变更），且 commit message 明确标明为 backward compatibility 修复，兼容性影响方向清晰。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 4 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 3 |
| 已覆盖行 | 0 |
| 未覆盖行 | 3 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc` |
| 优化级别 | `none` |
| 覆盖率工具 | `gcov (kernel)` |
- Kernel-level testing requires kernel build with CONFIG_GCOV_KERNEL=y, CONFIG_BT=y, CONFIG_BT_MGMT=y
- GCOV_PROFILE_mgmt.o := y needed in net/bluetooth/Makefile
- QEMU VM needed with Bluetooth virtual HCI device (hci_vhci module)
- User-space reproducer C program compiled and verified but cannot execute without kernel MGMT socket support

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `net/bluetooth/mgmt.c:9147-9149 (add_ext_adv_data)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | blocked_not_run | `test-entry-work/PCA-0001/reproducer.sh` | `sudo bash test-entry-work/PCA-0001/reproducer.sh` | test 1 (exact_len=6): ACCEPTED; test 2 (extra_len=7): ACCEPTED after patch (was REJECTED before); test 3 (short_len=5): REJECTED with MGMT_STATUS_INVALID_PARAMS; test 4 (min_len=3): ACCEPTED | Test 2 receiving MGMT_STATUS_SUCCESS instead of MGMT_STATUS_INVALID_PARAMS proves the '>' comparison at mgmt.c line 9149 was executed and extra bytes tolerated. gcov should confirm line 9149 coverage. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | skipped | Kernel VM environment not available. Contract verifies that inputs previously rejected by exact != check (e.g. data_len=7 when expected=6) are now accepted. Requires running kernel with CONFIG_BT=y, CONFIG_BT_MGMT=y. |

- **覆盖率**: 0/3 (0.00%)
- **未覆盖行**: 9147, 9148, 9149
- Patch changes input validation from '!=' to '>' for MGMT_OP_ADD_EXT_ADV_DATA length check
- Reproducer C program (mgmt_reproducer.c) compiled and validated syntactically
- Four test cases cover: exact match (6), extra bytes (7), too short (5), min size (3)
- Cannot run in current environment — needs kernel with Bluetooth MGMT + GCOV instrumentation

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-0001 | Kernel-level Bluetooth MGMT testing requires a running Linux kernel with CONFIG_BT=y, CONFIG_BT_MGMT=y, and a Bluetooth HCI device (real or virtual via hci_vhci). No such environment is available on the current host. | Build kernel from analysis_repo with CONFIG_GCOV_KERNEL=y, CONFIG_BT=y, CONFIG_BT_MGMT=y, GCOV_PROFILE_mgmt.o := y. Boot in QEMU VM with hci_vhci module. Run: sudo bash test-entry-work/PCA-0001/reproducer.sh |
| build | BLOCKER-0002 | Kernel before/after builds with gcov instrumentation require full kernel compilation with Kconfig changes and subsystem Makefile modifications, plus QEMU VM image. Not attempted without explicit authorization for large build operations and VM image downloads. | Configure kernel with 'scripts/config -e GCOV_KERNEL'. Add 'GCOV_PROFILE_mgmt.o := y' to net/bluetooth/Makefile. Build with 'make -j$(nproc)'. Set up QEMU VM with the instrumented kernel. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `contracts mentioned in finding_results` |
| coverage_data | `not_available — kernel gcov data requires VM execution` |
| execution_results | `test-entry-work/test-entry-verification.json` |
| impact_map | `test-entry-tasks.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/PCA-0001/mgmt_reproducer.c` |

## 建议

- 在配备 Bluetooth HCI 设备或 hci_vhci 模块的内核环境中运行测试入口: sudo bash test-entry-work/PCA-0001/reproducer.sh
- 使用 kernel gcov 插桩构建以验证补丁行覆盖率: 在 net/bluetooth/Makefile 中添加 GCOV_PROFILE_mgmt.o := y
- 验证 bluetoothd 在打补丁内核上的 MGMT_OP_ADD_EXT_ADV_DATA 行为，确认不再收到 MGMT_STATUS_INVALID_PARAMS 错误
- 对比 before/after 内核：旧内核应拒绝 data_len=7（预期=6）的请求，新内核应接受
