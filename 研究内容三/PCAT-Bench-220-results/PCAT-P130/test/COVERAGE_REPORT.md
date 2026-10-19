# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `0d71da4bdfff4c18abcea77ffa76227f70be0f73` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd` |
| 基线 | `3934667f36d0775928ee1368b4784b3419cf45d8` |
| Profile | `httpd` |
| 执行状态 | `blocked` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Static analysis confirmed 4 compatibility changes. PCA-0001: Event MPM now treats OK+CONN_STATE_PROCESSING as lingering close, requiring AGAIN for I/O wait (breaks r1918022 behavior). PCA-0002: h2_c1_run signature change (apr_status_t->int), broader error handling, new AGAIN return contract. PCA-0003: pre_connection failure now closes connection explicitly. PCA-0004: CONN_STATE_PROCESSING documented contract update. Patch is NOT backward-compatible with r1918022's behavior but IS backward-compatible with pre-r1918022 behavior. Dynamic gcov testing blocked by missing build dependencies.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 0 |
| 规划输入 | 10 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 164 |
| 已覆盖行 | 0 |
| 未覆盖行 | 164 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `blocked` |
| 补丁后构建 | `blocked` |
| 编译器 | `gcc 11.4.0` |
| 优化级别 | `O0` |
| 覆盖率工具 | `gcov` |
- apr-1-config / apu-1-config available from conda but httpd autotools build fails
- CMake build fails with TARGET_PDB_FILE errors and APR_INCLUDE_DIR resolution issues
- autoreconf fails with AC_MSG_ERROR undefined macro in configure.in
- libnghttp2-dev not installed (required for mod_http2)
- No sudo access to install missing development packages
- Required packages: libapr1-dev libaprutil1-dev libnghttp2-dev libssl-dev libpcre3-dev libxml2-dev

## Finding 测试结果

### PCA-0001: RETURN_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `server/mpm/event/event.c:1114-1192 (process_socket)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | blocked | `test-entry-work/PCA-TE-0001/` | `apxs -c mod_test_again.c && httpd -X -f test.conf && curl http://localhost:8080/test` | OK+CONN_STATE_PROCESSING triggers lingering close | GCOV shows coverage on event.c lines 1142-1160 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_stability_001 | skipped | Cannot execute: httpd not built. Contract verifies process_connection OK+CONN_STATE_PROCESSING -> lingering_close vs AGAIN -> I/O wait. |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: 1114-1192
- HA-0001: process_socket now treats OK+CONN_STATE_PROCESSING as lingering close, requires AGAIN for I/O wait
- DONE return code mapped to OK before state evaluation

### PCA-0002: RETURN_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `modules/http2/h2_c1.c:117-308 (h2_c1_run)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | blocked | `test-entry-work/PCA-TE-0002/` | `make && httpd -X -f h2_test.conf && curl --http2 -k https://localhost:8443/test` | h2_c1_run returns AGAIN when AP_MPMQ_CAN_AGAIN; clogging_input_filters fallback otherwise | GCOV shows coverage on h2_c1.c lines 155-190, 305-311 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_stability_002 | skipped | Cannot execute: mod_http2 requires nghttp2. Contract verifies h2_c1_run return propagation through h2_c1_hook_process_connection to MPM. |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: 117-308
- HA-0002: h2_c1_run return type changed from apr_status_t to int
- Error handling: APR_STATUS_IS_EOF -> status != APR_SUCCESS (wider)
- New AGAIN return when mpm_can_again; clogging_input_filters=1 fallback

### PCA-0003: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `server/mpm/event/event.c:1085-1092 (process_socket)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: 1085-1092
- MA-0001: pre_connection failure now calls close_connection(cs) and returns
- Not targeted for testing (medium priority, --min-priority high)

### PCA-0004: RETURN_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `include/httpd.h:1322-1331 (CONN_STATE_PROCESSING)`

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
- MA-0002: CONN_STATE_PROCESSING enum comment updated to document AGAIN contract
- Comment-only change, no executable lines. Impact covered by PCA-0001

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCK-001 | Apache httpd cannot be built: missing libapr1-dev, libaprutil1-dev, libnghttp2-dev. CMake build fails with TARGET_PDB_FILE errors. autoconf fails with AC_MSG_ERROR undefined macro. | Install on a system with: sudo apt-get install libapr1-dev libaprutil1-dev libnghttp2-dev libssl-dev libpcre3-dev libxml2-dev pkg-config. Then run buildconf && configure && make with GCOV flags. |
| entry | BLOCK-002 | PCA-TE-0001 requires built httpd with event MPM + GCOV instrumentation and a test module implementing process_connection hooks. Cannot execute without prior environment setup (BLOCK-001). | After httpd build: write test module with apxs, configure event MPM, run test HTTP requests, collect GCOV data. |
| entry | BLOCK-003 | PCA-TE-0002 requires mod_http2 built with nghttp2 library. Cannot execute without nghttp2-dev installation and full httpd build (BLOCK-001). | After httpd build with --enable-http2: configure SSL certificates for HTTPS/2, run HTTP/2 client requests, verify AGAIN return and clogging_input_filters fallback. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_data.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_plan | `test-entry-plan.md` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Install full httpd build dependencies and rebuild with GCOV (CFLAGS='-fprofile-arcs -ftest-coverage -O0 -g' LDFLAGS='-lgcov --coverage')
- Execute PCA-TE-0001: Write test module to verify OK+CONN_STATE_PROCESSING -> lingering_close and AGAIN -> I/O pollset behavior
- Execute PCA-TE-0002: Build mod_http2 with nghttp2, verify AGAIN return propagation and clogging_input_filters fallback
- Run Apache httpd test-framework to check for existing regressions in event MPM and HTTP/2 handling
- Verify third-party module compatibility with the new return contract (AGAIN vs OK in CONN_STATE_PROCESSING)
