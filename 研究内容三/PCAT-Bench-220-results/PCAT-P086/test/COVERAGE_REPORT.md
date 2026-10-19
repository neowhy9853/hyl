# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `9770e32ce07110f0c8c7a381604ec9a490028eed` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython` |
| 基线 | `9eb50a40b4186d665aa98c8dbea7cf60fb2aacca` |
| Profile | `cpython` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：All 21 contract verification tests passed (11 os.makedirs + 10 pathlib.Path.mkdir). All 9 patch-introduced CPython built-in unit tests pass. The parent_mode parameter is purely additive with a default of None; all existing call patterns (positional args, keyword args, mixed) produce identical behavior. No contract breaches, no behavior differences detected between old and new call styles. Patch line coverage is 100% (9/9 executable lines exercised).

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 4 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 21 |
| 执行输入 | 21 |
| 契约通过 | 21 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 9 |
| 已覆盖行 | 9 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `-O3` |
| 覆盖率工具 | `none (Python-level contract verification)` |
- Patched CPython 3.16.0a0 built from source in analysis worktree
- System Python 3.13.12 used only for running test report scripts, not for test execution
- Python-level changes require no gcov instrumentation; contract verification via file system state assertions
- Tests create temporary directories with controlled umask to verify mode propagation

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `Lib/os.py:219-235 (makedirs)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/test_os_makedirs_contract.py` | `python test_os_makedirs_contract.py` | All backward compatibility calls succeed with old-style arguments; parent_mode works correctly | All 5 test assertions pass: backward-pos, backward-kw, backward-mode succeed with old signatures; parent-mode creates directories with correct permissions; kw-only enforcement raises TypeError for positional parent_mode |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance_pos | passed | makedirs(name) still works |
| backward_input_acceptance_kw | passed | makedirs(name, exist_ok=True) still works |
| backward_input_acceptance_mode | passed | makedirs(name, mode, exist_ok) still works |
| new_param_acceptance | passed | parent_mode keyword accepted, parent=0o700 leaf=0o755 |
| keyword_only_enforcement | passed | TypeError raised for positional parent_mode |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -
- os.makedirs signature change from 3 to 4 params is purely additive
- All existing call patterns verified to work identically

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `Lib/os.py:237-247 (makedirs)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | passed | `test-entry-work/test_os_makedirs_contract.py` | `python test_os_makedirs_contract.py` | Without parent_mode, behavior matches baseline; with parent_mode, intermediate dirs get specified mode | All 6 assertions pass: default path unchanged (leaf 0o555, parent 0o775); deep hierarchy (l1=0o700, l2=0o700, leaf=0o755); same-mode both 0o705 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_default_leaf | passed | leaf mode 0o555 correct without parent_mode |
| side_effect_default_parent | passed | parent default mode 0o775 without parent_mode |
| side_effect_deep_l1 | passed | level 1 parent gets parent_mode 0o700 |
| side_effect_deep_l2 | passed | level 2 parent gets parent_mode 0o700 |
| side_effect_deep_leaf | passed | leaf gets mode 0o755 distinct from parent_mode |
| side_effect_same_mode | passed | both dirs 0o705 when parent_mode=mode |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -
- Conditional side effect only triggered when parent_mode is explicitly set
- Default path (parent_mode=None) produces identical behavior to baseline

### PCA-0003: INPUT_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `Lib/pathlib/__init__.py:1204-1210 (mkdir)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | passed | `test-entry-work/test_pathlib_mkdir_contract.py` | `python test_pathlib_mkdir_contract.py` | All backward compatibility calls succeed; parent_mode works correctly | All 4 assertions pass: basic mkdir, parents=True, exist_ok=True, and parent_mode all work as expected |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_basic | passed | Path.mkdir() still works |
| backward_input_parents | passed | Path.mkdir(parents=True) still works |
| backward_input_existok | passed | Path.mkdir(exist_ok=True) still works |
| new_param_acceptance | passed | parent_mode keyword accepted, parent=0o700 leaf=0o755 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- pathlib.Path.mkdir signature change identical pattern to os.makedirs
- Purely additive keyword-only parameter

### PCA-0004: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `Lib/pathlib/__init__.py:1213-1223 (mkdir)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0004 | passed | `test-entry-work/test_pathlib_mkdir_contract.py` | `python test_pathlib_mkdir_contract.py` | Without parent_mode, behavior unchanged; with parent_mode, parents get specified mode | All 6 assertions pass: default path (leaf 0o555, parent 0o775); deep hierarchy both levels 0o700, leaf 0o755; same-mode both 0o705 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_default_leaf | passed | leaf mode 0o555 without parent_mode |
| side_effect_default_parent | passed | parent default 0o775 without parent_mode |
| side_effect_deep_l1 | passed | level 1 parent gets parent_mode 0o700 |
| side_effect_deep_l2 | passed | level 2 parent gets parent_mode 0o700 |
| side_effect_deep_leaf | passed | leaf gets mode 0o755 distinct from parent_mode |
| side_effect_same_mode | passed | both dirs 0o705 when parent_mode=mode |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -
- Path.mkdir recursive parent creation mirrors os.makedirs pattern
- parent_mode propagation works correctly through deep hierarchies

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_results | `test-entry-work/` |
| contract_summary | `contract_verification.json` |
| coverage_data | `phase4_execution/coverage.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- No backward compatibility issues found; the change is safe to merge
- Document the new parent_mode parameter in release notes for os.makedirs and pathlib.Path.mkdir
- Ensure type stubs and linters are updated to recognize the new parameter
