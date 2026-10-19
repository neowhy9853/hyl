# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `e2164742` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `22b2f3d2a319af32e9f3add0b3cc7732cbf4733b` |
| Profile | `git` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Confirmed INPUT_CONTRACT_CHANGE breach: --negotiation-restrict no longer dies on invalid refs (exit 128 -> exit 0). API signature change to negotiate_using_fetch with all in-tree callers updated. Two additive ABI-only struct changes.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 3 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 104 |
| 已覆盖行 | 100 |
| 未覆盖行 | 4 |
| 补丁行覆盖率 | 96.15% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (GCC)` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Built with NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1
- Detached worktrees at /tmp/pca-git-before and analysis_repo
- CFLAGS=-O0 -g --coverage

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `builtin/fetch.c:1535-1563 (add_negotiation_tips)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing` | `git fetch --negotiation-restrict=nonexistent-ref .` | exit 0 (new behavior: silently ignore invalid ref) | gcov: fetch.c:1555-1556 (continue path) hit 3 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | Old behavior (before build): exit 128 with fatal error. New behavior (after build): exit 0, silently ignores invalid ref. Contract RELAXATION: previously git fetch --negotiation-restrict=bad-ref would die; now it silently continues. |

- **覆盖率**: 42/42 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I-PCA-0001 | INPUT_CONTRACT_CHANGE | fatal: no-such-ref is not a valid object (exit 128) | command succeeds (exit 0), invalid ref silently ignored | gcov confirms continue path at builtin/fetch.c:1555-1556 was hit 3 times |
- t5510-fetch.sh test 202 covers new behavior
- Contract breach confirmed via before/after binary comparison

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `fetch-pack.h:94-101 (negotiate_using_fetch)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | passed | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing` | `make git (compile-link verification)` | Build succeeds with new parameter | gcov: transport.c:467 executed 50 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | passed | All in-tree callers (transport.c:495-500) updated. Build succeeds. |

- **覆盖率**: 10/11 (90.91%)
- **未覆盖行**: fetch-pack.c:2242-2290 (negotiate_using_fetch body)
- New parameter appended. Passing NULL preserves old behavior.
- All 226 t5510-fetch.sh tests pass.

### PCA-0003: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `fetch-pack.h:19-28 (fetch_pack_args)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | passed | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing` | `make git (compile check)` | Build succeeds | Compile-time verification |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| struct_size_stability | passed | Additive field. struct fetch_pack_args size +1 pointer. Pointer-based code unchanged. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- Compile-time ABI change.

### PCA-0004: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `transport.h:40-53 (git_transport_options)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0004 | passed | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing` | `make git (compile check)` | Build succeeds | gcov: transport.c:467 executed 50 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| struct_size_stability | passed | Additive field to public header transport.h. struct size +1 pointer. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- Compile-time ABI change.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | PCA-0002-body | negotiate_using_fetch body requires --negotiate-only with protocol v2 and wait-for-done server support, not exercised by t5510-fetch.sh | Test with --negotiate-only against a protocol v2 server |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/_worktrees/patched/fetch.c.gcov` |
| execution_results | `` |
| impact_map | `` |
| report | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `` |

## 建议

- Review scripts using --negotiation-restrict/--negotiation-tip with potentially invalid refs
- Update external consumers of negotiate_using_fetch() to pass NULL for new param
- Consider adding --strict-negotiation-validation for users wanting old behavior
