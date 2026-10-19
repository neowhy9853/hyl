# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `324f7af5655a48841a079ac761fedef2ab3d1180` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup` |
| 基线 | `ec7911a3e50c50106b3b021ce6644ffd4cbf6269` |
| Profile | `c_project` |
| 执行状态 | `passed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：Patch line coverage 100% (7/7 executable lines covered). Behavior difference confirmed: POST+301 now automatically redirects to GET, whereas before the patch no redirect occurred. This is a genuine behavioral change — applications relying on the old behavior (no redirect for POST+301) will observe different HTTP session behavior. The change makes libsoup more standards-compliant with common HTTP client behavior (many HTTP clients redirect POST to GET on 301), but represents an incompatibility for users of the old behavior.

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
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 7 |
| 已覆盖行 | 7 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 11.4.0-1ubuntu1~22.04)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov (GCC)` |
- Built with --disable-gtk-doc --without-gnome --enable-debug=yes
- Dummy gtkdocize used for autoreconf
- Before build compiled without coverage flags (behavioral comparison only)
- After build compiled with -fprofile-arcs -ftest-coverage -O0 -g

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `libsoup/soup-session.c:845-853 (redirect_handler)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/_worktrees/patched/tests/.libs/redirect-test` | `LD_LIBRARY_PATH=<patched_libsoup> ./tests/.libs/redirect-test -d -d` | redirect-test: OK (exit code 0) with GET / following POST /301 redirect | gcov shows lines 849-850 executed (56 and 10* hits); debug output confirms 'GET /' follows 'POST /301' |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | breached | POST+301 behavior changed: Before — no automatic redirect (POST completes with 301 status). After — automatic redirect to GET (GET / sent to redirect target). Confirmed by debug output: before shows only 'POST /301 -> 301 Moved Permanently' then next test, after shows 'POST /301 -> 301 Moved Permanently' then 'GET / -> 200 OK'. The side effect manifest is not stable across the patch boundary. |

- **覆盖率**: 7/7 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| redirect-test-POST-301 | SIDE_EFFECT_CHANGE | POST /301 → 301 Moved Permanently → (no redirect) → next test | POST /301 → 301 Moved Permanently → redirect → GET / → 200 OK → next test | Before debug output: '20. POST /301<br>    -> 301 Moved Permanently<br>       Location: /<br><br>21. POST /302'. After debug output: '20. POST /301<br>    -> 301 Moved Permanently<br>       Location: /<br>    GET /<br>    -> 200 OK<br><br>21. POST /302'. Gcov confirms lines 849 (56 hits) and 850 (10* hits) — the new POST+301 code path is exercised. |
- The existing redirect-test was updated in the patch to expect POST+301 redirect but is lenient on completion validation — both before and after builds pass the test suite because the test does not assert that all expected requests were received.
- POST+307 (Temporary Redirect) still does NOT redirect as expected — verified by test case 23.
- GET+301 normal redirect unaffected — else-if branch at line 859 still handles safe methods correctly.
- Applications needing the old behavior should set SOUP_MESSAGE_NO_REDIRECT flag on SoupMessage.

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/phase3_contracts` |
| coverage_data | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/_worktrees/patched/libsoup/soup-session.c.gcov` |
| execution_results | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/phase4_execution` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Document the POST+301 redirect behavior change in release notes.
- Note that SOUP_MESSAGE_NO_REDIRECT flag can be used by applications that need to preserve the old behavior.
- Verify this change does not introduce security issues in applications that previously relied on POST+301 not being forwarded (e.g., CSRF protections).
- POST+307 remains unaffected — no redirect for non-safe methods on 307 is correct per RFC 2616.
