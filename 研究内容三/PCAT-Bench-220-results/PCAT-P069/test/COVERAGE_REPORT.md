# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `e671f885037435884f070493be753eb021e26e79` |
| 仓库 | `/home/soong/pca_benchmark/_repos/rsyslog` |
| 基线 | `f9f5b3ca41d64d8e48a5c7e6b98c72339a7f7547` |
| Profile | `rsyslog` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：The patch introduces a new config parameter (systemd.notifyReadyDelay) and changes the default systemd READY=1 timing from always-wait to immediate. While the config parameter change is additive and backward-compatible, the default behavior change (immediate READY=1 vs historical delayed) is a behavioral incompatibility for operators relying on rsyslog delaying READY=1 until module readiness. The new config option global(systemd.notifyReadyDelay='on') restores the historical behavior. Coverage gate not met (35% vs 80% threshold) due to daemon-mode paths not being exercisable in -N1 config validation mode.

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 4 |
| 执行输入 | 4 |
| 契约通过 | 1 |
| 契约违约 | 1 |
| 契约跳过 | 1 |
| 补丁可执行行 | 20 |
| 已覆盖行 | 7 |
| 未覆盖行 | 13 |
| 补丁行覆盖率 | 35.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0` |
| 优化级别 | `-O0 -g --coverage` |
| 覆盖率工具 | `gcov` |
- Build uses disposable git worktrees: BEFORE at parent commit 3e2147e53, AFTER at HEAD f9f5b3ca4
- autoconf-archive installed manually from .deb (missing on host)
- protobuf-c and snappy libraries extracted from .deb packages into ~/.local
- Docker socket access denied - container validation not available
- Only applied patch, no extra features enabled beyond testbench minimum

## Finding 测试结果

### PCA-0001: CONFIG_CLI_BEHAVIOR_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `tools/rsyslogd.c:2666-2682 (main)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | verified | `test-entry-work/PCA-0001/config_validation` | `rsyslogd -C -N1 -M"../runtime/.libs:../.libs" -f <config>` | Exit code 0 for valid configs, exit code 1 for unknown parameters | Config validation complete message: 'End of config validation run. Bye.' |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| config_acceptance_off | breached | global(systemd.notifyReadyDelay="off"): BEFORE rejects (exit 1, unknown param), AFTER accepts (exit 0) |
| config_acceptance_on | breached | global(systemd.notifyReadyDelay="on"): BEFORE rejects (exit 1, unknown param), AFTER accepts (exit 0) |
| default_behavior_stability | passed | Default config (no notifyReadyDelay): AFTER accepts (exit 0, default=off) |

- **覆盖率**: 2/3 (66.70%)
- **未覆盖行**: tools/rsyslogd.c:2669-2680 (daemon init path, requires systemd runtime)

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | CONFIG_CLI_BEHAVIOR_CHANGE | Exit code 1: parameter 'systemd.notifyReadyDelay' not known | Exit code 0: config validation passed | BEFORE binary at 3e2147e53 rejects new parameter; AFTER binary at f9f5b3ca4 accepts it |
| I2 | CONFIG_CLI_BEHAVIOR_CHANGE | Exit code 1: parameter 'systemd.notifyReadyDelay' not known | Exit code 0: config validation passed | Same as I1 - both off and on values accepted by patched binary |
- Config validation tests confirm the new parameter is accepted by patched binary
- Default behavior change (immediate READY=1 vs delayed) not observable in -N1 mode
- Config parsing coverage confirmed via gcov: 2 hits at glbl.c:1558

### PCA-0002: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `blocked`
- **目标**: `runtime/rsconf.c:90-200 (rsconfRegisterReadiness/rsconfSignalReady/rsconfWaitForModulesReady)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| readiness_barrier_side_effect | skipped | Module readiness barrier side effect only observable during daemon-mode systemd execution; -N1 config validation mode does not trigger the barrier |

- **覆盖率**: 0/14 (0.00%)
- **未覆盖行**: runtime/rsconf.c:107 (initModulesReadyCond - uncalled), runtime/rsconf.c:110-121 (initModulesReadyCond body - uncalled), runtime/rsconf.c:124-125 (rsconfShouldDelayReadyNotify - uncalled), runtime/rsconf.c:128-144 (rsconfRegisterReadiness - uncalled), runtime/rsconf.c:147-153 (rsconfSignalReady - uncalled), runtime/rsconf.c:157-191 (rsconfWaitForModulesReady - uncalled), runtime/rsconf.c:194-199 (rsconfReadyNotifySent - uncalled), runtime/rsconf.c:129 (pthread_once in Register - uncalled), runtime/rsconf.c:130 (early return in Register - uncalled), runtime/rsconf.c:132-144 (Register mutex body - uncalled), runtime/rsconf.c:148-149 (Signal early return - uncalled), runtime/rsconf.c:151-153 (Signal mutex body - uncalled), runtime/rsconf.c:159-191 (WaitFor body - uncalled), runtime/rsconf.c:195-198 (ReadyNotifySent body - uncalled)
- Side effect change requires daemon execution with systemd runtime
- Config validation mode (-N1) exits before the sd_notify code path
- Cannot test without systemd runtime or Docker container access

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | COV-DAEMON-PATH | tools/rsyslogd.c lines 2669-2680 (sd_notify guarded path) and runtime/rsconf.c lines 107-199 (readiness barrier) not reachable in config validation mode (-N1). Requires actual daemon execution with systemd runtime. | Run rsyslogd as daemon (with systemd) or use container-based test environment with Docker/Podman |
| finding | PCA-0002-TEST | PCA-0002 (SIDE_EFFECT_CHANGE) requires daemon-mode execution to observe the readiness barrier gating behavior change | Execute rsyslogd with HAVE_LIBSYSTEMD in a systemd container environment and verify sd_notify(READY=1) timing |
| environment | ENV-CONTAINER | Docker socket access denied; cannot run CI-style container validation | Grant Docker/Podman socket access or use a systemd-enabled VM for full testing |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_summary.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `N/A` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-plan.md` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- Document the default behavior change in release notes
- Verify that dependent systemd services using After=rsyslog.service handle the earlier READY=1 notification
- Consider whether operators need to add global(systemd.notifyReadyDelay='on') to existing configs
- Run full daemon-mode testing with systemd runtime or Docker container to verify sd_notify timing
- Achieve 80%+ coverage gate by running rsyslogd as daemon and triggering the readiness barrier
