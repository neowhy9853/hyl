# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `f346fcf977c22f12b509fff3c674dbfb67490a38` |
| 仓库 | `/home/soong/pca_benchmark/_repos/NetworkManager` |
| 基线 | `ec1522fa8c8997509624836b3625cdd237e23e69` |
| Profile | `networkmanager` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch intentionally changes the D-Bus SetManaged method signature from (bu) to (uu), breaking backward compatibility at the wire protocol level. The public libnm function nm_device_set_managed_async changes from gboolean to NMDeviceManaged enum, breaking source-level API compatibility (ABI preserved). Old deprecated synchronous API preserved as migration path. All 3 native test suites pass. New enum type and exported symbol are additive and backward compatible. NM_DEVICE_MANAGED_RESET side effect is additive and only triggered by new callers.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 5 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 0 |
| 规划输入 | 2 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 0 |
| 已覆盖行 | 0 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `0` |
| 覆盖率工具 | `gcov` |
- Host build with meson, coverage instrumentation enabled. D-Bus daemon not available. No before-build (baseline) created.

## Finding 测试结果

### PCA-0001: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `introspection/org.freedesktop.NetworkManager.Device.xml:404-410 (SetManaged)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | not_run | `test-entry-work/PCA-0001/entry.json` | `meson test -C build --no-rebuild --print-errorlogs test-devices-wifi` | All tests pass, confirming project-internal callers use new (uu) signature | gcov shows coverage on impl_device_set_managed (requires D-Bus) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| dbus_protocol | skipped | D-Bus protocol contract verification requires running NetworkManager daemon with D-Bus session |

- **覆盖率**: 0/4 (0.00%)
- **未覆盖行**: introspection/org.freedesktop.NetworkManager.Device.xml:404-410, src/core/devices/nm-device.c:15094-15110, src/core/devices/nm-device.c:20088-20094, src/libnm-client-impl/nm-device.c:1503-1509
- Native project tests pass (3/3). D-Bus wire protocol verification requires live daemon test.

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `src/libnm-client-public/nm-device.h:152-158 (nm_device_set_managed_async)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | not_run | `test-entry-work/PCA-0002/entry.json` | `meson test -C build --no-rebuild --print-errorlogs src/libnm-core-impl/tests/test-setting` | Project compiles and tests pass with new NMDeviceManaged type | Successful compilation confirms header validity; gcov requires D-Bus call |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_header_compatibility | skipped | Source-level compilation test with old gboolean callers requires external downstream code |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: src/libnm-client-public/nm-device.h:155-155, src/libnm-client-impl/nm-device.c:1485-1509
- Project compiles and 3 test suites pass. ABI compatible. Source incompatible. Deprecated sync API preserved.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLK-001 | D-Bus session bus and NetworkManager daemon not available in this test environment | Build patched code in VM/container with D-Bus and run integration tests |
| environment | BLK-002 | Before-build (baseline) not created - missing root access for full daemon test setup | Set up disposable VM with D-Bus for before/after comparison |
| coverage | BLK-003 | Core daemon SetManaged handler unreachable from unit tests | Use D-Bus mock or integration test framework to exercise the handler |
| coverage | BLK-004 | nm_device_set_managed_async requires live D-Bus connection | Use libnm mock objects or integration test suite |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `not_applicable` |
| coverage_data | `not_applicable` |
| execution_results | `not_applicable` |
| impact_map | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/f346fc/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `not_applicable` |

## 建议

- Test SetManaged with old (bu) signature gets TYPE_MISMATCH error
- Compile downstream consumers to detect source-level breakage
- Test new NM_DEVICE_MANAGED_RESET (2) value via D-Bus
- Run NetworkManager integration tests with live daemon
