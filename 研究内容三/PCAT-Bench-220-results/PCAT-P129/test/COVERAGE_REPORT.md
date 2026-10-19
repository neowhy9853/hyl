# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `dee1eb37d787d34cb37df7eab535240e1774293a` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd` |
| 基线 | `8ffa19a1f7eb03b156e6bdbda65b3d2a2de9dfe8` |
| Profile | `httpd` |
| 执行状态 | `passed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁修复了 mod_ssl 中 DH 参数自动选择的回归缺陷。补丁前，在未显式配置 DH 参数且证书文件不包含嵌入式 DH 参数的情况下，SSL_CTX_set_dh_auto() 未被调用，导致 TLS 1.2 DHE 密码套件不可用。补丁后，custom_dh_done 变量被提升到函数作用域，else 被替换为独立的 if (!custom_dh_done) 检查，确保在未加载自定义 DH 参数时始终启用自动选择。行为差异已通过 TLS 1.2 DHE 连接对比验证：BEFORE 握手失败（alert 40），AFTER 成功协商 DHE-RSA-AES256-GCM-SHA384。所有 3 个补丁变更行均被 gcov 确认执行（100% 行覆盖率）。判定为 incompatible 是因为补丁前的错误行为导致 TLS 1.2 DHE 密码套件不可用，而补丁恢复了正确的 DH 自动协商功能——这是一个有外部可观察影响的行为差异。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 2 |
| 执行输入 | 2 |
| 契约通过 | 2 |
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
| 编译器 | `gcc (Ubuntu 11.4.0) -O0 -g` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov (GCC)` |
- mod_ssl statically compiled into httpd
- APR/APR-util from bundled sources (srclib/)
- OpenSSL 3.6.3 from conda environment

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `modules/ssl/ssl_engine_init.c:1623-1628 (ssl_init_server_certs)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/build/after/install/test/httpd-test3.conf` | `httpd -f <config> -DFOREGROUND` | openssl s_client -tls1_2 -cipher 'DHE' reports DHE-RSA cipher negotiated | gcov confirms lines 1419, 1623, 1626 executed 10 times; openssl s_client shows DHE-RSA-AES256-GCM-SHA384 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability-TLS12-DHE | passed | BEFORE: handshake_failure alert 40, no DHE cipher negotiated. AFTER: DHE-RSA-AES256-GCM-SHA384 successfully negotiated. Confirms that SSL_CTX_set_dh_auto() is now properly invoked when no custom DH params are configured. |
| side_effect_manifest_stability-TLS13 | passed | Both before and after builds successfully negotiate TLSv1.3 with the same cipher. TLS 1.3 key exchange is handled differently from TLS 1.2 (DH is implicit), so no behavioral difference at the cipher level. |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | SIDE_EFFECT_CHANGE | Handshake failure: ssl/tls alert handshake failure (alert 40). No cipher negotiated (NONE). SSL_shutdown: shutdown while in init. | Handshake success: TLSv1.2, Cipher is DHE-RSA-AES256-GCM-SHA384. Server Temp Key shown. | BEFORE: openssl s_client reports alert handshake failure, cipher (NONE). AFTER: openssl s_client reports DHE-RSA-AES256-GCM-SHA384 negotiated. gcov confirms lines 1623, 1626 executed. The patch moved custom_dh_done to function scope and changed else to if(!custom_dh_done), enabling SSL_CTX_set_dh_auto() call that was previously skipped. |
- 测试使用自签名证书且不包含嵌入式 DH 参数，触发 custom_dh_done == 0 路径
- TLS 1.3 不受影响因为其密钥交换机制与 TLS 1.2 DHE 不同
- 所有 3 个补丁变更行均被覆盖：line 1419 (变量声明), line 1623 (if 条件), line 1626 (SSL_CTX_set_dh_auto 调用)

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/_worktrees/patched/modules/ssl/ssl_engine_init.c.gcov` |
| execution_results | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/test-entry-tasks.json` |
| test_inputs | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P069/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 验证在其他 OpenSSL 版本（1.0.x, 1.1.x, 3.x）下 DH 自动选择行为的一致性
- 检查具有不同 certfile 配置（多证书、engine ID）的 vhost 是否存在边缘情况
- 确认 mod_ssl 现有测试套件中 TLS 1.2 DHE 测试用例是否通过
- 考虑在回归测试中添加正反两组 SSL 配置（含/不含 DH 参数）的自动化测试
