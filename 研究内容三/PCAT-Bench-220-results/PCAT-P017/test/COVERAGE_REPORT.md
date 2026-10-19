# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `b61737679e1f5ce2aaf19d075784a40bd5f4938a` |
| 仓库 | `/home/soong/pca_benchmark/_repos/libxml2` |
| 基线 | `47f416a5829356f55efa6f48a7e668c8de359e5a` |
| Profile | `libxml2` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch tightens parseInteger() input contract by rejecting negative values that were previously silently wrapped by strtoul. Error message and detection point changed. This is an intentional security fix (preventing silent disable of --max-ampl on 32-bit), but it changes observable CLI behavior. CTest regression suite passes. Patch line coverage is 100%.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 3 |
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
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Both before (parent 47f416a) and after (b617376) built with Ninja, CMake, -O0 -g --coverage
- All 22 CTest tests pass on the patched build
- Host is x86_64 Ubuntu 24.04, not a 32-bit platform where the original bug manifests differently

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `xmllint.c:2501-2503 (parseInteger)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-0001 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --maxmem -1 --version` | stderr contains 'value not allowed: -1', exit code 1 | gcov shows 7 hits on xmllint.c:2502 |
| ENTRY-0002 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --max-ampl -1 --version` | stderr contains 'value not allowed: -1', exit code 1 | gcov shows 7 hits on xmllint.c:2502 |
| ENTRY-0003 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --pretty -1 --version` | stderr contains 'value not allowed: -1', exit code 1 | gcov confirms same code path |
| ENTRY-0004 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --maxmem 0 --version` | No value-not-allowed error, positive path works | gcov shows 4 hits on strtoul path (xmllint.c:2506+) |
| ENTRY-0005 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --maxmem 1000 --version` | No value-not-allowed error, positive path works | gcov confirms strtoul path coverage |
| ENTRY-0006 | passed | `test-entry-work/PCA-0001/` | `./build/xmllint --max-ampl -999999999 --version` | stderr contains 'value not allowed: -999999999', exit code 1 | gcov confirms negative check path |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | --maxmem -1: BEFORE prints 'integer out of range', AFTER prints 'value not allowed'. Detection point changed from strtoul-range-check to explicit '-' prefix check. Exit code same (1). |
| backward_input_acceptance | breached | --max-ampl -1: BEFORE prints 'integer out of range', AFTER prints 'value not allowed'. Same exit code (1). |
| backward_input_acceptance | breached | --pretty -1: BEFORE prints 'integer out of range', AFTER prints 'value not allowed'. Same exit code (1). |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1/I2/I3/I6 | INPUT_CONTRACT_CHANGE | strtoul('-1') wraps to ULONG_MAX on 64-bit (or wraps past range check on 32-bit); prints 'integer out of range: -1'; exit code 1 | Early '-' prefix check catches negative values; prints 'value not allowed: -1'; exit code 1 | gcov confirms L2501-L2503 executed 7 times; error message differs between builds |
| I4/I5 | INPUT_CONTRACT_CHANGE | Positive/zero value accepted via strtoul; no error; exit 0 | Same: positive/zero still accepted via strtoul; '-' check passes through; exit 0 | gcov confirms L2501 (if check) passed through (took else branch), L2506+ executed 4 times |
- All 3 CLI options affected: --maxmem, --max-ampl, --pretty
- On 64-bit: error message changed but both versions reject the input (exit 1)
- On 32-bit: old code silently accepts negative values as large unsigned; new code properly rejects
- CTest: all 22 tests pass on patched build
- Coverage: 100% of patch executable lines hit by directed tests

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase4_execution/contract_verification_data` |
| coverage_data | `phase4_execution/coverage_data.gcov` |
| execution_results | `phase4_execution/` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Verify any scripts passing negative values to --maxmem/--max-ampl/--pretty
- Update any test assertions that expect 'integer out of range' error message for negative values
- Consider documenting the new input validation in xmllint man page
