# PCA 兼容性变更分析报告

**仓库**: https://github.com/gregkh/linux.git
**基线**: 922a03b26e354a74a30b4a8220822072df3e54c4~1 (36c85f7029484d5ede769f8873d16e9c8e35533c)
**补丁**: 922a03b26e354a74a30b4a8220822072df3e54c4
**Profile**: kernel_6_6
**Patch来源**: https://github.com/gregkh/linux/commit/922a03b26e354a74a30b4a8220822072df3e54c4

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 2 |
| 高优先级测试 | 2 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 返回值约定变化 (RETURN_CONTRACT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.90
- **影响接口**: btmtk_usb_hci_wmt_sync (EXPORT_SYMBOL_GPL)
- **旧代码位置**: drivers/bluetooth/btmtk.c:681-682
- **新代码位置**: drivers/bluetooth/btmtk.c:682-683
- **类型**: RETURN_CONTRACT_CHANGE

### 变更前行为
当 WMT FUNC_CTRL 事件过短、不包含 status 字段时（skb_pull_data 返回 NULL），函数设置 err = -EINVAL 并跳转到 err_free_skb 标签，释放 SKB 并返回 -EINVAL。调用方通过 `err < 0` 检测到此错误条件后中止操作并打印 "Failed to send wmt func ctrl (-22)"。

### 变更后行为
当 WMT FUNC_CTRL 事件过短时，设置 status = BTMTK_WMT_ON_UNDONE，然后 break 退出 switch。随后执行 `if (wmt_params->status) *wmt_params->status = status;`（仅当 status 非 NULL 时写入），然后 fall-through 到 err_free_skb/err_free_wc 清理路径，返回 err（此时通常为 0，因为走到此路径意味着之前所有操作成功）。调用方的 `err < 0` 检查不再触发，将继续执行后续操作。

### 兼容性影响
该函数是 EXPORT_SYMBOL_GPL 导出的公共内核 API，被 btusb.c 中的多个调用点使用。调用方均使用 `err < 0` 来检测失败。此补丁前，在特定硬件（MT7925）上，设备发送不包含 status 字段的短事件，导致返回 -EINVAL 并使设备不可用。此补丁将短事件解释为 BTMTK_WMT_ON_UNDONE 并返回成功，从兼容性角度看是一种 return contract 放宽——原先返回错误的输入现在返回成功。该变更是有意为之的 bug fix，恢复了引入长度验证之前的原始行为，但从外部可观察接口语义来看，返回值约定已发生改变。

### 证据
```c
// drivers/bluetooth/btmtk.c:679-694 (补丁后)
	case BTMTK_WMT_FUNC_CTRL:
		if (!skb_pull_data(data->evt_skb,
				   sizeof(wmt_evt_funcc->status))) {
			status = BTMTK_WMT_ON_UNDONE;
			break;
		}

		wmt_evt_funcc = (struct btmtk_hci_wmt_evt_funcc *)wmt_evt;
		if (be16_to_cpu(wmt_evt_funcc->status) == 0x404)
			status = BTMTK_WMT_ON_DONE;
		else if (be16_to_cpu(wmt_evt_funcc->status) == 0x420)
			status = BTMTK_WMT_ON_PROGRESS;
		else
			status = BTMTK_WMT_ON_UNDONE;
		break;
```

```c
// drivers/bluetooth/btusb.c:2968-2974 (调用点示例)
		wmt_params.status = NULL;

		err = btmtk_usb_hci_wmt_sync(hdev, &wmt_params);
		if (err < 0) {
			bt_dev_err(hdev, "Failed to send wmt func ctrl (%d)", err);
			return err;
		}
```

```c
// drivers/bluetooth/btusb.c:3032-3038 (调用点示例)
		wmt_params.status = NULL;

		err = btmtk_usb_hci_wmt_sync(hdev, &wmt_params);
		if (err < 0) {
			bt_dev_err(hdev, "Failed to send wmt func ctrl (%d)", err);
			return err;
		}
```

```c
// drivers/bluetooth/btusb.c:3078-3084 (调用点示例, shutdown)
		wmt_params.status = NULL;

		err = btmtk_usb_hci_wmt_sync(hdev, &wmt_params);
		if (err < 0) {
			bt_dev_err(hdev, "Failed to send wmt func ctrl (%d)", err);
			return err;
		}
```

### 静态调用链
(未启用调用链分析)

### 复核建议
无需人工复核。补丁逻辑清晰：将过短事件统一处理为 ON_UNDONE。所有调用点对 FUNC_CTRL 均设置 wmt_params.status = NULL 且仅检查 err < 0，因此旧代码在短事件时会导致设备初始化/shutdown 失败并打印错误日志，新代码允许继续执行。

### 测试建议
在 MT7925 (USB ID 0e8d:e025) 硬件上测试 WMT FUNC_CTRL 命令的发送和响应处理，验证设备初始化流程完成后蓝牙功能正常可用；在没有该硬件的环境下，可通过编写内核模块测试桩模拟数据路径中 skb_pull_data 返回 NULL 的条件，验证函数返回 0 且调用方流程正确继续执行。

---

## PCA-0002: 错误/异常行为变化 (ERROR_EXCEPTION_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.90
- **影响接口**: btmtk_usb_hci_wmt_sync (EXPORT_SYMBOL_GPL)
- **旧代码位置**: drivers/bluetooth/btmtk.c:681-682
- **新代码位置**: drivers/bluetooth/btmtk.c:682-683
- **类型**: ERROR_EXCEPTION_CHANGE

### 变更前行为
当 WMT FUNC_CTRL 事件不包含 status 字段时，函数将短事件视为错误条件，设置 err = -EINVAL 并终止处理。调用方收到错误返回值后打印错误日志并中止设备设置/关闭流程。

### 变更后行为
当 WMT FUNC_CTRL 事件不包含 status 字段时，函数不再将短事件视为错误，而是将其解释为 BTMTK_WMT_ON_UNDONE（操作未完成但可继续），正常返回 0。调用方不会收到错误信号，设备设置/关闭流程继续执行。

### 兼容性影响
从信号语义来看，-EINVAL 返回值是调用方唯一的错误指示。补丁将某个意外但存在的硬件行为从错误条件重新分类为正常条件。这改变了该函数的错误模型：过去的 -EINVAL 表示 '无效输入，不应继续'，现在对于特定设备返回的短事件来说则变为 '可以继续'。如果其他 MediaTek 设备在正常操作中也发送短 FUNC_CTRL 事件，该变化将导致原本被正确中止的设置流程在数据不足的情况下继续执行。

### 证据
```c
// drivers/bluetooth/btmtk.c:679-694 (补丁后 — 短事件处理)
	case BTMTK_WMT_FUNC_CTRL:
		if (!skb_pull_data(data->evt_skb,
				   sizeof(wmt_evt_funcc->status))) {
			status = BTMTK_WMT_ON_UNDONE;
			break;
		}
		...
```

```c
// drivers/bluetooth/btmtk.c:704-712 (返回路径)
	if (wmt_params->status)
		*wmt_params->status = status;

err_free_skb:
	kfree_skb(data->evt_skb);
	data->evt_skb = NULL;
err_free_wc:
	kfree(wc);
	return err;
```

### 静态调用链
(未启用调用链分析)

### 复核建议
建议确认是否只有特定 MT7925 固件版本会发送短事件。如果是为了修复与某个已知固件版本的互操作性问题，该变更是安全且有意的。如果未来其他 MediaTek 设备固件版本的短事件具有不同的语义（例如确实应该返回 -EINVAL），则需要增加对设备/固件版本的判断。

### 测试建议
测试 FUNC_CTRL 短事件的边界条件：构造或模拟 skb 长度小于 sizeof(wmt_evt_funcc->status) 的情况，验证函数返回 0 且 *wmt_params->status（若非 NULL）被设置为 BTMTK_WMT_ON_UNDONE，而非早期的 -EINVAL 错误返回。可在 MediaTek 蓝牙设备设置和关闭流程中注入短事件并验证驱动行为正常。
