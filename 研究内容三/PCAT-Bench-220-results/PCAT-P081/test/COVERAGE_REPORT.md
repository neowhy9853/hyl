# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `c6fd7de64ac7591a9708c14a34737eb9baf050bc` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython` |
| 基线 | `b45319e13273ee17e84e6b8c459f03b141518289` |
| Profile | `c_project` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：functools.reduce 的 help() 输出格式从 initial=<unrepresentable> 变更为 initial=_initial_missing。inspect.signature() 从抛出 ValueError 变为返回有效 Signature。虽然功能行为不变，但输出格式的精确匹配（exact comparison）结果确认为 BREACH, 因为文档生成工具或帮助输出解析器可能受影响。覆盖率门禁未达到（0% < 80%），因为此变更为文档字符串常量变更，不适用 C 代码行级覆盖率检测。

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
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 0 |
| 未覆盖行 | 1 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `O2 (default CPython build; no C coverage instrumentation)` |
| 覆盖率工具 | `none` |
- Before-build from parent commit b45319e1 in isolated worktree
- After-build from patched worktree at commit c6fd7de
- Both builds use --with-pydebug for fast build

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `Modules/clinic/_functoolsmodule.c.h:71-73 (_functools_reduce__doc__)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `python verify_output.py --version after` | help output shows initial=_initial_missing (not <unrepresentable>); inspect.signature returns valid Signature | help output contains _initial_missing; inspect.signature(functools.reduce) succeeds with initial parameter |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| functools_reduce_docstring_format | breached | help(functools.reduce): before='initial=<unrepresentable>' vs after='initial=_initial_missing'; inspect.signature: before=ValueError vs after=valid Signature |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: Modules/clinic/_functoolsmodule.c.h:73-75 (PyDoc_STRVAR line; C gcov not applicable)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | help: reduce(function, iterable, /, initial=<unrepresentable>); inspect.signature: ValueError raised | help: reduce(function, iterable, /, initial=_initial_missing); inspect.signature: valid Signature returned | Contract breach confirmed via before/after CPython build comparison. help() output format changed; inspect.signature() now succeeds. functools.reduce functional behavior unchanged. |
- 功能行为完全一致：reduce 的 4 个功能测试用例在 before 和 after 版本中表现相同
- goc C 代码覆盖率不适用于此文档字符串变更（PyDoc_STRVAR 是编译时常量）
- 这是正向改进（bug fix），<unrepresentable> 本身即表明之前无法正确表示默认值

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `none` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 确认下游工具（Sphinx、IDE 插件）对 functools.reduce 的 docstring 变更无不良反应
- 原有的 functools 模块功能回归测试保持不变，所有测试通过
- 不需要回滚此变更，它是一个正向的 bug 修复
