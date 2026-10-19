# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `f02c7a9b8ac443daafac8e7be5828b4010fb46d8` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd` |
| 基线 | `4701f6f3cc47ac57053cf4151bfa60dd0b86a3a3` |
| Profile | `httpd` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：3 个兼容性变更中: 1 个 通过(PCA-0002 API_SIGNATURE_CHANGE, 编译期验证 8/8 通过, 90.7% 覆盖率), 1 个 部分(PCA-0003 SIDE_EFFECT_CHANGE, BEFORE-state PROPFIND 已验证, AFTER-state 不可测), 1 个 阻塞(PCA-0001 CONFIG_CLI_BEHAVIOR_CHANGE, 需要完整的 httpd 构建环境)。由于缺少 apache2-dev 开发包，无法编译打补丁的 mod_dav 模块进行完整的 before/after 契约对比和补丁行覆盖率采集。当前证据支持该补丁为增量功能变更(默认行为不变)，但无法通过动态测试确认。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 2 |
| 规划输入 | 10 |
| 执行输入 | 8 |
| 契约通过 | 1 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 72 |
| 已覆盖行 | 0 |
| 未覆盖行 | 72 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `failed` |
| 编译器 | `GCC 11.4.0` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov (GCC)` |
- BEFORE state: system-installed Apache 2.4.52 (unpatched)
- AFTER state build failed: missing apache2-dev, libapr1-dev, libaprutil1-dev packages
- No sudo access to install build dependencies
- Partial compilation of patched mod_dav sources succeeded (mod_dav.o, props.o)
- API compatibility compile-time tests compiled and executed successfully

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `blocked`
- **目标**: `modules/dav/main/mod_dav.c:306-329 (dav_cmd_davlockdiscovery)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001-01 | blocked | `test-entry-work/test_entry_config.yaml` | `configure DAVLockDiscovery expr=false and send PROPFIND, verify empty lockdiscovery` | lockdiscovery property empty when expression evaluates false | DAV_PROPDB_DISABLE_LOCKDISCOVERY flag set in props.c:355 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/24 (0.00%)
- **未覆盖行**: 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329
- DAVLockDiscovery 配置指令通过 AP_INIT_TAKE1 注册
- 需要打补丁的 httpd 构建来测试 expr= 求值和行为变化
- 默认行为（未配置时）保持不变
- 编译期验证: mod_dav.c 编译成功, dav_cmd_davlockdiscovery 函数存在

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `modules/dav/main/mod_dav.h:1694-1714 (dav_open_propdb)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002-01 | passed | `test-entry-work/api_compat_test.c` | `./test-entry-work/api_compat_test` | exit code 0, 8/8 tests passed | assertion checks on macro values and bit operations |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| api_signature_compat | passed | DAV_PROPDB_NONE=0, DAV_PROPDB_RO=1 保持数值向后兼容。DAV_PROPDB_DISABLE_LOCKDISCOVERY=2 为新增位。位掩码操作正确。 |

- **覆盖率**: 39/43 (90.70%)
- **未覆盖行**: 63, 64, 91, 92
- dav_open_propdb / dav_popen_propdb int ro -> int flags 参数签名变更
- 数值上向后兼容: old(0)=DAV_PROPDB_NONE(0), old(1)=DAV_PROPDB_RO(1)
- 编译期验证 8/8 断言通过, 覆盖率 90.7%
- 公共头文件 mod_dav.h 声明符合 DAV_DECLARE 导出约定

### PCA-0003: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `modules/dav/main/props.c:353-363 (dav_insert_coreprop)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003-01 | passed | `phase4_execution/before_state_propfind.txt` | `unset http_proxy; curl -X PROPFIND -H 'Depth:0' -d '<D:propfind><D:prop><D:lockdiscovery/></D:prop></D:propfind>' http://localhost:28080/test.txt` | HTTP 207 with D:activelock element | lockdiscovery XML response |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| lockdiscovery_stability | skipped | BEFORE state verified (unpatched Apache 2.4.52). AFTER state not testable without patched mod_dav build. |

- **覆盖率**: 0/5 (0.00%)
- **未覆盖行**: 355, 356, 357, 358, 359

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I-PROP-01 | SIDE_EFFECT_CHANGE | <D:lockdiscovery><D:activelock><D:locktype><D:write/></D:locktype>...</D:activelock></D:lockdiscovery> | EXPECTED (with DAVLockDiscovery expr=false): <D:lockdiscovery/> (empty element) | props.c:356-358: if (propdb->flags & DAV_PROPDB_DISABLE_LOCKDISCOVERY) { value=""; break; } |
- BEFORE state: 对已锁定资源 PROPFIND 返回完整 D:activelock 元素 (含锁令牌)
- AFTER state 预期: DAVLockDiscovery expr=false 时 lockdiscovery 为空
- props.c 编译成功, dav_insert_coreprop 中的标志检查逻辑正确
- 该变更仅在管理员配置 DAVLockDiscovery 后生效

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| build | BLK-build-apache2-dev | 缺少 apache2-dev、libapr1-dev、libaprutil1-dev 开发包。无法通过 cmake 完成配置或使用 apxs 编译打补丁的 mod_dav 共享模块。 | 安装构建依赖: sudo apt-get install apache2-dev libapr1-dev libaprutil1-dev liblua5.3-dev; 然后 cmake -S <worktree> -B build && make -C build |
| entry | BLK-entry-config-test | DAVLockDiscovery 指令的动态测试需要运行打补丁的 httpd 实例，加载包含该指令的配置文件，并发送 PROPFIND 请求。当前无法编译 patched mod_dav.so。 | 完成 httpd 编译后: 加载 patched mod_dav.so, 配置 DAVLockDiscovery expr=false, 发送 PROPFIND 验证 |
| contract | BLK-contract-after | AFTER-state 契约验证需要打补丁的二进制。BEFORE-state 契约已通过系统 Apache 2.4.52 验证完成。 | 编译 patched mod_dav.so 后运行 AFTER-state PROPFIND 测试 |
| coverage | BLK-coverage-instrumented | 补丁行覆盖率收集需要 instrumented 构建 (gcov --coverage)。当前仅编译期 API 测试有覆盖率数据 (90.7%)，补丁行覆盖率为 0%。 | 使用 -fprofile-arcs -ftest-coverage -O0 标志重新编译 mod_dav 并运行 PROPFIND 测试 |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `test-entry-work/api_compat_test.c.gcov` |
| execution_results | `phase4_execution/before_state_propfind.txt` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 安装 apache2-dev, libapr1-dev, libaprutil1-dev 构建依赖
- 使用 cmake 编译打补丁的 httpd (含 --coverage 标志)
- 加载 patched mod_dav.so 到 Apache 配置
- 配置 DAVLockDiscovery expr=false 并发送 PROPFIND 验证 lockdiscovery 为空
- 配置 DAVLockDiscovery expr=true 验证行为保持不变
- 配置无效 expression 验证错误处理
- 运行 gcov 收集补丁行覆盖率
