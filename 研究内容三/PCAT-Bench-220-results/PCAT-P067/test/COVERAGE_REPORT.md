# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `8aa55fd776d35f6d475a2fd5b5d9dcf8864c9f8a` |
| 仓库 | `/home/soong/pca_benchmark/_repos/rsyslog` |
| 基线 | `7491a61090ec7e78fb2910ca9a104c96fae468ee` |
| Profile | `rsyslog` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patched rsyslog build and nine directed allowed-sender tests completed without failures, providing meaningful after-only regression evidence. However, no matched baseline, old-v11 module/API probe, ABI layout probe, before/after contract comparison, or patch-line coverage was retained. These omissions prevent a compatible or incompatible conclusion.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 4 |
| 生成入口 | 4 |
| 验证入口 | 2 |
| 规划输入 | 9 |
| 执行输入 | 9 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 4 |
| 补丁可执行行 | 0 |
| 已覆盖行 | 0 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov flags configured; coverage output not retained` |
- Patched configure and build completed successfully before the OpenCode harness timeout.
- Nine directed allowed-sender scripts were recorded passed with zero failures across the original and continued session.
- The analysis worktree was cleaned before final artifacts were published.

## Finding 测试结果

### PCA-0001: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `not_run`
- **目标**: `runtime/net.h:148-245 (BEGINinterface(net) / netCURR_IF_VERSION)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | static_valid_not_run | `test-entry-work/PCA-0001/reproducer.sh` | `sh test-entry-work/PCA-0001/reproducer.sh /tmp/pca-rsyslog-before /tmp/pca-rsyslog-after` | The unchanged v11 consumer compiles against both versions; an after failure is a breach. | The compiler consumes each version's public net.h and checks netCURR_IF_VERSION. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| old_v11_consumer_compile_and_load | skipped | No matched baseline configured build or old-v11 external module was available. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- The source-level v11-to-v12 interface change remains statically established by analysis, but dynamic API compatibility was not tested.

### PCA-0002: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `runtime/tcpsrv.h:64-71 (tcpLstnParams_s)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | static_valid_not_run | `test-entry-work/PCA-0002/reproducer.sh` | `sh test-entry-work/PCA-0002/reproducer.sh /tmp/pca-rsyslog-before /tmp/pca-rsyslog-after` | The canonical layout observation remains equal; a size difference is a breach. | The compiler instantiates sizeof(tcpLstnParams_t) from each public header. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| tcp_listener_abi_layout | skipped | No matched baseline build, abidiff output, layout observation, or old binary consumer was available. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- A generated size probe is preserved for follow-up, but no executed ABI evidence exists in this recovery.

### PCA-0003: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `plugins/imtcp/imtcp.c:258-264 (modpdescr / inppdescr)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | runnable_verified | `tests/allowed-sender-modern.sh` | `timeout 180 make check TESTS='allowed-sender-modern.sh allowed-sender-empty-array.sh yaml-allowed-sender-modern.sh'` | Automake reports three requested tests passed and zero failed. | The native tests parse and enforce modern, YAML, and empty allowedsender arrays. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| allowedsender_config_matrix | skipped | Patched native tests ran, but the same matrix was not executed on a matched baseline. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- Patched native tests passed; this is meaningful after-only evidence, not a before/after compatibility proof.

### PCA-0004: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `plugins/imudp/imudp.c:566-576 (processPacket)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0004 | runnable_verified | `tests/allowed-sender-tcp-ok.sh` | `timeout 300 make check TESTS='allowed-sender-tcp-ok.sh allowed-sender-tcp-fail.sh allowed-sender-tcp-zero-mask.sh allowed-sender-tcp-hostname-ok.sh allowed-sender-tcp-hostname-fail.sh allowed-sender-wildcard-invalid-bits.sh'` | All six legacy/edge ACL scripts pass with zero failures. | The native tests observe listener allow/reject effects across address, mask, hostname, and wildcard inputs. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| allowed_sender_side_effects | skipped | Patched native tests ran, but no matched before side-effect/state snapshot was captured. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- Patched ACL regression tests passed; concurrency, cancellation, and before/after state comparison remain untested.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | before-build | No matched baseline rsyslog configured build was prepared or retained. | Create an isolated base_commit worktree and configure/build it with the same flags. |
| contract | PCA-0001-old-v11-module | The requested unchanged v11 external module compile/link/load probe did not run. | Build a v11 consumer against baseline headers and load it against both runtimes. |
| contract | PCA-0002-abi-layout | No abidiff, layout/offset harness, or old binary consumer result was captured. | Run abidiff plus a focused sizeof/alignment/offset and old-consumer probe on matched builds. |
| contract | PCA-0003-before-config | The configuration matrix ran only on the patched build. | Run the same modern/YAML/empty/legacy matrix on the baseline and compare canonical observations. |
| contract | PCA-0004-before-side-effects | No baseline listener ACL state or side-effect snapshot was captured. | Run the same ACL cases on baseline and compare acceptance, rejection, logs, and listener state. |
| coverage | patch-line-coverage | Coverage flags were configured, but no gcov data or executable patch-line classification was retained. | Rebuild after with coverage, rerun directed inputs, collect gcov, and evaluate the 80% gate. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/8aa55f/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Run the generated API and ABI probes on matched configured before/after builds.
- Repeat the configuration and side-effect matrix on the baseline and compare canonical observations.
- Collect gcov patch-line coverage and evaluate the 80% gate.
