# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `efbecbbb465c99ed608b06d72fa1982122382d00` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go` |
| 基线 | `5005a2068bc525f0d209cea43601a7d3f0a8cde5` |
| Profile | `golang` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：All 4 patch executable lines covered (100%). All 16 LocalCertificate tests pass. Behavior comparison confirms pure additive API change: LocalCertificate field added to ConnectionState struct with no modification to existing fields or behaviors. TLS handshake now records the local certificate chain, which is exposed through the new field. Resumed connections correctly report nil. No contract breaches. Coverage gate (80%) met.

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
| 已覆盖行 | 4 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `go1.27-devel (bootstrapped with go1.24.6)` |
| 优化级别 | `default (Go compiler standard optimizations)` |
| 覆盖率工具 | `go test -coverprofile (Go built-in coverage)` |
- Baseline Go built from base_commit=5005a2068 using go1.24.6 bootstrap
- Patched Go built from patched worktree using go1.24.6 bootstrap
- Build attempt 1 failed: system Go 1.18.1 incompatible with Go 1.28 source
- Build attempt 2 failed: bootstrap requires Go >= 1.24.6
- Build attempt 3 succeeded: downloaded go1.24.6, bootstrapped both baseline and patched toolchains

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `src/crypto/tls/common.go:325-335 (ConnectionState)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-0001/` | `go test -coverprofile=coverage_iter2.out -coverpkg=crypto/tls -run 'TestHandshake\|TestResumption\|TestClientAuth\|TestLocalCertificate' crypto/tls` | exit code 0, LocalCertificate populated correctly, nil on resumed connections | All 16 TestLocalCertificate sub-tests pass; all 4 handshake patch lines covered at cov8 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | passed | Baseline ConnectionState has no LocalCertificate field. Patched version adds the field and populates it during non-resumed TLS handshakes. Additive change only; no existing fields or behaviors modified. Field is correctly nil (zero value) on resumed connections. |

- **覆盖率**: 4/4 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-TE-0001-I1 | SIDE_EFFECT_CHANGE | ConnectionState struct does not contain LocalCertificate field; accessing it causes compilation error | ConnectionState.LocalCertificate [][]byte is populated during TLS handshake (client+server, TLS 1.2+1.3), nil on resumed connections | Baseline grep confirms no LocalCertificate in common.go. Patched tests confirm field is populated with correct DER certificate chain. |
- Iteration 1: TestLocalCertificate + TestLocalCertificateResumption achieved 50% coverage (TLS 1.3 paths only, TLS 1.2 paths skipped due to MinVersion-only constraint)
- Iteration 2: Added TestHandshake + TestResumption + TestClientAuth achieved 100% coverage (all 4 handshake paths covered)
- All 16 TestLocalCertificate sub-tests pass in all TLS version/callback combinations

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_iter2.out` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- No mandatory actions. This is a pure additive API change consistent with Go 1 compatibility promise.
- Optional: downstream projects consuming ConnectionState may add LocalCertificate inspection if they need to know which certificate was presented to the peer.
