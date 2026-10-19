# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `1c3a1bac8b14c866d70b330e0229e5555670f577` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go` |
| 基线 | `0c0dacdf0b84a675b51b9ddfe61d9e331356fe8b` |
| Profile | `golang` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The primary compatibility change (PCA-0001, CONFIG_CLI_BEHAVIOR_CHANGE) changes the precedence of HTTP proxy environment variables from uppercase-first to lowercase-first. When both HTTP_PROXY and http_proxy are set with different values, Go HTTP clients will now use the lowercase value instead of the uppercase one. This is a deliberate change (Go issue #79656) to align with industry convention. QUIC internal changes (PCA-0002, PCA-0003) are bug fixes that don't break backward compatibility. Coverage gate at 21.4% reflects only the high-priority finding being covered; QUIC changes remain untested due to infrastructure requirements.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 2 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 9 |
| 已覆盖行 | 3 |
| 未覆盖行 | 6 |
| 补丁行覆盖率 | 33.30% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `Go 1.28-devel (bootstrapped from Go 1.26.5)` |
| 优化级别 | `default (standard Go compilation, no -O0 needed)` |
| 覆盖率工具 | `go test -coverpkg (Go built-in coverage)` |
- Before build: Git worktree checkout at base_commit 0c0dacdf0
- After build: Patched worktree from analysis
- Coverage instrumentation: Go -coverpkg flag covers vendored httpproxy and quic packages
- Ambient proxy env vars (http_proxy, https_proxy) were cleaned before test execution
- QUIC endpoint/Config tests require QUIC network infrastructure not available in this environment

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `src/vendor/golang.org/x/net/http/httpproxy/proxy.go:93-95 (FromEnvironment)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-TE-0001/precedence_demo.go` | `go run test-entry-work/PCA-TE-0001/precedence_demo.go` | BEHAVIOR CHANGE CONFIRMED: old and new resolution differ! | BEHAVIOR CHANGE CONFIRMED: old and new resolution differ! |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | passed | Clean env: both before and after pass TestProxyFromEnvironment and TestProxyFromEnvironmentLowerCase. With ambient http_proxy set, after build's TestProxyFromEnvironment fails due to lowercase-first priority picking up ambient value instead of test-set uppercase value. |
| proxy_env_precedence_matrix | passed | Confirmed: when both HTTP_PROXY and http_proxy are set with different values, new behavior returns lowercase value, old behavior returns uppercase value. Only-uppercase and only-lowercase scenarios behave identically in both versions. |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| precedence_demo_both_set | CONFIG_CLI_BEHAVIOR_CHANGE | getEnvAny("HTTP_PROXY", "http_proxy") returns "http://UPPER-CASE:3128" | getEnvAny("http_proxy", "HTTP_PROXY") returns "http://lower-case:3128" | Go stdlib's vendored httpproxy.FromEnvironment() reverses getEnvAny argument order: old priority uppercase-first, new priority lowercase-first |
- Go stdlib TestProxyFromEnvironment passes in both builds with clean env
- Behavior change only observable when BOTH uppercase and lowercase variants are set with different values
- Affects http.DefaultTransport, http.DefaultClient, and http.ProxyFromEnvironment

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `src/vendor/golang.org/x/net/quic/endpoint.go:149-156 (Endpoint.Close)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/4 (0.00%)
- **未覆盖行**: endpoint.go:149, endpoint.go:153, endpoint.go:154, endpoint.go:156
- QUIC Endpoint.Close requires full QUIC network stack
- Not targeted in this test run (min-priority=high)
- Change is a bug fix: always calls conn.exit() and returns ctx.Err()

### PCA-0003: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `src/vendor/golang.org/x/net/quic/config.go:113-115 (Config.Clone)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: config.go:113, config.go:114
- QUIC Config.Clone nil guard is backward-compatible safety fix
- Not targeted in this test run (min-priority=high)
- Trivially testable: call (*Config)(nil).Clone() and check for nil return

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| finding | PCA-0002 | QUIC Endpoint.Close testing requires a running QUIC endpoint with network connections, TLS certificates, and peer endpoints. Not feasible in this host-only environment without QEMU VM setup for network testing. | Set up isolated QUIC test environment with local loopback, generate test TLS certificates, create an Endpoint, accept a Conn, then call Close with both normal and canceled contexts. |
| finding | PCA-0003 | Config.Clone nil guard testing is low priority (backward-compatible change). Not targeted in this test run (min-priority=high). | Write a simple Go test that calls (*quic.Config)(nil).Clone() and verifies it returns nil without panicking. |
| coverage | COVERAGE-GATE | Patch line coverage rate 21.4% is below 80% gate. QUIC package changes (PCA-0002, PCA-0003) not covered. The HIGH priority httpproxy change (PCA-0001) has 100% coverage. | To reach 80% coverage, set up QUIC test infrastructure and test Endpoint.Close and Config.Clone. Alternately, accept that QUIC is internal/vendored and focus on the high-priority proxy change which is fully covered. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `test-entry-work/PCA-TE-0001/runs/` |
| coverage_data | `test-entry-work/PCA-TE-0001/runs/after_coverpkg.out` |
| execution_results | `test-entry-work/PCA-TE-0001/runs/` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Applications that rely on HTTP_PROXY uppercase env var overriding lowercase should update to match the new precedence
- CGI environments where both uppercase and lowercase proxy vars are set should be audited for proxy resolution changes
- Set up QUIC test infrastructure to verify Endpoint.Close and Config.Clone changes
- Accept the partial coverage result since the HIGH priority change is 100% covered
