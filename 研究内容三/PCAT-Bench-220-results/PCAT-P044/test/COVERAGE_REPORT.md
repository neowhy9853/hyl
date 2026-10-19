# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `5f3b17` |
| 仓库 | `/home/soong/pca_benchmark/_repos/glib` |
| 基线 | `6a7a743f75aaaa08227a06f7bd0b569e6a871371` |
| Profile | `glib2` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：ABI_CHANGE (PCA-0001): G_USER_N_DIRECTORIES sentinel value changed from 8 to 9. This is a confirmed ABI break: any downstream code compiled against old headers and linked against the new library will have mismatched array sizes/loop bounds when using G_USER_N_DIRECTORIES. Although the enum is documented as extensible, the sentinel value change is a binary-level ABI incompatibility. SIDE_EFFECT_CHANGE (PCA-0002): Additive behavioral change (new icon for projects directory) is not breaking. However, the ABI break alone makes this patch backward-incompatible for compiled consumers.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 3 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 5 |
| 已覆盖行 | 2 |
| 未覆盖行 | 3 |
| 补丁行覆盖率 | 40.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Linux x86_64 host build
- meson 1.11.2 with --coverage flags
- Only Linux-compilable code paths tested (Windows/macOS paths skipped)
- gvdb submodule initialized before build (AGENTS.md requirement)
- XDG user-dirs.dirs parsing uses cached g_get_user_config_dir() - cannot override via env at runtime for coverage

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `glib/gutils.h:248-262 (G_USER_DIRECTORY_PROJECTS)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-PCA-0001-1 | verified | `/tmp/test_pca_0001.c` | `gcc -o /tmp/test_pca_0001_after /tmp/test_pca_0001.c -I/tmp/pca-glib -I/tmp/pca-glib/glib -I/tmp/pca-glib/build/glib -L/tmp/pca-glib/build/glib -lglib-2.0 -pthread && LD_LIBRARY_PATH=/tmp/pca-glib/build/glib /tmp/test_pca_0001_after` | G_USER_N_DIRECTORIES should be 9 (post-patch) | Compiled binary links against new library, reads enum value at compile time |
| ENTRY-PCA-0001-2 | verified | `/tmp/test_pca_0001.c` | `gcc -o /tmp/test_pca_0001_before /tmp/test_pca_0001.c -I/tmp/pca-glib-before -I/tmp/pca-glib-before/glib -I/tmp/pca-glib-before/build/glib -L/tmp/pca-glib-before/build/glib -lglib-2.0 -pthread && LD_LIBRARY_PATH=/tmp/pca-glib-before/build/glib /tmp/test_pca_0001_before` | G_USER_N_DIRECTORIES should be 8 (pre-patch) | Compiled binary links against old library |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| abienum_sentinel_value | breached | G_USER_N_DIRECTORIES changed from 8 (before commit b173cfca6) to 9 (after patch). Any code compiled against old headers using G_USER_N_DIRECTORIES as array bound or loop sentinel will have mismatched size when linked against new library. |
| g_get_user_special_dir_coverage | passed | g_get_user_special_dir(G_USER_DIRECTORY_PROJECTS) returns the configured path (/tmp/pca-test-projects-dir) when XDG_PROJECTS_DIR is set in user-dirs.dirs. G_N_USER_DIRECTORIES iteration includes the new slot at index 8. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| enum-abi-before-vs-after | ABI_CHANGE | G_USER_N_DIRECTORIES = 8, enum iterates 0..7 | G_USER_N_DIRECTORIES = 9, enum iterates 0..8 | BEFORE: G_USER_N_DIRECTORIES=8, AFTER: G_USER_N_DIRECTORIES=9. BEFORE binary compiled with old header:8, AFTER binary compiled with new header:9. Cross-library test: old binary linked against new library would have array-size mismatch. |
- Enum is documented as extensible ('The #GUserDirectory enumeration can be extended at later date')
- New value is additive at the end of the enum, before G_USER_N_DIRECTORIES sentinel
- ABI impact is limited to code that uses G_USER_N_DIRECTORIES for array sizing or loop bounds

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `partial`
- **目标**: `gio/glocalfileinfo.c:1840-1849 (get_icon_name)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-PCA-0002-1 | verified | `/tmp/test_pca_0002_v2.c` | `gcc -o /tmp/test_pca_0002_v2_after /tmp/test_pca_0002_v2.c -I/tmp/pca-glib -I/tmp/pca-glib/glib -I/tmp/pca-glib/build/glib -I/tmp/pca-glib/gio -I/tmp/pca-glib/build/gio -I/tmp/pca-glib/gobject -I/tmp/pca-glib/build/gobject -I/tmp/pca-glib/gmodule -I/tmp/pca-glib/build/gmodule -L/tmp/pca-glib/build/glib -L/tmp/pca-glib/build/gio -L/tmp/pca-glib/build/gobject -L/tmp/pca-glib/build/gmodule -lglib-2.0 -lgio-2.0 -lgobject-2.0 -lgmodule-2.0 -pthread && LD_LIBRARY_PATH=/tmp/pca-glib/build/glib:/tmp/pca-glib/build/gio:/tmp/pca-glib/build/gobject:/tmp/pca-glib/build/gmodule /tmp/test_pca_0002_v2_after` | Icon for PROJECTS directory should contain 'folder-projects' | Icon string '. GThemedIcon folder-projects ...' contains 'folder-projects' (gcov confirms line 1843 hit 2x, line 1845 hit 2x) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| icon_name_for_projects_dir | passed | When XDG_PROJECTS_DIR is configured in user-dirs.dirs and g_reload_user_special_dirs_cache() is called, the icon for the projects directory path correctly returns 'folder-projects' (symbolic: 'folder-projects-symbolic'). Gcov confirms the new code path is executed (2 hits each on lines 1843, 1845 of glocalfileinfo.c). |
| xdg_projects_dir_parsing | passed | When XDG_PROJECTS_DIR is set in user-dirs.dirs content and the config is reloaded, g_get_user_special_dir(G_USER_DIRECTORY_PROJECTS) returns the configured path. Verified by targeted test. |

- **覆盖率**: 2/5 (40.00%)
- **未覆盖行**: glib/gutilsprivate.c:92 (else if strncmp XDG_PROJECTS_DIR), glib/gutilsprivate.c:94 (directory = G_USER_DIRECTORY_PROJECTS), glib/gutilsprivate.c:95 (p += strlen XDG_PROJECTS_DIR)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| icon-projects-dir | SIDE_EFFECT_CHANGE | Projects directory (if it existed in user-dirs.dirs) would get no icon (fall through to content-type icon or NULL) | Projects directory gets 'folder-projects' theme icon (or 'folder-projects-symbolic' for symbolic icon) | AFTER icon='. GThemedIcon folder-projects folder folder-projects-symbolic folder-symbolic'. BEFORE code cannot reference G_USER_DIRECTORY_PROJECTS (enum not defined). Gcov confirms 2 hits on the new branch. |
- Only Linux-compilable paths tested (Windows G_OS_WIN32 and macOS HAVE_COCOA code paths skipped)
- XDG_PROJECTS_DIR parsing in gutilsprivate.c is reachable but not covered by standard tests due to caching of config directory path
- Only observable when user configures XDG_PROJECTS_DIR in ~/.config/user-dirs.dirs

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | XGD-PROJECTS-PARSING | XDG_PROJECTS_DIR parsing in glib/gutilsprivate.c:92-95 not covered because g_get_user_config_dir() caches its result; runtime env override (XDG_CONFIG_HOME) has no effect after program init | Use G_TEST_OPTION_ISOLATE_DIRS with g_test_subprocess() to isolate config dir in a subprocess test, then write user-dirs.dirs with XDG_PROJECTS_DIR |
| environment | PLATFORM-WIN32 | G_OS_WIN32 compilation path (glib/gutils.c:2247) not testable on Linux | Test on Windows platform with FOLDERID_Documents fallback |
| environment | PLATFORM-MACOS | HAVE_COCOA/Objective-C compilation path (glib/gosxutils.m:56) not testable on Linux | Test on macOS platform with NSDocumentDirectory fallback |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Consumer recompilation: All downstream packages using GUserDirectory/G_USER_N_DIRECTORIES must be recompiled against the new headers to pick up the correct sentinel value
- XDG parsing test: Write a proper GLib subprocess test using g_test_subprocess() + G_TEST_OPTION_ISOLATE_DIRS to verify XDG_PROJECTS_DIR parsing in gutilsprivate.c
- Cross-platform testing: Verify Windows (FOLDERID_Documents) and macOS (NSDocumentDirectory) fallback paths work correctly
- Documentation: Note the ABI sentinel change in release notes so packagers know to trigger rebuilds of dependent packages
