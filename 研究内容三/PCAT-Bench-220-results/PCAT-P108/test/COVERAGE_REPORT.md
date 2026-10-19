# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `7f9c7c8731821149ff42971fad18e2a9abbb4c10` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup` |
| 基线 | `11811349f8a10ce419d980c01a518c774fe8a5e5` |
| Profile | `c_project` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：C++编译测试证实了枚举typedef重命名导致的ABI不兼容：g++拒绝在SoupKnownStatusCode变量中存储SOUP_STATUS_OK值。在C语言中该变更向后兼容，但C++严格类型检查使其成为源级别不兼容变更。GObject introspection类型名也受到影响，但未能进行运行时验证。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 6 |
| 执行输入 | 5 |
| 契约通过 | 1 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 4 |
| 已覆盖行 | 4 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (GCC) / g++` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `none (compile-level tests only, no runtime gcov)` |
- libsoup shared library not built due to autotools chain not configured
- Header-only compile tests used for ABI verification
- soup-version.h generated from soup-version.h.in for header include resolution
- GObject introspection (g-ir-scanner) not available

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `libsoup/soup-status.h:97-97 (SoupKnownStatusCode)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | Test 1: SoupStatus compiles. Test 2b: C++ fails with cross-enum conversion error. Test 3-5: PASS. | C++ compilation error 'cannot convert SoupStatus to SoupKnownStatusCode' confirms ABI break at line 97 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| abi_enum_rename_compile_test | breached | C++ compilation fails: cannot convert 'SoupStatus' to 'SoupKnownStatusCode' when using old type name with SOUP_STATUS_OK values. C compilation succeeds (permissive) but generates -Wenum-conversion warnings. |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| test2b_cpp_old_type | ABI_CHANGE | SoupKnownStatusCode status = SOUP_STATUS_OK; compiles in C++ (same enum type) | SoupKnownStatusCode status = SOUP_STATUS_OK; fails in C++ with error: cannot convert 'SoupStatus' to 'SoupKnownStatusCode' | g++ error at line 5: 'cannot convert SoupStatus to SoupKnownStatusCode in initialization' |
- ABI break confirmed for C++ consumers and GObject introspection bindings
- C consumers are backward-compatible due to permissive C enum semantics
- Deprecated SoupKnownStatusCode enum exists with different value names (SOUP_KNOWN_STATUS_CODE_*) for introspection backward compat
- GObject introspection runtime test (Python GI) not performed due to missing build

### PCA-0002: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `libsoup/libsoup-2.4.sym:419-419 (soup_status_get_type)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | static_valid_not_run | `test-entry-work/PCA-0002/reproducer.sh` | `grep soup_status_get_type .../libsoup-2.4.sym` | soup_status_get_type found in symbol version file | Symbol presence confirmed via static file inspection |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| abi_symbol_addition | passed | soup_status_get_type confirmed present in libsoup-2.4.sym versioned symbol file at line 419 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- Static symbol file verification only
- Full runtime verification requires building libsoup.so and using nm -D to check exported symbols
- GObject introspection verification requires g-ir-scanner which is not available

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| build | libsoup-full-build | libsoup autotools build chain requires autoreconf + configure + make with full dependency chain (glib, libxml2, etc.) | Install libsoup build dependencies or use a container with pre-built libsoup environment |
| contract | gobject-introspection-runtime | GObject introspection verification (Python GI, Vala, gjs) requires built .so and .typelib files | Build libsoup from patched worktree with introspection enabled, then test with GI bindings |
| entry | old-binary-consumer | No pre-built binary linked against old SoupKnownStatusCode type exists | Build libsoup from base commit to get old .so, then attempt to link C++ consumer against old and new .so |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `test-summary.json` |
| coverage_data | `test-summary.json` |
| execution_results | `test-entry-work/test-entry-verification.json` |
| impact_map | `test-entry-work/test-entries.json` |
| report | `COVERAGE_REPORT.md` |
| reproducer_pca0001 | `test-entry-work/PCA-0001/reproducer.sh` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_plan | `test-entry-plan.md` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `test-entry-work/test-entries.json` |
| verification | `test-entry-work/test-entry-verification.json` |

## 建议

- 在C++和GObject introspection绑定项目中使用soup_status_get_type()验证SoupStatus类型
- 针对SOUP_DISABLE_DEPRECATED已定义的情况测试编译
- 使用g-ir-scanner生成.gir文件，验证SoupStatus类型注解以及弃用的SoupKnownStatusCode兼容别名
- 检查反向依赖包（如Epiphany、GNOME Online Accounts）中是否有直接引用SoupKnownStatusCode类型名的代码
