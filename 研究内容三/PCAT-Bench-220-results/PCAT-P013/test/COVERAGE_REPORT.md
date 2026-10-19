# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `07ae6f133ad7a4e7ed506f6a511809b1fc3d1465` |
| 仓库 | `/home/soong/pca_benchmark/_repos/cpython` |
| 基线 | `71cf3130c6e5dd903837b6871af99156c799fd1e` |
| Profile | `cpython` |
| 执行状态 | `passed` |
| 向后兼容结论 | `compatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁修复了 parse_config_h() 对 pyconfig.h 中双引号字符串值未正确剥离引号的 bug。行为变化已通过直接 API 测试、get_config_vars 间接影响验证以及项目原生测试三种方式确认。所有变化均属预期修复，不引入意外回归。补丁行覆盖率达到 100%（3/3），故障排除。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 5 |
| 执行输入 | 5 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 3 |
| 已覆盖行 | 3 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O3 -g (default build)` |
| 覆盖率工具 | `python -m trace (Python line coverage)` |
- 补丁仅修改 Python 代码（Lib/sysconfig/__init__.py, Lib/test/test_sysconfig.py），无需 C 扩展重编译
- before/after 构建均从 base_commit 71cf3130c6 出发，after 额外应用 patch.diff
- 使用 Python trace module 收集变更行覆盖率

## Finding 测试结果

### PCA-0001: RETURN_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `Lib/sysconfig/__init__.py:437-453 (parse_config_h)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/probe_parse_config_h.py` | `{VERSION_DIR}/bin/python3 test-entry-work/PCA-0001/probe_parse_config_h.py` | exit_code: 0 (after), 1 (before) for quote-stripping assertion | parse_config_h() called with mock config.h containing quoted and unquoted #define values; all 4 assertions passed (after) |
| PCA-TE-0002 | runnable_verified | `test-entry-work/PCA-0001/run_native_test.sh` | `{VERSION_DIR}/bin/python3 -m test test_sysconfig -m test_PY_BUILTIN_HASHLIB_HASHES_in_vars` | exit_code: 0 (after), 4/NO TESTS RAN (before) — test exists only in patched version | test_PY_BUILTIN_HASHLIB_HASHES_in_vars executes and asserts PY_BUILTIN_HASHLIB_HASHES does not start with quote |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| return_contract_stability | passed | RETURN_CONTRACT_CHANGE 对应的契约验证：parse_config_h() 返回字典中带双引号的字符串值应在补丁后被剥离引号。before/after 对比：before 构建中 PY_BUILTIN_HASHLIB_HASHES 保留引号（exit=1），after 构建中引号被剥离（exit=0）。before 构建无新增测试方法（NO TESTS RAN），after 构建测试通过（SUCCESS）。行为差异确认与预期完全一致，无意外回归。 |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | RETURN_CONTRACT_CHANGE | parse_config_h 返回带引号的字符串值：'"md5,sha1,sha256"'、'"42"' | parse_config_h 返回剥离引号的字符串值：'md5,sha1,sha256'、42 (int) | before_probe exit=1 (3 failures), after_probe exit=0 (0 failures) |
| I2 | RETURN_CONTRACT_CHANGE | get_config_vars()['PY_BUILTIN_HASHLIB_HASHES'] = '"md5,sha1,sha2,sha3,blake2"' (含引号) | get_config_vars()['PY_BUILTIN_HASHLIB_HASHES'] = 'md5,sha1,sha2,sha3,blake2' (无引号) | before 构建中 get_config_vars 返回带引号的配置值；after 构建中返回无引号的值 |
| I3 | RETURN_CONTRACT_CHANGE | 新增测试 test_PY_BUILTIN_HASHLIB_HASHES_in_vars 不存在（未合入补丁）— NO TESTS RAN | 新增测试执行并通过 — SUCCESS (1 test) | before: NO TESTS RAN exit=4; after: SUCCESS exit=0 |
- 所有 3 条补丁可执行行（L440 quoted_re 初始化、L449 walrus 匹配、L450 引号剥离）均被覆盖执行
- 直接 API 测试和行为验证均确认补丁正确实现了引号剥离行为
- 构建时生成的 _sysconfigdata 中 PY_BUILTIN_HASHLIB_HASHES 在补丁后也不再包含外围引号

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_trace/` |
| execution_results | `phase4_execution/` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 通知下游依赖 sysconfig.parse_config_h() 或直接读取 _sysconfigdata 中字符串配置值的项目，升级后字符串值不再包含外围双引号
- 如果外部工具依赖带引号的原始 pyconfig.h 字符串值（如直接解析 _sysconfig_vars_*.json），需要适配去掉引号逻辑
