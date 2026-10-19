# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `24c6bbc92b6dd0ce9b7ff799049498299f70f97d` |
| 仓库 | `/home/soong/pca_benchmark/_repos/cpython` |
| 基线 | `d8ff4f8e56217133be6e22592aa60a1fab331d8e` |
| Profile | `cpython` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：OUTPUT_FORMAT_CHANGE (PCA-0001) confirmed with 9 evidence points from real before/after CPython builds. ZipInfo.FileHeader() output for cp437-encodable filenames without UTF-8 flag changed: encoding from UTF-8 to cp437, flag_bits from 0x0800 to 0x0000. Append-mode central directory now preserves cp437 encoding. Intended gh-84353 fix but represents genuine public API output change. Patch line coverage: 100% (5/5 new/modified executable lines). Coverage gate (80%) met.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 19 |
| 执行输入 | 19 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 2 |
| 补丁可执行行 | 5 |
| 已覆盖行 | 5 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `python3 -m trace --count` |
- Two disposable worktrees at base commit d8ff4f8e56 in compatibility-testing/build-before and build-after
- After worktree patched with PCAT-P015/patch.patch
- configure/make logs: evidence/configure-before.log, evidence/configure-after.log, evidence/make-before.log, evidence/make-after.log
- Probe script: evidence/probe_contract.py
- Probe results: evidence/probe_results_before.json, evidence/probe_results_after.json
- Probe run logs: evidence/probe_before.log, evidence/probe_after.log
- Trace coverage: evidence/trace_run.log, evidence/zipfile.__init__.cover
- Comparison: evidence/comparison_results.json

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `Lib/zipfile/__init__.py:566-577 (_encodeFilenameFlags)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `evidence/probe_contract.py` | `{build-after}/python evidence/probe_contract.py after evidence/` | cp437-encodable names without UTF-8 flag produce different FileHeader output between before and after | Trace coverage confirms all patch lines hit: _encodeFilenameFlags L569(29h) L570(20h) L572(9h) L574(29h) L576(11h). Full evidence in evidence/zipfile.__init__.cover |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0001-output_format-1 | skipped | Before/after diff verified via evidence/comparison_results.json (9 diffs). Full contract suite requires running CPython native zipfile tests. |

- **覆盖率**: 4/4 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| fh-cp437-fuenf | OUTPUT_FORMAT_CHANGE | flags=0x0800 bytes=66c3bc6e66 (utf-8) | flags=0x0000 bytes=66816e66 (cp437) | evidence/comparison_results.json |
| fh-cp437-cafe | OUTPUT_FORMAT_CHANGE | flags=0x0800 bytes=636166c3a9 | flags=0x0000 bytes=63616682 | evidence/comparison_results.json |
| fh-cp437-resume | OUTPUT_FORMAT_CHANGE | flags=0x0800 bytes=72c3a973756dc3a9 | flags=0x0000 bytes=728273756d82 | evidence/comparison_results.json |
| fh-cp437-muenchen | OUTPUT_FORMAT_CHANGE | flags=0x0800 bytes=4dc3bc6e6368656e | flags=0x0000 bytes=4d816e6368656e | evidence/comparison_results.json |
| ascii-hello.txt | OUTPUT_FORMAT_CHANGE | flags=0x0800 | flags=0x0000 | UTF-8 flag cleared on ASCII encode |
| ascii-simple | OUTPUT_FORMAT_CHANGE | flags=0x0800 | flags=0x0000 | UTF-8 flag cleared on ASCII encode |
| ascii-test_file.zip | OUTPUT_FORMAT_CHANGE | flags=0x0800 | flags=0x0000 | UTF-8 flag cleared on ASCII encode |
| flagbits-clearing | OUTPUT_FORMAT_CHANGE | resulting_flags=0x0800 | resulting_flags=0x0000 | _encodeFilenameFlags clears flag on success |
| append-preservation | SIDE_EFFECT_CHANGE | orig_flag_bits=0x0800 | orig_flag_bits=0x0000 | cp437 filename preserved after append |
- OUTPUT_FORMAT_CHANGE confirmed: 9/19 probe results changed, all 10 unchanged tests validate intentional non-regression
- Core: cp437-encodable names w/o UTF-8 flag now encoded as cp437 instead of converted to UTF-8
- Additional: ASCII names with UTF-8 flag now properly cleared on successful encoding
- Unicode-only names and UTF8-flag-prefixed names correctly unchanged in both implementations

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `Lib/zipfile/__init__.py:1816-1822 (_open_to_write)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | runnable_verified | `evidence/probe_contract.py` | `{build-after}/python evidence/probe_contract.py after evidence/` | flag_bits for new writes or append operations differ between before and after | _open_to_write line 1819 covered with 4 hits (evidence/zipfile.__init__.cover) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0002-side_effect-1 | skipped | Append-preservation confirms side effect. New writes unchanged for ASCII due to _encodeFilenameFlags clearing. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| append-preservation | SIDE_EFFECT_CHANGE | orig_flag_bits=0x0800 | orig_flag_bits=0x0000 | evidence/comparison_results.json append-preservation |
- PCA-0002 intertwined with PCA-0001: net effect for new ASCII writes same (flags=0x0000)
- SIDE_EFFECT manifests during append to existing ZIPs with legacy-encoded filenames
- LZMA and non-seekable branches not covered: no LZMA/streaming inputs in probes

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | COV-001 | ZIP_LZMA branch not exercised | Add LZMA compression test case |
| coverage | COV-002 | Non-seekable branch not exercised | Test ZipFile with BytesIO stream |

## 产物

| Artifact | Path |
|---|---|
| configure_after_log | `evidence/configure-after.log` |
| configure_before_log | `evidence/configure-before.log` |
| contract_summary | `phase3_contracts/contracts.jsonl` |
| coverage_data | `evidence/zipfile.__init__.cover` |
| execution_results | `evidence/comparison_results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| make_after_log | `evidence/make-after.log` |
| make_before_log | `evidence/make-before.log` |
| probe_results_after | `evidence/probe_results_after.json` |
| probe_results_before | `evidence/probe_results_before.json` |
| probe_script | `evidence/probe_contract.py` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Verify no production code depends on FileHeader() UTF-8 output for cp437-encodable names
- Run full Lib/test/test_zipfile/ suite against both builds
- Test LZMA and non-seekable paths for completeness
