# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `de9c5c5b597bf97aa03145de129fb579b5a0e953` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnf` |
| 基线 | `c9ae937afb79829ac544d20bdd9675a0dd2b1060` |
| Profile | `dnf` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The INPUT_CONTRACT_CHANGE is a backward-compatible relaxation restoring pre-v4.15.0 behavior. Contract verification (pure Python, 10/10 passed) confirmed correct behavior. However, the full DNF test suite is blocked by missing native bindings, so conclusive backward compatibility cannot be determined without runtime test execution with all dependencies available.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 10 |
| 执行输入 | 10 |
| 契约通过 | 10 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 2 |
| 已覆盖行 | 0 |
| 未覆盖行 | 2 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `n/a` |
| 优化级别 | `n/a` |
| 覆盖率工具 | `n/a` |
- Native DNF bindings (libdnf, hawkey, librepo, rpm, libcomps, gpg) are not installed on this host
- Building the project succeeds (cmake + cmake --build) but all 91 test modules fail at import time
- Import chain: dnf/__init__.py -> dnf/base.py -> libdnf.transaction (ModuleNotFoundError)
- Only the pure-Python function rpm2py_format was testable in isolation via contract verification script

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `dnf/cli/commands/repoquery.py:68-74 (rpm2py_format)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-work/PCA-0001/contract_verify.py` | `/usr/bin/python3 /home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-work/PCA-0001/contract_verify.py` | exit code 0, all contract tests pass | pure-Python rpm2py_format function executes with both old and new code paths |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | passed | All 10 contract assertions passed: lowercase tags preserved (identical old/new), uppercase tags change by design (from literal to formatted), invalid/unknown tags unaffected |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: dnf/cli/commands/repoquery.py:70 (key = key.lower()), dnf/cli/commands/repoquery.py:79 (return '{0.' + key + fill + '}')

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| uppercase_simple | INPUT_CONTRACT_CHANGE | "%{NAME}" from OLD code: '%{{NAME}}' (literal pass-through) | "%{NAME}" from NEW code: '{0.name}' (formatted) | contract_verify.py: uppercase_simple test: old='%{{NAME}}' vs new='{0.name}' |
- Full DNF test suite cannot execute because native C bindings (libdnf, hawkey, librepo, rpm, libcomps, gpg) are not installed on this host
- The dnf/cli/commands/repoquery module transitively imports libdnf through dnf.base, causing ImportError
- Contract verification was performed in isolation with the pure-Python rpm2py_format function - 10/10 passed

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | B1 | Missing native DNF Python bindings (libdnf, hawkey, librepo, rpm, libcomps, gpg) prevent importing dnf.base and running the full test suite | Install distribution packages: python3-libdnf, python3-hawkey, python3-librepo, python3-rpm, python3-libcomps, python3-gpg |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-work/PCA-0001/contract_verify.py (verification output)` |
| coverage_data | `n/a (coverage requires test execution)` |
| execution_results | `n/a (full test suite blocked by missing native deps)` |
| impact_map | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing/test-entry-work/PCA-0001/contract_verify.py` |

## 建议

- Install native DNF Python bindings and re-run the full test suite
- Run: /usr/bin/python3 -m unittest -v tests.test_repoquery tests.test_cli tests.test_output tests.test_base
- After build: ctest --test-dir build --output-on-failure
- The INPUT_CONTRACT_CHANGE is low-risk (backward-compatible relaxation, restores pre-existing behavior)
