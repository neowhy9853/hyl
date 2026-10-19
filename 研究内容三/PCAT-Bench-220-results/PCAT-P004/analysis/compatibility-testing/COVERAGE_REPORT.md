# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `c6d4181a1e8281b4e446ba83aa8eb06021cafdc7` |
| 仓库 | `/home/soong/pca_benchmark/_repos/kernel` |
| 基线 | `ffc253263a1375a65fa6c9f62a893e9767fbebfa` |
| Profile | `kernel_6_6` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：真实 before/after headers_install、同源探针和 type-aware acceptance contract 确认 CTL_MAXNAME 从 10 收紧为 8，nlen 9/10 从接受变为拒绝，且要求至少 9 个路径分量的同一旧消费者从可编译变为静态断言失败。唯一编译期目标已验证，按用户口径覆盖率为 1/1=100%；runtime gcov 对宏声明不适用。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 8 |
| 执行输入 | 8 |
| 契约通过 | 0 |
| 契约违约 | 1 |
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
| 覆盖率工具 | `GCC 13.3.0 compile-time target verification plus gcov control; target macro runtime gcov N/A` |
- before/after 均从 base_commit 创建 detached worktree，补丁只应用于 after；git diff --check 通过。
- 两个 worktree 分别完成 headers_install；同一用户态 C probe 只切换安装头文件路径。
- 补丁后精确符号检索没有发现内核执行代码引用 CTL_MAXNAME，因此无需构建或启动内核来证明本次编译期契约变化。
- 按用户指定的同类 benchmark 口径，唯一编译期 patch target 记为 1/1=100%；gcov 对目标头文件真实输出 No executable lines。

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `include/uapi/linux/sysctl.h:30-30 (CTL_MAXNAME)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `test-entry-work/PCA-0001/reproducer.sh` | `bash test-entry-work/PCA-0001/reproducer.sh phase2_environment/headers-before phase2_environment/headers-after` | before value/count/bytes=10/10/40, after=8/8/32; nlen 9 and 10 tighten; legacy compile fails only after | headers_install output expanded include/uapi/linux/sysctl.h:30 into both executable probes |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | 官方 type-aware acceptance probe 对 nlen=9 观测到 before rc=0/accepted=1，after rc=1/accepted=0。 |

- **覆盖率**: 1/1 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I1-describe | INPUT_CONTRACT_CHANGE | CTL_MAXNAME=10 array_count=10 array_bytes=40 | CTL_MAXNAME=8 array_count=8 array_bytes=32 | phase4_execution/raw/describe.before.stdout and describe.after.stdout |
| I5-old-valid-9/I6-old-boundary-10 | INPUT_CONTRACT_CHANGE | nlen 9 and 10 accepted (exit 0) | nlen 9 and 10 rejected (exit 1) | phase3_contracts/contract_verification.json and phase4_execution/raw/nlen-{9,10}.* |
| I8-legacy-compile | INPUT_CONTRACT_CHANGE | unchanged CTL_MAXNAME >= 9 downstream source compiles | same source fails its static assertion | phase4_execution/raw/legacy.before.rc, legacy.after.rc, and legacy.after.stderr |
- 实际 headers_install、编译和执行验证了公开宏输入边界变化，而不是仅做文本 diff。
- nlen=-1、0、8、9、10、11 覆盖了无效、空值类、新边界、旧有效/新无效、旧边界和两侧均无效输入。
- 变化行属于宏声明，没有 runtime gcov counter；有效目标 1/1 已验证并按用户口径记为 100%。

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| coverage | patch_line_gcov | gcov 对 include/linux/sysctl.h 实测输出 No executable lines；#define 宏声明没有运行时计数器。有效 patch-target coverage 已由 headers_install、宏展开、边界执行和静态断言验证为 1/1=100%。 | 无需伪造 runtime gcov；保留 gcov 控制输出和编译期目标证据。 |
| environment | kernel_sysctl_runtime | 精确源码检索只发现 CTL_MAXNAME 定义，没有内核执行代码消费该宏；QEMU 中调用二进制 sysctl 接口无法形成补丁行可达证据，因此未构建或启动 before/after 内核。 | 若另需验证基线自身的废弃 sysctl syscall 行为，可在启用相应 syscall/config 的匹配内核上独立测试，但该结果不能替代本补丁的编译期契约证据。 |
| finding | static_call_chain | C AST 依赖检查缺少 tree_sitter，且目标为宏声明；按 Skill 规则 static_call_chains 保留空数组，未使用 grep/正则伪造调用链。 | 如必须生成 AST 调用链，安装 tree_sitter；宏无函数调用关系时结果仍可能为空。 |

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

- 通知依赖 CTL_MAXNAME 分配数组、校验 nlen 或要求至少 9/10 个路径分量的用户态项目。
- 若收紧是有意行为，应在 UAPI 兼容性说明中明确重编译消费者的行为变化并提供迁移方案。
- 不要把公开头文件的编译期契约变化误解为当前内核执行路径已经使用新的上限。
