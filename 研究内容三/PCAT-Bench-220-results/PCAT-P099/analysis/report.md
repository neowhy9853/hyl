# PCAT-P099 静态兼容性分析报告

- 源仓库：`/home/soong/pca_benchmark/_repos/linux`
- 隔离补丁后 worktree：已清理（原路径：`/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis/_worktrees/patched`）
- 基线：`09b8a7aa5a341bb345dc492aac139525efa13515`
- 补丁：`09dc18894148381d3bfc550083b1236043870dce`
- Profile：`kernel_6_6`
- 模式：`normal`
- 变更：7 个文件、9 个候选 hunk、45 行新增、1 行删除
- 最终 finding：3（High 2、Medium 0、Low 1）

## 结论

该补丁确认引入用户可观察的兼容性变化。它修复了一个内存 pin 权限一致性问题，但同时收紧了 `ibv_rereg_mr`/uverbs 的输入契约：以只读方式 pin 的 `ib_umem` 不再允许仅通过 `IB_MR_REREG_ACCESS` 升级为可写。受影响输入在补丁后于驱动执行硬件或状态修改前返回 `-EACCES`。

新增的 `ib_umem_check_rereg()` 声明和导出符号是加法接口，本身不构成破坏性 ABI 变化；`CONFIG_INFINIBAND_USER_MEM=n` 下新增的 inline stub 返回 `-EOPNOTSUPP`，用于保证调用点可编译并维持不支持 user memory 的配置契约。

## PCA-0001：INPUT_CONTRACT_CHANGE

- 优先级：High
- 置信度：0.99
- 位置：`drivers/infiniband/core/umem.c:334`
- 接口：`ibv_rereg_mr / IB_USER_VERBS_CMD_REREG_MR`

补丁前，hns_roce、irdma、mlx5 和 rxe 没有统一检查原 umem 的 writable pin 属性，access-only 的 RO→RW 重新注册可继续并可能成功。补丁后，只有同时满足以下条件才返回 `-EACCES`：

1. `umem != NULL`；
2. 设置 `IB_MR_REREG_ACCESS`；
3. 未设置 `IB_MR_REREG_TRANS`；
4. 新 access 含 `LOCAL_WRITE`、`REMOTE_WRITE`、`REMOTE_ATOMIC` 或 `MW_BIND`；
5. `umem->writable == false`。

NULL umem、原 umem writable、新 access 只读、未设置 `REREG_ACCESS`，或 `REREG_ACCESS|REREG_TRANS` 均由 helper 放行。

## PCA-0002：ERROR_EXCEPTION_CHANGE

- 优先级：High
- 置信度：0.99
- 位置：`drivers/infiniband/core/umem.c:339`
- 接口：`ibv_rereg_mr / IB_USER_VERBS_CMD_REREG_MR`

新增错误为 `-EACCES`，`ib_uverbs_rereg_mr()` 通过 `PTR_ERR(new_mr)` 原样向用户态传播。hns_roce、irdma、mlx5、rxe 从可能成功或返回后续驱动错误变为前置 `EACCES`；mlx4 的 access-only RO→RW 从后置 `-EPERM` 变为前置 `-EACCES`。无效 rereg flag 仍优先返回 `-EOPNOTSUPP`。

## PCA-0003：SIDE_EFFECT_CHANGE

- 优先级：Low
- 置信度：0.98
- 位置：`drivers/infiniband/sw/rxe/rxe_verbs.c:1329`
- 接口：五个驱动的 `rereg_user_mr` callback

新增检查全部位于危险副作用之前：

- hns：mailbox 分配、MPT query/destroy、MR 字段修改之前；
- irdma：hardware dereg、PD/access 修改、PBL/umem 释放之前；
- mlx4：MPT 获取、PD/access 修改之前；
- mlx5：UMR/revoke、umem 脱离和 `reg_pages` 更新之前；
- rxe：PD put/get、`mr->ibmr.pd` 和 `mr->access` 修改之前。

因此 helper 返回 `-EACCES` 时，补丁后应保持 MR/PD/umem 状态不变且硬件副作用计数为零。该项校准为 Low，是因为每个真实硬件路径都需要特定设备；用户要求的完整测试仍会覆盖全部 wrapper。

## mlx4 特例

`IB_MR_REREG_ACCESS|IB_MR_REREG_TRANS` 被 helper 明确放行，因为设置 TRANS 表示后续可重新 pin。mlx4 随后保留自己的 `ib_access_writable()` 检查，并继续以 `-EPERM` 拒绝该组合；该补丁没有把 mlx4 的组合路径误改为支持。

## 用户入口与静态调用路径

有界源码核对确认：`ib_uverbs_rereg_mr()` 校验命令与 access flag，调用 `ib_dev->ops.rereg_user_mr(...)`，再将 `ERR_PTR` 通过 `PTR_ERR` 返回。五个受影响驱动均注册了该 callback。

请求的 AST 静态调用链未生成：环境缺少 C callgraph 所需的 `tree_sitter`，Skill 禁止使用 grep/ctags 作为替代，因此 `callchains.json` 和每条 finding 的 `static_call_chains` 保持空数组。此限制不影响上述直接分派与错误传播的源码证据。

## 后续定向测试

测试应优先尝试真实 RXE/uverbs；若环境不具备权限、rdma-core、RXE 网络设备或所需内核配置，则使用源码派生的独立 C harness 验证 helper 全分支和五个驱动的 early-return/副作用顺序，并用 gcov 明确区分 mock 覆盖与真实硬件覆盖。

## 产物

- `analysis.json`：最终结构化 findings
- `analysis-context.json`：紧凑候选与源码证据
- `candidates.json`：全部候选 hunk
- `effective-profile.yaml`：解析后的 `kernel_6_6` profile
- `priority-calibration-report.json`：确定性优先级校准
- `patch.diff`：实际分析补丁
- `callchains.json`：空数组（缺少 `tree_sitter`）
