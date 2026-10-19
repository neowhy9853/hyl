# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `4b5d8a0163fe4e9a4ac074f407e0599ba27acf68` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `42d960748efa79a31e72cc36d983aca244dc167e` |
| Profile | `git` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Patch expands format allowlist for -L from PATCH\|NO_OUTPUT to also include RAW, NAME, NAME_STATUS, and SUMMARY. This is an additive/relaxing change: previously erroring CLI combinations now produce correct output. No regressions detected. All 95 t4211-line-log.sh tests pass. Coverage confirms changed code paths exercised. Blocked stat formats remain correctly blocked.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 1 |
| 契约违约 | 0 |
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
| 编译器 | `gcc (gcov)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov` |
- Host: 2026-07-23, ref ea97ad8d0
- C toolchain, curl, OpenSSL, expat, zlib, Perl, Tcl/Tk present
- Built with NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1
- CFLAGS="-O0 -g --coverage" LDFLAGS="--coverage"

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `revision.c:3181-3189 (setup_revisions)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-0001 | passed | `/tmp/pca-git-after/t/t4211-line-log.sh` | `make -C t -j4 NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 t4211-line-log.sh` | All 95 tests pass (88 baseline + 7 new format tests) | gcov: revision.c line 3181 hit 174 times, line 3187 hit 5 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | passed | Before: git log -L --raw/--name-only/--name-status/--summary dies with "-L does not yet support the requested diff format". After: same commands produce correct metadata-only output. Blocked formats (--stat/--numstat/--shortstat/--dirstat) correctly continue to produce error. |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | CONFIG_CLI_BEHAVIOR_CHANGE | fatal: -L does not yet support the requested diff format | :100644 100644 <oid> <oid> M	file.txt<br>:000000 100644 0000000 <oid> A	file.txt | Contract verification run with git.before and git.after on test repo at /tmp/pca-test-verify/testrepo |
- Additive/relaxing change: previously erroring option combinations now produce output
- All 95 t4211-line-log.sh tests pass (88 before + 7 new format tests)
- gcov confirms guard condition hit 174 times, die fired 5 times (blocked formats)
- Expression continuation lines (3184-3186) marked non-executable by gcov
- Blocked formats continue to produce correct error

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/git/pca-results/4b5d8a/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- No further action required for this patch - additive change with no compatibility impact
- Monitor any user scripts that explicitly tested for git log -L --raw failing
