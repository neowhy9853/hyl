# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `3a052d55fbfca49d8d435cdd2110fb2667594c61` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnsmasq` |
| 基线 | `1eab169173fc4c8579a3db61186096fe117e6aca` |
| Profile | `dnsmasq` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Both PCA findings confirmed via executed tests with gcov evidence. PCA-0001 (MEDIUM): non-QUERY TCP requests no longer enter forwarding logic - intended regression fix. PCA-0002 (LOW): EDNS0/buffer init now applies to non-QUERY TCP requests. 100% patch line coverage achieved.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 0 |
| 契约违约 | 2 |
| 契约跳过 | 0 |
| 补丁可执行行 | 4 |
| 已覆盖行 | 4 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (GCC) 14.2.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Built with COPTS=-DHAVE_DNSSEC for DNSSEC support
- Build has no-conntrack, no-DBus, no-UBus, no-IDN, no-Lua
- Network namespace not available; tests use high ports (10600+) on loopback

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `failed`
- **目标**: `src/forward.c:2570-2576 (tcp_request)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-0001/reproducer.py` | `python3 test-entry-work/PCA-0001/reproducer.py {BEFORE_BIN} {AFTER_BIN} 10600` | Before: non-QUERY enters forwarding path. After: non-QUERY blocked, RCODE response sent. | gcov: before forwarding block hit, after forwarding block not entered (#####) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | breached | Before: forwarding block entered, ede=EDE_NOT_READY set, no TCP response. After: !flags guard blocks forwarding, ede=EDE_UNSET preserved, RCODE=4 response sent. |

- **覆盖率**: 4/4 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | SIDE_EFFECT_CHANGE | response_len=0 (no TCP response), log: 'reply opcode is not implemented (EDE: not ready)' | response_len=29, OPCODE=4, RCODE=4 (NOTIMP), log: 'reply opcode is not implemented' | gcov: before line 2583=1 (ede=EDE_NOT_READY), after line 2585=##### (ede unchanged) |
- Behavior confirmed: NON-QUERY TCP request prevented from entering forwarding logic. This is the intended regression fix per commit message.

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `failed`
- **目标**: `src/forward.c:2461-2475 (tcp_request)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-0001/reproducer.py` | `python3 test-entry-work/PCA-0001/reproducer.py {BEFORE_BIN} {AFTER_BIN} 10600` | add_edns0_config, memset, memcpy now executed for non-QUERY requests | gcov: after lines 2466=1, 2469=1, 2471=1; before EDNS0 code not reached (#####) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | breached | Before: add_edns0_config/memset/memcpy not executed for non-QUERY. After: all executed (gcov hits on lines 2466, 2469, 2471). |

- **覆盖率**: 4/4 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2 | SIDE_EFFECT_CHANGE | add_edns0_config not called for non-QUERY; out_header buffer uninitialized | add_edns0_config called for non-QUERY; out_header initialized with memset+memcpy | gcov: after lines 2466=1, 2469=1, 2471=1. Before: EDNS0 code inside QUERY branch not reached (#####). |
- EDNS0 processing now applies to non-QUERY TCP requests. Required for proper out_header initialization for response generation.

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts` |
| coverage_data | `COVERAGE_REPORT.md` |
| execution_results | `phase4_execution` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Verify no infrastructure relies on dnsmasq forwarding non-QUERY TCP requests
- Confirm EDNS0 processing on non-QUERY requests does not cause unexpected side effects
