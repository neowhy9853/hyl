# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `23c056c83cebad03f716c7af490c8bec9753ec90` |
| 仓库 | `/home/soong/pca_benchmark/_repos/ruby` |
| 基线 | `0b2b21767beb73cd8497ac6b18248e7b87dc433e` |
| Profile | `ruby` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Purely additive API change: Integer#bit_count is a new public method with no modifications to existing API, contracts, or behavior. All new code paths are exercised with 100% line coverage. The method correctly returns population counts for fixnum and bignum ranges, raises ArgumentError for negative integers per specification, and matches the documented contract. Before the patch, the method did not exist (NoMethodError). This is backward compatible.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 1 |
| 规划输入 | 306 |
| 执行输入 | 306 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 29 |
| 已覆盖行 | 29 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (GCC)` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Out-of-tree builds in /tmp/pca-ruby-build-before (before) and /tmp/pca-ruby-build-after (after)
- Before source: /tmp/pca-ruby-before at base commit 0b2b21767b
- After source: analysis_repo with patch applied
- Core build (miniruby) sufficient for Integer smoke tests per AGENTS.md

## Finding 测试结果

### PCA-0001: API_SIGNATURE_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `numeric.c:6656-6656 (Integer#bit_count)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-0001 | passed | `test-entry-work/PCA-0001/smoke_bit_count.rb` | `./miniruby smoke_bit_count.rb` | exit code 0, ALL TESTS PASSED | gcov shows execution counts on numeric.c:5736,5767 (bit_count functions) and bignum.c:7033 |
| ENTRY-0002 | blocked | `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/_worktrees/patched/test/ruby/test_integer.rb` | `./ruby -Ilib -Itest test/ruby/test_integer.rb --name test_bit_count` | test_bit_count passes | coverage on numeric.c new lines for bit_count |
| ENTRY-0003 | blocked | `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/_worktrees/patched/test/ruby/test_integer.rb` | `./ruby -Ilib -Itest test/ruby/test_integer.rb --name test_bit_count_for_negative_numbers` | ArgumentError raised for negatives | coverage on negative path in rb_fix_bit_count |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | passed | Before: Integer#bit_count does not exist (NoMethodError). After: Integer#bit_count returns correct popcount for positive integers, raises ArgumentError for negative. This is a purely additive API change with no modification to existing contracts. |

- **覆盖率**: 29/29 (100.00%)
- **未覆盖行**: -
- Smoke test passed all 306 assertions covering fixnum, bignum, boundary cases, and negative integer rejection
- Native test_bit_count/test_bit_count_for_negative_numbers blocked: requires test-unit gem (not available in offline build environment)
- ENTRY-0001 covers all assertions from the native tests with equivalent coverage
- gcov confirms 100% executable line coverage on bit_count code in numeric.c and bignum.c

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| entry | PCA-0001/ENTRY-0002 | Native test_bit_count requires test-unit gem. Not available in offline build environment. | Install bundled gems (test-unit) to run native test suite |
| entry | PCA-0001/ENTRY-0003 | Same as ENTRY-0002: requires test-unit gem for native test_bit_count_for_negative_numbers. | Install bundled gems (test-unit) to run native test suite |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `compatibility-testing/test-summary.json` |
| coverage_data | `compatibility-testing/test-summary.json` |
| execution_results | `compatibility-testing/test-summary.json` |
| impact_map | `compatibility-testing/phase1_impact` |
| report | `compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `compatibility-testing/test-entry-tasks.json` |
| test_inputs | `compatibility-testing/test-entry-work/PCA-0001/smoke_bit_count.rb` |

## 建议

- No remediation needed. Integer#bit_count works correctly and is fully covered by tests.
- If full native test suite integration is desired, provide offline-available test-unit gem.
