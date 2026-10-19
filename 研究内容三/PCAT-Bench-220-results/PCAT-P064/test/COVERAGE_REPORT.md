# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `fb38e40` |
| 仓库 | `/home/soong/pca_benchmark/_repos/haproxy` |
| 基线 | `9bc37232f40b3c672d660e3f5f684621b2ed0e12` |
| Profile | `haproxy` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：非测试设计缺陷——该条件本身就是触发特定 varint 编码边界跨越的罕见场景。从语义分析看这是 bug fix，仅添加 len -= len_sz_diff 一行修正，不会引入新的兼容性破坏。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 3 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 0 |
| 未覆盖行 | 1 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu/GNU)` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Host: Linux x86_64 (WSL2 kernel 6.18.33.2)
- OpenSSL headers 3.0.18 / runtime 3.0.13 - mixed versions, not used for crypto conclusions
- vtest/varnishtest not installed - QUIC protocol reg-tests cannot run
- QUIC client: aioquic Python library (no native ngtcp2/quiche)

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `src/quic_tx.c:2038-2044 (qc_do_build_pkt)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/test-entries.json` | `haproxy -c -f /tmp/pca-quic-test.cfg` | exit code 0 (config validation passes) | gcov: line 2041 coverage would prove reachability; config parsing alone does not reach qc_do_build_pkt |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_validation_stability | passed | haproxy -c -f quic-test.cfg: before exit 0, after exit 0 |
| feature_list_stability | passed | haproxy -vv: both versions have +QUIC +QUIC_OPENSSL_COMPAT features |
| runtime_quic_connection | passed | aioquic H3 connection to quic4@127.0.0.1:18443 succeeded (AFTER binary), proving packet building code path is alive |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: src/quic_tx.c:2041 (len -= len_sz_diff;) - narrow_condition: requires QUIC Initial packet < QUIC_INITIAL_PACKET_MINLEN (1200 bytes) AND varint encoding size change on padding. Normal QUIC connections have Initial packets > 1200 bytes so padding path not triggered.
- Config validation (-c) passes identically before and after the patch
- QUIC connection established successfully with AFTER binary (proves packet building code path is alive)
- Line 2041 (len -= len_sz_diff) requires specific edge case not hit in normal connections
- Coverage gate not met (0% vs 80%) due to narrow condition requiring specific packet sizing

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLK-001 | vtest/varnishtest not installed on host | Install vtest (varnishtest) to run haproxy QUIC reg-tests |
| environment | BLK-002 | No native QUIC client (ngtcp2/quiche) for wire-level packet capture and format comparison | Install ngtcp2-client or similar for before/after QUIC packet comparison |
| input | BLK-003 | QUIC Initial packet padding edge case (line 2041) requires specific packet sizing to trigger varint encoding boundary crossing | Use a configurable QUIC client (e.g. ngtcp2) sending sub-1200 byte Initial packets |

## 产物

| Artifact | Path |
|---|---|
| analysis_json | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis.json` |
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/_worktrees/patched/src/quic_tx.c.gcov` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| patch_diff | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/patch.diff` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 在配备 vtest/varnishtest 的环境中运行 haproxy QUIC reg-tests
- 使用可构造特定包大小的 QUIC 测试工具（如 ngtcp2）发送 < 1200 字节的 Initial 包
- 确认修复后的 wire format 符合 RFC 9000/9001
