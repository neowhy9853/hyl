# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `c090f1d17b280c98630914334d341a2fa3318117` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnsmasq` |
| 基线 | `fa48bdb939c34213cac8b92db0f070ceeb69e51e` |
| Profile | `dnsmasq` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch introduces a resource lifetime change (PCA-0001) and side effect change (PCA-0002) for DNSSEC TCP child processes. These changes add a CHILD_LIFETIME (150s) timeout via alarm() to prevent DNSSEC TCP children from hanging indefinitely, and add a PIPE_OP_KILLED notification mechanism to unblock the parent when timeout occurs. While both changes are bug fixes (fixing a DoS vector where DNSSEC TCP children could hang forever), they modify the resource lifecycle and internal IPC protocol. The changes affect the dns_protocol surface - a DNS client that would previously hang forever now receives a STAT_ABANDONED response after ~150s. Dynamic testing was blocked by the lack of a controlled network environment to create a DNSSEC TCP timeout scenario. Both binaries build and start correctly with identical compile-time options.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 0 |
| 规划输入 | 10 |
| 执行输入 | 2 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 22 |
| 已覆盖行 | 0 |
| 未覆盖行 | 22 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov` |
- Both before (fa48bdb) and after (c090f1d) binaries built successfully with CFLAGS='-Wall -W -O0 -g --coverage' LDFLAGS='--coverage' COPTS='-DHAVE_DNSSEC'
- Both binaries produce 42 .gcno files each (identical count)
- DNSSEC, DHCP, DHCPv6 features enabled in both builds
- Full DNSSEC TCP forwarding timeout test requires a controlled network environment with an upstream that accepts TCP but never replies, which cannot be created in the current sandbox (no network namespace or container privileges)

## Finding 测试结果

### PCA-0001: RESOURCE_LIFETIME_CHANGE

- **优先级**: `medium`
- **状态**: `blocked`
- **目标**: `src/dnsmasq.c:2262-2273 (swap_to_tcp)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-0001 | blocked | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/test-entry-work/PCA-0001` | `timeout 200 bash run_test.sh` | TCP process for DNSSEC validation timed out | CHILD_LIFETIME timeout triggers SIGALRM → PIPE_OP_KILLED |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| resource_lifetime_duration | skipped | Requires controlled network environment with an upstream DNS server that accepts TCP but never replies. Without network namespace/container, cannot set up the required upstream black-hole TCP listener. |

- **覆盖率**: 0/7 (0.00%)
- **未覆盖行**: src/dnsmasq.c:2265 alarm(CHILD_LIFETIME), src/dnsmasq.c:2266 close(daemon->netlinkfd), src/dnsmasq.c:2267 read_write(pipefd[1], &a, 1, RW_WRITE), src/dnsmasq.c:2268 daemon->pipe_to_parent = pipefd[1], src/dnsmasq.c:2269 daemon->forward_to_tcp = forward, src/dnsmasq.c:2270 daemon->header_to_tcp = header, src/forward.c:2243 daemon->forward_to_tcp = NULL
- GCov confirms all changed lines are marked ##### (not covered) during basic startup test
- The alarm(CHILD_LIFETIME) call is only reachable when swap_to_tcp() forks a child for DNSSEC TCP forwarding
- The forward_to_tcp = NULL guard in forward.c is only reachable after a successful TCP DNSSEC exchange
- Before/after binary comparison: --version shows expected version string difference, --help output is identical

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `blocked`
- **目标**: `src/dnsmasq.c:1335-1376 (sig_handler)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-0002 | blocked | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/test-entry-work/PCA-0002` | `Same as PCA-0001 (concurrent test - both findings triggered by same timeout scenario)` | PIPE_OP_KILLED sent through pipe, parent processes STAT_ABANDONED | Child calls read_write() with PIPE_OP_KILLED before _exit(0) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest | skipped | Same dependency as PCA-0001. The SIGALRM handler changes are only exercised when a DNSSEC TCP child times out, which requires the same controlled network environment. |

- **覆盖率**: 0/15 (0.00%)
- **未覆盖行**: src/dnsmasq.c:1338 daemon->pipe_to_parent != -1 (SIGALRM child detection), src/dnsmasq.c:1344 forward_to_tcp check, src/dnsmasq.c:1346 _exit(0) for normal TCP child, src/dnsmasq.c:1355 daemon->header_to_tcp check, src/dnsmasq.c:1357 op = PIPE_OP_KILLED assignment, src/dnsmasq.c:1358 status = STAT_ABANDONED assignment, src/dnsmasq.c:1360-1365 read_write calls for PIPE_OP_KILLED notification, src/dnsmasq.c:1367 my_syslog timeout message, src/dnsmasq.c:1369 _exit(0), src/cache.c:1002-1003 case PIPE_OP_KILLED label, src/cache.c:1013-1017 read_write for status/ret_len/packet/forward/uid, src/cache.c:1020-1024 PIPE_OP_RESULT conditional read, src/cache.c:1030 uid == forward->uid check, src/cache.c:1032 op == PIPE_OP_RESULT work counter guard, src/cache.c:1039-1040 return_reply / pop_and_retry_query
- All SIGALRM handler changed lines marked ##### (not covered) during startup test
- The sig_handler changes only activate when SIGALRM is delivered to a TCP child process with daemon->forward_to_tcp set
- The child detection change from pid != getpid() to daemon->pipe_to_parent != -1 is a minor behavioral refinement

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | ENV-0001 | Full DNSSEC TCP timeout test requires a controlled network environment with an upstream DNS server that accepts TCP connections but never replies. This requires network namespace or container capabilities not available in the current sandbox. | Set up a controlled upstream TCP black-hole listener (e.g., nc -l -p 53 in a network namespace) and configure dnsmasq to forward to it. Run dnsmasq with DNSSEC enabled, send a query with DO bit that triggers TCP forwarding (e.g., a query where the response is truncated), and observe the 150s timeout behavior. |
| environment | ENV-0002 | The 150s CHILD_LIFETIME timeout makes automated testing time-consuming. Each timeout test iteration takes ~150s. | Accept the time cost or temporarily lower CHILD_LIFETIME in config.h to a smaller value (e.g., 5 seconds) for testing purposes. |
| entry | ENTRY-0001-BLOCKED | PIPE_OP_KILLED is internal IPC between parent and child processes. Direct observation requires strace -e trace=write on the child process or kernel-level tracing. | Run dnsmasq under strace with -f flag to trace child write() calls. Filter for the fd corresponding to the pipe and look for op=6 (PIPE_OP_KILLED) byte. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/phase4_execution/coverage_results.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Set up a controlled upstream TCP black-hole listener to verify the timeout behavior
- Temporarily reduce CHILD_LIFETIME to 5s for rapid automated testing
- Run strace -f on the child process to confirm PIPE_OP_KILLED (op=6) write() on the pipe before _exit(0)
- Verify the syslog message 'TCP process for DNSSEC validation timed out' appears in daemon logs
- Use gcov to confirm all changed lines are exercised (src/dnsmasq.c:2265, src/dnsmasq.c:2268-2270, src/cache.c:1002-1040, src/dnsmasq.c:1344-1373, src/forward.c:2243)
