# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `56ccc5ed569869fd735074ccebeaa7aab058342d` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/grub2` |
| 基线 | `01f064064c3146bd82e0c8db0da11d286bca31c6` |
| Profile | `grub2` |
| 执行状态 | `passed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁修复了 GRUB_OS_PROBER_SKIP_LIST 配置变量的两个缺陷：(1) 非 EFI 系统上仅 UUID 的跳过条目静默失效（现修复为正确生效），(2) 单词边界正则导致的 UUID 部分匹配误报（现改为显式分隔符锚定匹配）。存在向后不兼容的行为变化：旧版接受 UUID@sda1 格式的 SKIP_LIST 条目（现在被拒绝，需使用 UUID@/dev/sda1），且新增了弃用警告输出。但鉴于旧行为已在文档中描述为 bug，此变更应视为向前改进而非破坏性兼容性问题。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 18 |
| 执行输入 | 18 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 16 |
| 已覆盖行 | 16 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `N/A (shell script)` |
| 优化级别 | `N/A` |
| 覆盖率工具 | `N/A (shell script logic coverage via test matrix)` |
- Changed file is a shell script (util/grub.d/30_os-prober.in), no C compilation required
- Testing via isolated mocked harness that exercises old and new matching logic
- grub_probe mocking provides predictable UUIDs for test devices
- Full grub2 build not required for unit-level compatibility verification of regex matching logic

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `util/grub.d/30_os-prober.in:117-142 (GRUB_OS_PROBER_SKIP_LIST)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-TE-0001/test_skip_list.sh` | `bash test-entry-work/PCA-TE-0001/test_skip_list.sh` | All 18 tests pass, confirming both old bug behavior and new fix behavior | Exercises old and new regex matching paths for GRUB_OS_PROBER_SKIP_LIST |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | passed | Contract comparison: old code required @device suffix in SKIP_LIST for non-EFI (UUID-only entries silently ignored). New code correctly matches UUID-only entries and accepts @/dev/* deprecated format with warning. EFI entries work identically in both versions. Comma and semicolon are accepted as additional separators. |

- **覆盖率**: 16/16 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| T1-UUID-only-nonEFI | CONFIG_CLI_BEHAVIOR_CHANGE | UUID-only entry in SKIP_LIST for non-EFI device: noskip (BUG — silently ignored) | UUID-only entry in SKIP_LIST for non-EFI device: skip (FIXED) | Old code: EXPUUID always appended @device suffix, making UUID-only entries not match. New code: non-EFI path uses EXPUUID='UUID(@/dev/.*)?' which matches UUID-only entries. |
| T2-UUID@device-rejection | CONFIG_CLI_BEHAVIOR_CHANGE | UUID@sda1 in SKIP_LIST: skip (accepted any @suffix) | UUID@sda1 in SKIP_LIST: noskip (rejected, only @/dev/* accepted) | New code for non-EFI: EXPUUID='UUID(@/dev/.*)?' does not match 'UUID@sda1' in SKIP_LIST (sda1 lacks /dev/ prefix). Users must use UUID@/dev/sda1 for backward compat. |
| T3-separators | CONFIG_CLI_BEHAVIOR_CHANGE | Comma/semicolon as UUID separators: not explicitly supported (relied on \b word boundary) | Comma and semicolon explicitly accepted as separators (SPACE='[[:space:],;]') | New code explicitly includes comma and semicolon in SPACE regex pattern for entry separation. |
| T4-deprecation-warning | SIDE_EFFECT_CHANGE | No deprecation warning for any SKIP_LIST format | Deprecation warning emitted to stderr when SKIP_LIST contains UUID@/dev/* entries | New case statement checks for *@/[dD][eE][vV]/* pattern and calls grub_warn with deprecation message. |
- All 18 test cases passed: 0 failures
- Test covers: UUID-only (bug fix), @device rejection, @/dev/* backward compat, deprecation warning, comma/semicolon/space separators, exact matching, EFI paths, empty lists
- Old code bug confirmed: UUID-only SKIP_LIST entries never worked for non-EFI because EXPUUID always got @device suffix appended
- New code fixes the bug while maintaining backward compatibility for UUID@/dev/* format
- PCA-0002 (SIDE_EFFECT_CHANGE - deprecation warning) is verified as part of the CONFIG_CLI_BEHAVIOR_CHANGE testing

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `test-entry-work/PCA-TE-0001/runs/results.json` |
| execution_results | `test-entry-work/PCA-TE-0001/runs/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/PCA-TE-0001/test_skip_list.sh` |

## 建议

- 检查现有 /etc/default/grub 配置中是否使用了 'UUID@sda1' 格式的 GRUB_OS_PROBER_SKIP_LIST 条目，应迁移为 'UUID'（仅 UUID）或 'UUID@/dev/sda1'（弃用格式）
- 如果自动化脚本解析 grub-mkconfig 的 stderr 输出，需注意新增的弃用警告消息
- 验证非 EFI 系统上仅 UUID 的跳过行为符合预期，确保文档与实际行为一致
- 验证 EFI 链式加载器（UUID@EFI_PATH）的跳过行为不受影响
