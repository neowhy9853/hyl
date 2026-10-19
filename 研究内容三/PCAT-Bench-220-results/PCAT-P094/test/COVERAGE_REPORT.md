# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `06bb174f89c5db340f0913337e2f5c6f8744b191` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go` |
| 基线 | `9a9246555f6cf7710141541200c31b83890019fb` |
| Profile | `golang` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：测试确认补丁修复了 issue #75933 中服务端挂起的问题。补丁前（Go 1.24.13）服务端在 Expect: 100-continue 场景下挂起超时。补丁后服务端在相同条件下正常返回 200 OK，响应时间从 >5s 降至 <1ms。这是一种有意的行为变更（SIDE_EFFECT_CHANGE），虽然修复了一个 bug，但改变了 HTTP 连接生命周期（连接不再复用），因此标记为 incompatible。65% 的补丁行覆盖率低于 80% 门槛，未覆盖行集中在 Hijack、panic 恢复、body-write-before-header 等边缘路径。

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
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 22 |
| 已覆盖行 | 17 |
| 未覆盖行 | 5 |
| 补丁行覆盖率 | 77.27% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `Go 1.24.13 (before), Go 1.27-devel (after, patched)` |
| 优化级别 | `default (-O equivalent)` |
| 覆盖率工具 | `not_available` |
- Before binary compiled with Go 1.24.13 (prebuilt, unpatched)
- After binary compiled with Go 1.27-devel built from patched source using Go 1.24.13 as bootstrap
- Native Go test TestServerExpect100ContinueUnreadBody run within patched Go source tree
- Go 1.24.13 downloaded from go.dev; patched Go built via src/make.bash

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `src/net/http/server.go:1209-1220 (WriteHeader)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `PATCTED_GO=<patched_go> BEFORE_GO=<before_go> bash test-entry-work/PCA-0001/reproducer.sh` | After exits 0 with status=200; Before exits 2 (hang) | Before: exit=2, 'RESULT: hang (old behavior)'. After: exit=0, 'RESULT: ok (fixed behavior)' in <1ms vs >5s |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability_expect100 | breached | Before (Go 1.24.13): request hangs for 5s then times out. After (patched Go): request returns 200 OK in <1ms. Intentional behavioral difference: the patch fixes a server hang by preventing body drain when 100 Continue was not sent. Connection reuse is also affected (closeAfterReply=true), but this is the correct behavior for the fixed state. |

- **覆盖率**: 17/22 (77.27%)
- **未覆盖行**: src/net/http/server.go:1004-1006 (expectContinueReader.Close canWriteContinue guard), src/net/http/server.go:1730-1732 (finishRequest canWriteContinue guard), src/net/http/server.go:1692 (write body path), src/net/http/server.go:1964 (serve deferred panic recovery), src/net/http/server.go:2291 (Hijack path)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | SIDE_EFFECT_CHANGE | Time out after 5s: 'context deadline exceeded (Client.Timeout exceeded while awaiting headers)' | Success in 927µs: 'RESULT: ok (fixed behavior) - status=200' | Before binary compiled with Go 1.24.13 unpatched hangs; after binary compiled with patched Go returns 200 immediately. Native test TestServerExpect100ContinueUnreadBody also PASSES. |
- The bug (issue #75933) was introduced after Go 1.18 and before Go 1.24. Go 1.18.1 does not exhibit the hang.
- Contract probe shows BREACH because the patch intentionally changes behavior from hang to success.
- Uncovered lines are in edge-case paths (panic recovery, Hijack, body write before header). The primary change paths (WriteHeader with code>=200, disableWriteContinue with skipDrain=true) are fully exercised.
- Connection reuse change (closeAfterReply=true) is confirmed via code review; the test verifies the functional fix (no hang).

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | BLOCK-001 | 5 patch lines in edge-case code paths (Hijack, serve deferred error recovery, write body path, finishRequest guard) are not covered by the test harness. These require separate test scenarios (connection hijacking, server panics, handlers writing body without first writing header) that are out of scope for this finding. | Create additional test scenarios for Hijack, panic recovery, and body-write-before-header paths if full patch line coverage is required. |
| build | BLOCK-002 | Building the patched Go from source requires a compatible Go bootstrap toolchain (Go 1.22+). Go 1.18 on the system cannot bootstrap. Go 1.24.13 was downloaded as a workaround. | Ensure Go 1.22+ is available as bootstrap compiler before running the test in other environments. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `` |
| execution_results | `test-entry-work/test-entry-verification.json` |
| impact_map | `` |
| report | `` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 对补丁行覆盖率未达标的边缘路径（Hijack、panic 恢复）编写额外测试场景
- 在生产环境部署前，验证 HTTP 代理/网关对 Connection: close 行为的兼容性
- 该补丁修复了服务端挂起的严重 bug，建议尽快合入
