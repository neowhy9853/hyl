# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `pca_patch_e61190` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `3fbef193c7e49e8edb5a4421c465df67de944da6` |
| Profile | `git` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The single compatibility change (OUTPUT_FORMAT_CHANGE for the usage string) is a minor, intentional text update that adds two new subcommand names to the error message. The exit code (1), output channel (stderr), and all behavioral contracts other than exact string content are preserved. The commit does not break any existing usage patterns. Downstream consumers that parse the exact usage string text may need to update their patterns, but the semantic contract (exit code 1 on error, error output on stderr) is unchanged.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 1 |
| 执行输入 | 1 |
| 契约通过 | 2 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 1 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `tclsh (wish for GUI)` |
| 优化级别 | `N/A (Tcl script, no compilation needed)` |
| 覆盖率工具 | `not_applicable` |
- git-gui.sh is a Tcl/Tk script - no compilation or gcov coverage needed
- Before/after worktrees created at /tmp/pca-git-before and /tmp/pca-git-after
- Tcl runtime usage test executed via standalone Tcl harness
- Source-level verification confirms the string change in git-gui.sh
- Full Tk GUI test blocked by no interactive display (tk_messageBox blocks with xvfb)

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `git-gui.sh:3130-3130 (usage)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E-PCA-0001-001 | passed | `/tmp/test_usage_after.tcl` | `tclsh /tmp/test_usage_after.tcl` | Usage string contains '{blame\|browser\|citool\|gui\|pick}', exit 1 | USAGE_STRING: usage: git-gui [{blame\|browser\|citool\|gui\|pick}] |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | Usage string changed from '{blame\|browser\|citool}' to '{blame\|browser\|citool\|gui\|pick}' |
| exit_code_preserved | passed | Exit code 1 in both versions |
| output_channel_preserved | passed | stderr used in both versions |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | usage: git-gui [{blame\|browser\|citool}] | usage: git-gui [{blame\|browser\|citool\|gui\|pick}] | git-gui.sh line 3113 (before) vs line 3130 (after); confirmed by Tcl runtime test |
- The output format breach is expected and intentional - the commit adds gui and pick as explicit subcommands
- The exit code contract (always 1) and output channel (stderr) are preserved
- All executable patch lines (the changed line in the default case) are covered by the test
- Full GUI execution via wish+Tk blocked by interactive display requirement

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | COV-0001 | git-gui.sh is a Tcl/Tk script; gcov coverage instrumentation is not applicable. Source-line verification is sufficient. | N/A |
| entry | GUI-0001 | Full git-gui.sh Tk GUI execution requires an interactive X11 display. xvfb-run starts but tk_messageBox blocks waiting for user input. | Run on a machine with interactive display, or modify test to use non-blocking Tk stubs |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `source_line_verification (no gcov)` |
| execution_results | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Review any wrapper scripts or documentation that match the exact usage string '{blame\|browser\|citool}'
- Update integration tests that assert on the exact subcommand list in error output
- No semantic breakage expected for end users
