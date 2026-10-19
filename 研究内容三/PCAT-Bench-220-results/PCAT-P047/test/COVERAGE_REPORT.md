# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `66dfb3c` |
| 仓库 | `/home/soong/pca_benchmark/_repos/NetworkManager` |
| 基线 | `c0691de32218bded6ca3e2279c484575da8cbf31` |
| Profile | `networkmanager` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The INPUT_CONTRACT_CHANGE is additive (relaxed): nm_wifi_utils_wps_key_to_psk() accepts 64 hex-char PSKs in addition to 8-63 char passphrases. The new function is 100% covered (10/10 executable lines) by unit tests across 12 boundary cases. The supplicant callback (18/18 executable lines uncovered) requires live WPS event from wpa_supplicant, not reachable from unit tests. Coverage gate (80%) not met due to this untestable path. No behavioral regression detected for existing inputs.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 12 |
| 执行输入 | 12 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 28 |
| 已覆盖行 | 10 |
| 未覆盖行 | 18 |
| 补丁行覆盖率 | 35.70% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov (gcc 13.3.0)` |
- Build with -Dclat=false -Dppp=false -Dmodem_manager=false -Dnbft=false -Dovs=false -Dman=false for missing deps
- Coverage build uses -O0 -fprofile-arcs -ftest-coverage via meson -Db_coverage=true
- Before (baseline) build not performed - patch already applied to worktree
- Only host-level unit tests executed; privileged/live-network tests require disposable VM

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `src/core/devices/wifi/nm-device-wifi.c:2198-2213 (supplicant_iface_wps_credentials_cb)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `build/src/core/devices/wifi/test-devices-wifi` | `meson test -C build test-devices-wifi` | test_wps_key_to_psk passes all 12 input boundary cases | gcov shows nm_wifi_utils_wps_key_to_psk called 12 times, all executable lines covered |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | passed | New function nm_wifi_utils_wps_key_to_psk() accepts 8-63 char passphrases (same as old code) AND 64 hex-char PSKs. 12 test cases cover: valid passphrases (8,9,14,63), valid 64 hex-char PSK, mixed-case 64 hex, invalid hex char, empty, too short (7), too long (65), invalid UTF-8, embedded NUL. All 6 valid inputs accepted, all 6 invalid rejected. Old behavior for 8-63 char passphrases preserved. |

- **覆盖率**: 10/28 (35.70%)
- **未覆盖行**: src/core/devices/wifi/nm-device-wifi.c:2183, src/core/devices/wifi/nm-device-wifi.c:2184, src/core/devices/wifi/nm-device-wifi.c:2185, src/core/devices/wifi/nm-device-wifi.c:2187, src/core/devices/wifi/nm-device-wifi.c:2189, src/core/devices/wifi/nm-device-wifi.c:2190, src/core/devices/wifi/nm-device-wifi.c:2191, src/core/devices/wifi/nm-device-wifi.c:2194, src/core/devices/wifi/nm-device-wifi.c:2196, src/core/devices/wifi/nm-device-wifi.c:2197, src/core/devices/wifi/nm-device-wifi.c:2199, src/core/devices/wifi/nm-device-wifi.c:2200, src/core/devices/wifi/nm-device-wifi.c:2203, src/core/devices/wifi/nm-device-wifi.c:2204, src/core/devices/wifi/nm-device-wifi.c:2205, src/core/devices/wifi/nm-device-wifi.c:2209, src/core/devices/wifi/nm-device-wifi.c:2211, src/core/devices/wifi/nm-device-wifi.c:2214
- nm_wifi_utils_wps_key_to_psk(): 10/10 executable lines covered (100%)
- supplicant_iface_wps_credentials_cb(): 0/15 executable lines covered - requires live wpa_supplicant with WPS credentials event
- Before/after behavior comparison not performed - baseline build would require separate worktree at base_commit
- All 12 test cases in test_wps_key_to_psk pass, covering the full input boundary matrix

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | before_build | Before (baseline) build requires separate worktree at base_commit c0691de; patch already applied to analysis worktree | Create separate worktree at base_commit and rebuild with same coverage options |
| coverage | callback-coverage | supplicant_iface_wps_credentials_cb requires live wpa_supplicant D-Bus WPS credentials event; not reachable from unit tests | Run in disposable VM with mock wpa_supplicant or actual WPS-capable AP |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/_worktrees/patched/build/` |
| execution_results | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/phase4_execution/results.md` |
| impact_map | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/66dfb3/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `N/A - used project-native test (12 input cases in test_wps_key_to_psk)` |

## 建议

- Coverage gate not met due to supplicant callback (requires VM with wpa_supplicant). The new function itself is 100% covered.
- To reach 80% coverage: set up disposable VM with mock WPS credentials and trigger the callback path.
- No regression found in existing 8-63 char passphrase handling.
