# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `04d0a30ca93c` |
| 仓库 | `/home/soong/pca_benchmark/_repos/libsoup` |
| 基线 | `00858a9740fd67cbf3b6ee4ba6def1b681e3c9da` |
| Profile | `libsoup` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch adds errno==ERANGE overflow detection to Content-Length header validation. Previously, overflowed values were silently accepted (both saturating to G_MAXUINT64). Now they are properly rejected. This is an INPUT_CONTRACT_CHANGE: the set of accepted inputs is narrowed. While this is a bug fix per RFC 9110, it changes externally observable behavior - requests with overflowing Content-Length values that were previously accepted will now be rejected. Patch impact coverage: 100% (5/5 executable lines covered).

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 5 |
| 已覆盖行 | 5 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `0` |
| 覆盖率工具 | `gcov` |
- Build uses /home/soong/pca_benchmark/.venv-pcat-build/bin/meson with -Doptimization=0 -Db_coverage=true

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `libsoup/soup-message-headers.c:297-310 (soup_message_headers_append_common)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/tmp/pca-libsoup-after/build/test-overflow` | `/tmp/pca-libsoup-after/build/test-overflow` | overflow values are rejected (return FALSE), valid values accepted (return TRUE) | gcov shows lines 300-307 hit 11-13 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | BEFORE: identical overflow Content-Length values returned TRUE (incorrectly matched as equal, both saturate to G_MAXUINT64). AFTER: returns FALSE (properly rejected via errno==ERANGE). The breach is the intended input contract tightening per RFC 9110. |

- **覆盖率**: 5/5 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-0001-key-overflow-test | INPUT_CONTRACT_CHANGE | overflow Content-Length values accepted (saturate to G_MAXUINT64, erroneously match as equal) | overflow Content-Length values rejected (errno==ERANGE, return FALSE) | Test output: BEFORE key test returned TRUE, AFTER key test returned FALSE. gcov confirms lines 300-307 are executed. |
- The patch fixes a bug where g_ascii_strtoull overflow was not detected, allowing invalid Content-Length values to pass validation.
- This is an INPUT_CONTRACT_CHANGE: previously accepted overflowed values are now rejected.
- All changed lines (5 executable lines) are covered with 11-13 hits.
- The existing header-parsing-test suite (12 subtests) passes on both before and after builds.
- Behavior difference is confirmed and is the intended effect of the patch (bug fix).

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/tmp/pca-libsoup-after/build/soup-message-headers.c.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Document that overflowing Content-Length values are now rejected per RFC 9110
- Verify no downstream consumers depend on overflowed Content-Length values being silently accepted
- Include this fix in release notes as a security/correctness improvement
