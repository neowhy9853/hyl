# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `ef191c4` |
| 仓库 | `/home/soong/pca_benchmark/_repos/haproxy` |
| 基线 | `b9fa07bd205ddd993c84e29d5b0324a84d032578` |
| Profile | `haproxy` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Patch fixes BUG/MINOR: ACL deletion error message corrected from 'Unknown map identifier' to 'Unknown ACL identifier'. Behavioral difference fully confirmed via before/after binary comparison. Coverage gate narrowly missed (75% vs 80%) due to short-circuit evaluation on line 1001 leaving condition uncovered. Map context behavior unchanged as expected.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 4 |
| 已覆盖行 | 3 |
| 未覆盖行 | 1 |
| 补丁行覆盖率 | 75.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Build: TARGET=linux-glibc USE_OPENSSL=1 USE_QUIC=1 USE_QUIC_OPENSSL_COMPAT=1 USE_LUA=1 USE_PCRE2=1 ARCH_FLAGS='-O0 -g --coverage' LDFLAGS='--coverage'
- HAProxy 3.5-dev0, Linux 6.18.33.2 WSL2 x86_64

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `src/map.c:998-1009 (cli_parse_del_map)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/binary` | `haproxy -f <config> -db; echo 'del acl <ref> <key>' \| socat - UNIX-CONNECT:<socket>` | Unknown ACL identifier for ACL context | Unknown ACL identifier |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | passed | BEFORE: 'del acl' -> 'Unknown map identifier'; AFTER: 'del acl' -> 'Unknown ACL identifier'. Map context unchanged. |

- **覆盖率**: 3/4 (75.00%)
- **未覆盖行**: 1003 (MAP branch)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | Unknown map identifier. Please use #<id> or <file>. | Unknown ACL identifier. Please use #<id> or <file>. | gcov confirms lines 1002+1005 reached; BEFORE/AFTER binary output comparison |
- LOW priority bug fix for CLI error diagnostic
- Behavior change confirmed via before/after binary comparison
- Line 1003 (MAP branch) behaviorally verified with separate 'del map' test

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `generated inline` |
| coverage_data | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/_worktrees/patched/map.c.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/phase4_execution/coverage_run_results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `generated inline` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing/phase4_execution/results.json` |

## 建议

- No remediation needed - beneficial bug fix
- If automation parses CLI 'Unknown map identifier' for ACL ops, update to match 'Unknown ACL identifier'
