# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `b8cda126b` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `67ad42147a7acc2af6074753ebd03d904476118f` |
| Profile | `git` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch changes the output format of the IP address passed to git daemon access hooks for IPv6 connections. Before: '0.0.0.0' (corrupted). After: '::1' (correct). This is a bug fix that corrects clearly wrong behavior, but any script or hook that consumed the corrupted IPv6 address will observe a different value. The new die() path for unexpected address families is also a behavior change (daemon now terminates connection instead of silently producing garbage). Coverage gate (80%) not met because AF_INET and die() branches remain untested (75% achieved).

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 1 |
| 执行输入 | 1 |
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 16 |
| 已覆盖行 | 12 |
| 未覆盖行 | 4 |
| 补丁行覆盖率 | 75.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Build with NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 due to missing Cargo and Conda libiconv issues
- IPv6 loopback available and tested
- BEFORE build uses commit 67ad42147 (unfixed parent of b8cda126b)
- AFTER build uses commit b8cda126b (the patch)

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `daemon.c:674-693 (lookup_hostname)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `GIT_EXEC_PATH=<build> PCA_BINARY=<build>/git bash test-entry-work/PCA-0001/reproducer.sh` | Access hook receives correct IPv6 address for IPv6 connections | gcov confirms AF_INET6 changed path executed (lines 679,682-684,690-696,701): 12/16 executable lines covered |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | BEFORE (unfixed): access hook receives ip='0.0.0.0' (corrupted due to hardcoded AF_INET on sockaddr_in6). AFTER (fixed): access hook receives ip='::1' (correct IPv6 address). The output format for IPv6 connections changed from corrupted to correct. |

- **覆盖率**: 12/16 (75.00%)
- **未覆盖行**: daemon.c:680 (AF_INET branch: struct sockaddr_in *sa), daemon.c:681 (AF_INET branch: addr = &sa->sin_addr), daemon.c:686 (die() branch: unexpected address family call), daemon.c:687 (die() branch: ai_family argument)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-TE-0001 | OUTPUT_FORMAT_CHANGE | Access hook receives ip='0.0.0.0' | Access hook receives ip='::1' | Daemon access hook log captured both values. BEFORE: ip='0.0.0.0', AFTER: ip='::1'. Confirmed by gcov that the AF_INET6 path in the patched code was executed. |
- The patch is a bug fix that corrects IPv6 address handling in git daemon's lookup_hostname()
- Before the fix, IPv6 addresses were corrupted (read as sockaddr_in on sockaddr_in6 memory, producing 0.0.0.0)
- After the fix, IPv6 addresses are correctly formatted
- Coverage < 80% because AF_INET branch and die() branch were not exercised in this test (IPv6-only connection)
- To reach 80%+ coverage, test would need IPv4 connection (AF_INET branch) and simulated unexpected address family (die() branch)

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | UNCOVERED-AF_INET | AF_INET branch (lines 680-681) not covered: test focused on IPv6 (the affected code path). IPv4 test would cover it but does not test the fix. | Run an additional test with IPv4 connection to daemon. |
| coverage | UNCOVERED-DIE | die() branch (lines 686-687) not covered: requires getaddrinfo to return an unexpected address family, which cannot be triggered with normal network configuration. | Fault injection or simulated unexpected address family to cover this error path. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `test-entry-work/test-entry-verification.md` |
| coverage_data | `/tmp/pca-fixed-380484/daemon.c.gcov` |
| execution_results | `phase4_execution/` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/PCA-0001/reproducer.sh` |

## 建议

- Review any git daemon access hooks or scripts that parse the IP address argument for IPv6 connections
- Test with IPv4 connection to confirm AF_INET path still works correctly (expected: no regression)
- Review if any deployment uses 'probe' or 'ping' via daemon hostname interpolation (%IP) with IPv6 addresses
