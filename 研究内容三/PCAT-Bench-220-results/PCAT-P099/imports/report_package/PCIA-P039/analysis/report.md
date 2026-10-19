# PCA 兼容性变更分析报告

**仓库**: /data7/wanghy/tmp/opencode/linux-src (originally https://github.com/gregkh/linux.git)
**基线**: HEAD (v7.2-rc4, commit 1590cf032)
**补丁**: 09dc18894148381d3bfc550083b1236043870dce
**Profile**: kernel_6_6
**补丁应用状态**: already_applied (等效的上游提交已合入主线 v7.2-rc4)

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 7 |
| 候选变更 | 9 |
| 兼容性变更 | 3 |
| 高优先级测试 | 2 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

本补丁在 RDMA 子系统中新增了一个导出的内核函数 `ib_umem_check_rereg()`，使用 `EXPORT_SYMBOL` 导出，并在所有 RDMA 驱动程序的 `rereg_user_mr` 回调中调用该函数。当用户空间应用程序尝试通过 `IBV_REREG_MR_ACCESS` 将某个内存区域（MR）的访问权限从只读变更为可写，而该 MR 在最初注册时并未以可写方式 pin 住时，该补丁会返回 `-EACCES`。此前，这种操作在未检查底层 umem 可写状态的情况下即被允许，这可能构成安全漏洞。该补丁修复了 CVE 相关的安全问题（修复标记：b40656aa7d55）。

回移植补丁源自 gregkh/linux.git 稳定版代码库，由 Jason Gunthorpe 撰写，Sasha Levin 和 Greg Kroah-Hartman 签名。等效的上游提交为 badad6fad60d。

---

## PCA-0001: 输入契约变更 — rereg_user_mr UAPI 收紧

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: `rereg_user_mr` (RDMA userspace verbs API, `ibv_rereg_mr`)
- **旧代码位置**: `drivers/infiniband/core/umem.c:326-328` (补丁 diff)
- **新代码位置**: `drivers/infiniband/core/umem.c:326-344` (补丁 diff)
- **类型**: `INPUT_CONTRACT_CHANGE`

### 变更前行为

调用 `ibv_rereg_mr` 并设置 `IBV_REREG_MR_ACCESS` 标志将 MR 从只读访问权限变更为可写访问权限时，操作会成功，即使底层 umem 最初并未按可写方式 pin 住（即 `umem->writable` 为 false）。这可能导致安全漏洞：调用方获得了对未正确 pin 住的内存的写访问权限。

### 变更后行为

如果 MR 最初注册为只读（`umem->writable` == false），且调用方尝试通过 `IB_MR_REREG_ACCESS`（不伴随 `IB_MR_REREG_TRANS`）将访问权限变更为可写，则操作现在返回 `-EACCES`。只有当 MR 最初注册为可写，或同时使用 `IB_MR_REREG_TRANS` 重新注册时，才允许将访问权限变更为可写。

### 兼容性影响

以前在 `rereg_user_mr` 中将 RO→RW 访问变更视为成功的用户空间 RDMA 应用程序，现在将收到 `-EACCES` 错误。这是一个收紧的输入契约变更：之前被接受的合法输入现在被拒绝了。

受影响的标志组合为：`IB_MR_REREG_ACCESS` 单独设置（不伴随 `IB_MR_REREG_TRANS`），且新的访问标志包含可写权限（`IB_ACCESS_LOCAL_WRITE`、`IB_ACCESS_REMOTE_WRITE`、`IB_ACCESS_REMOTE_ATOMIC` 或 `IB_ACCESS_MW_BIND`），而原始 MR 注册时没有可写权限。

此变更影响所有 RDMA 驱动程序（hns、irdma、mlx4、mlx5、rxe 以及任何其他调用 `ib_umem_check_rereg` 的驱动程序）。

### 证据

```c
// drivers/infiniband/core/umem.c
int ib_umem_check_rereg(struct ib_umem *umem, int flags, int new_access_flags)
{
	if (!umem)
		return 0;

	if ((flags & IB_MR_REREG_ACCESS) && !(flags & IB_MR_REREG_TRANS))
		if (ib_access_writable(new_access_flags) && !umem->writable)
			return -EACCES;
	return 0;
}
EXPORT_SYMBOL(ib_umem_check_rereg);

// drivers/infiniband/hw/hns/hns_roce_mr.c
	ret = ib_umem_check_rereg(mr->pbl_mtr.umem, flags, mr_access_flags);
	if (ret)
		goto err_out;

// drivers/infiniband/hw/irdma/verbs.c
	ret = ib_umem_check_rereg(iwmr->region, flags, new_access);
	if (ret)
		return ERR_PTR(ret);

// drivers/infiniband/hw/mlx4/mr.c
	err = ib_umem_check_rereg(mmr->umem, flags, mr_access_flags);
	if (err)
		return ERR_PTR(err);

// drivers/infiniband/hw/mlx5/mr.c
	err = ib_umem_check_rereg(mr->umem, flags, new_access_flags);
	if (err)
		return ERR_PTR(err);
```

### 复核建议

确认 `umem->writable` 在所有注册 MR 的代码路径上被正确设置。检查是否存在任何可能合法将 RO MR 重新注册为 RW MR 的用例（例如，最初使用只读访问创建、后续需要写访问的 MR）。

### 测试建议

使用包含 `IBV_REREG_MR_ACCESS` 标志（不伴随 `IBV_REREG_MR_TRANS`）和包含写位的目标访问标志，对初始以只读访问注册的 MR 执行 `ibv_rereg_mr()` 调用的回归测试。验证返回码为 `-EACCES`（而非成功）。

---

## PCA-0002: ABI 变更 — 新增 EXPORT_SYMBOL

- **测试优先级**: HIGH
- **置信度**: 1.0
- **影响接口**: `ib_umem_check_rereg` (EXPORT_SYMBOL)
- **旧代码位置**: `drivers/infiniband/core/umem.c:326-328` (补丁 diff)
- **新代码位置**: `drivers/infiniband/core/umem.c:326-344` (补丁 diff)
- **类型**: `ABI_CHANGE`

### 变更前行为

内核导出符号表中不存在符号 `ib_umem_check_rereg`。任何依赖它的外部内核模块将无法加载。

### 变更后行为

通过 `EXPORT_SYMBOL` 新增导出的内核符号 `ib_umem_check_rereg`。该符号现在对加载的内核模块可见，并且新的 IB 核心模块将所有内核模块的符号依赖版本提升到包含该新符号的版本。

### 兼容性影响

在稳定版内核中新增导出的符号属于 ABI 变更。内核模块的符号依赖关系（通过 `Module.symvers` 跟踪）现在要求 IB 核心模块提供 `ib_umem_check_rereg`。对 IB 核心模块重新编译的树外 RDMA 驱动程序将期望此符号存在。重新编译的驱动程序无法在不包含此符号的旧内核上加载，且升级到包含此补丁的新内核可能需要重新编译树外模块。

### 证据

```c
// drivers/infiniband/core/umem.c
int ib_umem_check_rereg(struct ib_umem *umem, int flags, int new_access_flags)
{
	...
}
EXPORT_SYMBOL(ib_umem_check_rereg);

// include/rdma/ib_umem.h (public header)
int ib_umem_check_rereg(struct ib_umem *umem, int flags, int new_access_flags);
```

### 复核建议

如果下游内核模块政策要求，需在发行版内核 ABI 白名单 / kABI 跟踪中记录该符号。

### 测试建议

通过验证 `/proc/kallsyms` 或 `Module.symvers` 中是否存在该符号来确认符号可见性。尝试加载一个使用该符号编译的树外 RDMA 内核模块，验证其正确链接。

---

## PCA-0003: 错误异常变更 — !CONFIG_INFINIBAND_USER_MEM 存根

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: `ib_umem_check_rereg` 存根 (`include/rdma/ib_umem.h`)
- **旧代码位置**: `include/rdma/ib_umem.h:203-207` (补丁 diff)
- **新代码位置**: `include/rdma/ib_umem.h:205-215` (补丁 diff)
- **类型**: `ERROR_EXCEPTION_CHANGE`

### 变更前行为

在配置为 `!CONFIG_INFINIBAND_USER_MEM` 的内核构建中，`rereg_user_mr` 驱动程序回调不会被调用（因为用户空间 RDMA 需要 `CONFIG_INFINIBAND_USER_MEM`）。不存在对应的存根。

### 变更后行为

在不配置 `CONFIG_INFINIBAND_USER_MEM` 的情况下，新增的 `ib_umem_check_rereg` 存根无条件返回 `-EOPNOTSUPP`。如果任何代码路径在此配置下调用了 `rereg_user_mr` 驱动程序回调，它将收到 `-EOPNOTSUPP` 并失败。

### 兼容性影响

理论上，在此配置下行为会发生变化：任何到达该代码路径的调用都会收到 `-EOPNOTSUPP`，而之前行为未定义。但实际上，`rereg_user_mr` 仅通过要求 `CONFIG_INFINIBAND_USER_MEM` 的 `ib_uverbs` 层调用，因此该存根不会被触及。这是一个仅存在于编译期的兼容性变更，运行时影响极小。

### 证据

```c
// include/rdma/ib_umem.h (CONFIG_INFINIBAND_USER_MEM=n)
static inline int ib_umem_check_rereg(struct ib_umem *umem, int flags,
				      int new_access_flags)
{
	return -EOPNOTSUPP;
}
```

### 复核建议

人工确认在 `!CONFIG_INFINIBAND_USER_MEM` 配置下，`rereg_user_mr` 驱动程序回调确实无法被触发。如果下游内核拥有不经过 uverbs 层即调用 `rereg_user_mr` 的树外补丁，该存根变更可能会破坏其行为。

### 测试建议

低优先级：如果下游使用 `CONFIG_INFINIBAND_USER_MEM=n` 的内核配置，则以仅包含 `IB_MR_REREG_ACCESS` 标志（不伴随 `IB_MR_REREG_TRANS`）的 `ibv_rereg_mr` 进行回归测试，验证其是否正确失败。

---
