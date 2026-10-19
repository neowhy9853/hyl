# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `2a95a616e9da16f49dfc55b11d7ca9f079bbb430` |
| 仓库 | `https://github.com/golang/go` |
| 基线 | `f192b5be2ef8f82e627e923ea72507c38b9f5ea5` |
| Profile | `golang` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁在 CrossOriginProtection.AddTrustedOrigin 中新增了对 userinfo 部分的检查，导致之前被接受的含 userinfo 的 origin 现在被拒绝。虽然浏览器不会发送含 userinfo 的 Origin 头（RFC 6454），但通过代码直接调用此 API 的调用方行为发生改变。补丁行覆盖率 100%，确认兼容性变更存在且被测试覆盖。错误消息文本也发生了变化（增加了 'userinfo' 字样），但影响较小。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 13 |
| 执行输入 | 13 |
| 契约通过 | 2 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 2 |
| 已覆盖行 | 2 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `Go 1.25.0 (bootstrap) → Go 1.28-devel (patched)` |
| 优化级别 | `default (Go compiler standard optimization)` |
| 覆盖率工具 | `go test -cover (Go built-in coverage)` |
- Before: Go 1.25.0 pre-built binary (has CrossOriginProtection but without userinfo check)
- After: Go built from patched worktree source (commit 2a95a616e9da) with Go 1.25.0 bootstrap
- Coverage collected via go test -coverprofile on net/http package with -run TestCrossOriginProtectionAddTrustedOriginErrors

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `src/net/http/csrf.go:68-69 (AddTrustedOrigin)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified_and_executed | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/test-entry-work/PCA-TE-0001/main.go` | `go run main.go` | userinfo origins (https://@example.com, https://user:pass@example.com) rejected in after build, accepted in before build | before: userinfo origins accepted (nil error); after: userinfo origins rejected with 'userinfo, path, query, and fragment are not allowed' error |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | Userinfo origins (https://@example.com, https://user:pass@example.com, https://user@example.com) were accepted before patch (nil error) but rejected after patch. This is the intended compatibility change — input contract tightened to reject origins with userinfo parts. |
| valid_acceptance_preserved | passed | Valid origins without userinfo (https://example.com, https://example.com:8080, http://example.com) are accepted by both before and after versions. |
| invalid_rejection_preserved | passed | Origins with path/query/fragment/missing-scheme/missing-host are rejected by both versions. Note: error message text changed from 'path, query, and fragment are not allowed' to 'userinfo, path, query, and fragment are not allowed'. |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | INPUT_CONTRACT_CHANGE | AddTrustedOrigin("https://@example.com") = <nil> (accepted) | AddTrustedOrigin("https://@example.com") = error: invalid origin "https://@example.com": userinfo, path, query, and fragment are not allowed | before_output.txt and after_output.txt show rejection change for 3 userinfo test cases |
| I2 | ERROR_EXCEPTION_CHANGE | invalid origin "https://example.com/": path, query, and fragment are not allowed | invalid origin "https://example.com/": userinfo, path, query, and fragment are not allowed | Error message text changed for path/query/fragment rejection cases — 'userinfo' added to error description |
- Confirmed INPUT_CONTRACT_CHANGE: origins with userinfo now rejected. Browsers never send userinfo in Origin headers per RFC 6454, so practical impact is limited to programmatic callers.
- Secondary ERROR_EXCEPTION_CHANGE: error message text changed for already-rejected inputs. Low practical impact.
- Coverage: 100% of patched lines reached. Both new lines (68, 69) are executed during test.

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/before_output.txt` |
| coverage_data | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/phase4_execution/coverage.out` |
| execution_results | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/phase4_execution/` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/test-entry-tasks.json` |
| report | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/test-entry-work/PCA-TE-0001/main.go` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P032/compatibility-testing/test-entry-work/PCA-TE-0001/main.go` |

## 建议

- 审查所有调用 AddTrustedOrigin 的代码，确认是否传入了含 userinfo 的 origin 字符串
- 如有代码依赖旧的错误消息文本（'path, query, and fragment are not allowed'），需更新到新文本（'userinfo, path, query, and fragment are not allowed'）
- 此变更为安全加固，建议尽快合并
