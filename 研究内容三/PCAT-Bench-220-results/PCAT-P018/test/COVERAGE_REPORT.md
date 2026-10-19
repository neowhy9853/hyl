# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `d3352554e4c1f052b914cda7b415d06b7eab5dfa` |
| 仓库 | `/home/soong/pca_benchmark/_repos/libxml2` |
| 基线 | `6be0acd2afb3f55af3c721e1e35ac6675df3057a` |
| Profile | `libxml2` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The --maxmem CLI option behavior changed. Old: always OOM. New: correctly enforces limit. Bug fix restoring documented behavior. Users who never used --maxmem are unaffected.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 7 |
| 执行输入 | 7 |
| 契约通过 | 4 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 6 |
| 已覆盖行 | 6 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov` |
- Both before (6be0acd) and after (d335255) builds completed successfully with Ninja.
- Coverage flags: --coverage for compile and link.

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `xmllint.c:3075-3083 (xmllintMain)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh <xmllint-binary>` | Without --maxmem/--maxmem 0: exit 0. With --maxmem 1: exit 9 (OOM). With --maxmem 100000+: exit 0. | xmllint --maxmem code path at xmllint.c:3078-3083 is reached when --maxmem specified with non-zero value |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | breached | BEFORE(6be0acd): --maxmem 100000 fails exit 9. AFTER(d335255): --maxmem 100000 succeeds exit 0. Expected breach - bug fix. |
| config_cli_default_behavior | passed | No --maxmem and --maxmem 0: both before and after behave identically (exit 0). |
| config_cli_oom_behavior | passed | --maxmem 1: both before and after OOM with exit 9 (1 byte too small). |
| config_cli_error_message | breached | BEFORE: Maximum memory exceeded (0 bytes). AFTER: Maximum memory exceeded (1 bytes). Error message now reflects actual limit. |
| config_cli_large_limit | passed | --maxmem 10000000: AFTER succeeds (exit 0), BEFORE OOMs (exit 9). |

- **覆盖率**: 6/6 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| cov-3-maxmem-100000 | CONFIG_CLI_BEHAVIOR_CHANGE | exit 9, Maximum memory exceeded (0 bytes) | exit 0 | gcov confirms xmllint.c:3080 executed 4 times. BEFORE always OOMs. AFTER works correctly. |
| cov-4-maxmem-10000000 | CONFIG_CLI_BEHAVIOR_CHANGE | exit 9, Maximum memory exceeded (0 bytes) | exit 0 | Same root cause. BEFORE OOMs on any non-zero --maxmem. AFTER works correctly. |
- Bug fix restoring documented --maxmem behavior.
- Old: xmllintMaxmem=0 inside if(lint->maxmem!=0). New: xmllintMaxmem=lint->maxmem.
- gcov: all changed lines (3078-3083) covered.

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `/tmp/pca-libxml2-after/build/xmllint.c.gcov` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- No remediation needed - bug fix restoring intended behavior.
- Update any workflows using --maxmem that relied on broken behavior.
