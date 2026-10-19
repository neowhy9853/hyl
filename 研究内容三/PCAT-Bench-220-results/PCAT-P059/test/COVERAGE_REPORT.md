# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `f603a4f920e6953b11667d424956fd47373870e9` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnsmasq` |
| 基线 | `c090f1d17b280c98630914334d341a2fa3318117` |
| Profile | `dnsmasq` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：1 SIDE_EFFECT_CHANGE finding (LOW). Before/after binaries build identically (--coverage -O0 -g) and operate identically in forwarder mode. DNSSEC wildcard corner case cannot be verified without controlled DNSSEC testbed. Patch is RFC 4035 bug fix. gcov: 10.27% dnssec.c coverage (35 gcda files). Patched lines need DNSSEC-signed responses.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 16 |
| 已覆盖行 | 0 |
| 未覆盖行 | 16 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Build with HAVE_DNSSEC enabled
- nettle/hogweed/gmp available
- 35 .gcno files, 35 .gcda files produced
- dnssec.c: 10.27% coverage (114/1110 lines)

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `src/dnssec.c:572-592 (validate_rrset)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| e1 | passed | `test-entry-work/test_wildcard_dnssec.py` | `python3 test-entry-work/test_wildcard_dnssec.py` | Both before and after binaries respond identically to DNS queries | dnsmasq starts, binds to port, responds to UDP queries |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| c1 | passed | Basic forwarder mode: both binaries produce identical rcode for example.com (0), google.com (0), nonexistent.test.local (3). *.example.com times out (no upstream wildcard). |

- **覆盖率**: 0/7 (0.00%)
- **未覆盖行**: src/dnssec.c:572, src/dnssec.c:576, src/dnssec.c:577, src/dnssec.c:579, src/dnssec.c:587, src/dnssec.c:689, src/dnssec.c:2275

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| bd1 | SIDE_EFFECT_CHANGE | Standard DNS forwarding rcode=0/3 | Standard DNS forwarding rcode=0/3 | All 4 test queries produce identical rcodes between before and after binaries |
- Patch is documented bug fix for DNSSEC wildcard corner case per RFC 4035
- STAT_SECURE_WILDCARD removed; wildcard status via wild_offset int parameter
- New guard skips wildcard expansion when name is already the wildcard pattern
- Full behavioral verification requires controlled DNSSEC testbed

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | blk1 | Requires controlled DNSSEC testbed with signed zones, trust anchors, recursive resolver config | Set up BIND/Knot as authoritative server; configure dnsmasq trust-anchor; query *.example.com with DO bit |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/` |
| coverage_data | `` |
| execution_results | `phase4_execution/test_results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-work/test-entries.json` |
| test_inputs | `test-entry-work/test_wildcard_dnssec.py` |

## 建议

- Set up controlled DNSSEC testbed with BIND/Knot as signed zone authoritative server
- Configure dnsmasq with trust-anchor pointing to test zone
- Query *.example.com A with DO bit set to verify NOERROR vs SERVFAIL
- Query a.example.com A to verify wildcard expansion works correctly
- Run gcov with full DNSSEC test to confirm patched lines covered
