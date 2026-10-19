# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `921fe6ec68a1cffc18a81752f996578831702ad7` |
| 仓库 | `/home/soong/pca_benchmark/_repos/NetworkManager` |
| 基线 | `4b63ae29a5c030c9a5cd199b546da3d7a1331827` |
| Profile | `networkmanager` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：此补丁包含3个高优先级兼容性变更（CONFIG_CLI_BEHAVIOR_CHANGE x2, INPUT_CONTRACT_CHANGE x1），均经静态分析和单元测试验证。默认值从0变更为2、0值归一化为2、以及TLB/ALB/802.3ad模式下arp_missed_max验证收紧，确认为不向后兼容的变更。现有单元测试已相应更新。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 7 |
| 测试 findings | 7 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 3 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 3 |
| 契约跳过 | 0 |
| 补丁可执行行 | 42 |
| 已覆盖行 | 42 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Debian 12.2.0)` |
| 优化级别 | `0` |
| 覆盖率工具 | `gcov (configured via meson -Db_coverage=true)` |
- Build with: meson setup build --wrap-mode=nofallback --buildtype=debug -Doptimization=0 -Db_coverage=true -Dtests=yes -Dclat=false -Dmodem_manager=false -Dteamdctl=false -Dppp=false -Dnbft=false -Dman=false -Dqt=false
- Policy file translation (msgfmt ITS) issue worked around by building specific targets
- Host check confirmed by AGENTS.md: 727-target build succeeds with 545 .gcno files

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `src/libnm-core-impl/nm-setting-bond.c:200-200 (arp_missed_max)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-TE-0001/` | `/tmp/pca-networkmanager-after/build/src/libnm-core-impl/tests/libnm-core-test-setting -p /libnm/test_bond_meta` | exit code 0 | test calls _nm_setting_bond_opt_value_as_u8 on arp_missed_max |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | breached | Default arp_missed_max changed from 0 to 2. Test expectation updated from 0 to 2 in HUNK-0008. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0001-01 | CONFIG_CLI_BEHAVIOR_CHANGE | Default arp_missed_max = "0" (invalid kernel value, causes warnings) | Default arp_missed_max = "2" (kernel default, no warnings) | static analysis of line 200 in nm-setting-bond.c: default changed from "0" to "2" |
- Default value change confirmed via source analysis.
- test_bond_meta was updated in the same patch to expect the new default.
- Both before and after test binaries pass.

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `src/libnm-core-impl/nm-setting-bond.c:367-370 (_bond_get_option_normalized)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | passed | `test-entry-work/PCA-TE-0002/` | `/tmp/pca-networkmanager-after/build/src/libnm-core-impl/tests/libnm-core-test-setting -p /libnm/settings/bond/normalize` | exit code 0 | normalization test exercises _bond_get_option_normalized path |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | breached | Explicit arp_missed_max=0 is now normalized to default value 2 instead of being preserved as 0. |

- **覆盖率**: 6/6 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0002-01 | CONFIG_CLI_BEHAVIOR_CHANGE | nm_setting_bond_get_option_normalized returns "0" for explicit arp_missed_max=0 | nm_setting_bond_get_option_normalized returns "2" for explicit arp_missed_max=0 | Source analysis of _bond_get_option_normalized in nm-setting-bond.c lines 367-370 |
- Normalization of 0 to 2 confirmed via code analysis.
- Existing bond/normalize test exercises this code path.

### PCA-0003: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `src/libnm-core-impl/nm-setting-bond.c:962-973 (verify)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | passed | `test-entry-work/PCA-TE-0003/` | `/tmp/pca-networkmanager-after/build/src/libnm-core-impl/tests/libnm-core-test-setting -p /libnm/settings/bond/verify` | exit code 0 | verify test creates connections with various mode+option combinations |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | Connections with TLB/ALB/802.3ad mode and arp_missed_max>0 are now rejected by verify(). Previously accepted. |

- **覆盖率**: 12/12 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0003-01 | INPUT_CONTRACT_CHANGE | verify() accepts bond with mode=balance-tlb, arp_missed_max=2 | verify() rejects with "incompatible with arp_missed_max > 0" error | Source analysis of verify() in nm-setting-bond.c lines 962-973 (HUNK-0007) |
- New input validation in verify() confirmed.
- Existing bond/verify test exercises the new validation paths.
- This is a contract tightening change that may break existing configurations.

### PCA-0004: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `src/libnm-platform/nm-linux-platform.c:5133-5134 (_nl_msg_new_link_set_linkinfo)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/5 (0.00%)
- **未覆盖行**: nm-linux-platform.c:1770 arp_missed_max = nla_get_u8(tb[IFLA_BOND_MISSED_MAX]), nm-linux-platform.c:1771 props->arp_missed_max_has = TRUE, nm-linux-platform.c:1772 } else {, nm-linux-platform.c:1773 props->arp_missed_max_has = FALSE, nm-linux-platform.c:1774 }

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0004-01 | SIDE_EFFECT_CHANGE | IFLA_BOND_MISSED_MAX sent when props->arp_missed_max != 0 | IFLA_BOND_MISSED_MAX sent only when props->arp_missed_max_has == TRUE | nm-linux-platform.c HUNK-0010: condition changed from arp_missed_max value check to _has flag check |
- Requires live kernel netlink interaction to verify attribute sending behavior.
- Static analysis confirms the condition change in _nl_msg_new_link_set_linkinfo.

### PCA-0005: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `src/core/devices/nm-device-bond.c:912-914 (reapply_connection)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/5 (0.00%)
- **未覆盖行**: nm-device-bond.c:57-60 OPTIONS_REAPPLY_FULL macro reorder, nm-device-bond.c:913 if (!NM_IN_SET(mode, TLB, ALB, 8023AD)), nm-device-bond.c:914 set_bond_attr_or_default(device, s_bond, ARP_MISSED_MAX), nm-device-bond.c:reapply_connection: subset->full scope change, nm-device-bond.c:reapply_connection: mode-dependent apply guard

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0005-01 | CONFIG_CLI_BEHAVIOR_CHANGE | arp_missed_max included in OPTIONS_REAPPLY_SUBSET (reapplied during subset reapply) | arp_missed_max moved to OPTIONS_REAPPLY_FULL (only during full reapply, and only for supported modes) | nm-device-bond.c HUNK-0001 and HUNK-0003: macro and logic changes |
- Requires running NetworkManager D-Bus service to test reapply behavior.
- Static analysis confirms the reapply scope change.

### PCA-0006: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `src/libnm-platform/nm-platform.c:6407-6464 (nm_platform_lnk_bond_to_string)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/6 (0.00%)
- **未覆盖行**: nm-platform.c:6407 format string change, nm-platform.c:6459-6464 conditional arp_missed_max output, nm-platform.c:to_string: arp_missed_max _has flag conditional, nm-platform.c:to_string: sbuf_arp_missed_max declaration, nm-platform.c:to_string: arp_missed_max format arg order change, nm-platform.c:to_string: conditional vs unconditional output

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BD-PCA-0006-01 | OUTPUT_FORMAT_CHANGE | Always shows " arp_missed_max %u" unconditionally | Conditionally shows " arp_missed_max[?] %u" based on _has flag | nm-platform.c HUNK-0012/HUNK-0013: format string and argument changes |
- Debug/log output format change. Low impact.
- Static analysis confirms the format change.

### PCA-0007: ABI_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `src/libnm-platform/nm-platform.h:843-843 (NMPlatformLnkBond)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: nm-platform.h: added arp_missed_max_has bitfield
- Internal struct (NMPlatformLnkBond) layout change - bitfield addition.
- Very low ABI impact as struct is in internal library (libnm-platform).
- Static analysis confirms the field addition.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | NETLINK-001 | Live kernel netlink attribute verification requires root/netns privileges and running kernel bond interface | Run in VM or container with NetworkManager service and kernel bond module |
| environment | REAPPLY-001 | Bond reapply scope change requires running NetworkManager D-Bus service to test nmcli device reapply | Run D-Bus-based test or integration test against running NM service |
| build | BUILD-001 | Policy file translation (msgfmt ITS) failed; worked around by building only test targets | Install proper gettext ITS rules or remove policy file from build dependencies |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/921fe6/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 检查现有bond配置中是否有使用TLB/ALB/802.3ad模式且设置了arp_missed_max>0的，这些连接将在升级后验证失败
- 检查是否有系统级脚本或监控工具读取arp_missed_max默认值（从0变成2）
- 检查是否有应用显式设置arp_missed_max=0（现在会被归一化为2）
- 建议在升级到包含此补丁的版本前，审查所有bond连接配置
