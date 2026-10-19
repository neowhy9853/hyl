# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `922a03b26e354a74a30b4a8220822072df3e54c4` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux` |
| 基线 | `36c85f7029484d5ede769f8873d16e9c8e35533c` |
| Profile | `kernel_6_6` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch changes the return contract of EXPORT_SYMBOL_GPL function btmtk_usb_hci_wmt_sync: too-short WMT FUNC_CTRL events now return 0 instead of -EINVAL. Static code inspection confirms the change is correct and intentional (fix for MT7925 regression). All callers in btusb.c (lines 2970, 3034, 3080) set wmt_params.status=NULL and check err<0, making the behavioral change safe from a static perspective. Dynamic verification with actual hardware is needed to confirm no adverse effects on other MediaTek BT device variants.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 0 |
| 规划输入 | 0 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 2 |
| 已覆盖行 | 0 |
| 未覆盖行 | 2 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc` |
| 优化级别 | `O0` |
| 覆盖率工具 | `gcov` |
- Kernel module btmtk.ko cannot be built without full kernel .config
- Dynamic test requires MT7925/7922 USB BT adapter
- Static code inspection completed successfully

## Finding 测试结果

### PCA-0001: RETURN_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `not_run`
- **目标**: `drivers/bluetooth/btmtk.c:682-683 (btmtk_usb_hci_wmt_sync)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | static_valid_not_run | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | btmtk_usb_hci_wmt_sync returns 0 (not -EINVAL) for too-short FUNC_CTRL event | Static: patch code at btmtk.c:682-683 confirmed. Dynamic: requires MT7925/7922 hardware. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_stability | skipped | Dynamic contract verification requires MT7925/7922 USB BT hardware for before/after comparison |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: 682, 683
- Static code inspection confirms patch correctly applied
- Old err=-EINVAL replaced by status=BTMTK_WMT_ON_UNDONE; break;
- All three callers in btusb.c set wmt_params.status=NULL and check err<0

### PCA-0002: ERROR_EXCEPTION_CHANGE

- **优先级**: `high`
- **状态**: `not_run`
- **目标**: `drivers/bluetooth/btmtk.c:682-683 (btmtk_usb_hci_wmt_sync)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | static_valid_not_run | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | No -EINVAL error; short FUNC_CTRL event treated as BTMTK_WMT_ON_UNDONE | Static: patch code at btmtk.c:682-683 confirmed. Dynamic: requires MT7925/7922 hardware. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| error_exception_stability | skipped | Dynamic contract verification requires MT7925/7922 USB BT hardware for before/after comparison |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: 682, 683
- Error model changed: short event no longer produces -EINVAL
- Intentional fix for regression on MT7925 firmware version 20260106153314

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-ENV-001 | Dynamic testing requires MT7925 (USB ID 0e8d:e025) or MT7922 (0489:e0e2) MediaTek Bluetooth USB adapter with firmware version 20260106153314 | Attach compatible MTK BT adapter to test machine |
| build | BLOCKER-BUILD-001 | Kernel module drivers/bluetooth/btmtk.c cannot be built with gcov without full kernel .config and modules_prepare | Generate kernel config (make defconfig + enable CONFIG_GCOV_KERNEL=y, CONFIG_BT=m, CONFIG_BT_MTK=m) and run make modules_prepare |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/` |
| coverage_data | `phase4_execution/` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Test with MT7925 (0e8d:e025) USB BT adapter to verify Bluetooth initialization succeeds
- Test with MT7922 (0489:e0e2) to confirm no regression on hardware with full-length FUNC_CTRL events
- Build kernel with CONFIG_GCOV_KERNEL=y and verify code coverage hits lines 682-683 in btmtk.c
- Verify dmesg shows no 'Failed to send wmt func ctrl' error during adapter initialization
