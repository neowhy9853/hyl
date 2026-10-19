# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `183c9f8f5c7367a65ff6b0574ba966ad158c1ad8` |
| 仓库 | `/home/soong/pca_benchmark/_repos/ruby` |
| 基线 | `3760fedbffb87b29d554f3b270b7c92c9a660a50` |
| Profile | `ruby` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁新增 Time.parse 的 zone: 关键字参数，属于纯加法兼容性变更。所有不使用 zone: 的调用方行为在 BEFORE 和 AFTER 间完全一致。全部 5 个契约点验证通过，补丁行覆盖率 100%（2/2），0 合约违反。zone: 参数仅在调用方显式传入且解析日期字符串不含时区时生效，不影响任何现有行为。BEFORE 版本因 Ruby 4.1 的未知关键字静默忽略行为接受但忽略 zone:，AFTER 版本显式处理。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 5 |
| 执行输入 | 5 |
| 契约通过 | 5 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 2 |
| 已覆盖行 | 2 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0 --coverage` |
| 覆盖率工具 | `Ruby Coverage.lines + gcov (C files)` |
- Built from git worktrees: BEFORE=77d0d22b (parent), AFTER=183c9f8f (patch)
- lib/time.rb is pure Ruby, coverage measured via Ruby Coverage.lines API
- C gcov collected from time.c (35.96% line coverage, time.c not changed by this patch)

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `lib/time.rb:385-396 (Time.parse)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/tmp/pca-test-after/test_parse.rb` | `ruby --disable-gems -I /tmp/pca-test-after/lib -I /home/soong/pca_benchmark/_repos/ruby/.ext/x86_64-linux -I /home/soong/pca_benchmark/_repos/ruby/.ext/common /tmp/pca-test-after/test_parse.rb` | Time.parse accepts zone: keyword and returns correct timezone-aware result | Coverage.lines shows line 393 (d[:zone] \|\| zone) hit 5x |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_compat_basic | passed | Time.parse('2024-01-01 12:00:00') without zone: produces identical result in BEFORE and AFTER: '2024-01-01 12:00:00 +0800' |
| backward_compat_tz_in_string | passed | Time.parse('2024-01-01 12:00:00+01:00') with timezone in string works identically in both versions: results match |
| backward_compat_now_arg | passed | Time.parse with positional now argument continues to work identically in both versions |
| zone_arg_new_feature | passed | Time.parse('2024-01-01 12:00:00', zone: 'UTC') returns UTC time in AFTER version. BEFORE silently ignores zone: (Ruby 4.1 unknown keyword behavior), returns local time. |
| zone_arg_ignored_when_tz_present | passed | Time.parse('2024-01-01 12:00:00+01:00', zone: 'UTC') uses +01:00 from string (d[:zone] is truthy), zone:UTC correctly ignored. Same behavior. |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2 | INPUT_CONTRACT_CHANGE | zone: silently ignored, result=local time (+0800) | zone: explicitly handled, result=UTC | gcov line 393 hit 5x; BEFORE Ruby 4.1 silently accepts unknown keywords but ignores them |
- All 5 contract points verified PASS
- 100% patch line coverage (lines 388 and 393)
- Ruby 4.1 silently accepts unknown keywords - BEFORE version accepts zone: but ignores it
- Additive change: existing callers without zone: see identical behavior

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/phase4_execution/behavior_diff.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 无需采取任何回归措施 - 变更为纯加法兼容
- 文档注意：zone: 参数仅在日期字符串不包含时区/偏移时生效
- 建议在 API 文档中明确 zone: 参数的优先级行为（日期字符串内时区优先于 zone:）
