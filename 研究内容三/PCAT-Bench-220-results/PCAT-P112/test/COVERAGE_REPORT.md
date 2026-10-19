# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `becb3a0ab8aa986f829efb77a52d53e75419c413` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup` |
| 基线 | `21e5e79b0a0ea426b0d3319c519c2b2df3f43f19` |
| Profile | `libsoup` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁将 HTTP 重定向处理中无 host URI 的行为从崩溃（SIGSEGV）改为返回 SOUP_STATUS_MALFORMED 错误。虽然新行为更安全、正确，但这构成向后不兼容的行为变更：依赖旧崩溃行为的调用方现在会收到 HTTP 错误而非进程终止。所有补丁变更行（4 条可执行行）均已通过 redirect-test 覆盖，覆盖率 100%。PCA-0002/0003 的 defensive 检查也被间接触发。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 1 |
| 执行输入 | 1 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 4 |
| 已覆盖行 | 4 |
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
| 覆盖率工具 | `gcov (GCC 11.4.0)` |
- 使用 autotools (autoreconf + configure + make) 构建
- 禁用了 SSL (--disable-ssl) 和 GNOME (--without-gnome) 支持以简化构建依赖
- 创建了两个隔离 worktree：baseline (base_commit) 和 patched (patch applied)
- 补丁版本的 redirect-test 程序被用于测试基线库和补丁库

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `libsoup/soup-session.c:890-890 (redirect_handler)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/_worktrees/patched/tests/.libs/redirect-test` | `LD_LIBRARY_PATH=<libsoup_lib> ./redirect-test` | redirect-test: OK (exit 0) with patched library; SIGSEGV (exit 139) with baseline library on bad-no-host redirect | gcov coverage: soup-session.c:890 executed 32 times, error branch (line 891) entered 2 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | passed | 输入契约验证通过：补丁前重定向到无 host URI（如 about:blank）导致 SIGSEGV 崩溃；补丁后返回 SOUP_STATUS_MALFORMED 错误。新行为正确拒绝无效输入而不崩溃，正常重定向（有 host 的 URL）不受影响。 |

- **覆盖率**: 4/4 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| redirect-to-about:blank | INPUT_CONTRACT_CHANGE | 进程因 SIGSEGV 崩溃 (exit code 139)，日志中有 GLib 警告（无害） | 测试通过 (exit code 0)，输出 "redirect-test: OK"，/bad-no-host 测试用例正确收到 SOUP_STATUS_MALFORMED | Before: `LD_LIBRARY_PATH=baseline/libsoup/.libs ./redirect-test` → exit 139 (SIGSEGV)。After: `LD_LIBRARY_PATH=patched/libsoup/.libs ./redirect-test` → exit 0 (OK)。gcov 确认 soup-session.c:890 行被执行 32 次，错误分支（行 891）被进入 2 次。 |
- 补丁的 redirect-test 新增了 /bad-no-host 测试用例，验证对无 host 重定向的正确处理
- gcov 显示: soup-session.c:890 覆盖 32 次执行 (完整路径覆盖), soup-uri.c:968 覆盖 204 次, soup-uri.c:992-993 覆盖 196 次
- 所有 4 条补丁变更可执行行均已被 redirect-test 测试覆盖

### PCA-0002: INPUT_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `libsoup/soup-uri.c:968-968 (soup_uri_host_hash)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- 非高优先级 finding，按 --min-priority high 过滤未生成专项测试入口
- redirect-test 间接触发了 soup_uri_host_hash（从 GHashTable 内部调用），gcov 显示该行被执行 204 次
- defensive g_return_val_if_fail 检查，正常路径已覆盖

### PCA-0003: INPUT_CONTRACT_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `libsoup/soup-uri.c:992-993 (soup_uri_host_equal)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 2/2 (100.00%)
- **未覆盖行**: -
- 非高优先级 finding，按 --min-priority high 过滤未生成专项测试入口
- redirect-test 间接触发了 soup_uri_host_equal（从 GHashTable 内部调用），gcov 显示该行被执行 196 次
- defensive g_return_val_if_fail 检查，正常路径已覆盖

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| entry | PCA-0002-medium | finding PCA-0002 测试优先级为 medium，按 --min-priority high 过滤未生成测试入口 | 若需要覆盖 PCA-0002，使用 --min-priority medium 重新运行 test_entry_planner.py |
| entry | PCA-0003-medium | finding PCA-0003 测试优先级为 medium，按 --min-priority high 过滤未生成测试入口 | 若需要覆盖 PCA-0003，使用 --min-priority medium 重新运行 test_entry_planner.py |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/contract_verification.json` |
| coverage_data | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/coverage-data.json` |
| execution_results | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 依赖 libsoup 进行 HTTP 重定向的应用程序应更新其错误处理逻辑，捕获 SOUP_STATUS_MALFORMED 状态码
- 确认所有 HTTP 重定向场景下的正常流程不受影响（已验证 redirect-test 全部通过）
- 建议对 PCA-0002（soup_uri_host_hash）和 PCA-0003（soup_uri_host_equal）进行专项 NULL host 路径测试
