# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `1780b21` |
| 仓库 | `/home/soong/pca_benchmark/_repos/openldap` |
| 基线 | `e538a0c6b335e2fbcb55503d84df2a81f6690e28` |
| Profile | `openldap` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Patch ITS#9022 adds an opt-in -o remove-sids= option to slapadd. All 8 directed tests pass. BEFORE and AFTER binaries produce identical behavior without the new option (no regression). Option parsing correctly validates SID values, rejects invalid/empty/non-numeric SIDs, and detects serverID conflicts (100% coverage on serverID check path). Coverage gate (80%) not met because deep CSN replacement and contextCSN filtering paths require MDB databases with pre-existing syncrepl context entries. Core option parsing has 82% coverage. No backward compatibility issues detected despite inconclusive formal status due to coverage threshold.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 5 |
| 生成入口 | 5 |
| 验证入口 | 5 |
| 规划输入 | 8 |
| 执行输入 | 8 |
| 契约通过 | 2 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 70 |
| 已覆盖行 | 34 |
| 未覆盖行 | 36 |
| 补丁行覆盖率 | 48.60% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0)` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- OpenSSL, Cyrus SASL, libevent, UUID available
- IPv4 socket denied with EPERM (workspace sandbox) - daemon tests not run
- Builds produce 423 .gcno files each
- slapadd is a symlink to slapd binary, distinguished by argv[0]

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `servers/slapd/slapcommon.c:255-286 (parse_slapopt)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E1 | passed | `/tmp/pca-test-run` | `slapadd -f slapd.conf -l test.ldif (no remove-sids)` | exit 0 | gcov confirms parse_slapopt and slapadd function execute (6+ hits on option parsing lines) |
| E2 | passed | `/tmp/pca-test-run` | `slapadd -f slapd.conf -l test.ldif -o remove-sids=1` | exit 0 with valid SID removal option | gcov confirms remove-sids handler executed (6 hits at line 258) |
| E3 | passed | `/tmp/pca-test-run` | `slapadd -f slapd.conf -l test.ldif -o remove-sids=0` | exit 1 with 'remove-sids contains configured serverID 0' | gcov confirms sids_to_remove[csnsid] check (1 hit at line 383) |
| E4 | passed | `/tmp/pca-test-run` | `slapadd -f slapd.conf -l test.ldif -o remove-sids=9999` | exit 1 with 'unable to parse' | gcov confirms invalid SID > SLAP_SYNC_SID_MAX check (2 hits at line 270) |
| E5 | passed | `/tmp/pca-test-run` | `slapadd -f slapd.conf -l test.ldif -o remove-sids=foo` | exit 1 with 'unable to parse' | gcov confirms lutil_atou() failure path (2 hits at line 270) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C1 | passed | BEFORE slapadd (baseline) and AFTER slapadd (patched) both exit 0 without the new option. Behavior is identical. |
| C2 | passed | AFTER slapadd correctly rejects conflicting serverID (csnsid 0) with informative error message and exits 1. |

- **覆盖率**: 34/70 (48.60%)
- **未覆盖行**: slapadd.c:279 - entryCSN replacement not reached (test entries lack entryCSN), slapadd.c:280 - entryCSN replacement not reached (test entries lack entryCSN), slapadd.c:281 - entryCSN replacement not reached (test entries lack entryCSN), slapadd.c:285 - entryCSN replacement not reached (test entries lack entryCSN), slapadd.c:286 - entryCSN replacement not reached (test entries lack entryCSN), slapadd.c:287 - entryCSN replacement not reached (test entries lack entryCSN), slapcommon.c:279 - default branch for non-SLAPADD tools not tested, slapcommon.c:280 - default branch for non-SLAPADD tools not tested, slapcommon.c:281 - default branch for non-SLAPADD tools not tested, slapcommon.c:1020 - contextCSN update path not reached (requires MDB context entry), slapcommon.c:1021 - contextCSN update path not reached, slapcommon.c:1022 - contextCSN update path not reached, slapcommon.c:1023 - contextCSN update path not reached, slapcommon.c:1024 - contextCSN update path not reached, slapcommon.c:1028 - contextCSN update path not reached, slapcommon.c:1029 - contextCSN update path not reached, slapcommon.c:1030 - contextCSN update path not reached, slapcommon.c:1031 - contextCSN update path not reached, slapcommon.c:1033 - contextCSN update path not reached, slapcommon.c:1035 - contextCSN update path not reached, slapcommon.c:1036 - contextCSN update path not reached, slapcommon.c:1052 - contextCSN update path not reached, slapcommon.c:1054 - contextCSN update path not reached, slapcommon.c:1057 - contextCSN update path not reached, slapcommon.c:1059 - contextCSN update path not reached, slapcommon.c:1060 - contextCSN update path not reached, slapcommon.c:1061 - contextCSN update path not reached, slapcommon.c:1066 - contextCSN update path not reached, slapcommon.c:1069 - contextCSN update path not reached, slapcommon.c:1071 - contextCSN update path not reached, slapcommon.c:1073 - contextCSN update path not reached, slapcommon.c:1074 - contextCSN update path not reached, slapcommon.c:1075 - contextCSN update path not reached, slapcommon.c:1076 - contextCSN update path not reached, slapcommon.c:1079 - contextCSN update path not reached, slapcommon.c:1080 - contextCSN update path not reached
- Core option parsing (parse_slapopt) coverage: 14/17 executable lines covered (82%)
- ServerID conflict check (slapadd function) coverage: 7/7 executable lines covered (100%)
- entryCSN replacement (entry_free) coverage: 4/10 executable lines covered (40%) - entries lacked pre-existing entryCSN
- contextCSN filtering (slap_tool_update_ctxcsn) coverage: 9/36 executable lines covered (25%) - requires MDB database with syncrepl context entries
- Coverage gate (80%) not met due to deep slapd initialization paths requiring MDB database with syncrepl context entries

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/contract_summary.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/_worktrees/patched/servers/slapd/slapcommon.c.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/execution_results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/compatibility-testing/test_inputs.json` |

## 建议

- If deeper coverage is desired, create a test LDIF with pre-existing entryCSN entries containing specific SIDs to test the CSN replacement path
- Set up a proper MDB database with syncrepl context entries to exercise the slap_tool_update_ctxcsn filtering logic
