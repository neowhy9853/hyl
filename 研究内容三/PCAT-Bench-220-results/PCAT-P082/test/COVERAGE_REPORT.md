# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `6ca5cdba185aeb3b7f72ae0dd61b6a9685d8c416` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython` |
| 基线 | `5dd5c8b5a66af18904d4e015ce3120e2686ddb23` |
| Profile | `c_project` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：3 of 4 findings (all high-priority) verified through compilation and execution tests. All functional tests passed with no contract breaches. However, patch line coverage could not be measured due to the header-dominant nature of this change. The patch is purely additive and functionally correct, but coverage evidence is insufficient for a definitive 'compatible' conclusion.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 3 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 3 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 0 |
| 已覆盖行 | 0 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (Ubuntu 11.4.0)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `none` |
- Header-only patch change; full CPython build not performed
- Tests performed via minimal C compilation harness against patched headers
- Before headers from base_commit, after headers from analysis_repo worktree
- Python 3.13 runtime from /data2/wanghy/conda_dir used for linking

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Include/critical_section.h:4-94 (PyCriticalSection / PyCriticalSection2)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-0001/test_struct_abi.c` | `./test-entry-work/PCA-0001/runs/test_struct_abi` | Exits 0 with 'RESULT: PASS' | sizeof(PyCriticalSection)=16 sizeof(PyCriticalSection2)=24 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| binary_abi_compatibility | passed | BEFORE: compile FAILED (types not in Limited API). AFTER: compile OK, execute PASS. sizeof and offsetof verified. Struct layout is accessible in post-patch Limited API. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BEFORE-vs-AFTER-LimitedAPI | ABI_CHANGE | COMPILE_FAILED: PyCriticalSection not defined in Limited API | COMPILE_OK_EXECUTE_PASS: sizeof(PyCriticalSection)=16 sizeof(PyCriticalSection2)=24 | Before compile error: unknown type name PyCriticalSection. After: struct members _cs_prev (offset 0), _cs_mutex (offset 8), _cs_mutex2 (offset 16) verified. |
- Struct layout frozen as full-abi in stable_abi.toml
- Member offsets verified: _cs_prev=0, _cs_mutex=8, _cs_mutex2=16
- Cannot verify ABI stability across releases without additional CPython versions

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Include/critical_section.h:59-69 (PyCriticalSection_Begin / PyCriticalSection_End / PyCriticalSection2_Begin / PyCriticalSection2_End)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | verified | `test-entry-work/PCA-0002/test_function_api.c` | `./test-entry-work/PCA-0002/runs/test_function_api` | Exits 0 with 'RESULT: PASS', all 4 function pointers non-NULL | PyCriticalSection_Begin=0x7e3352d3e4aa PyCriticalSection_End=0x7e3352d3e4ab... |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | passed | BEFORE: compile FAILED (PyCriticalSection types and functions not in Limited API). AFTER: compile OK, execute PASS. All 4 function pointers resolved via dynamic linker. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BEFORE-vs-AFTER-LimitedAPI-func | API_SIGNATURE_CHANGE | COMPILE_FAILED: unknown type name PyCriticalSection, PyCriticalSection_Begin not declared | COMPILE_OK_EXECUTE_PASS: PyCriticalSection_Begin=0x7e..., _End=0x7e..., _2Begin=0x7e..., _2End=0x7e... | Before: 8 compile errors for unknown types and undeclared identifiers. After: 4 function pointers resolve to valid addresses in libpython3.13. |
- 4 new exported functions added to Limited API / Stable ABI
- Functions are also registered in PC/python3dll.c via EXPORT_FUNC for Windows DLL
- Non-free-threaded build only; free-threaded linkage not tested

### PCA-0003: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Include/critical_section.h:71-97 (Py_BEGIN_CRITICAL_SECTION / Py_END_CRITICAL_SECTION / Py_BEGIN_CRITICAL_SECTION2 / Py_END_CRITICAL_SECTION2)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | verified | `test-entry-work/PCA-0003/test_macro_api.c` | `./test-entry-work/PCA-0003/runs/test_macro_api` | Exits 0 with 'RESULT: PASS', all 4 macros defined | Py_BEGIN_CRITICAL_SECTION macro defined: PASS, ... |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | passed | BEFORE: Py_BEGIN_CRITICAL_SECTION not defined under Py_LIMITED_API. AFTER: all 4 macros (Py_BEGIN_CRITICAL_SECTION, Py_END_CRITICAL_SECTION, Py_BEGIN_CRITICAL_SECTION2, Py_END_CRITICAL_SECTION2) defined and accessible. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| BEFORE-vs-AFTER-LimitedAPI-macro | API_SIGNATURE_CHANGE | #ifdef Py_BEGIN_CRITICAL_SECTION -> false (not defined) | #ifdef Py_BEGIN_CRITICAL_SECTION -> true, all 4 macros defined and usable | Before: macros hidden behind #ifndef Py_LIMITED_API. After: macros defined before Py_LIMITED_API guard in public header. |
- 4 macros added to Stable ABI in stable_abi.toml
- CPython internal header uses #undef to redefine as no-ops for non-free-threaded builds
- For Limited API users, macros always expand to full struct+call form

### PCA-0004: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `Include/cpython/critical_section.h:34-61 (Py_BEGIN_CRITICAL_SECTION / Py_END_CRITICAL_SECTION / Py_BEGIN_CRITICAL_SECTION2 / Py_END_CRITICAL_SECTION2)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- Skipped per --min-priority high directive
- Change is functionally equivalent: no-ops replaced with no-ops in non-free-threaded builds
- Only affects non-Py_LIMITED_API, non-Py_GIL_DISABLED code paths

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| finding | PCA-0004 | Low priority finding excluded by --min-priority high. Non-free-threaded macro no-op optimization with negligible external effect. | Re-run test entry planner with --min-priority all if full coverage is needed. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `test-summary.json` |
| coverage_data | `not applicable - header-only change` |
| execution_results | `test-entry-verification.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/test-entries.json` |

## 建议

- Rebuild CPython with gcov instrumentation and run 'make test' to measure actual coverage of changed lines in extension.c and python3dll.c
- Run CPython's stable_abi.py check script to verify ABI declarations
- Test with free-threaded build (--disable-gil) for full struct expansion path
- Test low-priority finding PCA-0004
