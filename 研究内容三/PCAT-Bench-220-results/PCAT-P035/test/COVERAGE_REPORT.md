# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `632838` |
| 仓库 | `/home/soong/pca_benchmark/_repos/ruby` |
| 基线 | `8ff8963995e6df14c0ec589a526a268dde4b9cc5` |
| Profile | `ruby` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch changes the input contract of Time.xmlschema, Time.iso8601, and Time.rfc3339: strings with leading/trailing whitespace that previously raised ArgumentError are now silently stripped and parsed correctly. 3/4 contract probes show behavioral change (BEFORE: reject, AFTER: accept). The change is intentional (bug fix per commit message) but is a confirmed INPUT_CONTRACT_CHANGE - code relying on the old rejection behavior for validation will be silently affected.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 7 |
| 执行输入 | 7 |
| 契约通过 | 1 |
| 契约违约 | 3 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 1 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Built with: --disable-install-doc --disable-yjit --disable-zjit optflags="-O0 --coverage" LDFLAGS="--coverage"
- Built date_core.so extension manually from ext/date sources
- Ruby-level patch in lib/time.rb - gcov covers C code only (time.c: 25.14%)

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `lib/time.rb:670-676 (Time._xmlschema)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/test-entry-work/PCA-0001/test_xmlschema_whitespace.rb` | `/tmp/pca-ruby-after-build/ruby --disable-gems -I/tmp/pca-ruby-after/lib -I/tmp/pca-ruby-after-build -I/tmp/pca-ruby-after/ext/date/lib test_xmlschema_whitespace.rb` | exit code 0 (all assertions pass) | Patched line lib/rime.rb:673 (time.strip) reached - confirmed by behavior change in contract probe |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| input_acceptance_leading_whitespace | breached | Input "  	  1985-04-12T23:20:50.52Z": BEFORE raises ArgumentError (can't parse), AFTER correctly parses to Time(1985-04-12 23:20:50.52 UTC) |
| input_acceptance_trailing_whitespace | breached | Input "1985-04-12T23:20:50.52Z  	 ": BEFORE raises ArgumentError (can't parse), AFTER correctly parses to Time(1985-04-12 23:20:50.52 UTC) |
| input_acceptance_tab_whitespace | breached | Input "	1985-04-12T23:20:50.52Z	": BEFORE raises ArgumentError (can't parse), AFTER correctly parses to Time(1985-04-12 23:20:50.52 UTC) |
| input_acceptance_no_whitespace | passed | Input "1985-04-12T23:20:50.52Z" (control): BEFORE and AFTER both correctly return Time(1985-04-12 23:20:50.52 UTC) - no behavior change |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-TE-0001-I1 | INPUT_CONTRACT_CHANGE | REJECTED: can't parse | ACCEPTED: 1985-04-12 23:20:50 UTC | Leading whitespace input. BEFORE raises ArgumentError from time.c parser. AFTER passes time.strip then parses correctly. |
| PCA-TE-0001-I2 | INPUT_CONTRACT_CHANGE | REJECTED: can't parse | ACCEPTED: 1985-04-12 23:20:50 UTC | Trailing whitespace input. BEFORE raises ArgumentError. AFTER strips whitespace and parses correctly. |
| PCA-TE-0001-I3 | INPUT_CONTRACT_CHANGE | REJECTED: can't parse | ACCEPTED: 1985-04-12 23:20:50 UTC | Tab whitespace input (leading and trailing). BEFORE rejects. AFTER handles correctly. |
- The patch intentionally relaxes input contract for Time.xmlschema/iso8601/rfc3339 to accept leading/trailing whitespace.
- This is a deliberate bug fix documented in commit message: "Fix Time.xmlschema handling leading and trailing whitespaces"
- 3 contract breaches are expected - they represent the intentional behavioral change (bug fix)
- All 7 directed test assertions pass on patched (AFTER) build
- No-whitespace control test PASSES on both builds - no regression

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/phase4_execution/coverage.json` |
| execution_results | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- Review callers that may depend on Time.xmlschema raising ArgumentError for whitespace-padded inputs as a validation mechanism
- Update any test fixtures that expected ArgumentError for whitespace-padded XMLSchema timestamps
- Verify that Time.parse (which delegates to xmlschema in some paths) is not unexpectedly affected
