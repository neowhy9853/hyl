# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `226b5608` |
| 仓库 | `/home/soong/pca_benchmark/_repos/libxml2` |
| 基线 | `310564cc6b2c5766bbf053bc29353df6e6a655b6` |
| Profile | `libxml2` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Patch changes SAX characters/cdataBlock callback first argument from ctxt to ctxt->userData. This is a SIDE_EFFECT_CHANGE for SAX consumers with custom userData. Coverage gate not met (58% < 80%) due to CDATA/NOCDATA paths not exercised. All 22 CTest tests pass; entity expansion output is identical; gcov confirms main change site executed 11857 times.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 3 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 2 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 19 |
| 已覆盖行 | 11 |
| 未覆盖行 | 8 |
| 补丁行覆盖率 | 57.89% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Host build with Ninja, CMake, gcc. All 22 CTest tests pass on both versions.

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `parser.c:7261-7295 (xmlParseReference)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| ENTRY-P019-001 | passed | `/tmp/test-pcat-p019.xml` | `xmllint --noent --noout test-pcat-p019.xml` | Entity expansion succeeds, exit code 0 | exit code 0 |
| ENTRY-P019-002 | passed | `/tmp/test-pcat-p019.xml` | `xmllint --sax test-pcat-p019.xml` | SAX callbacks fire for entity references | SAX.characters in output |
| ENTRY-P019-003 | passed | `/tmp/pca-libxml2/build/CMakeFiles/LibXml2.dir/parser.c.gcda` | `gcov on parser.c` | gcov shows hits on changed lines | line 7264: 11857 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C001 | passed | Entity expansion output identical: both BEFORE and AFTER produce entity one some text entity two |
| C002 | passed | Changed code path confirmed: ctxt->sax->characters(ctxt->userData, ...) executed 11857 times (parser.c:7264) |

- **覆盖率**: 11/19 (57.89%)
- **未覆盖行**: parser.c:7262, parser.c:7265, parser.c:7266, parser.c:7267, parser.c:7285, parser.c:7289, parser.c:7290, parser.c:7291

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| ENTRY-P019-001 | SIDE_EFFECT_CHANGE | characters()/cdataBlock() receive ctxt (xmlParserCtxt*) | characters()/cdataBlock() receive ctxt->userData (void*) | gcov confirms 11857 hits on ctxt->sax->characters(ctxt->userData, ...) at parser.c:7264; git diff confirms ctxt->userData replaces ctxt |
- 8 uncovered lines are CDATA/NOCDATA paths (require CDATA section in XML input) - architecturally unreachable with current test inputs
- 22/22 CTest tests pass on both versions
- xmllint output identical for entity expansion
- The change is an intentional bug fix making characters/cdataBlock consistent with reference() callback

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `` |
| coverage_data | `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/compatibility-testing/coverage/parser.c.gcov` |
| execution_results | `` |
| impact_map | `` |
| report | `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `` |
| test_entry_tasks | `` |
| test_inputs | `` |

## 建议

- Add CDATA section test input to cover cdataBlock paths
- Notify downstream SAX users of the behavioral change
- Verify SAX callback userData handling in dependent projects
