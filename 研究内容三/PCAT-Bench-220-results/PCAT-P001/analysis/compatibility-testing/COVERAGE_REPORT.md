# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `632ca5e16e3e3141e559b9b4a4e588d252d0df2a` |
| 仓库 | `/home/soong/pca_benchmark/_repos/linux` |
| 基线 | `ffc253263a1375a65fa6c9f62a893e9767fbebfa` |
| Profile | `kernel_6_6` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：编译期 before/after probe 确认 struct input_event 的大小和连续记录步长均从 24 增至 32；真实 QEMU 双内核进一步确认旧 24 字节 uinput write 与 evdev read 从成功变为 -1/EINVAL，而各内核 native-size 对照均成功。四个 UAPI/输入契约均被突破。按用户指定 benchmark 口径，唯一编译期 patch target 已验证，覆盖率 1/1=100%；runtime gcov 对声明不适用。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 2 |
| 生成入口 | 2 |
| 验证入口 | 2 |
| 规划输入 | 5 |
| 执行输入 | 5 |
| 契约通过 | 0 |
| 契约违约 | 4 |
| 契约跳过 | 0 |
| 补丁可执行行 | 1 |
| 已覆盖行 | 1 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `mixed` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `GCC 13.3.0` |
| 优化级别 | `-O0 -g` |
| 覆盖率工具 | `Benchmark patch-target coverage via GCC type layout/offsetof probes; runtime gcov N/A for a struct field declaration` |
- 编译期 probe 使用稀疏 benchmark 的 before/after 头文件；运行时 probe 使用 _repos/kernel 完整仓库在 base_commit 创建的隔离 detached worktree。
- before/after 内核均完成 headers_install、静态 initramfs 探针构建和 bzImage 构建；所有产物位于 compatibility-testing/runtime-evdev。
- 按内核 headers_install 的用户态导出语义，仅将 raw 头中的 __user 注解定义为空。
- 双内核通过无特权 QEMU TCG 启动；guest 内用 uinput 创建虚拟键盘并通过真实 /dev/input/eventX 执行 syscall。
- 唯一新增行是非可执行结构体字段声明；按用户指定 benchmark 口径，已验证的编译期目标按 1/1=100% 计入有效覆盖，runtime gcov 仍为 N/A。

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `include/uapi/linux/input.h:47-47 (struct input_event)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh` | ABI_CHANGE_DETECTED，after_size/after_stride 大于 before 值 | GCC 对真实 patched input.h 中 compat_reserved 执行 offsetof，并对 before/after 结构体生成不同的 sizeof 与数组步长 |
| PCA-TE-0002 | runnable_verified | `test-entry-work/PCA-0001/runtime_evdev.sh` | `timeout 600 bash test-entry-work/PCA-0001/runtime_evdev.sh` | before 的旧 24 字节 write/read 成功；after 的相同调用返回 EINVAL；native-size 对照均成功 | QEMU guest 内 write(/dev/uinput) 与 read(/dev/input/eventX) 实际执行 input_event_from_user/input_event_to_user 路径，并输出双侧成功标记 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| uapi_struct_size_stability | breached | 同一用户态 probe 的 sizeof(struct input_event) 从基线 24 变为补丁后 32。 |
| evdev_record_stride_stability | breached | 同一用户态 probe 的 struct input_event 数组步长从 24 变为 32。 |
| evdev_legacy_write_acceptance | breached | 真实内核中 write(/dev/uinput, old_record, 24) 从返回 24 变为 -1/EINVAL。 |
| evdev_legacy_read_buffer_acceptance | breached | 真实内核中 read(/dev/input/eventX, buffer, 24) 从返回 24 变为 -1/EINVAL；native-size 读取在两侧均成功。 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1-default-layout | ABI_CHANGE | sizeof=24, align=8, offsets(type/code/value)=16/18/20, stride=24 | sizeof=32, align=8, offsets(type/code/value)=16/18/20, stride=32 | phase4_execution/abi_probe/default.before.txt and default.after.txt |
| I2-new-field | ABI_CHANGE | field probe 编译失败：没有 compat_reserved 成员 | field probe 编译运行成功：compat_reserved_offset=24 | phase4_execution/abi_probe/field_probe.before.stderr and field.after.txt |
| I3-time64-layout | ABI_CHANGE | _TIME_BITS=64 build: sizeof/stride=24/24 | _TIME_BITS=64 build: sizeof/stride=32/32 | phase4_execution/abi_probe/time64.before.txt and time64.after.txt |
| I4-evdev-legacy-record-io | INPUT_CONTRACT_CHANGE | 24 字节 uinput write 和 evdev read 均返回 24 | 24 字节 uinput write 和 evdev read 均返回 -1/EINVAL；32 字节 native 对照成功 | runtime-evdev/results/before.console.log, after.console.log, and runtime_summary.json |
- 实际编译与执行确认了公开 UAPI 类型布局差异，而不是仅比较文本。
- 原有 type/code/value 字段偏移保持 16/18/20，新增字段位于偏移 24；结构体尾部扩展导致整体对齐后增长 8 字节。
- 变化行属于类型声明，没有 gcov 可执行计数器；按 benchmark 有效目标口径，编译期目标 1/1 已验证并记为 100%。
- 真实双内核测试执行了 uinput write(2) 与 evdev read(2)：旧 24 字节记录在补丁内核中均被 EINVAL 拒绝，native 32 字节路径保持可用。

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | patch_line_gcov | runtime gcov 对结构体字段声明不适用；有效 patch-target coverage 已由编译期布局/offsetof probe 验证为 1/1=100%。 | 无需补充 runtime gcov；保留编译期目标覆盖与真实 QEMU ABI 契约证据。 |

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
| runtime_after_log | `runtime-evdev/results/after.console.log` |
| runtime_before_log | `runtime-evdev/results/before.console.log` |
| runtime_summary | `runtime-evdev/results/runtime_summary.json` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 不要在现有 evdev UAPI 结构体尾部直接增加字段；若必须扩展，设计显式版本化的新记录格式或协商机制。
- 为既有 24 字节用户态程序保留兼容解析/复制路径，或拒绝合入这一未版本化的稳定 UAPI 布局变化。
- 将本次无特权 QEMU + 静态 initramfs + uinput 流程复用于其他需要真实内核 syscall 验证的 kernel case。
