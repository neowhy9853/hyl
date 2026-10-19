# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `5235467b9183a8be8675aed17bd5b5a993975da7` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython` |
| 基线 | `c3972f2795bf9270008d09dc6919b9735e20c606` |
| Profile | `c_project` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：本次补丁对 python -m inspect CLI 接口进行了重大重构，引入4个已确认的兼容性变更：2个高优先级（OUTPUT_FORMAT_CHANGE 和 CONFIG_CLI_BEHAVIOR_CHANGE）和2个中优先级（ERROR_EXCEPTION_CHANGE）。所有6项契约测试均发现破坏性变化。具体来说：(1) --details 输出格式结构性变化（新增 Source 字段、字段重命名、别名解析）；(2) 内置模块从无条件拒绝变为 --details 模式下成功返回信息；(3) 错误消息文本完全变更；(4) traceback 被 replace 为格式良好的错误消息。虽然这些变更是有意的功能改进（NEWS 文件记录），但它们构成对被依赖的输出格式、错误消息和退出行为的破坏性变更。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 2 |
| 生成入口 | 5 |
| 验证入口 | 5 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 0 |
| 契约违约 | 6 |
| 契约跳过 | 0 |
| 补丁可执行行 | 120 |
| 已覆盖行 | 0 |
| 未覆盖行 | 120 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (CPython ./configure && make)` |
| 优化级别 | `-O0 (debug build, no PGO)` |
| 覆盖率工具 | `not_applicable_cli_contract_testing` |
- Python 3.15.0a8+ built from source for both before and after builds
- No gcov instrumentation needed - testing CLI behavioral output contracts
- Before: base_commit c3972f27, After: patched commit 5235467b

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `Lib/inspect.py:3475-3490 (_main)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| TE-0001-01 | verified | `test-entry-work/TE-0001-01.sh` | `python -m inspect unittest --details` | Source: and Submodule search paths: keywords in stdout | Source: in stdout |
| TE-0001-02 | verified | `test-entry-work/TE-0001-02.sh` | `python -m inspect os:path.join --details` | looked up as in stdout | looked up as in stdout |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| output_format_stability_unittest | breached | Before: no Source field, singular search path. After: has Source field, plural search paths. |
| output_format_stability_alias | breached | Before: Target=os:path.join. After: Target=posixpath:join (looked up as "os:path.join") |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | OUTPUT_FORMAT_CHANGE | No 'Source:' field; 'Submodule search path' (singular) | Has 'Source:' field; 'Submodule search paths' (plural) | Stdout diff confirms field addition and rename |
| I2 | OUTPUT_FORMAT_CHANGE | Target: os:path.join | Target: posixpath:join (looked up as "os:path.join") | Stdout diff confirms alias resolution and Source field addition |
- Output format is the primary compatibility concern
- Source field is a net-new addition
- Submodule search path -> Submodule search paths rename affects parsers

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `Lib/inspect.py:3478-3485 (_main)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| TE-0002-01 | verified | `test-entry-work/TE-0002-01.sh` | `python -m inspect sys --details` | exit code 0 with formatted output | Target: sys in stdout |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability_builtin_details | breached | Before: exit 1, error on stderr. After: exit 0, details on stdout. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I3 | CONFIG_CLI_BEHAVIOR_CHANGE | exit 1, 'Can't get info for builtin modules.' on stderr | exit 0, formatted details on stdout | Exit code change from 1 to 0, output moves from stderr to stdout |
- Most impactful behavioral change: built-in modules now succeed with --details
- Exit code change from 1 to 0 breaks scripts relying on failure

### PCA-0003: ERROR_EXCEPTION_CHANGE

- **优先级**: `medium`
- **状态**: `failed`
- **目标**: `Lib/inspect.py:3478-3485 (_main)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| TE-0003-01 | verified | `test-entry-work/TE-0003-01.sh` | `python -m inspect sys` | exit code 1 | exit code 1 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| error_message_stability_sys | breached | Before: 'Can't get info for builtin modules.'. After: 'No source code available for builtin module' |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I4 | ERROR_EXCEPTION_CHANGE | 'Can't get info for builtin modules.' | 'No source code available for builtin module' | Stderr error message text completely different |
- Error message text change affects string-matching scripts
- Same exit code (1) as before

### PCA-0004: ERROR_EXCEPTION_CHANGE

- **优先级**: `medium`
- **状态**: `failed`
- **目标**: `Lib/inspect.py:3351-3445 (_get_details_for_cli)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| TE-0004-01 | verified | `test-entry-work/TE-0004-01.sh` | `python -m inspect _testcapi` | exit code 1 and formatted error line | exit 1 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| error_message_stability_testcapi | breached | Before: OSError traceback. After: 'No source code available for defining module' |
| error_message_stability_source_suffixes | breached | Before: TypeError traceback. After: 'Failed to retrieve source code for given target' |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I5 | ERROR_EXCEPTION_CHANGE | OSError traceback for extension module | 'No source code available for defining module' | Traceback replaced with clean error message |
| I6 | ERROR_EXCEPTION_CHANGE | TypeError traceback for data target | 'Failed to retrieve source code for given target' | Traceback replaced with clean error message |
- Clean error messages replace tracebacks for better UX
- New error paths detected for previously silent failures

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| finding | PCA-0003 | Low priority findings not targeted for testing (only High priority was selected) | Extend --min-priority to medium to test medium-priority error message changes |
| finding | PCA-0004 | Low priority findings not targeted for testing (only High priority was selected) | Extend --min-priority to medium to test medium-priority error message changes |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `not_applicable` |
| execution_results | `phase4_execution/behavior_diff.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 审核并更新任何解析 python -m inspect --details 输出的脚本或文档
- 检查 CI/CD 流程中是否依赖特定错误消息字符串匹配 (如 'Can't get info for builtin modules.')
- 检查是否有脚本依赖 python -m inspect <builtin> --details 的 exit 1 行为
- 更新任何捕获并解析 'Submodule search path' (单数形式) 的自动化工具
- 考虑在 CHANGELOG 中明确标记这些 CLI 变更对自动化脚本的影响
