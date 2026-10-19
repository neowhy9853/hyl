# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `f6ae8ef451f38e3f2f3ec6fc43cc8806ecfe125a` |
| 仓库 | `/home/soong/pca_benchmark/_repos/openldap` |
| 基线 | `18403607b96254ba7556b64961465ff5bd0af03e` |
| Profile | `openldap` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：The patch changes the default lloadd feature set: proxyauthz is now enabled by default (LLOAD_FEATURE_PROXYAUTHZ via LLOAD_FEATURES_DEFAULT). Previously lload_features was zero-initialized (no features). This SIDE_EFFECT_CHANGE is confirmed by gdb variable inspection (BEFORE: $1=0, AFTER: $1=LLOAD_FEATURE_PROXYAUTHZ), gcov coverage (config_feature function switch/case executed 3x, new default initialization confirmed), and config parsing tests (enable/disable/feature keywords all work correctly). Deployments that rely on proxyauthz being OFF by default will experience a behavioral change: the Proxy Authorization control will now be sent to backend servers on every proxied operation. Backend servers that do not support this control may reject operations if the control is marked critical. Additionally, SASL-bind deployments now require backend servers to support the Who Am I? extended operation. A MEDIUM-priority finding (config schema attribute rename) was not tested per priority filter. Runtime LDAP traffic testing blocked by sandbox socket restriction.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 3 |
| 执行输入 | 3 |
| 契约通过 | 3 |
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
| 编译器 | `gcc (Ubuntu 11.4.0) 13.0` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov (GCC) 13.0` |
- Build configured with --enable-slapd=yes --enable-mdb=yes --enable-balancer=yes --with-tls=openssl --with-cyrus-sasl=yes
- Before binary built at parent commit 18403607b9 (correct base before patch)
- After binary built at patched worktree (f6ae8e applied)
- Sandbox denies IPv4 socket bind (EPERM); daemon runtime tests not possible
- Config check mode (-t) and gdb variable inspection used as alternative

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `servers/lloadd/lload.h:187-190 (LLOAD_FEATURES_DEFAULT)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/run_config_test.sh` | `bash test-entry-work/PCA-0001/run_config_test.sh` | Config check succeeded for enable/disable/feature keywords; gdb shows lload_features=0 (BEFORE) vs LLOAD_FEATURE_PROXYAUTHZ (AFTER) | gcov confirms config_feature() switch/case executed 3x; *fp\|=mask and lload_features recalculation executed 3x |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| proxyauthz_default_off_on_change | passed | BEFORE: lload_features=0 (gdb $1=0). AFTER: lload_features=LLOAD_FEATURE_PROXYAUTHZ (gdb $1=LLOAD_FEATURE_PROXYAUTHZ). Behavioral change confirmed: proxyauthz default changed from OFF to ON. |
| enable_keyword_parsing | passed | 'enable proxyauthz' in config: config check succeeded (AFTER binary). Coverage confirms CFG_FEATURE_ENABLE branch executed 2x. |
| disable_keyword_parsing | passed | 'disable proxyauthz' in config: config check succeeded (AFTER binary). Coverage confirms CFG_FEATURE_DISABLE branch executed 1x. |

- **覆盖率**: 3/3 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| B1 | SIDE_EFFECT_CHANGE | lload_features = 0 at main() entry; proxyauthz feature OFF by default | lload_features = LLOAD_FEATURE_PROXYAUTHZ at main() entry; proxyauthz feature ON by default | gdb output: BEFORE (parent 18403607b9) $1=0, AFTER (patched f6ae8e) $1=LLOAD_FEATURE_PROXYAUTHZ. gcov: config.c lines 2116, 2119, 2120, 2122, 2124, 2125, 2131, 2135-2139, 2155, 2162, 2174, 2188 all executed. Run config files: config_enable_only.conf, config_disable_only.conf, config_feature_only.conf all pass config check. |
- Runtime LDAP traffic testing (verifying actual Proxy Authorization control on the wire) blocked: sandbox denies IPv4 socket bind (EPERM)
- Config parsing tests completed successfully using -t (config check) mode
- Variable inspection via gdb confirms the default value change
- gcov coverage of config_feature() function confirms new code paths executed
- Config tests performed: enable (pass), disable (pass), feature (legacy, pass), unknown feature (correctly rejected)

### PCA-0002: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `servers/lloadd/config.c:398-425 (config_back_cf_table)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- MEDIUM priority finding excluded from testing by --min-priority high filter
- Schema round-trip testing (cn=config LDIF export/import) requires a running slapd instance, blocked by IPv4 socket restrictions
- Attribute name aliasing (olcBkLloadFeature as alias of olcBkLloadFeatureEnable) ensures backward compatibility for existing LDIF entries

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | EPERM_socket_bind | Workspace sandbox denies IPv4 socket bind (errno=13 EPERM). lloadd daemon runtime tests requiring network access cannot execute. | Run dynamic daemon tests (proxyauthz control on the wire) in a socket-capable container or VM. |
| finding | PCA-0002 | MEDIUM priority finding excluded by --min-priority high filter. Schema round-trip cn=config LDIF testing also requires socket-capable slapd instance. | If schema attribute compatibility is a concern, run cn=config LDIF round-trip tests with old olcBkLloadFeature attribute name in a socket-capable environment. |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `compatibility-testing/phase4_execution/` |
| coverage_data | `compatibility-testing/coverage_data/` |
| execution_results | `compatibility-testing/phase4_execution/corrected_config_test.txt` |
| impact_map | `compatibility-testing/phase1_impact/` |
| report | `compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `compatibility-testing/test-entry-tasks.json` |
| test_inputs | `compatibility-testing/phase3_inputs/` |

## 建议

- Review all existing lloadd deployments: if backend servers do not support Proxy Authorization control, add 'disable proxyauthz' to lloadd configs
- For SASL-bind deployments, verify backend servers support the LDAP Who Am I? extended operation
- Run runtime LDAP traffic tests in a socket-capable container/VM to verify actual control-on-wire behavior
- Consider testing PCA-0002 (config schema attribute rename) if using automation that generates cn=config LDIF entries
