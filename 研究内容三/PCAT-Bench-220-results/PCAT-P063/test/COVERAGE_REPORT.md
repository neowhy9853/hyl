# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `98b1fd4ff9a719f34131fa04cbd93f92c0c362f7` |
| 仓库 | `/home/soong/pca_benchmark/_repos/haproxy` |
| 基线 | `b9aa1c0e644a1a97f7b2ba780b8e17f841a225e4` |
| Profile | `haproxy` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Static analysis confirmed 1 ERROR_EXCEPTION_CHANGE (PCA-0001) in H3 PUSH_PROMISE error handling. The change fixes a bug where H3_ERR_ID_ERROR (0x108) was incorrectly treated as consumed bytes via b_del(), risking buffer corruption. The fix properly calls qcc_set_error() and jumps to error handler. Contract verification (version, features, mux, config) passed with identical before/after behavior. However, the H3 PUSH_PROMISE code path could not be exercised without vtest/varnishtest, so runtime behavior comparison is not possible.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 2 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 4 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 3 |
| 已覆盖行 | 0 |
| 未覆盖行 | 3 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc 13.3.0` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- vtest/varnishtest not installed - H3 QUIC protocol tests not runnable
- OpenSSL header 3.0.18 vs runtime 3.0.13 mismatch detected
- Lua 5.4 and PCRE2 headers available
- Both builds produced 233 .gcno files confirming coverage instrumentation

## Finding 测试结果

### PCA-0001: ERROR_EXCEPTION_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `src/h3.c:2074-2079 (h3_rcv_buf)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001-H3-CONFIG | static_valid_not_run | `test-entry-work/PCA-0001/h3_config_test.sh` | `bash test-entry-work/PCA-0001/h3_config_test.sh` | Both binaries accept/reject the same H3 QUIC configurations identically | exit code 0 |
| PCA-TE-0001 | needs_env | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | H3 PUSH_PROMISE frame triggers connection error via qcc_set_error and goto err | TRACE_ERROR message or gcov coverage of src/h3.c:2077-2079 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| version_output_stability | passed | Before and after binaries produce identical version output |
| feature_list_stability | passed | Feature lists identical including +QUIC, +QUIC_OPENSSL_COMPAT, +SSL, +LUA, +PCRE2 |
| mux_protocol_stability | passed | Available multiplexer protocols identical: quic (FE\|BE), h2, h1, fcgi, spop |
| config_parsing_stability | passed | Both binaries accept same valid config and reject same invalid configs |

- **覆盖率**: 0/3 (0.00%)
- **未覆盖行**: src/h3.c:2077, src/h3.c:2078, src/h3.c:2079
- H3 QUIC code path requires QUIC connection with H3 ALPN - not reachable via HTTP/1.1
- Full coverage requires vtest/varnishtest or custom H3 client
- Contract verification confirmed identical before/after behavior for all testable paths
- PCA-0001 is a bug fix: old code treated H3_ERR_ID_ERROR (0x108) as consumed byte count

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-001 | vtest/varnishtest not installed in test environment | Install vtest and run HAProxy reg-tests for H3/QUIC |
| entry | BLOCKER-002 | No H3 QUIC client available to send PUSH_PROMISE frame on backend connection | Use vtest with H3 QUIC test script to trigger the PUSH_PROMISE error path |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/results.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Install vtest/varnishtest for H3/QUIC protocol regression tests
- Run HAProxy reg-tests to verify H3 PUSH_PROMISE error handling
- Verify no resource leaks in the new error exit path
- Test backport compatibility for commit 4a8bb2fe5
