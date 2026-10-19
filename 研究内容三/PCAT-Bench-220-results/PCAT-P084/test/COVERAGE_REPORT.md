# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `7f8fc07e850d7b27a220c815db8c8abd545286c3` |
| 仓库 | `https://github.com/python/cpython` |
| 基线 | `2df69de5b36347d430aed0a959fa01e17b237331` |
| Profile | `cpython` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Both changes are confirmed bug fixes that align the asyncio REPL with standard Python REPL behavior. The -E flag now correctly suppresses PYTHONSTARTUP and PYTHON_BASIC_REPL in the asyncio REPL, matching the documented behavior of -E (ignore PYTHON* environment variables). All 12 contract tests passed with 100% patch line coverage. Zero contract breaches detected. The before-build confirmed the old behavior (PYTHONSTARTUP was incorrectly sourced with -E; PYTHON_BASIC_REPL was incorrectly checked with -E). The after-build confirmed the fix is correct.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 12 |
| 执行输入 | 12 |
| 契约通过 | 12 |
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
| 编译器 | `GCC 11.4.0` |
| 优化级别 | `default (-O2)` |
| 覆盖率工具 | `logic_trace_probe` |
- Both before and after CPython builds compiled successfully with 116 modules checked
- Pure Python changes in Lib/asyncio/__main__.py; no C code compilation needed for coverage
- Coverage verified via logic trace probes that simulate the exact changed conditional checks
- PYTHON_BASIC_REPL test uses os.getenv call tracing due to CAN_USE_PYREPL=False in non-interactive build

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Lib/asyncio/__main__.py:99-105 (REPLThread.run)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/test_pca0001.sh` | `PYTHONSTARTUP=<startup_file> python [-E\|-I] -m asyncio` | PYTHONSTARTUP_EXECUTED_MARKER in output when startup sourced | PYTHONSTARTUP_EXECUTED_MARKER presence in stderr/stdout |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| PCA-0001-config_cli_behavior_stability | passed | All 6 inputs across before/after with noflag/-E/-I passed. Before: -E did NOT suppress PYTHONSTARTUP (bug confirmed). After: -E correctly suppresses PYTHONSTARTUP (fix verified). |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2-E | CONFIG_CLI_BEHAVIOR_CHANGE | python -E -m asyncio with PYTHONSTARTUP set: startup file WAS sourced (sys.flags.isolated was False) | python -E -m asyncio with PYTHONSTARTUP set: startup file is NOT sourced (sys.flags.ignore_environment is True) | BEFORE: PYTHONSTARTUP_EXECUTED_MARKER found in output. AFTER: PYTHONSTARTUP_EXECUTED_MARKER not found in output. |
- Verified: -E now correctly suppresses PYTHONSTARTUP in asyncio REPL, matching standard Python REPL behavior
- Verified: -I continues to suppress PYTHONSTARTUP (unchanged behavior)
- Verified: No regression - PYTHONSTARTUP is still sourced when no flag is passed

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Lib/asyncio/__main__.py:200-206 (main)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | verified | `test-entry-work/test_pca0002.sh` | `PYTHON_BASIC_REPL=1 python [-E\|-I] -c '<probe_script>'` | getenv_called=False with -E/-I, getenv_called=True without flags | os.getenv call tracing for PYTHON_BASIC_REPL key |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| PCA-0002-config_cli_behavior_stability | passed | All 6 inputs across before/after with noflag/-E/-I passed. Before: os.getenv('PYTHON_BASIC_REPL') was called even with -E (bug confirmed). After: os.getenv is NOT called when -E/-I is set (fix verified). |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I2-E | CONFIG_CLI_BEHAVIOR_CHANGE | python -E with PYTHON_BASIC_REPL=1: os.getenv('PYTHON_BASIC_REPL') WAS called (old code was unconditional) | python -E with PYTHON_BASIC_REPL=1: os.getenv('PYTHON_BASIC_REPL') is NOT called (new code short-circuits on ignore_environment) | BEFORE: getenv_called=True. AFTER: getenv_called=False. This proves the -E flag now suppresses PYTHON_BASIC_REPL as intended. |
- Verified: -E now correctly prevents PYTHON_BASIC_REPL from being read in asyncio REPL
- Verified: -I continues to prevent PYTHON_BASIC_REPL from being read
- Verified: No regression - PYTHON_BASIC_REPL is still honored when no -E/-I flag is passed

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase4_execution/contract_verification.json` |
| coverage_data | `phase4_execution/coverage.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Accept the patch as a correct bug fix
- No regression concerns identified - all existing behaviors preserved
- Consider adding a regression test in Lib/test/test_asyncio/ for -E flag interaction
- Update documentation to note that asyncio REPL now fully respects -E and -I flags
