# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `5bbd22ff78daf010c5bd19c466a0c45ac78503d4` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go` |
| 基线 | `c19862e5f8415b4f24b189d065ed739517c548ba` |
| Profile | `golang` |
| 执行状态 | `blocked` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：静态分析确认 SIDE_EFFECT_CHANGE：ReadHeaderTimeout 配置项的有效范围扩大至非加密 HTTP/2 客户端前言检测阶段。此前此阶段无超时限制，补丁后受 ReadHeaderTimeout 约束。这是 CVE-2026-56853 的安全修复，属于有意向后不兼容变更。动态测试因缺少 Go 1.24.6+ 引导工具链而无法执行构建和覆盖测试。补丁中新增的 TestServerUnencryptedHTTP2HeaderTimeout 测试覆盖了关键场景（客户端无响应、缓慢发送前言、请求头超时），可作为回归测试运行。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 3 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 10 |
| 已覆盖行 | 0 |
| 未覆盖行 | 10 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `blocked` |
| 补丁后构建 | `blocked` |
| 编译器 | `Go bootstrap required (go1.24.6+)` |
| 优化级别 | `N/A` |
| 覆盖率工具 | `N/A` |
- System Go is go1.18.1. Go 1.26 release branch requires go1.24.6+ as bootstrap toolchain (src/cmd/dist/notgo124.go)
- No suitable Go bootstrap binary found on system. Download go1.24.6+ from https://go.dev/dl/ to proceed with build.
- Alternatively, use a pre-built Go toolchain from the release-branch.go1.26 CI artifacts.

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `src/net/http/server.go:1970-1980 (c.serve)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | needs_env | `test-entry-work/PCA-0001/run_native_test.sh` | `GOROOT=<patched-goroot> <patched-goroot>/bin/go test -v -run 'TestServerUnencryptedHTTP2HeaderTimeout' -count=1 -timeout=120s net/http` | PASS: All subtests pass (client sends nothing, client sends slowly, header read expires) | Test exercises conn.serve() -> maybeServeUnencryptedHTTP2() path with ReadHeaderTimeout deadline set. The test assertion `time.Since(start) == srv.ReadHeaderTimeout` confirms the timeout deadline is active. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| unencrypted_http2_header_timeout | skipped | Contract verification skipped: Cannot build Go from source without go1.24.6+ bootstrap. The contract would verify: (1) ReadHeaderTimeout is applied before HTTP/2 preface Peek(), (2) connections without HTTP/2 preface are closed after ReadHeaderTimeout, (3) slow preface writes do not extend the deadline. |

- **覆盖率**: 0/10 (0.00%)
- **未覆盖行**: src/net/http/server.go:980, src/net/http/server.go:1041, src/net/http/server.go:1974, src/net/http/server.go:1975, src/net/http/server.go:1976, src/net/http/server.go:2107, src/net/http/server.go:2108, src/net/http/server.go:2109, src/net/http/server.go:2110, src/net/http/server.go:2111
- Patch adds TestServerUnencryptedHTTP2HeaderTimeout which exercises 3 scenarios: client-sends-nothing (times out), client-sends-slowly (deadline not extended), header-read-expires (time counts against ReadHeaderTimeout)
- The test uses testing/synctest for deterministic time control in Go tests
- Build blocked: Go 1.26 requires go1.24.6+ as bootstrap (notgo124.go: Go 1.26 and later requires Go 1.24.6 as the minimum bootstrap toolchain)
- System has go1.18.1 which is insufficient. To proceed: install go1.24.6+ or use a pre-built Go toolchain.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCK-BOOTSTRAP-GO124 | Go 1.26 release branch (base commit c19862e5f) requires go1.24.6+ as bootstrap toolchain. System Go is go1.18.1. Building from source is blocked without a suitable GOROOT_BOOTSTRAP. | Install Go 1.24.6 or later: download from https://go.dev/dl/, extract to a location, and pass GOROOT_BOOTSTRAP=/path/to/go1.24.6 to the build. |
| build | BLOCK-BUILD-GO126 | The patched Go toolchain must be built from source to run tests that exercise the standard library's net/http server behavior changes. | Build Go from the patched worktree: cd <analysis_repo>/src && GOROOT_BOOTSTRAP=/path/to/go1.24.6 ./make.bash |
| coverage | BLOCK-COVERAGE | Coverage instrumentation requires a built Go toolchain. Go's coverage tool (go test -cover) requires the standard library to be built with coverage support. | Build Go with coverage flags: go test -cover -coverpkg=net/http -run TestServerUnencryptedHTTP2HeaderTimeout net/http |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `` |
| execution_results | `` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `` |

## 建议

- 安装 Go 1.24.6+ 引导工具链后构建补丁后 Go，运行 TestServerUnencryptedHTTP2HeaderTimeout 验证超时行为
- 对已部署 UnencryptedHTTP2 的生产服务器，审核 ReadHeaderTimeout 配置以确保其值在当前语义下合适
- 若需独立控制 HTTP/2 前言检测超时和请求头读取超时，考虑引入新配置项（如 H2PrefaceTimeout）
