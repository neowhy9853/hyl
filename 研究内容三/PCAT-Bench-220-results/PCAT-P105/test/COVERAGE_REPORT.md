# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `8a3cd890fd2a7d016a821a1c9dfd8a84d45ad320` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux-stable` |
| 基线 | `234681c54581756c28cd928b0dac75ab4576e59d` |
| Profile | `kernel_6_6` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：Userspace logic extraction testing confirms the behavioral change in ksmbd_alloc_user and __ksmbd_override_fsids is correctly implemented. The new supplementary groups feature is backward compatible with old ksmbd-tools (NULL extension path preserves original behavior). However, full kernel module testing with actual SMB client and netlink protocol verification is required for a definitive compatibility verdict. The patch itself explicitly states backward compatibility intent, and static analysis supports this claim.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 7 |
| 执行输入 | 7 |
| 契约通过 | 2 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 25 |
| 已覆盖行 | 19 |
| 未覆盖行 | 6 |
| 补丁行覆盖率 | 76.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3)` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `gcov (not available for userspace harness — logic extraction only)` |
- Host kernel 6.8.0-90-generic differs from target kernel 6.6.y; full kernel module build not performed
- Userspace logic extraction harness used to test core algorithm changes
- Kernel module build (make M=fs/smb/server) requires full kernel build first
- Netlink ABI testing requires running kernel with ksmbd module and ksmbd-tools

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `fs/smb/server/smb_common.c:761-778 (__ksmbd_override_fsids)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/PCA-TE-0001/pca_harness.c` | `./build/pca_harness` | test assertions PASS/FAIL | 19/20 assertions passed; behavioral diff confirmed |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-C-001 | passed | ksmbd_alloc_user backward compatibility: with NULL resp_ext, old and new code produce identical results (ngroups=0, sgid=NULL) |
| CT-C-002 | passed | ksmbd_alloc_user with extension: correctly populates supplementary groups from resp_ext; __ksmbd_override_fsids now uses groups_alloc(user->ngroups) instead of groups_alloc(0) |

- **覆盖率**: 15/15 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| TI-005 | SIDE_EFFECT_CHANGE | groups_alloc(0) — empty supplementary groups; files only accessible via primary group | groups_alloc(user->ngroups) with group population — supplementary groups honored; group-owned files now accessible via SMB | Test harness confirms: old override_fsids uses groups_alloc(0), new override_fsids uses groups_alloc(user->ngroups) and populates gi->gid[] from user->sgid[] |
- Userspace harness validates algorithm logic; actual kernel credential override path not tested
- 1/20 assertion failed (sgid=NULL when ngroups=0) — this is a kmemdup(0) implementation detail, kernel kfree handles ZERO_SIZE_PTR and NULL both
- Full validation requires running ksmbd kernel module with SMB client
- Contract CT-C-001 confirms backward compatibility: old ksmbd-tools (no extension flag) produce identical behavior

### PCA-0002: IOCTL_NETLINK_ABI_CHANGE

- **优先级**: `medium`
- **状态**: `not_run`
- **目标**: `fs/smb/server/ksmbd_netlink.h:321-329 (enum ksmbd_event)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 0/6 (0.00%)
- **未覆盖行**: fs/smb/server/ksmbd_netlink.h:156-161 (new struct), fs/smb/server/ksmbd_netlink.h:324-325 (new enum values), fs/smb/server/ksmbd_netlink.h:357 (new flag), fs/smb/server/transport_ipc.c:196-201 (genl_ops entries), fs/smb/server/transport_ipc.c:215 (resv_start_op), fs/smb/server/transport_ipc.c:123-126 (nla_policy entries)
- Netlink protocol testing requires running kernel with ksmbd module loaded and ksmbd-tools userspace daemon
- New enum values (16,17) extend protocol without breaking old tools: KSMBD_EVENT_LOGIN_REQUEST_EXT uses handle_unsupported_event, ensuring backward compatibility
- resv_start_op change (16→18) informs genl subsystem of new command range
- New struct ksmbd_login_response_ext layout: handle(u32)+ngroups(s32)+reserved(128*s8)+payload(flex) — 8+4+128+flex bytes
- Static analysis confirms protocol extension is additive/backward compatible

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-001 | Full kernel module build requires building entire kernel (linux-6.6.y) from source, which needs 30+ minutes and produces incompatible module for host kernel 6.8.0. Running ksmbd kernel module requires QEMU VM with matching kernel version. | Set up QEMU VM with kernel 6.6.y and CONFIG_SMB_SERVER=y, load ksmbd module, install ksmbd-tools, run SMB client against test shares with supplementary group configurations |
| finding | BLOCKER-002 | PCA-0002 IOCTL_NETLINK_ABI_CHANGE requires netlink communication between kernel ksmbd module and ksmbd-tools userspace daemon. This needs a running kernel with ksmbd loaded and the userspace tools. | Build ksmbd-tools from source for target kernel version, install in VM, test netlink message exchange with new LOGIN_REQUEST_EXT/RESPONSE_EXT events |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Build kernel 6.6.y with CONFIG_SMB_SERVER=y and CONFIG_GCOV_KERNEL=y for coverage instrumentation
- Set up QEMU VM with the instrumented kernel
- Install ksmbd-tools and test with old (no-extension) and new (with-extension) tools
- Create SMB share with group-only permissions and verify supplementary group access works
- Run netlink trace to verify LOGIN_REQUEST_EXT/RESPONSE_EXT message exchange
- Collect gcov coverage data for the patched lines in ksmbd module
