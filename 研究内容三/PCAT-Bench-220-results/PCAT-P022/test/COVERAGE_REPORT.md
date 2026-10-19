# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `e397c8` |
| 仓库 | `/home/soong/pca_benchmark/_repos/vim` |
| 基线 | `e6f47839a8a8b4790a037bfec32b784b308e4133` |
| Profile | `vim` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Patch fixes a bug where extendnew() and extend() left the return value uninitialized when the second argument was NULL. The change is a bug fix that makes behavior predictable and correct. 100% patch-line coverage achieved (17/17 executable lines). All 6 contract tests pass on patched binary. The 2 before/after behavioral differences are confirmed bug fixes, not regressions. No backward incompatible changes for non-NULL inputs.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 4 |
| 验证入口 | 4 |
| 规划输入 | 8 |
| 执行输入 | 8 |
| 契约通过 | 6 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 17 |
| 已覆盖行 | 17 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (GCC)` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- ncursesw available
- Huge features enabled with terminal support
- Builds produce vim binary with --coverage instrumentation
- Host check confirmed by AGENTS.md overlay on 2026-07-23

## Finding 测试结果

### PCA-0001: RETURN_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `src/dict.c:1350-1394 (dict_extend_func)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/_worktrees/patched/src/testdir/test_listdict.res` | `cd src/testdir && make test_listdict.res` | Test_listdict_extend and Test_listdict_extendnew pass | 6 executions of 'goto theend' in dict.c line 1352 |
| PCA-TE-0001-contract | passed | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/contract_test.vim` | `src/vim --clean -X -Z -u NONE -i NONE -S contract_test.vim` | ALL CONTRACT TESTS PASSED | 8/8 contract assertions pass on patched binary |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_extendnew_null_dict | passed | extendnew({'a':'A','b':9}, test_null_dict()): BEFORE returns v:t_null (type=0) [BROKEN], AFTER returns proper dict copy {'a':'A','b':9}. 4 gcov executions confirm coverage. |
| return_contract_extend_null_dict | passed | extend({'a':'A','b':9}, test_null_dict()): BEFORE preserves original dict, AFTER preserves original dict. No behavioral difference. |
| return_contract_extend_empty_dict | passed | extend({'a':'A'}, {}): Both BEFORE and AFTER work correctly. No behavioral difference. |

- **覆盖率**: 8/8 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| extendnew_null_dict | RETURN_CONTRACT_CHANGE | returns v:t_null (type=0) - uninitialized return value | returns proper dict copy {'a':'A','b':9} | gcov line dict.c:1352 hit 6 times; before/after binary comparison confirmed breach. This is a bug fix. |
- The old behavior was a bug - rettv was left uninitialized when d2 was NULL in extendnew() path
- Patch moves the NULL check after the is_new copy block and jumps to theend label which properly sets rettv
- Only affects calls with NULL second argument (test_null_dict())
- All non-NULL behavior is identical before and after

### PCA-0002: RETURN_CONTRACT_CHANGE

- **优先级**: `low`
- **状态**: `passed`
- **目标**: `src/list.c:3026-3062 (list_extend_func)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | passed | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/_worktrees/patched/src/testdir/test_listdict.res` | `cd src/testdir && make test_listdict.res` | Test_listdict_extend and Test_listdict_extendnew pass | 6 executions of 'goto theend' in list.c line 3028 |
| PCA-TE-0002-contract | passed | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/contract_test.vim` | `src/vim --clean -X -Z -u NONE -i NONE -S contract_test.vim` | ALL CONTRACT TESTS PASSED | 8/8 contract assertions pass on patched binary |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_extendnew_null_list | passed | extendnew([1,2,3], test_null_list()): BEFORE returns v:t_null (type=0) [BROKEN], AFTER returns proper list copy [1,2,3]. 6 gcov executions confirm coverage. |
| return_contract_extend_null_list | passed | extend([1,2,3], test_null_list()): BEFORE preserves original list, AFTER preserves original list. No behavioral difference. |
| return_contract_extend_empty_list | passed | extend([1,2,3], []): Both BEFORE and AFTER work correctly. No behavioral difference. |

- **覆盖率**: 9/9 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| extendnew_null_list | RETURN_CONTRACT_CHANGE | returns v:t_null (type=0) - uninitialized return value | returns proper list copy [1,2,3] | gcov line list.c:3028 hit 6 times; before/after binary comparison confirmed breach. This is a bug fix. |
- The old behavior was a bug - rettv was left uninitialized when l2 was NULL in extendnew() path
- Patch moves the NULL check inside the if-block and jumps to theend label which properly sets rettv
- Only affects calls with NULL second argument (test_null_list())
- All non-NULL behavior is identical before and after

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/_worktrees/patched/src/dict.c.gcov` |
| execution_results | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- No further action needed - existing test_listdict.vim tests already verify the fix
- The patch is safe for inclusion in any downstream branch
- Downstream consumers do not need to update their scripts unless they were previously working around the NULL return bug
