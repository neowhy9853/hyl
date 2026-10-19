# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `dcd5b5fe` |
| 仓库 | `/home/soong/pca_benchmark/_repos/vim` |
| 基线 | `6f02e5cd7c27fc098d0b8dfec99542c7663a807e` |
| Profile | `vim` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Behavioral change confirmed: screenpos() curscol with rightleft now returns a different value (left-aligned screen column instead of reading-order). This is a documented bug fix that aligns with existing documentation. All 18 tests pass, 100% patch line coverage. Contract breached as expected.

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
| 补丁可执行行 | 3 |
| 已覆盖行 | 3 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Huge features build with --enable-terminal --disable-gui
- 146 .gcno files generated
- Rightleft feature (FEAT_RIGHTLEFT) enabled

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `src/move.c:1560-1575 (textpos2screenpos)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-0001` | `cd src/testdir && make test_cursor_func.res` | Test_screenpos_rightleft passes (all 18 tests) | gcov: move.c lines 1564/1568/1570 hit |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | screenpos() curscol with rightleft changed from reading-order to left-aligned. This is a documented bug fix that aligns with existing documentation. |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | curscol counted in reading order (right-aligned) | curscol counted from left side of window (left-aligned) | gcov confirms patched lines executed 4 times (rightleft branch). Test_screenpos_rightleft validates new behavior. |
- Bug fix: screenpos() curscol was incorrect with rightleft
- All 18 tests pass including new Test_screenpos_rightleft
- Documentation updated in runtime/doc/builtin.txt

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `move.c.gcov` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Monitor Vim plugin compatibility for screenpos() calls with rightleft
- Document the fix in release notes
