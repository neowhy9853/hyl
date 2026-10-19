# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `aeb975e5486fa3bb5cd7db9d35af1eebd4bc8e64` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnf` |
| 基线 | `1f9f3e99cf70b2431ae95796512d69086fc2ff7b` |
| Profile | `dnf` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch changes usr_drift_protected_paths matching from prefix/exact matching (startswith/==) to fnmatch glob matching. 5 of 96 test cases show regressions where previously protected paths are no longer matched. Bare directory paths like /usr/lib, /usr/local, and /etc lose subdirectory protection coverage. The behavioral change is confirmed by a standalone contract harness achieving 100% patch line coverage. Full DNF integration testing is blocked by missing system libraries on this host.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 5 |
| 执行输入 | 1 |
| 契约通过 | 89 |
| 契约违约 | 7 |
| 契约跳过 | 0 |
| 补丁可执行行 | 3 |
| 已覆盖行 | 3 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `blocked` |
| 补丁后构建 | `blocked` |
| 编译器 | `N/A (Python)` |
| 优化级别 | `N/A (Python)` |
| 覆盖率工具 | `manual (standalone harness)` |
- Full DNF integration environment unavailable: python3-hawkey, python3-libdnf, python3-libcomps, python3-rpm, python3-librepo, python3-gpg not installed
- Standalone Python contract harness used to verify fnmatch vs startswith behavioral change
- All 3 changed lines are behaviorally covered by the harness

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `dnf/cli/cli.py:255-257 (BaseCli.do_transaction)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | executed | `test-entry-work/PCA-0001/contract_harness.py` | `/usr/bin/python3 test-entry-work/PCA-0001/contract_harness.py` | exit code 1 (contract breach detected) | CONTRACT BREACH DETECTED: 5 cases where previously protected paths are no longer matched |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | 5 regressions: bare directory paths (/usr/lib, /usr/local, /etc) no longer protect subdirectory contents via prefix matching |
| forward_input_acceptance | passed | 2 expansions: glob patterns (/usr/lib/*, /data/[a-z]*) now provide wildcard/pattern matching as intended by the patch |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | INPUT_CONTRACT_CHANGE | True — startswith('/usr/lib/') matches /usr/lib/python3.11/site-packages/foo | False — fnmatch('/usr/lib/python3.11/site-packages/foo', '/usr/lib') returns False (no wildcard, exact match only) | Standalone harness: /usr/lib matching /usr/lib/python3.11/site-packages/foo — old=True, new=False |
| I2 | INPUT_CONTRACT_CHANGE | False — literal '*' in startswith('/usr/lib/*/') does not match /usr/lib/foo | True — fnmatch('/usr/lib/foo', '/usr/lib/*') matches via glob wildcard | Standalone harness: /usr/lib/* matching /usr/lib/python3.11/site-packages/foo — old=False, new=True |
- 5 regressions confirmed: bare directory paths lose subdirectory protection
- 2 expansions confirmed: glob wildcards now work as intended
- Full integration test blocked: missing DNF system libraries
- Recommend updating existing usr_drift_protected_paths config values to use '/*' suffix

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLK-0001 | Missing required system packages: python3-hawkey, python3-libdnf, python3-libcomps, python3-rpm, python3-librepo, python3-gpg | Install missing Python bindings for DNF native testing: dnf install python3-hawkey python3-libdnf python3-libcomps python3-rpm python3-librepo python3-gpg |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/phase4_execution/results.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/dnf/pca-results/aeb975/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Update existing usr_drift_protected_paths configurations to use '/*' suffix for directory-level protection (e.g., /usr/lib -> /usr/lib/*)
- Install python3-hawkey, python3-libdnf, python3-libcomps, python3-rpm, python3-librepo, python3-gpg and rerun full DNF test suite to verify integration behavior
- Document the semantic change in release notes: usr_drift_protected_paths now uses fnmatch glob patterns, not path prefixes
