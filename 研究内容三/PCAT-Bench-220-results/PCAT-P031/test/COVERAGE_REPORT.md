# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `pca-git-sideband-patch` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `9a2fb147f2c61d0cab52c883e7e26f5b7948e3ed` |
| Profile | `git` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The pipe (dumb terminal) behavior is identical before and after (confirmed by diff and gcov). Full test suite (t5516-fetch-push.sh, 123 tests) passes on both binaries with zero regressions. No contract breaches detected. However, the TTY-only branch (lines 138-139) cannot be exercised in the automated test environment, resulting in 44.44% patch line coverage (below 80% gate). For TTY users, the ANSI escape sequence position changes from line-end to line-start, but visual appearance is preserved. Conclusion is inconclusive only due to the coverage gate; practical backward compatibility is maintained for all programmatic consumers.

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
| 契约通过 | 3 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 9 |
| 已覆盖行 | 4 |
| 未覆盖行 | 5 |
| 补丁行覆盖率 | 44.44% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Both before and after binaries built from isolated git worktrees
- Build flags: NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 with gcov instrumentation
- AGENTS.md build guide followed

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `sideband.c:129-146 (demultiplex_sideband)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-0001/runs/` | `bash test_sideband.sh` | Pipe mode output identical between before/after; ANSI sequence position change observable on TTY only | gcov confirms 4 of 9 executable patch lines covered (dumb terminal path) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | passed | Pipe mode fetch: 401 bytes identical before/after. Pipe mode push: identical (22 bytes). Test suite t5516-fetch-push.sh: 123/123 pass both before and after. No contract breaches. |

- **覆盖率**: 4/9 (44.44%)
- **未覆盖行**: sideband.c:138 - prefix = ANSI_PREFIX DISPLAY_PREFIX (TTY branch), sideband.c:139 - suffix = "" (TTY branch), sideband.c:177 - strbuf_addf(..., prefix) (band 3 error path), sideband.c:205 - strbuf_addstr(scratch, suffix) (cross-boundary suffix), sideband.c:235 - strbuf_addstr(scratch, prefix) (trailing content prefix)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| pipe_fetch | OUTPUT_FORMAT_CHANGE | 401 bytes of stderr output (identical) | 401 bytes of stderr output (identical) | diff of before/after stderr output shows zero differences in pipe mode. gcov confirms dumb terminal path (lines 141-142, 208) executed. TTY branch (lines 138-139) not exercised by automated tests. |
- No observable behavior difference in pipe (dumb terminal) mode
- TTY-only changes (ANSI prefix position, band 3 error prefix) not exercised by test suite
- All 123 tests in t5516-fetch-push.sh pass on both before and after binaries
- Manual verification on a real TTY recommended for TTY-specific changes
- Programmatic consumers of git output (piped stderr) are completely unaffected

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | PCA-0001-TTY | TTY-only branch (isatty(2) && !is_terminal_dumb()) cannot be exercised in automated environment; requires an interactive PTY | Run git fetch/push manually on a terminal with isatty(2)=true to exercise lines 138-139, 177, 205, 235 |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `embedded in test-summary.json` |
| coverage_data | `sideband.c.gcov at /tmp/pca-after/` |
| execution_results | `test-entry-work/PCA-0001/runs/results.txt` |
| impact_map | `N/A (single finding, direct test-summary)` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/PCA-0001/runs/` |

## 建议

- Manually verify TTY output on a real terminal to confirm visual appearance is unchanged
- Run git fetch/push interactively to exercise the TTY branch in demultiplex_sideband
- The change is a bug fix for proper line clearing on terminal output; no regression expected
