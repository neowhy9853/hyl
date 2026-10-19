# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `42d960748efa79a31e72cc36d983aca244dc167e` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `558057cf4f43ea3b28c5e0b1b2250cab362f1a6a` |
| Profile | `git` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch introduces 3 confirmed compatibility changes: (1) OUTPUT_FORMAT_CHANGE (medium): blank-line separator removed in git log -L output - affects scripts parsing -L output. (2) CONFIG_CLI_BEHAVIOR_CHANGE (low): --full-diff now rejected with -L. (3) OUTPUT_FORMAT_CHANGE (low): pickaxe/diff-filter now properly filter commits with -L. All changes are intentional (per commit message) and improve correctness. Coverage: 100% (19/19 patch executable lines). Regression: 88/88 tests pass on patched vs 80/83 on baseline.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 3 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 1 |
| 契约违约 | 2 |
| 契约跳过 | 0 |
| 补丁可执行行 | 19 |
| 已覆盖行 | 19 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (GCC)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov` |
- NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 used for reproducible builds
- CFLAGS="-O0 -g --coverage" LDFLAGS="--coverage"
- Detached /tmp worktrees used for baseline and patched builds per AGENTS.md

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `line-log.c:1003-1020 (line_log_queue_pairs)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-PCA-0001 | passed | `t/t4211-line-log.sh` | `git log -L:func2:file.c --oneline -1` | No blank line between commit header and diff | line_log_queue_pairs() executed (• 196 calls from gcov) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | Before: blank line present between commit header and diff. After: no blank line. Test repo used: /tmp/pca-compare. |

- **覆盖率**: 7/7 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | printed blank line ("<br>") between commit header and diff using fprintf(rev->diffopt.file, "%s<br>", prefix) in line_log_print() | no blank line; show_log() and separator emission deferred to log_tree_diff_flush() | diff confirms blank line removed: before has blank line on line 2, after starts diff on line 2 |
- Output difference confirmed via before/after binary comparison
- gcov: 196 calls to line_log_queue_pairs(), all patch lines covered
- Regression test: t4211 test 88 "-L --oneline has no extra blank line before diff" passes

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `revision.c:3179-3188 (setup_revisions)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-PCA-0002 | passed | `revision.c` | `git log -L1,24:b.c --full-diff` | fatal error and exit code 128 | die() in setup_revisions executed (2 calls from gcov on line 3185) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | breached | Before: command succeeds (exit 0) and shows diff output. After: fatal error (exit 128) with message "-L does not yet support the requested diff format". |

- **覆盖率**: 5/5 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2 | CONFIG_CLI_BEHAVIOR_CHANGE | git log -L --full-diff succeeds (exit 0) and shows diff output for range | git log -L --full-diff fails with fatal error (exit 128) | Before: 22 lines of output + EXIT:0. After: "fatal: -L does not yet support the requested diff format" + EXIT:128 |
- Behavior confirmed via before/after binary comparison
- gcov: 2 die() calls on line 3185 confirm the rejection path was exercised
- Regression test: t4211 test 87 "--full-diff is not yet supported with -L" passes

### PCA-0003: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `log-tree.c:1185-1190 (log_tree_commit)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-PCA-0003 | passed | `t/t4211-line-log.sh` | `git log -L:func2:file.c --diff-filter=M --format=%s --no-patch` | Filter works: only Modify commit shown | log_tree_commit() + line_level_traverse path in log-tree.c (260 calls) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | Before: 2 commits shown (Add + Modify), filter not working. After: 1 commit shown (Modify only), filter works correctly. |

- **覆盖率**: 7/7 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I3 | OUTPUT_FORMAT_CHANGE | 2 commits shown (--diff-filter=M had no effect, both Add and Modify commits displayed) | 1 commit shown (--diffilter=M correctly excludes the root Add commit) | Before output line count: 2 ("Modify func2() in file.c" + "Add func1() and func2() in file.c"). After output line count: 1 ("Modify func2() in file.c" only) |
- Behavior confirmed via before/after binary comparison
- gcov: 260 calls to log_tree_commit(), 227 line_level_traverse checks, all patch lines covered
- Regression test: t4211 tests 84-86 for --diffilter and -S pass
- 3 tests that were test_expect_failure in baseline are now test_expect_success

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/tmp/pca-patched/line-log.c.gcov,/tmp/pca-patched/log-tree.c.gcov,/tmp/pca-patched/revision.c.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Review scripts that parse git log -L output for blank-line dependencies
- Check for any scripts/aliases using git log -L --full-diff (will now error)
- Verify that the new pickaxe/diff-filter behavior with -L is correct for your workflow
- The blank-line change is the highest-impact item (medium priority) - test any downstream parsers
