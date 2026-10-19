# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `71ca70a0f62cfc30dfacfd2ee0952a86e2e64055` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup` |
| 基线 | `4e0fe0f16215b2f481356e879bc05661862ae4ad` |
| Profile | `libsoup` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：SoupSessionAsync and SoupSessionSync now default to system CA certificate validation (ssl-use-system-ca-file=TRUE, tls-database=system-CA-database) instead of no validation (FALSE/NULL). This is a deliberate security-hardening incompatibility acknowledged by the patch author. Plain SoupSession behavior is unchanged. Patch line coverage is 100% (5/5 executable lines covered).

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 1 |
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
| 编译器 | `gcc` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Built libsoup 2.72.0 from source using meson on Ubuntu 22.04 host
- libpsl dependency replaced with stub library for build compatibility
- Both before (4e0fe0f1) and after (71ca70a0) builds completed successfully
- Coverage instrumented build with -fprofile-arcs -ftest-coverage -O0

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `libsoup/soup-session.c:270-288 (soup_session_constructor)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-TE-0001/test_program.c` | `LD_LIBRARY_PATH=<build>/libsoup ./test-before && ./test-after` | SoupSessionAsync: ssl-use-system-ca-file=FALSE before, TRUE after; tls-database=NULL before, SET after | Confirmed: both before and after test programs executed successfully, output shows SoupSessionAsync property changes as expected |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability:SoupSessionAsync_defaults | breached | SoupSessionAsync default construction: ssl-use-system-ca-file changed from FALSE to TRUE; tls-database changed from NULL to system-CA-database. Intentional breach documented by patch author for security hardening. |
| side_effect_manifest_stability:plain_SoupSession_defaults | passed | Plain SoupSession default construction: ssl-use-system-ca-file remains TRUE, tls-database remains system-CA-database. No change. |

- **覆盖率**: 5/5 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| SoupSessionAsync-default | SIDE_EFFECT_CHANGE | ssl-use-system-ca-file=FALSE, tls-database=NULL | ssl-use-system-ca-file=TRUE, tls-database=system-ca-database | Test program output confirmed before/after property defaults differ; gcov confirmed changed lines (276,277,278,280,285 in patched soup-session.c) were executed 2x |
- GObject property defaults for SoupSessionAsync changed: ssl-use-system-ca-file FALSE→TRUE, tls-database NULL→system-CA-database
- Plain SoupSession behavior unchanged (already had system CA by default)
- 100% patch-line coverage achieved (5/5 executable lines covered)
- This is an intentional incompatibility for security improvement

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| finding | PCA-0002 | Medium-priority finding not tested under --min-priority high. PCA-0002 covers notify::tls-database GObject signal emission behavior change, which requires more complex signal-connection test harness. | Set --min-priority medium or all to include this finding in a further test pass |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `/tmp/soup-session.c.gcov` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Audit downstream applications using SoupSessionAsync/SoupSessionSync without explicit TLS configuration
- For affected applications, either configure custom CA certificates via tls-database property or set ssl-use-system-ca-file=FALSE if self-signed certs are intentionally trusted
- Consider migrating from deprecated SoupSessionAsync/SoupSessionSync to plain SoupSession
- Run PCA-0002 (medium-priority notify::tls-database signal test) with lower min-priority threshold
