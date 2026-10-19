# PCA 兼容性变更分析报告

**仓库**: /data7/wanghy/tmp/linux
**基线**: 36c41e9724c9a7a7cda37f5a4e9d94f25c8031c4~1 (d68b621bb5a48051932f1017a6e1bc9b18f854d0)
**补丁**: 36c41e9724c9a7a7cda37f5a4e9d94f25c8031c4
**Profile**: kernel_6_6
**Patch Source**: https://github.com/gregkh/linux/commit/36c41e9724c9a7a7cda37f5a4e9d94f25c8031c4

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 9 |
| 公共候选 | 3 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

## Patch Metrics

| metric | value |
|---|---:|
| `patch_lines` | 215 |
| `raw_hunks` | 9 |
| `candidate_hunks` | 9 |
| `changed_files` | 4 |
| `churn` | 85 |
| `diff_added_lines` | 73 |
| `diff_deleted_lines` | 12 |

---

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: NCM gadget net_device生命周期（sysfs拓扑 + uevents）
- **类型**: SIDE_EFFECT_CHANGE
- **代码位置**: drivers/usb/gadget/function/u_ether.c:896-923
- **Profile**: kernel_6_6

### 变更前行为

NCM gadget的net_device在首次bind时通过`gether_register_netdev()`注册, 并通过`SET_NETDEV_DEV`将parent永久设为gadget设备。gadget断开后net_device保留对已释放gadget设备的dangling parent引用, 造成sysfs悬空链接。net_device在instance释放时销毁, 重新连接时需重新注册。

### 变更后行为

新增`gether_attach_gadget()`/`gether_detach_gadget()`导出函数使用`device_move()`动态管理net_device的sysfs父设备关系。首次bind调用`gether_register_netdev()`注册net_device, 后续bind通过`device_move`将net_device迁移到gadget设备下（DPM_ORDER_DEV_AFTER_PARENT）, unbind时通过`device_move`迁回`/sys/devices/virtual/`。net_device在bind/unbind间持久存在。

### 兼容性影响

net_device的sysfs层级结构在bind/unbind期间动态变化, 在`/sys/devices/virtual/net/<iface>`与gadget设备之间迁移。这改变了udev事件类型（KOBJ_MOVE替代KOBJ_ADD/KOBJ_REMOVE）, 可能影响依赖sysfs路径或netlink device事件监控的用户空间工具（如udev规则、网络管理器、监控脚本）。同时net_device持久化意味着DHCP客户端/服务器可以保留租约, 这是预期改进但仍属于行为变更。

### 证据

```c
// drivers/usb/gadget/function/u_ether.c:899-910
int gether_attach_gadget(struct net_device *net, struct usb_gadget *g)
{
	int ret;

	ret = device_move(&net->dev, &g->dev, DPM_ORDER_DEV_AFTER_PARENT);
	if (ret)
		return ret;

	gether_set_gadget(net, g);
	return 0;
}
EXPORT_SYMBOL_GPL(gether_attach_gadget);
```

```c
// drivers/usb/gadget/function/f_ncm.c:1442-1453 (ncm_bind)
	scoped_guard(mutex, &ncm_opts->lock)
		if (ncm_opts->bind_count == 0) {
			if (!device_is_registered(&ncm_opts->net->dev)) {
				gether_set_gadget(ncm_opts->net, cdev->gadget);
				status = gether_register_netdev(ncm_opts->net);
			} else
				status = gether_attach_gadget(ncm_opts->net, cdev->gadget);
```

```c
// drivers/usb/gadget/function/u_ether.c:912-918
void gether_detach_gadget(struct net_device *net)
{
	struct eth_dev *dev = netdev_priv(net);

	device_move(&net->dev, NULL, DPM_ORDER_NONE);
	dev->gadget = NULL;
}
EXPORT_SYMBOL_GPL(gether_detach_gadget);
```

### 静态调用链

（未生成）

### 复核建议

验证NCM gadget反复bind/unbind时`/sys/class/net/<iface>/device`软链接是否始终有效, 以及`udevadm monitor`捕获的事件类型是否从ADD/REMOVE变为MOVE。

### 测试建议

测试NCM gadget的bind/unbind循环: 通过configfs创建gadget配置, 反复绑定/解绑NCM function, 监控`/sys/class/net/<iface>/device`路径和udev事件, 确认net_device不丢失且DHCP客户端持续工作。

---

## 排除候选说明

| 候选 | 文件 | 排除原因 |
|------|------|----------|
| HUNK-0007 | u_ether.c | 纯增量API: 新增EXPORT_SYMBOL_GPL函数, 不改变已有接口 |
| HUNK-0008 | u_ether.h | 纯增量API: 新增函数声明和DEFINE_FREE宏, 不改变已有接口 |
| HUNK-0009 | u_ncm.h | 内核内部结构体变更（bool bound→int bind_count）, 仅被in-tree代码使用(f_ncm.c, legacy/ncm.c), 无外部可观察影响 |
| HUNK-0001~0006 | f_ncm.c | 内部static函数变更, 不直接构成公共接口变化 |

## 产物位置

所有分析产物位于: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/`

- `analysis.json` — 最终分析结果（已通过校验）
- `report.md` — 本报告
- `candidates.json` — 所有候选hunk
- `analysis-context.json` — 分析上下文
- `effective-profile.yaml` — 有效profile
- `patch.diff` — 补丁副本
- `_worktrees/patched/` — 已应用补丁的隔离worktree
