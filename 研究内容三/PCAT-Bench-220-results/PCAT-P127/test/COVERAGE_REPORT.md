# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `8b68438b2e0b38909b5b2f76e22ceccd2fa48278` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd` |
| 基线 | `d7ec293abc89a0dde9cc730acfa7ba838601a197` |
| Profile | `httpd` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：This patch introduces multiple confirmed breaking changes: (1) H2HeaderStrictness config directive completely removed -- existing httpd configurations using it will fail startup. (2) Public API functions removed/renamed (h2_util_ignore_header, h2_req_ignore_header, h2_req_ignore_trailer, h2_res_ignore_trailer) -- external modules linking against old symbols will fail. (3) HTTP/2 protocol behavior changed -- nghttp2 RFC9113 validation always disabled, whitespace always stripped instead of rejected. (4) H2_CONF_HEADER_STRICTNESS enum removed from public header, shifting subsequent enum values and breaking ABI. (5) Public macros removed (H2_HD_MATCH_LIT_CS, H2_CREATE_NV_*). All findings confirmed via static source code comparison but runtime coverage testing could not be performed due to build environment limitations.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 9 |
| 测试 findings | 6 |
| 规划入口 | 6 |
| 生成入口 | 6 |
| 验证入口 | 6 |
| 规划输入 | 0 |
| 执行输入 | 0 |
| 契约通过 | 6 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 27 |
| 已覆盖行 | 0 |
| 未覆盖行 | 27 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `blocked` |
| 补丁后构建 | `blocked` |
| 编译器 | `gcc (Ubuntu 11.4.0)` |
| 优化级别 | `not_applicable` |
| 覆盖率工具 | `not_available` |
- Full httpd build requires autotools configure step and runtime dependencies (APR, APR-util, nghttp2, OpenSSL)
- nghttp2-devel not installed on this host; httpd mod_http2 module requires nghttp2 headers to build
- Static API/ABI header verification was performed using pre/post-patch source comparison
- Dynamic (runtime/coverage) testing blocked by build environment requirements

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_config.c:937-942 (h2_cmds)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | Confirmed: H2HeaderStrictness absent from command_rec table | grep found 'H2HeaderStrictness' in old code but absent in new code |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | breached | H2HeaderStrictness directive fully removed. Pre-patch: directive present at h2_config.c:967. Post-patch: directive absent. This is a confirmed breaking config change -- existing configs with this directive will cause httpd startup failure. |

- **覆盖率**: 0/9 (0.00%)
- **未覆盖行**: uncovered_1, uncovered_2, uncovered_3, uncovered_4, uncovered_5, uncovered_6, uncovered_7, uncovered_8, uncovered_9

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0001 | CONFIG_CLI_BEHAVIOR_CHANGE | H2HeaderStrictness directive supported with values highest/rfc7540/rfc9113 | H2HeaderStrictness directive completely removed; existing configs will fail | Pre-patch: AP_INIT_TAKE1("H2HeaderStrictness", ...) at h2_config.c:967. Post-patch: grep returns no match for H2HeaderStrictness in h2_config.c. |
- Static verification confirmed directive removal
- Build environment missing nghttp2-devel; full httpd runtime verification blocked

### PCA-0002: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_session.c:957-966 (h2_session_create)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | nghttp2_option_set_no_rfc9113_leading_and_trailing_ws_validation(options, 1) | Hardcoded 1 (validation disabled) replacing runtime config value |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | nghttp2 RFC9113 validation always disabled. Pre-patch: config-controlled (header_strictness >= 9113 enabled validation). Post-patch: always disabled (hardcoded 1). HTTP/2 clients with whitespace in headers will no longer receive RST_STREAM but will be silently accepted. |

- **覆盖率**: 0/10 (0.00%)
- **未覆盖行**: uncovered_1, uncovered_2, uncovered_3, uncovered_4, uncovered_5, uncovered_6, uncovered_7, uncovered_8, uncovered_9, uncovered_10

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0002 | INPUT_CONTRACT_CHANGE | nghttp2_option_set_no_rfc9113_leading_and_trailing_ws_validation(options, h2_config_sgeti(s, H2_CONF_HEADER_STRICTNESS) < 9113) | nghttp2_option_set_no_rfc9113_leading_and_trailing_ws_validation(options, 1) | h2_session.c:963: hardcoded 1 replaces dynamic config value, removing runtime-configurable validation behavior |
- Source code confirms behavioral change -- dynamic config replaced by hardcoded disable
- Full HTTP/2 runtime testing blocked by build requirements

### PCA-0003: OUTPUT_FORMAT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_util.c:1456-1469 (add_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | strip_field_value_ws(nv) called in add_header | strip_field_value_ws defined at h2_util.c:1416, called at h2_util.c:1459 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability | breached | New strip_field_value_ws() function strips leading/trailing whitespace from all HTTP/2 header field values. Pre-patch: values preserved verbatim. Post-patch: values trimmed. This is a normative output format change affecting all HTTP/2 response headers. |

- **覆盖率**: 0/8 (0.00%)
- **未覆盖行**: uncovered_1, uncovered_2, uncovered_3, uncovered_4, uncovered_5, uncovered_6, uncovered_7, uncovered_8

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0003 | OUTPUT_FORMAT_CHANGE | Header field values stored verbatim; no whitespace transformation applied | strip_field_value_ws(nv) called, removing leading/trailing spaces and tabs from values | h2_util.c:1416 new static function; called at h2_util.c:1459 and h2_util.c:1703 |
- strip_field_value_ws confirmed present and called in all header processing paths
- Static verification confirms behavioral change; runtime verification blocked

### PCA-0004: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_util.h:374-380 (h2_util_ignore_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0004 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | h2_util_ignore_header removed; h2_util_ignore_resp_header added | Pre-patch header: int h2_util_ignore_header(const char *name) at line 396. Post-patch header: int h2_util_ignore_resp_header(const char *name) at line 377. Old symbol absent. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | breached | h2_util_ignore_header() removed from public header h2_util.h. Replaced by h2_util_ignore_resp_header(). External modules using old symbol will fail to link. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0004 | API_SIGNATURE_CHANGE | int h2_util_ignore_header(const char *name); (h2_util.h:396) | int h2_util_ignore_resp_header(const char *name); (h2_util.h:377) | Pre-patch git show confirms old declaration; post-patch grep confirms new name only |
- Header declaration change confirmed via pre/post-patch comparison
- All internal callers updated (h2_c2_filter.c:498, h2_util.c:2446)

### PCA-0005: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_util.h:342-349 (h2_req_ignore_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0005 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | h2_req_ignore_header removed from public header | Pre-patch: int h2_req_ignore_header(const char *name, size_t len) at h2_util.h:345. Post-patch: absent. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | breached | h2_req_ignore_header() removed from public API. Made static internal with changed signature (nghttp2_nv*). External modules cannot use this function. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0005 | API_SIGNATURE_CHANGE | int h2_req_ignore_header(const char *name, size_t len); (h2_util.h:345) | (removed; internal static only) | Pre-patch declaration confirmed; post-patch grep returns no match for h2_req_ignore_header |
- Public API removal confirmed via header file comparison
- No public replacement provided for request header ignore checking

### PCA-0007: API_SIGNATURE_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/http2/h2_util.h:342-349 (h2_res_ignore_trailer)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0007 | static_verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-work/test_api_config_removal.sh` | `bash test_api_config_removal.sh` | h2_res_ignore_trailer renamed to h2_ignore_resp_trailer with expanded behavior | Pre-patch: int h2_res_ignore_trailer at h2_util.h:347. Post-patch: int h2_ignore_resp_trailer at h2_util.h:346. New function also checks IgnoredResponseHeaders. |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | breached | h2_res_ignore_trailer() renamed to h2_ignore_resp_trailer() with behavioral expansion: now also filters hop-by-hop response headers (upgrade, connection, keep-alive, transfer-encoding) from trailers, in addition to IgnoredResponseTrailers. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| static-0007 | API_SIGNATURE_CHANGE | int h2_res_ignore_trailer(name, len) { return ignore_header(IgnoredResponseTrailers, name, len); } | int h2_ignore_resp_trailer(name, len) { return (contains_name(IgnoredResponseHeaders, &nv) \|\| contains_name(IgnoredResponseTrailers, &nv)); } | h2_util.c:1685-1693: new implementation with dual header+trailer filtering. IgnoredResponseHeaders array at h2_util.c:1625-1630. |
- Rename confirmed via header/file comparison
- Behavioral expansion (additional IgnoredResponseHeaders filtering) confirmed via source code review
- len parameter silently dropped (uses strlen) in new implementation

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| build | BLOCKER-0001 | Apache httpd build requires autotools configure step and multiple dependencies (APR, APR-util, nghttp2, OpenSSL, PCRE). nghttp2-devel not installed. Full build attempted but could not complete without installing additional development packages. | Install nghttp2-devel and other missing build dependencies, run autotools configure with appropriate flags, then build with gcov instrumentation for coverage testing. |
| environment | BLOCKER-0002 | Dynamic (runtime) testing of HTTP/2 protocol behavior requires a running Apache httpd instance with mod_http2 loaded, TLS certificates configured, and an HTTP/2-capable client. This environment has not been provisioned. | Set up a dedicated test environment with: Apache httpd build artifacts, self-signed TLS certificates, test virtual host configuration, and curl built with HTTP/2 support for client-side testing. |
| coverage | BLOCKER-0003 | Coverage instrumentation (gcov) requires recompilation with -fprofile-arcs -ftest-coverage -O0 flags. Build prerequisite not met (BLOCKER-0001). | Resolve BLOCKER-0001 first, then rebuild with gcov instrumentation flags to enable patch line coverage measurement. |
| finding | BLOCKER-0004 | Findings PCA-0006, PCA-0008, PCA-0009 have medium priority and were filtered out by --min-priority high. These findings (API rename, macro removal, input contract change) were not included in the test plan. | Re-run test_entry_planner with --min-priority medium to include PCA-0006, PCA-0008, PCA-0009 in the test plan. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-summary.json` |
| coverage_data | `not_available` |
| execution_results | `not_available` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-tasks.json` |
| report | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-plan.md` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P067/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `not_generated` |

## 建议

- Provide migration documentation for the removed H2HeaderStrictness directive
- Document API migration path: h2_util_ignore_header -> h2_util_ignore_resp_header, h2_req_ignore_trailer -> h2_ignore_req_trailer, h2_res_ignore_trailer -> h2_ignore_resp_trailer
- Notify third-party module developers about public API breaks and macro removals
- Set up full build environment and re-run tests with runtime HTTP/2 protocol verification
- Re-run test_entry_planner with --min-priority medium to include PCA-0006, PCA-0008, PCA-0009
