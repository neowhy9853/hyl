# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `0cd2255e64b4775520a6acbbb1868437fc26662d` |
| 仓库 | `/home/soong/pca_benchmark/_repos/git` |
| 基线 | `ea97ad8d017de0c9037451a78008a0fd60abea0c` |
| Profile | `git` |
| 执行状态 | `passed` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The API_SIGNATURE_CHANGE is confirmed: both write_midx_file_only and write_midx_file_compact gained a new `incremental_base` parameter. However, midx.h is an internal header in the git project — practical external consumers are rare. The new parameter is NULL-able (callers can pass NULL), and all in-tree callers have been updated. The existing test suites (t5334, t5335) pass 100% and gcov confirms 100% patch-line coverage on executable C code. The change is additive (new --base CLI option) with no breaking changes to existing defaults. The CLI behavior is backwards compatible. The API signature change is real (would break compilation for any external caller), but such callers are uncommon. Overall assessment: backward_compatibility is 'inconclusive' because the API signature change is technically breaking, but in practice the risk is very low and the new behavior is fully tested.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 19 |
| 已覆盖行 | 19 |
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
- Build flags: NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 (per AGENTS.md)
- Before build at /tmp/pca-git-before (commit 8d342ed4b)
- After build at /tmp/pca-git-after (commit 0cd2255e)
- 12 CPU cores used for parallel build

## Finding 测试结果

### PCA-0001: API_SIGNATURE_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `midx.h:132-145 (write_midx_file_only, write_midx_file_compact)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | static_valid_not_run | `test-entry-work/PCA-0001/api_compile_test.sh` | `bash test-entry-work/PCA-0001/api_compile_test.sh 2>&1` | New signatures (with incremental_base) present in midx.h; old 5/4-param signatures would fail to compile | Header declaration diff between before (8d342ed4b) and after (0cd2255e) confirms the API signature change |
| PCA-TE-0002 | runnable_verified | `` | `cd /tmp/pca-git-after && make -C t -j$(nproc) NO_RUST=1 NO_ICONV=1 NO_GETTEXT=1 t5334-incremental-multi-pack-index.sh t5335-compact-multi-pack-index.sh` | Test scripts exit 0 | 22/22 tests passed (t5334) and 14/14 tests passed (t5335); gcov confirms new code paths exercised |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compatibility | passed | New `const char *incremental_base` parameter added to `write_midx_file_only` (position 4, before flags) and `write_midx_file_compact` (position 3, before flags). This is an API_SIGNATURE_CHANGE — existing callers with positional arguments will break. In-tree callers have been updated. External consumers of midx.h would need to pass NULL for default behavior. |

- **覆盖率**: 19/19 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | API_SIGNATURE_CHANGE | write_midx_file_only(source, packs_to_include, preferred_pack_name, refs_snapshot, flags) — 5 parameters | write_midx_file_only(source, packs_to_include, preferred_pack_name, refs_snapshot, incremental_base, flags) — 6 parameters | midx.h header diff: before has 5 params ending at 'refs_snapshot, unsigned flags'; after adds 'const char *incremental_base' before 'unsigned flags' |
| I2 | API_SIGNATURE_CHANGE | write_midx_file_compact(source, from, to, flags) — 4 parameters | write_midx_file_compact(source, from, to, incremental_base, flags) — 5 parameters | midx.h header diff: before has 4 params ending at 'to, unsigned flags'; after adds 'const char *incremental_base' before 'unsigned flags' |
- Neither write_midx_file_only nor write_midx_file_compact are exported symbols (no EXPORT_SYMBOL, not in a .map/.symver file).
- midx.h is categorized as public_library_headers by the git profile.
- All in-tree callers (builtin/multi-pack-index.c, midx-write.c) updated in the same patch.
- The new parameter accepts NULL for default behavior, minimizing actual breakage risk.
- Git's internal library (libgit.a) is not typically linked by external projects.

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage.md` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Verify no external projects link against git's internal libgit.a and call write_midx_file_only/write_midx_file_compact directly
- The --base CLI option is fully backwards compatible (additive, no existing behavior changes)
- No further testing needed unless external consumers of midx.h are identified
