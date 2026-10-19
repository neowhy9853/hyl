# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `3fbef193c7e49e8edb5a4421c465df67de944da6` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `7c7c7ba4cea2f0063efa2a2a0d7c3d05ed8766fb` |
| Profile | `git` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Confirmed 6 contract breaches across 2 findings. Path-before-rev argument ordering removed (PCA-0001). Stricter input validation with git rev-parse and git ls-tree (PCA-0001). Error handling improved with show_parse_err (PCA-0002). Coverage gate not met because gcov is inapplicable to Tcl scripts; behavioral verification was used instead.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 6 |
| 契约跳过 | 0 |
| 补丁可执行行 | 110 |
| 已覆盖行 | 0 |
| 未覆盖行 | 110 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (gcov)` |
| 优化级别 | `O0` |
| 覆盖率工具 | `N/A (Tcl script, behavioral comparison used)` |
- Patch modifies git-gui.sh (Tcl/Tk script). Line-level gcov coverage not applicable.
- xvfb-run used for virtual display (no physical X server).
- Build with NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 per AGENTS.md.
- Before worktree: /tmp/pca-before-3fbef1 (commit 7c7c7ba4c)
- After worktree: /tmp/pca-after-3fbef1 (commit 3fbef193c)

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `git-gui.sh:2999-3103 (selected_paths)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/test-entry-work/PCA-TE-0001` | `cd <test-repo> && xvfb-run -a <git-gui.sh> blame\|browser <args>` | Before: exit 124 (timeout - GUI opens for invalid args); After: exit 1 with error message | Error message on stderr containing rev/path validation error |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | Path-before-rev ordering removed. Old parser accepted 'git gui blame <path> <rev>', new parser rejects it with 'not a valid rev' error. |
| rev_validation | breached | Old parser only validated hex-looking revs. New parser validates ALL revs with git rev-parse --verify. |
| path_validation | breached | Old parser did not validate path existence in target rev. New parser uses git ls-tree to verify path exists. |

- **覆盖率**: 0/63 (0.00%)
- **未覆盖行**: git-gui.sh:line-3002, git-gui.sh:line-3003, git-gui.sh:line-3004, git-gui.sh:line-3005, git-gui.sh:line-3006, git-gui.sh:line-3007, git-gui.sh:line-3008, git-gui.sh:line-3009, git-gui.sh:line-3010, git-gui.sh:line-3011, git-gui.sh:line-3012, git-gui.sh:line-3013, git-gui.sh:line-3014, git-gui.sh:line-3015, git-gui.sh:line-3016, git-gui.sh:line-3017, git-gui.sh:line-3018, git-gui.sh:line-3019, git-gui.sh:line-3020, git-gui.sh:line-3021, git-gui.sh:line-3022, git-gui.sh:line-3023, git-gui.sh:line-3024, git-gui.sh:line-3025, git-gui.sh:line-3026, git-gui.sh:line-3027, git-gui.sh:line-3028, git-gui.sh:line-3029, git-gui.sh:line-3030, git-gui.sh:line-3031, git-gui.sh:line-3032, git-gui.sh:line-3033, git-gui.sh:line-3034, git-gui.sh:line-3035, git-gui.sh:line-3036, git-gui.sh:line-3037, git-gui.sh:line-3038, git-gui.sh:line-3039, git-gui.sh:line-3040, git-gui.sh:line-3041, git-gui.sh:line-3042, git-gui.sh:line-3043, git-gui.sh:line-3044, git-gui.sh:line-3045, git-gui.sh:line-3046, git-gui.sh:line-3047, git-gui.sh:line-3048, git-gui.sh:line-3049, git-gui.sh:line-3050, git-gui.sh:line-3051, git-gui.sh:line-3052, git-gui.sh:line-3053, git-gui.sh:line-3054, git-gui.sh:line-3055, git-gui.sh:line-3056, git-gui.sh:line-3057, git-gui.sh:line-3058, git-gui.sh:line-3059, git-gui.sh:line-3060, git-gui.sh:line-3061, git-gui.sh:line-3062, git-gui.sh:line-3063, git-gui.sh:line-3064

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | INPUT_CONTRACT_CHANGE | exit 124 (timeout - opens blame GUI, accepts path-before-rev ordering) | exit 1 - 'fatal: test-file.txt is not a valid rev' | Path-before-rev ordering ('git gui blame <path> <rev>') accepted in before, rejected in after |
| I2 | INPUT_CONTRACT_CHANGE | exit 124 (timeout - accepts extra argument) | exit 1 - error/usage message | Extra argument silently accepted in before, rejected with error in after |
| I3 | INPUT_CONTRACT_CHANGE | exit 124 (timeout - accepts --line= as non-first arg) | exit 1 - usage message | --line= position strict enforcement in after, loose in before |
| I4 | INPUT_CONTRACT_CHANGE | exit 124 (timeout - opens blank blame window) | exit 1 - '<path> is not a filename in rev <rev>' | Non-existent path with explicit rev in before had no ls-tree validation; after validates with git ls-tree |
| I5 | INPUT_CONTRACT_CHANGE | exit 124 (timeout - no rev validation) | exit 1 - 'fatal: <rev> is not a valid rev' | Invalid rev silently accepted in before; after rejects with git rev-parse --verify |
- 5 test inputs executed with before/after comparison.
- All 5 show behavioral differences confirming INPUT_CONTRACT_CHANGE.
- Coverage not applicable (Tcl script).

### PCA-0002: ERROR_EXCEPTION_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `git-gui.sh:3002-3010 (show_parse_err)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | verified | `manual` | `cd <test-repo> && xvfb-run -a <git-gui.sh> browser <non-existent-path>` | Before: exit 124 (blank browser window); After: exit 1 with error message | Error message on stderr: path not found in rev |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| error_output_format | breached | Error handling changed from silent GUI blank window to explicit error message on stderr with exit code 1. |

- **覆盖率**: 0/8 (0.00%)
- **未覆盖行**: git-gui.sh:line-3002, git-gui.sh:line-3003, git-gui.sh:line-3004, git-gui.sh:line-3005, git-gui.sh:line-3006, git-gui.sh:line-3007, git-gui.sh:line-3008, git-gui.sh:line-3009

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I6 | ERROR_EXCEPTION_CHANGE | exit 124 (timeout - blank browser window, no feedback) | exit 1 - '<path> is not a directory in rev <rev>' | Error display changed from blank GUI window to clear stderr error message via show_parse_err |
- 1 test input executed.
- Error message format changed. show_parse_err introduced for consistent error display.
- Coverage not applicable (Tcl script).
- Low priority - error improvements unlikely to break legitimate usage.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | COV-N/A-001 | Patch modifies git-gui.sh, a Tcl/Tk script. Line-level gcov/instrumentation coverage is not applicable to Tcl scripts. Behavioral before/after comparison was used instead. | No action needed. Behavioral contract verification has been completed as a substitute. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `N/A (Tcl script, no gcov data)` |
| execution_results | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Update any scripts that use 'git gui blame <path> <rev>' to use standard '<rev> <path>' ordering.
- Verify if any automation parses git-gui error message text or exit codes.
- The changes improve error handling and reduce confusion from blank GUI windows.
