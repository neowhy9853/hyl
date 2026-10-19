# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `1d4e965829eef4cdb089a984fda21ca465a1f534` |
| 仓库 | `/home/soong/pca_benchmark/_repos/cpython` |
| 基线 | `baf11a4e9a9d6542a1f3a891c670da36c89cbc96` |
| Profile | `cpython` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：sys.lazy_modules changed from dict to set — a verified, intentional API signature change per PEP 810. The type change breaks code using dict methods (subscript, .keys(), .items()) on sys.lazy_modules. All normal-execution-path lines are covered by gcov; only fault-injection error paths remain uncovered. The test suite confirms the new set-based behavior works correctly.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 3 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 15 |
| 已覆盖行 | 10 |
| 未覆盖行 | 5 |
| 补丁行覆盖率 | 66.70% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O0 -g (for coverage build), default for before/after behavior build` |
| 覆盖率工具 | `gcov (GCC)` |
- Before worktree created from base_commit baf11a4e9a9d6542a1f3a891c670da36c89cbc96
- After worktree is the analysis_repo patched worktree
- Build with ./configure --without-ensurepip && make -j8
- _dbm and _decimal missing (not required for lazy import tests)
- Coverage build used CFLAGS='-O0 -g -fprofile-arcs -ftest-coverage' LDFLAGS='--coverage'

## Finding 测试结果

### PCA-0001: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `Python/import.c:275-281 (_PyImport_InitLazyModules)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/probe_contract.py` | `<patched-python> test-entry-work/PCA-0001/probe_contract.py` | isinstance(sys.lazy_modules, set) is True, isinstance(sys.lazy_modules, dict) is False | exit code 0, type shows <class 'set'> |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CTR-001 | passed | sys.lazy_modules type change confirmed: dict->set. This is the documented intentional change per PEP 810 — not a regression but a verified compatibility break. |
| CTR-002 | passed | Dict operations (subscript, .keys(), .items()) fail on new set type as expected. Before build accepts dict ops, after build rejects them. |
| CTR-003 | passed | Set operations (.add(), 'in', len(), clear()) work on new set type. Before build lacks .add() on dict. |

- **覆盖率**: 10/15 (66.70%)
- **未覆盖行**: import.c:4473 (fromname allocation failure - fault injection needed), import.c:4480 (PySet_Add failure - fault injection needed), import.c:4578 (PySet_Add failure in LazyImportModuleLevelObject - fault injection needed), import.c:5670 (PySet_Discard failure - fault injection needed), import.c:5691 (PyDict_DelItem failure - fault injection needed)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | API_SIGNATURE_CHANGE | type=<class 'dict'>, isinstance(dict)=True, isinstance(set)=False | type=<class 'set'>, isinstance(dict)=False, isinstance(set)=True | gcov confirmed lines 279-280 executed (49 runs each) |
- Uncovered lines are memory-allocation failure paths or error-return paths requiring fault injection — architecturally unreachable with normal test inputs.
- Full test suite (112 tests) passes on both before and after builds.
- Behavioral contract breach intentionally documented in PEP 810 and NEWS fragment.
- Coverage gate (80%) not met due to fault-injection-only lines. With fault injection, all lines are coverable.

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | BLK-001 | 5 of 15 new/modified executable lines are error-return paths that cannot be exercised without fault injection (e.g., LD_PRELOAD malloc failure shim). These are architecturally unreachable with normal test inputs. | Use fault injection (e.g., force malloc failure) to cover the remaining 5 error paths and reach the 80% coverage gate. |
| coverage | BLK-002 | Coverage was measured only on Python/import.c. Include/internal/pycore_interp_structs.h changes are compile-time (struct layout), not executable at runtime — gcov does not produce meaningful coverage for struct declarations. | Coverage measurement of header struct changes is not applicable — verified by compilation success. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_inputs/contract_verification.json` |
| coverage_data | `../_worktrees/patched/Python#import.c.gcov` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Update all downstream code using sys.lazy_modules from dict-style access to set membership checks.
- Use fault injection to cover error-handling paths in _PyImport_InitLazyModules, register_from_lazy_on_parent, _PyImport_LazyImportModuleLevelObject, and _imp__set_lazy_attributes_impl.
- Run Lib/test/test_lazy_import/__init__.py as a regression gate.
- Document the type change in release notes and migration guides.
