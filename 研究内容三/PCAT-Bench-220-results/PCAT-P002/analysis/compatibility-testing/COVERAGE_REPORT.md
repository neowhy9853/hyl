# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `3310153e66dddd35668e409c053cb72e3ae224ce` |
| 仓库 | `/home/soong/pca_benchmark/_repos/linux` |
| 基线 | `ffc253263a1375a65fa6c9f62a893e9767fbebfa` |
| Profile | `kernel_6_6` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：真实 before/after 编译与执行确认 UINPUT_VERSION 从 5 变为 6，并确认依赖旧公开值的下游源码由可编译变为静态断言失败，两个兼容性契约均被突破。按用户指定 benchmark 口径，唯一编译期 patch target 已验证，覆盖率 1/1=100%；runtime gcov 对宏声明不适用。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 1 |
| 执行输入 | 1 |
| 契约通过 | 0 |
| 契约违约 | 2 |
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
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `Benchmark patch-target coverage via GCC macro expansion/static assertion; runtime gcov N/A for #define` |
- 基线使用 base_commit 的 detached worktree，补丁后使用 analysis_repo；编译产物全部位于 compatibility-testing。
- 本例无需构建整个内核：两个最小用户态探针分别强制包含补丁前后的准确 UAPI 头文件。
- 唯一变化行是非可执行宏声明；按用户指定 benchmark 口径，已验证的编译期目标按 1/1=100% 计入有效覆盖，runtime gcov 仍为 N/A。

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `include/uapi/linux/uinput.h:46-46 (UINPUT_VERSION)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh /home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/compatibility-testing/phase2_environment/before /home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/_worktrees/patched` | before_version=5, after_version=6, legacy before compile succeeds, legacy after compile fails | GCC expanded the exact target header in both trees and produced distinct macro values |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| uapi_macro_value_stability | breached | 同一探针的输出由基线 5 变为补丁后 6。 |
| downstream_compile_compatibility | breached | 依赖公开旧值 5 的同一下游源码在基线编译成功，在补丁后因静态断言失败而无法编译。 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1 | ABI_CHANGE | UINPUT_VERSION=5 | UINPUT_VERSION=6 | phase4_execution/raw/version.before.stdout and version.after.stdout |
| I1 | ABI_CHANGE | legacy consumer compile exit 0 | legacy consumer compile exit 1 with failed UINPUT_VERSION == 5 assertion | phase4_execution/raw/legacy.before and legacy.after.stderr |
- 实际编译与执行验证了公开宏值变化，而不是仅做文本比较。
- 变化行属于宏声明，没有 gcov 可执行计数器；按 benchmark 有效目标口径，编译期目标 1/1 已验证并记为 100%。
- uinput_ioctl_handler 的 UI_GET_VERSION 分支会消费该宏，但真实 ioctl before/after 内核测试未执行。

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | patch_line_gcov | runtime gcov 对 #define 宏声明不适用；有效 patch-target coverage 已由宏展开和静态断言验证为 1/1=100%。 | 无需补充 runtime gcov；保留编译期目标覆盖证据。 |
| environment | ui_get_version_runtime_before_after | 真实 ioctl 对比需要分别构建并启动基线/补丁后内核、启用 uinput，并提供可访问的 /dev/uinput；当前未配置该 VM/设备环境。 | 若需运行时补充验证，在隔离 QEMU VM 中分别启动两套内核并调用 ioctl(fd, UI_GET_VERSION, &version)。 |

## 产物

| Artifact | Path |
|---|---|
| behavior_diff | `phase4_execution/behavior_diff.json` |
| contract_summary | `phase3_contracts/contract_verification.json` |
| coverage_data | `phase4_execution/coverage_data.json` |
| coverage_iterations | `phase4_execution/coverage_iterations.json` |
| entry_verification | `test-entry-work/test-entry-verification.json` |
| execution_results | `phase4_execution/results.json` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 通知依赖 UINPUT_VERSION 精确值、静态断言或条件编译分支的用户态项目适配版本 6。
- 发布前确认内核运行时 UI_GET_VERSION 返回值与安装的 UAPI 头文件一致。
- 如需完整运行时证据，在隔离 VM 中对基线和补丁后内核分别执行 UI_GET_VERSION ioctl。
