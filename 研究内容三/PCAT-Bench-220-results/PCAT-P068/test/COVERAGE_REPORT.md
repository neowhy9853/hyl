# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `5e320c` |
| 仓库 | `/home/soong/pca_benchmark/_repos/rsyslog` |
| 基线 | `f89892ec84edcb39df3e3535c3c00cc7f15fab76` |
| Profile | `rsyslog` |
| 执行状态 | `passed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Patch intentionally introduces config incompatibilities in strict secure-default mode: (1) explicit streamdriver.mode="0" with TLS-capable driver rejected, (2) omitted mode promoted to 1. Behavior in backward-compatible and warn modes unchanged. All findings confirmed design-intent with >=80% coverage gate met.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 3 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 55 |
| 已覆盖行 | 48 |
| 未覆盖行 | 7 |
| 补丁行覆盖率 | 87.27% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0)` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov (GCC 13.3.0)` |
- host build without container; autoconf-archive macros copied from prior worktree

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `plugins/imtcp/imtcp.c:455-473 (applySecureDefaultsToStreamDriver)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E1 | passed | `tests/compat-configformat-rainerscript.sh` | `make check TESTS="compat-configformat-rainerscript.sh"` | strict mode rejects explicit streamdriver.mode="0" with TLS-capable driver | applySecureDefaultsToStreamDriver called 12 times; streamDriverModeSet=true branch entered 2 times; LogError line 463 executed 1 time |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C1 | passed | Config contract: explicit mode 0 with TLS-capable driver in strict mode fails with RS_RET_PARAM_ERROR |

- **覆盖率**: 17/18 (94.40%)
- **未覆盖行**: plugins/imtcp/imtcp.c:500 (setLegacyStrmDrvrMode)
- Intentional behavior change per commit message: strict secure-default hardening

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `tools/omfwd.c:2153-2171 (applySecureDefaultsToForwarding)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E2 | passed | `tests/compat-configformat-rainerscript.sh` | `make check TESTS="compat-configformat-rainerscript.sh"` | Mode promoted from 0 to 1 in strict mode with TLS-capable driver | applySecureDefaultsToForwarding called 24 times; *streamDriverMode=1 executed in imtcp line 470 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C2 | passed | Behavior contract: omitted mode promoted to 1 (TLS) in strict mode with TLS-capable effective driver |

- **覆盖率**: 18/20 (90.00%)
- **未覆盖行**: tools/omfwd.c:2748 (legacy path), tools/omfwd.c:2559 (ratelimitNewFromConfig)
- Intentional secure-default behavior change; backward-compatible mode unchanged

### PCA-0003: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `plugins/imtcp/imtcp.c:430-453 (warnIfInsecureListenerConfigured)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E3 | passed | `tests/compat-configformat-yaml.sh` | `make check TESTS="compat-configformat-yaml.sh"` | Warning emitted for TLS-capable global default driver with mode 0 in warn mode | warnIfInsecureListenerConfigured called 11 times; glblWarnIfInsecureDefault called for TLS warning |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C3 | passed | Output contract: warn mode detects TLS-capable drivers from global default and emits warning |

- **覆盖率**: 8/10 (80.00%)
- **未覆盖行**: runtime/glbl.c (truncated), runtime/glbl.c:838 (gcov mismatch)
- Warning coverage expanded to effective driver resolution; new warnings for previously silent configs

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/5e320c/compatibility-testing/coverage/` |
| execution_results | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/5e320c/compatibility-testing/phase4_execution/` |
| impact_map | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/5e320c/compatibility-testing/phase1_impact/` |
| report | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/5e320c/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/5e320c/compatibility-testing/test-entry-work/` |
| test_entry_tasks | `` |
| test_inputs | `` |

## 建议

- Update rsyslog configs using strict mode with TLS-capable drivers to use streamdriver.mode="1" or ptcp
- Run full testbench in container for additional validation
- Review documentation for strict mode behavior changes
