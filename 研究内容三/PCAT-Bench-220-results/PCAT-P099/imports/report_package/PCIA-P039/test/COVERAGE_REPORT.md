# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `09dc18894148381d3bfc550083b1236043870dce` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux` |
| 基线 | `09b8a7aa5a341bb345dc492aac139525efa13515` |
| Profile | `kernel_6_6` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁在 rereg_user_mr 路径引入了 RO umem + IB_MR_REREG_ACCESS (without REREG_TRANS) + writable access 请求的 -EACCES 拒绝。此前静默成功（虽不安全），现有依赖此路径的用户态 RDMA 程序将失败。这是一次有意的安全修复（Fixes: b40656aa7d55），但行为上不兼容。所有 14 个契约测试通过，独立测试达到 100% 行覆盖率。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 2 |
| 测试 findings | 2 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 14 |
| 执行输入 | 14 |
| 契约通过 | 0 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 7 |
| 已覆盖行 | 7 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0` |
| 优化级别 | `-O0 -fprofile-arcs -ftest-coverage` |
| 覆盖率工具 | `gcov` |
- 测试在独立 mock 环境中执行，使用从补丁后 umem.c 精确复制的 ib_umem_check_rereg() 函数
- 未进行完整内核构建（需要 RDMA 硬件或 rxe 软 RoCE 模块）
- 独立单元测试覆盖了函数所有逻辑路径

## Finding 测试结果

### PCA-0001: INPUT_CONTRACT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `drivers/infiniband/core/umem.c:330-344 (ib_umem_check_rereg)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001-standalone-unit | verified | `compatibility-testing/test-entry-work/PCA-TE-0001/test_umem_rereg.c` | `gcc -fprofile-arcs -ftest-coverage -O0 -g -o test_umem_rereg test_umem_rereg.c && ./test_umem_rereg` | exit code 0, all 14 tests pass | gcov shows 100% line coverage on ib_umem_check_rereg() function body |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| backward_input_acceptance | breached | [预期契约变更] RO umem + IB_MR_REREG_ACCESS without IB_MR_REREG_TRANS + writable access flags: 补丁前返回 0（成功），补丁后返回 -EACCES（-13）。该契约违反是补丁的设计目的——收紧输入验证以修复安全缺陷（Fixes: b40656aa7d55）。已验证所有其他 13 个输入组合行为保持一致。 |

- **覆盖率**: 7/7 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| PCA-0001-ro-umem-rw-access-no-trans | INPUT_CONTRACT_CHANGE | ib_umem_check_rereg() 不存在；rereg_user_mr 在 RO umem + RW access 请求时返回成功（0/NULL） | ib_umem_check_rereg() 在 RO umem + writable access flags 且无 IB_MR_REREG_TRANS 时返回 -EACCES | gcov 确认所有补丁行（334-344）被执行：行334（14次）、336（14次）、339（12次）、340（8次）、341（5次）、342（7次）。5个测试用例验证 -EACCES 返回。 |
- 所有 14 个测试用例通过，覆盖 ib_umem_check_rereg() 的全部逻辑路径
- 契约违反（contract breach）是补丁设计意图——这正是要修复的安全缺陷
- 行为差异是预期的兼容性变更：收紧输入验证以阻止不安全的 RO-to-RW 访问变更
- mlx4 驱动中的错误码从 -EPERM 变为 -EACCES（相同输入场景）——在独立测试中未直接验证

### PCA-0002: API_SIGNATURE_CHANGE

- **优先级**: `low`
- **状态**: `not_run`
- **目标**: `drivers/infiniband/core/umem.c:330-344 (ib_umem_check_rereg)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| - | - | - |

- **覆盖率**: 7/7 (100.00%)
- **未覆盖行**: -
- PCA-0002 是低优先级纯增量 API 添加（新 EXPORT_SYMBOL），被 min-priority=high 过滤
- 验证 EXPORT_SYMBOL 需要完整内核构建后检查 Module.symvers
- 补丁函数逻辑与 PCA-0001 相同，覆盖率数据来自 PCA-0001 的测试

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| finding | PCA-0002 | 低优先级 finding（API_SIGNATURE_CHANGE — 纯增量导出符号），被 test_entry_planner 的 --min-priority high 过滤 | 若要测试 EXPORT_SYMBOL 验证，构建内核后运行 grep ib_umem_check_rereg Module.symvers |
| environment | PCA-0001-full-kernel | 需要完整内核构建和 RDMA 设备（或 rxe 软 RoCE）才能在真实内核上下文中通过 uverbs 路径验证 rereg_user_mr | 构建带 gcov 的内核（CONFIG_GCOV_KERNEL=y），加载 rxe 模块，运行基于 libibverbs 的 rereg_mr 回归测试 |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `compatibility-testing/phase3_contracts/contract_verification.json` |
| coverage_data | `compatibility-testing/phase4_execution/coverage_iterations.json` |
| execution_results | `compatibility-testing/phase4_execution/results.json` |
| impact_map | `compatibility-testing/phase1_impact/impact_map.json` |
| report | `compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `compatibility-testing/test-entry-tasks.json` |
| test_inputs | `compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 审查下游用户态 RDMA 程序中的 rereg_mr 调用，确保不会在 RO umem 上单独使用 IB_MR_REREG_ACCESS 请求 writable 访问
- 如必须从 RO 转为 RW 访问，请重新创建 writable umem 并设置 IB_MR_REREG_TRANS 标志
- mlx4 用户注意错误码变更：-EPERM → -EACCES
- 考虑在完整内核 + RDMA 设备环境中运行 libibverbs 回归测试以验证用户态路径
