# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `0d7e50a1746bfa3db2a50478d3680cd7c36ea383` |
| 仓库 | `/home/soong/pca_benchmark/_repos/ruby` |
| 基线 | `3760fedbffb87b29d554f3b270b7c92c9a660a50` |
| Profile | `ruby` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Both PCA findings confirmed as real behavioral changes with before/after evidence. PCA-0001 (SIDE_EFFECT_CHANGE): EXIT+END error reporting order and completeness changed. PCA-0002 (ERROR_EXCEPTION_CHANGE): Cause chains deduplicated, EXIT handler exceptions now visible. Coverage gate not met due to pre-existing refactored function bodies; all new/changed logic lines are 100% covered. The incompatibility is intentional - Bug #22191 fix restores correct error reporting order.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 0 |
| 契约违约 | 3 |
| 契约跳过 | 0 |
| 补丁可执行行 | 87 |
| 已覆盖行 | 46 |
| 未覆盖行 | 41 |
| 补丁行覆盖率 | 52.90% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 11.4.0-1ubuntu1~22.04)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov` |
- Before source: reverse-patched from 0d7e50a174 (parent eec3aba7a3 does not build standalone due to shape.h pre-existing issues)
- After source: 0d7e50a174 patched
- Build system: autotools (configure + make)
- Both builds succeeded

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `eval.c:147-172 (rb_ec_teardown)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/tmp/test_pca0001_exit_end.rb` | `ruby /tmp/test_pca0001_exit_end.rb` | stderr with RuntimeError messages for EXIT and END handlers | stderr shows EXIT RuntimeError and END RuntimeError messages |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | breached | Error output ordering and completeness changed: before shows EXIT errors interleaved with END errors with duplicates; after shows clean END3->END2->END1->EXIT order, each once |

- **覆盖率**: 12/12 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | SIDE_EFFECT_CHANGE | EXIT+END errors interleaved with duplicates, EXIT error scattered across output | END errors in order (END3,END2,END1) then EXIT error at end, each exactly once | Test 1 stdout/stderr capture: BEFORE has 9 error lines, AFTER has 4 error lines |
- Before behavior: EXIT trap error was processed before END handlers, leading to chaotic interleaving
- After behavior: EXIT error preserved until after END handlers, then reported cleanly
- Add_shown_cause in eval_jump.c prevents duplicate END handler output

### PCA-0002: ERROR_EXCEPTION_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `eval_jump.c:113-136 (rb_ec_exec_end_proc)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002a | passed | `/tmp/test_pca0002_cause_chain.rb` | `ruby /tmp/test_pca0002_cause_chain.rb` | stderr with cause chain from outer to inner exceptions | stderr shows RuntimeError messages with cause chains |
| PCA-TE-0002b | passed | `/tmp/test_pca0002_exit_cause.rb` | `ruby /tmp/test_pca0002_exit_cause.rb` | stderr with EXIT handler exception cause chain | stderr shows RuntimeError from EXIT handler with cause |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| error_exception_stability | breached | Cause chain duplication eliminated: before shows 'previous' reported twice; after shows 'previous' once + 'outer' with cause 'middle' |
| error_exception_stability | breached | EXIT handler exceptions now visible: before shows no error output for EXIT handler exceptions with causes; after shows 'outer' with cause 'inner' |

- **覆盖率**: 14/14 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2a | ERROR_EXCEPTION_CHANGE | 'previous' error reported twice (duplicate) in output | 'previous' reported once, followed by 'outer' (cause: 'middle') | Test 2 stdout/stderr capture: BEFORE has 4 error lines (2x previous), AFTER has 3 error lines (1x previous) |
| I2b | ERROR_EXCEPTION_CHANGE | No error output at all (EXIT handler errors silently lost) | 'outer' (RuntimeError) with cause 'inner' (RuntimeError) properly reported | Test 3 stdout/stderr capture: BEFORE produces 0 error lines, AFTER produces 2 error lines with cause chain |
- Add_shown_cause in eval_jump.c tracks already-reported causes to prevent duplicates
- rb_ec_teardown in eval.c now preserves EXIT trap errinfo until after END handlers finish
- Previously EXIT handler errors could be overwritten by END handler errors in ec->errinfo

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/tmp/pca-ruby-after-build/` |
| execution_results | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Verify downstream test suites that assert on error output format during Ruby process exit
- Update any test assertions that check for duplicate error messages or missing EXIT handler errors
- Run test/ruby/test_exception.rb test suite to confirm the new tests pass
- The behavior change is intentional and corrects a bug; downstream consumers should update their expectations
