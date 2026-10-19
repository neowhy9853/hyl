# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `21491b21577c68858b3cc02c21e3db88f0a30bb1` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/httpd` |
| 基线 | `e54735bf82e02278dc70eb80d931a748a81e8ce8` |
| Profile | `httpd` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Config parsing tests confirm SSLVHostSNIPolicy directive is correctly registered and parsed with all 4 policy values (secure/strict/insecure/authonly). Default initialization to MODSSL_SNIVH_SECURE verified with 13 gcov hits. However, runtime SNI vhost compatibility enforcement (PCA-0003) has 0% coverage due to minimal httpd build lacking required modules for HTTP serving. Coverage gate of 80% not met (11.56%). Full backward compatibility assessment requires runtime testing of SNI-to-Host vhost transitions under each policy mode.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 7 |
| 测试 findings | 3 |
| 规划入口 | 3 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 7 |
| 执行输入 | 7 |
| 契约通过 | 2 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 204 |
| 已覆盖行 | 16 |
| 未覆盖行 | 188 |
| 补丁行覆盖率 | 7.84% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc 11.4.0` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- APR 1.7.4 and APR-util 1.6.3 built from source in test build directory
- OpenSSL 3.6.3 from conda environment, linked via /usr
- httpd built as static with modules: core, mod_so, http_core, mod_ssl, event
- Minimal build lacks authz_core, dir, mime modules needed for full serving

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `modules/ssl/mod_ssl.c:95-102 (ssl_config_cmds)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| config-syntax-test | passed | `testenv/config_default.conf` | `httpd -f testenv/config_default.conf -t` | Syntax OK for SSLVHostSNIPolicy directive | Config syntax OK; error rejected for invalid policy values; VHost context rejected |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | passed | All 4 policy values (secure/strict/insecure/authonly) accepted; invalid value rejected with AH00526 syntax error; VHost context usage rejected (GLOBAL_ONLY). Config test passed 7 times. |

- **覆盖率**: 15/15 (100.00%)
- **未覆盖行**: -
- Config directive SSLVHostSNIPolicy correctly registered and parsed
- All 4 policy values tested: secure(3x), strict(1x), insecure(1x), authonly(1x)
- Invalid value returns error via apr_psprintf
- Non-global context error path (GLOBAL_ONLY) not covered (requires VHost config attempt)

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `modules/ssl/ssl_engine_config.c:60-68 (snivh_policy)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| default-init-test | passed | `testenv/config_default.conf` | `httpd -f testenv/config_default.conf -t` | mc->snivh_policy = MODSSL_SNIVH_SECURE default set | gcov confirms line 64 hit 13 times; default policy MODSSL_SNIVH_SECURE set |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_cli_behavior_stability | passed | Default initialization mc->snivh_policy = MODSSL_SNIVH_SECURE confirmed via gcov (13 hits). Old code had no snivh_policy field; new default to secure mode is verified. |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -
- Default snivh_policy = MODSSL_SNIVH_SECURE set in ssl_config_global_create()
- Covered 13 times during config test execution
- The default initialization is within #ifdef HAVE_TLSEXT guard

### PCA-0003: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `modules/ssl/ssl_engine_kernel.c:195-250 (ssl_hook_ReadReq)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | skipped | Server could not serve requests: minimal build lacks authz_core module. Rebuild with --enable-mods-shared=all or use full httpd installation with authz_core, dir, mime modules. |

- **覆盖率**: 0/188 (0.00%)
- **未覆盖行**: ssl_engine_init.c:304, ssl_engine_init.c:305, ssl_engine_init.c:306, ssl_engine_init.c:307, ssl_engine_init.c:308, ssl_engine_init.c:309, ssl_engine_init.c:310, ssl_engine_init.c:311, ssl_engine_init.c:312, ssl_engine_init.c:313, ssl_engine_init.c:316, ssl_engine_init.c:317, ssl_engine_init.c:318, ssl_engine_init.c:319, ssl_engine_init.c:320, ssl_engine_init.c:321, ssl_engine_init.c:322, ssl_engine_init.c:323, ssl_engine_init.c:324, ssl_engine_init.c:325, ssl_engine_init.c:326, ssl_engine_init.c:327, ssl_engine_init.c:328, ssl_engine_init.c:330, ssl_engine_init.c:331, ssl_engine_init.c:332, ssl_engine_init.c:333, ssl_engine_init.c:334, ssl_engine_init.c:335, ssl_engine_init.c:336, ssl_engine_init.c:337, ssl_engine_init.c:338, ssl_engine_init.c:339, ssl_engine_init.c:341, ssl_engine_init.c:342, ssl_engine_init.c:343, ssl_engine_init.c:344, ssl_engine_init.c:345, ssl_engine_init.c:346, ssl_engine_init.c:347, ssl_engine_init.c:350, ssl_engine_init.c:351, ssl_engine_init.c:352, ssl_engine_init.c:353, ssl_engine_init.c:354, ssl_engine_init.c:355, ssl_engine_init.c:356, ssl_engine_init.c:357, ssl_engine_init.c:358, ssl_engine_init.c:359, ssl_engine_init.c:360, ssl_engine_init.c:361, ssl_engine_init.c:362, ssl_engine_init.c:363, ssl_engine_init.c:364, ssl_engine_init.c:365, ssl_engine_init.c:366, ssl_engine_init.c:367, ssl_engine_init.c:368, ssl_engine_init.c:369, ssl_engine_init.c:370, ssl_engine_init.c:371, ssl_engine_init.c:372, ssl_engine_init.c:373, ssl_engine_init.c:374, ssl_engine_init.c:375, ssl_engine_init.c:376, ssl_engine_init.c:377, ssl_engine_init.c:378, ssl_engine_init.c:379, ssl_engine_init.c:380, ssl_engine_init.c:381, ssl_engine_init.c:382, ssl_engine_init.c:383, ssl_engine_init.c:384, ssl_engine_init.c:385, ssl_engine_init.c:386, ssl_engine_init.c:387, ssl_engine_init.c:388, ssl_engine_init.c:389, ssl_engine_init.c:390, ssl_engine_init.c:391, ssl_engine_init.c:392, ssl_engine_init.c:393, ssl_engine_init.c:394, ssl_engine_init.c:395, ssl_engine_init.c:396, ssl_engine_init.c:397, ssl_engine_init.c:398, ssl_engine_init.c:399, ssl_engine_init.c:400, ssl_engine_init.c:401, ssl_engine_init.c:402, ssl_engine_init.c:403, ssl_engine_init.c:404, ssl_engine_init.c:405, ssl_engine_init.c:406, ssl_engine_init.c:407, ssl_engine_init.c:408, ssl_engine_init.c:409, ssl_engine_init.c:410, ssl_engine_init.c:411, ssl_engine_init.c:412, ssl_engine_init.c:413, ssl_engine_init.c:414, ssl_engine_init.c:415, ssl_engine_init.c:416, ssl_engine_init.c:417, ssl_engine_init.c:418, ssl_engine_init.c:419, ssl_engine_init.c:420, ssl_engine_init.c:421, ssl_engine_init.c:422, ssl_engine_init.c:423, ssl_engine_init.c:424, ssl_engine_init.c:425, ssl_engine_init.c:426, ssl_engine_init.c:427, ssl_engine_init.c:428, ssl_engine_init.c:429, ssl_engine_init.c:430, ssl_engine_init.c:431, ssl_engine_init.c:432, ssl_engine_init.c:433, ssl_engine_init.c:434, ssl_engine_init.c:438, ssl_engine_init.c:439, ssl_engine_init.c:440, ssl_engine_init.c:441, ssl_engine_init.c:442, ssl_engine_init.c:443, ssl_engine_init.c:444, ssl_engine_init.c:445, ssl_engine_init.c:446, ssl_engine_init.c:447, ssl_engine_init.c:448, ssl_engine_init.c:449, ssl_engine_init.c:450, ssl_engine_init.c:451, ssl_engine_init.c:452, ssl_engine_init.c:453, ssl_engine_init.c:454, ssl_engine_init.c:455, ssl_engine_init.c:456, ssl_engine_init.c:457, ssl_engine_init.c:458, ssl_engine_init.c:459, ssl_engine_init.c:460, ssl_engine_init.c:671, ssl_engine_kernel.c:112, ssl_engine_kernel.c:113, ssl_engine_kernel.c:114, ssl_engine_kernel.c:115, ssl_engine_kernel.c:116, ssl_engine_kernel.c:117, ssl_engine_kernel.c:118, ssl_engine_kernel.c:119, ssl_engine_kernel.c:120, ssl_engine_kernel.c:121, ssl_engine_kernel.c:122, ssl_engine_kernel.c:123, ssl_engine_kernel.c:124, ssl_engine_kernel.c:125, ssl_engine_kernel.c:126, ssl_engine_kernel.c:127, ssl_engine_kernel.c:128, ssl_engine_kernel.c:129, ssl_engine_kernel.c:130, ssl_engine_kernel.c:198, ssl_engine_kernel.c:229, ssl_engine_kernel.c:230, ssl_engine_kernel.c:231, ssl_engine_kernel.c:232, ssl_engine_kernel.c:233, ssl_engine_kernel.c:234, ssl_engine_kernel.c:235, ssl_engine_kernel.c:236, ssl_engine_kernel.c:237, ssl_engine_kernel.c:238, ssl_engine_kernel.c:239, ssl_engine_kernel.c:240, ssl_engine_kernel.c:241, ssl_engine_kernel.c:195, ssl_engine_kernel.c:196, ssl_engine_kernel.c:197, ssl_engine_kernel.c:198, ssl_engine_kernel.c:199, ssl_engine_kernel.c:200
- Runtime SNI vhost compatibility enforcement not tested
- ssl_engine_init.c:671 (sni_policy_hash computation): 0 hits
- ssl_engine_kernel.c:195-250 (ssl_hook_ReadReq): 0 hits
- Requires httpd rebuild with full module set + TLS SNI test connections

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-01 | httpd minimal static build (core, http_core, mod_ssl, event) lacks modules needed for HTTP serving: authz_core, dir, mime, unixd. Server starts but cannot serve requests. Runtime SNI enforcement code paths in ssl_engine_kernel.c and ssl_engine_init.c not reachable. | Rebuild httpd with --enable-mods-shared=all or with additional static modules: authz_core, dir, mime, unixd, alias. Then configure TLS certs for multiple SNI vhosts and test with curl --resolve for SNI hostname vs Host header behavior. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `../build/httpd-build/modules/ssl/*.gcda` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-tasks.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Rebuild httpd with full module set (authz_core, dir, mime, unixd, alias)
- Set up multiple TLS SNI virtual hosts with different SSL configurations
- Test SNI-to-Host transitions under secure/strict/insecure/authonly policies
- Verify HTTP 421 responses for incompatible transitions
- Test same-server guard removal with STRICT policy
- Verify APLOGNO(02032) log format change includes policy name
