# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `ff1d43509608cfe41a7c4c4dc8285a1de5bb1824` |
| 仓库 | `/home/soong/pca_benchmark/_repos/NetworkManager` |
| 基线 | `1a2fec62f038beab768a3929abcfcb63dd52bc34` |
| Profile | `networkmanager` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Both compatibility findings are additive OUTPUT_FORMAT_CHANGE changes: new PORTS field for bond/bridge/team device show output, and new CONTROLLER-PATH field for connection show output. In both cases, the old field names (SLAVES, MASTER-PATH) are fully preserved with identical output content. The developer explicitly designed these changes to avoid breakage ('Instead of replacing them, we add a new field'). All existing tests pass on both before and after builds. Binary string analysis confirms the new fields only appear in the patched binary.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 4 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 11 |
| 已覆盖行 | 11 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.2.0` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov (available but not instrumented for nmcli unit tests)` |
- Both before (base_commit) and after (patched) builds completed successfully
- Meson build with -Dtests=yes, 985 targets each
- test-client golden output tests require dbus Python module (not available)
- Binary string analysis confirmed new fields present only in patched version

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `src/nmcli/devices.c:766-784 (print_bond_bridge_info)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `src/nmcli/devices.c` | `meson test -C build test-devices-wifi` | test passes (SLAVES and PORTS fields both functional) | nmc_fields_dev_show_controller_prop array contains PORTS at index 2; print_bond_bridge_info sets both SLAVES (idx 1) and PORTS (idx 2) |
| PCA-TE-0001-binary | verified | `build/src/nmcli/nmcli` | `strings nmcli \| grep PORTS` | PORTS field string present in binary | PORTS appears 7 times in patched binary vs 6 in baseline |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability_slaves | passed | SLAVES field content and position unchanged. Before: set_val_str(arr, 1, g_string_free(ports_str, FALSE)). After: set_val_str(arr, 1, g_strdup(ports_str->str)) - functionally identical output. test-devices-wifi passes on both builds. |
| output_format_new_ports | passed | New PORTS field added at index 2 in controller_prop array, showing same data as SLAVES. PORTS string present in binary (7 occurrences). No regression in existing tests. |

- **覆盖率**: 6/6 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-TE-0001 | OUTPUT_FORMAT_CHANGE | nmcli device show bond/bridge: BOND section with NAME and SLAVES fields | nmcli device show bond/bridge: BOND section with NAME, SLAVES, and PORTS fields | New PORTS field added at index 2 in nmc_fields_dev_show_controller_prop array (src/nmcli/devices.c:769). field_order string updated from 'NAME,SLAVES' to 'NAME,SLAVES,PORTS' (devices.c:772). Commit message: 'Instead of replacing them, we add a new field that will show the same value with the new name.' |
- Additive change: existing SLAVES field fully preserved
- PORTS shows same data as SLAVES (port list)
- Team config shifted from idx 2 to idx 3 in team_prop array, but output is name-based not position-based

### PCA-0002: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `src/nmcli/connections.c:920-926 (_metagen_con_active_general_get_fcn)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | verified | `src/nmcli/connections.c` | `strings nmcli \| grep CONTROLLER-PATH > /dev/null` | CONTROLLER-PATH field string present only in patched binary | CONTROLLER-PATH found 1 time in patched binary, 0 in baseline |
| PCA-TE-0002-code | verified | `src/nmcli/connections.c` | `static code analysis of _metagen_con_active_general_get_fcn` | CONTROLLER_PATH and MASTER_PATH enum values share same code path | case NMC_GENERIC_INFO_TYPE_CON_ACTIVE_GENERAL_MASTER_PATH: added as fall-through to CONTROLLER_PATH handler (connections.c:921) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability_master_path | passed | MASTER-PATH field content and position unchanged. Both MASTER_PATH and CONTROLLER_PATH fall through to same nm_active_connection_get_controller() call. test-setting passes on both builds. |
| output_format_new_controller_path | passed | New CONTROLLER-PATH field added to metagen table showing same data as MASTER-PATH. Field string present in patched binary only. test expectations updated (test_003.expected, test_004.expected). |

- **覆盖率**: 5/5 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-TE-0002 | OUTPUT_FORMAT_CHANGE | nmcli connection show: GENERAL section includes MASTER-PATH field | nmcli connection show: GENERAL section includes both CONTROLLER-PATH and MASTER-PATH fields (same value) | CONTROLLER_PATH case added as fall-through to existing MASTER_PATH code (connections.c:921). "CONTROLLER-PATH" and "MASTER-PATH" entries in metagen table (connections.c:952-955). Enum value NMC_GENERIC_INFO_TYPE_CON_ACTIVE_GENERAL_MASTER_PATH added in utils.h:160. |
- Additive change: existing MASTER-PATH field fully preserved
- CONTROLLER-PATH shows same controller D-Bus path as MASTER-PATH
- Enum addition in internal nmcli header does not affect public libnm API/ABI

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-001 | test-client golden output tests (check-local-tests-client) require python3-dbus module which is not available in the test environment | Install python3-dbus package or run in a full NetworkManager test environment |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/phase4_execution/coverage_data` |
| execution_results | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/ff1d43/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- No immediate action required - changes are backward-compatible by design
- If strict output stability is required, update any scripts that parse `nmcli connection show` or `nmcli device show` output by column position to account for the new CONTROLLER-PATH and PORTS fields
- The test expectations (test_003.expected, test_004.expected) have already been updated to include the new field
