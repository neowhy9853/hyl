# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `09dc18894148381d3bfc550083b1236043870dce` |
| 仓库 | `/home/soong/pca_benchmark/_repos/linux` |
| 基线 | `09b8a7aa5a341bb345dc492aac139525efa13515` |
| Profile | `kernel_6_6` |
| 执行状态 | `failed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：静态证据与 3 个类型感知 Mock 契约共同确认兼容性边界发生变化：旧可接受的 non-writable RO->RW access-only rereg 在 after 返回 EACCES，mlx4 errno 从 EPERM 变为 EACCES，失败前副作用被消除。真实 RXE 端到端因 provider 不支持 rereg 而未验证，实际补丁行覆盖率为 0%，但该阻塞不否定已确认的契约差异。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 3 |
| 测试 findings | 3 |
| 规划入口 | 3 |
| 生成入口 | 3 |
| 验证入口 | 3 |
| 规划输入 | 17 |
| 执行输入 | 17 |
| 契约通过 | 0 |
| 契约违约 | 3 |
| 契约跳过 | 0 |
| 补丁可执行行 | 21 |
| 已覆盖行 | 0 |
| 未覆盖行 | 21 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `mixed` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc 13.3.0` |
| 优化级别 | `kernel -O2 -g；Mock -O0 -g` |
| 覆盖率工具 | `gcov 13.3.0 + CONFIG_GCOV_KERNEL per-object instrumentation` |
- before/after 均从指定 base_commit 创建在 compatibility-testing/environment 下的隔离 worktree，after 单独应用 patch。
- QEMU 8.2.2 使用 TCG、最小静态 /init 和内嵌 initramfs；无宿主 root/KVM。
- kernel -Og 构建因 kernel compile-time signedness assertions 失败，按 kernel gcov 指南回退到 -O2；Mock 仍以 -O0 采集精确行覆盖。
- 仅 umem.o 与 rxe_verbs.o 开启 kernel gcov；真实 RXE provider 在 userspace 阻止 rereg，因此目标补丁行未执行。

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `drivers/infiniband/core/umem.c:334-342 (ib_umem_check_rereg)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001-REAL | blocked_before_kernel_callback | `real-rxe/rxe_probe.c` | `sh real-rxe/run_one.sh before; sh real-rxe/run_one.sh after` | before RO->RW accepted；after errno=EACCES | QEMU serial JSON and kernel gcov |
| PCA-TE-0001-MOCK | runnable_verified | `mock/mock_rereg.c` | `sh mock/build_and_run.sh` | before accept；after -EACCES | PCAT_P099_MOCK_SUITE_PASS and mock gcov |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0001-backward_input_acceptance-1 | breached | access-only non-writable RO->LOCAL_WRITE 从 before ret=0/errno=0 变为 after ret=-13/errno=13。 |

- **覆盖率**: 0/5 (0.00%)
- **未覆盖行**: drivers/infiniband/core/umem.c:334, drivers/infiniband/core/umem.c:336, drivers/infiniband/core/umem.c:339, drivers/infiniband/core/umem.c:340, drivers/infiniband/core/umem.c:341

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I07 | INPUT_CONTRACT_CHANGE | hns/irdma/mlx5/rxe ret=0；mlx4 ret=-EPERM | 五驱动均 ret=-EACCES | mock/logs/before-after.diff and phase3_contracts/contracts.jsonl |
- Mock 直接复用补丁 helper 源码并覆盖 NULL、writable/non-writable、readonly/LOCAL_WRITE/REMOTE_WRITE/REMOTE_ATOMIC、ACCESS/TRANS/PD 组合。
- 真实 uverbs 端到端结果因 librxe provider 不支持 rereg_mr 而不完整。

### PCA-0002: ERROR_EXCEPTION_CHANGE

- **优先级**: `high`
- **状态**: `failed`
- **目标**: `drivers/infiniband/core/umem.c:339-341 (ib_umem_check_rereg)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | runnable_verified | `mock/mock_rereg.c` | `sh mock/build_and_run.sh` | after RO->RW=-EACCES；CONFIG_USER_MEM=n=-EOPNOTSUPP；invalid flag=-EOPNOTSUPP | gcov helper return counts and PCAT_P099_MOCK_SUITE_PASS |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0002-error_exception_stability-1 | breached | mlx4 RO->RW 从 before EPERM 变为 after EACCES；其他四驱动从成功变为 EACCES。 |

- **覆盖率**: 0/2 (0.00%)
- **未覆盖行**: drivers/infiniband/core/umem.c:341, include/rdma/ib_umem.h:211

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I07-mlx4 | ERROR_EXCEPTION_CHANGE | ret=-1 errno=EPERM | ret=-13 errno=EACCES | phase3_contracts/contracts.jsonl |
- CONFIG_INFINIBAND_USER_MEM=n 仅由独立编译 Mock 验证，未作为可启动的 uverbs 内核环境运行。
- 实际 rdma-core errno=EACCES 映射未验证，因为 provider 未把请求提交到内核。

### PCA-0003: SIDE_EFFECT_CHANGE

- **优先级**: `low`
- **状态**: `failed`
- **目标**: `drivers/infiniband/sw/rxe/rxe_verbs.c:1329-1344 (rxe_rereg_user_mr)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | runnable_verified | `mock/mock_rereg.c` | `sh mock/build_and_run.sh` | helper=-EACCES 时五驱动在硬件/PD/MR 修改前返回 | 五驱动 wrapper gcov counts and ordered JSON effect manifests |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| CT-PCA-0003-side_effect_manifest_stability-1 | breached | before 可出现 mailbox/hw_dereg/mpt_get/umr/PD/MR 副作用；after 五驱动拒绝路径的副作用清单为空。 |

- **覆盖率**: 0/15 (0.00%)
- **未覆盖行**: drivers/infiniband/hw/hns/hns_roce_mr.c:280, drivers/infiniband/hw/hns/hns_roce_mr.c:281, drivers/infiniband/hw/hns/hns_roce_mr.c:282, drivers/infiniband/hw/irdma/verbs.c:3247, drivers/infiniband/hw/irdma/verbs.c:3248, drivers/infiniband/hw/irdma/verbs.c:3249, drivers/infiniband/hw/mlx4/mr.c:469, drivers/infiniband/hw/mlx4/mr.c:470, drivers/infiniband/hw/mlx4/mr.c:471, drivers/infiniband/hw/mlx5/mr.c:1701, drivers/infiniband/hw/mlx5/mr.c:1702, drivers/infiniband/hw/mlx5/mr.c:1703, drivers/infiniband/sw/rxe/rxe_verbs.c:1329, drivers/infiniband/sw/rxe/rxe_verbs.c:1330, drivers/infiniband/sw/rxe/rxe_verbs.c:1331

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| I16 | SIDE_EFFECT_CHANGE | RO->RW 可记录 mailbox_alloc/hw_dereg/mpt_get/umr/PD/MR 字段修改 | 五驱动 ret=-EACCES 且 effects 为空、计数为 0 | phase3_contracts/contracts.jsonl and mock/logs/after.jsonl |
- mlx4 ACCESS\|TRANS 控制保持 mpt_get 后 EPERM，验证了补丁保留的特殊路径。
- hns、irdma、mlx4、mlx5 无对应硬件；Mock 未覆盖真实 firmware/mailbox/UMR/PD 引用实现。

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| entry | real-rxe-uverbs | 当前 rdma-core librxe provider 对 ibv_rereg_mr 返回 ret=-4/errno=EOPNOTSUPP，kernel gcov 证实没有调用 rxe_rereg_user_mr。 | 使用支持 rereg_mr 的 rdma-core/RXE provider，或构造直接提交 IB_USER_VERBS_CMD_REREG_MR 的 uverbs harness。 |
| environment | hardware-drivers | 没有 hns、irdma、mlx4、mlx5 RDMA 硬件及对应 firmware，因此仅验证了编译语义与受控 Mock 顺序。 | 在配备对应设备与 firmware 的 before/after 内核上重复同一输入矩阵并采集设备状态与 kernel gcov。 |
| coverage | actual-patch-lines | 真实 QEMU 入口在 userspace provider 层终止，21 条补丁可执行行实际覆盖为 0%；Mock 等价路径 21/21 不计作真实补丁行覆盖。 | 先解除 provider rereg capability 阻塞，再执行 QEMU RXE；硬件驱动补丁行需要相应真实设备。 |
| environment | config-user-mem-n-runtime | CONFIG_INFINIBAND_USER_MEM=n stub 已独立编译和 gcov 验证，但该配置没有可用的真实 uverbs MR 端到端路径。 | 若需内核级编译覆盖，可构建最小 KUnit/module consumer 调用 header stub；其结论仍是编译期单元契约。 |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/phase1_impact/impact_map.json` |
| mock_diff | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/mock/logs/before-after.diff` |
| real_after_log | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/real-rxe/logs/qemu-after.log` |
| real_before_log | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/real-rxe/logs/qemu-before.log` |
| report | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/test-entry-tasks.json` |
| test_entry_verification | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/test-entry-work/test-entry-verification.json` |
| test_inputs | `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 在支持 rereg_mr 的 rdma-core/RXE provider 上复跑 QEMU before/after，确认 libibverbs 返回值、errno 和 MR 失败后状态。
- 在 hns、irdma、mlx4、mlx5 实机上验证早退前无 firmware/mailbox/UMR/PD/MR 副作用，并采集补丁行覆盖率。
- 应用侧应把 access-only RO->RW 的 EACCES 作为新契约处理，改用 REREG_TRANS 重新 pin 或初始注册 writable umem。
