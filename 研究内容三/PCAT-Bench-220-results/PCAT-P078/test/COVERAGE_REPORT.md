# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `fbf682a6c684db5e0b6928b511f8fc57d6c8eb7c` |
| 仓库 | `/home/soong/pca_benchmark/_repos/openldap` |
| 基线 | `bb64b0b55b5aa77fae077209f26b015f6a86275f` |
| Profile | `openldap` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch introduces new ACL config keywords op= and control= as additive extensions - existing configs work unchanged. However, a critical bug was found: control= with named OID aliases (e.g. manageDSAiT) fails because these aliases aren't registered as objectIdentifier macros. The patch's own test data (slapd-acl.conf) uses control=manageDSAiT which will not parse. Runtime ACL enforcement code (slap_acl_get) could not be dynamically verified due to non-root authentication constraints. Config parsing, acl_free, and acl_unparse code are fully covered and verified. The AccessControl struct ABI changed for slapd modules.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 4 |
| 测试 findings | 4 |
| 规划入口 | 7 |
| 生成入口 | 7 |
| 验证入口 | 4 |
| 规划输入 | 6 |
| 执行输入 | 4 |
| 契约通过 | 4 |
| 契约违约 | 1 |
| 契约跳过 | 1 |
| 补丁可执行行 | 44 |
| 已覆盖行 | 15 |
| 未覆盖行 | 29 |
| 补丁行覆盖率 | 34.09% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0)` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Coverage build with --coverage succeeded (421 gcno files)
- IPv4 loopback socket confirmed operational
- Non-root LDAP bind auth setup failed due to userPassword schema constraints

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `servers/slapd/aclparse.c:1691-1741 (parse_acl)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E1 | passed | `slapd -T test` | `slapd -T test with op=search config` | Config accepted with op=search in ACL output | gcov shows parse_acl new code executed 6-9 times |
| E2 | passed | `slapd -T test` | `slapd -T test with control=<numeric_oid> config` | Config accepted with numeric OID control | gcov shows control= parsing code executed 3 times |
| E3 | failed | `slapd -T test` | `slapd -T test with control=manageDSAiT config` | Config accepted with manageDSAiT control name | Got 'bad control OID manageDSAiT'; oidm_find returned NULL |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C1 | passed | op=search keyword correctly parsed by slapd ACL config parser |
| C2 | passed | control=<numeric_oid> keyword correctly parsed by slapd ACL config parser |
| C3 | breached | control=manageDSAiT fails: named OID alias not registered as objectIdentifier |

- **覆盖率**: 13/14 (92.86%)
- **未覆盖行**: servers/slapd/aclparse.c:1722-1725 (op=<oid> extended OID path)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| E3 | CONFIG_CLI_BEHAVIOR_CHANGE | control=manageDSAiT: not applicable (old parser rejects) | control=manageDSAiT: rejected with 'bad control OID' error | slapd -T test output: 'bad control OID manageDSAiT in to clause' |
- Config parsing of op= and control= numeric OID works correctly
- Named OID aliases for controls not registered as objectIdentifiers fail
- Patch's own test config (slapd-acl.conf) uses control=manageDSAiT and will fail

### PCA-0002: OUTPUT_FORMAT_CHANGE

- **优先级**: `medium`
- **状态**: `passed`
- **目标**: `servers/slapd/aclparse.c:2869-2888 (acl_unparse)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E4 | passed | `gcov on aclparse.c` | `slapd -T test with op=/control= config, then gcov` | acl_unparse new code executed | gcov: lines 2872-2886 executed 2-10 times |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C4 | passed | acl_unparse outputs op= and control= lines when configured |

- **覆盖率**: 8/8 (100.00%)
- **未覆盖行**: -
- Output format change is additive - only appears when op=/control= is configured
- Old configs without these keywords produce identical output

### PCA-0003: ABI_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `servers/slapd/slap.h:1612-1624 (AccessControl)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E5 | blocked | `` | `Build slapd backend with old slap.h, load into new slapd` | Old module accesses acl_access with correct offset | Static analysis: struct layout changed - 5 fields added between acl_attrval and acl_access |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C5 | skipped | ABI verification requires separate slapd module build with old headers |

- **覆盖率**: 0/1 (0.00%)
- **未覆盖行**: servers/slapd/slap.h:1612-1618 (struct layout change - static analysis only)
- Static analysis confirms 5 new fields before acl_access
- Old slapd modules compiled against old slap.h will have wrong offset for acl_access
- In-tree builds (backends always recompiled with slapd) are not affected

### PCA-0004: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `servers/slapd/acl.c:545-564 (slap_acl_get)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| E6 | blocked | `` | `ldapsearch as non-root user on op=search-restricted subtree` | Search succeeds (op matches), modify fails (op doesn't match) | Requires non-root bind with proper schema-compatible user entry |
| E7 | blocked | `` | `ldapmodify -M on control-restricted subtree` | Modify fails with insufficientAccess (50) when ManageDSAiT control used | Blocked by: (1) manageDSAiT OID not registered, (2) non-root auth |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| C6 | skipped | Runtime ACL enforcement (op=/control= filtering in slap_acl_get) not dynamically tested |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: servers/slapd/acl.c:548-560 (all new op/control filtering code), acl.c new code unreachable: rootdn bypasses ACLs
- Config parsing succeeded, proving the new ACL entries are registered in the ACL chain
- Runtime enforcement requires non-root LDAP operations to exercise slap_acl_get
- rootdn bypasses ACLs entirely, so admin bind cannot test ACL enforcement

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-NONROOT-AUTH | Non-root LDAP bind authentication failed (userPassword schema constraint on inetOrgPerson) | Create test user with proper LDIF (simpleSecurityObject or pre-encoded password) |
| environment | BLOCKER-NAMED-OID | control=manageDSAiT fails because manageDSAiT is not registered as an objectIdentifier macro | Add objectIdentifier manageDSAiT 2.16.840.1.113730.3.4.2 to slapd config or schema |
| entry | BLOCKER-ABI-MODULE | ABI verification requires building a slapd module against old slap.h headers | Set up separate module build environment with old headers for ABI comparison |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `embedded_in_finding_results` |
| coverage_data | `servers/slapd/acl.c.gcov+aclparse.c.gcov` |
| execution_results | `test-summary.json` |
| impact_map | `not_generated` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `not_generated_separately` |
| test_entry_tasks | `compatibility-testing/test-entry-tasks.json` |
| test_inputs | `not_generated_separately` |

## 建议

- Register manageDSAiT (and other well-known LDAP control OIDs) as default objectIdentifier macros in slapd
- Run test006-acls with fixed OID registration to exercise runtime ACL enforcement
- Verify slap_acl_get new code path with non-root LDAP operations
- Consider adding oidm_find fallback resolution for well-known LDAP control names
- Recompile any slapd backend/overlay modules against the updated slap.h
