# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `a8982b0376885b5007b5c6bbbfedfde7bb941a54` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup` |
| 基线 | `a6d1d7aa49c264efc9d520ffe555299b7a92466e` |
| Profile | `c_project` |
| 执行状态 | `blocked` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Testing is blocked due to missing build dependencies (intltool for autogen.sh, libsoup-2.4-dev for linking). The static analysis identified 2 compatibility changes (PCA-0001 HIGH: conditional Authorization header removal, PCA-0002 MEDIUM: append-to-replace semantic change). Both are SIDE_EFFECT_CHANGE in the auth manager's HTTP header handling. Without being able to build and instrument the library, we cannot execute contract verification or measure patch-line coverage. The generated test artifacts (reproducer.sh + harness.c) are structurally complete and ready to execute once dependencies are installed.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 0 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 3 |
| 已覆盖行 | 0 |
| 未覆盖行 | 3 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (Ubuntu 13.3.0)` |
| 优化级别 | `N/A` |
| 覆盖率工具 | `gcov (not executed)` |
- Build blocked: autogen.sh requires intltoolize (package intltool) which is not installed
- sudo not available for package installation
- System has glib-2.0 and gio-2.0 runtime but lacks libsoup-2.4 development package
- The analysis worktree uses autotools (2016-era); modern repo uses meson
- Full test requires Apache HTTP server with Digest auth (native test at tests/auth-test.c)

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `libsoup/soup-auth-manager.c:446-454 (update_authorization_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | needs_env | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | Before patch: Authorization header stripped; After patch: Authorization header preserved | gcov coverage on lines 449-450 after sending request with manual Authorization header |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_auth_header_preservation | skipped | Cannot compile instrumented libsoup: autogen.sh requires intltoolize (intltool package), and soup-version.h.in needs configure to generate soup-version.h |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: 449, 450
- Test entry (reproducer.sh + harness.c) has been generated and is syntactically valid
- Harness uses in-process SoupServer (no Apache needed) but requires compiled libsoup
- Native test do_message_has_authorization_header_test exists in tests/auth-test.c with Apache requirement
- Commit includes g_test_bug('775882') reference for the bug this patch fixes

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `libsoup/soup-auth-manager.c:456-462 (update_authorization_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: 459
- Medium priority - not targeted by default (planner was run with --min-priority high)
- Tests the append-to-replace semantic change in Authorization header manipulation

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCK-ENV-001 | intltoolize not found. The autogen.sh script in the 2016-era analysis worktree requires intltool to generate the configure script. Without configure, soup-version.h (needed for compilation) cannot be generated from soup-version.h.in. | Install intltool package: sudo apt install intltool OR sudo yum install intltool |
| build | BLOCK-BLD-001 | libsoup-2.4.pc not found (development package missing). While the shared library libsoup2.4-1 is installed, the pkg-config file and development headers are not available. This prevents linking test programs against the system libsoup. | Install libsoup-2.4 development package: sudo apt install libsoup2.4-dev |
| entry | BLOCK-ENT-001 | Cannot compile or run the test harness without built libsoup library. Both the reproducer.sh script (which builds from analysis worktree) and the harness.c (which links against libsoup) require a working libsoup build environment. | Resolve BLOCK-ENV-001 and BLOCK-BLD-001 first, then re-run the reproducer |
| contract | BLOCK-CTR-001 | Contract probe side_effect_auth_header_preservation cannot execute: before/after binaries are not available. The probe requires instrumented builds of both baseline (base_commit) and patched (analysis worktree) versions of libsoup. | Build both baseline and patched libsoup with gcov instrumentation after resolving environment blockers |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `test-entry-work/test-entry-verification.json` |
| coverage_data | `` |
| execution_results | `` |
| impact_map | `` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `` |

## 建议

- 安装 intltool: sudo apt install intltool
- 安装 libsoup 开发包: sudo apt install libsoup2.4-dev
- 运行 reproducer.sh 构建并测试基准版和补丁版 libsoup
- 使用 gcov 采集 libsoup/soup-auth-manager.c 第 446-454 行的覆盖率数据
- 对比 before/after 行为: 手动设置 Authorization 头在无缓存凭证时是否被保留
- 针对 native test 运行 /auth/authorization-header-request (需要 Apache)
