# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux
**基线**: HEAD (1229e2e57a5c2980ccd457b9b53ea0eed5a22ab3)
**补丁**: ba760c38b38b4fc5377f30bea492deba5f17df60
**Profile**: kernel_6_6

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 输入契约变更 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: MGMT_OP_ADD_EXT_ADV_DATA (Bluetooth MGMT 协议命令)
- **旧代码位置**: net/bluetooth/mgmt.c:9147-9148
- **新代码位置**: net/bluetooth/mgmt.c:9147-9149
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为

MGMT_OP_ADD_EXT_ADV_DATA 要求传入的 `data_len` 必须精确等于 `struct_size(cp, data, cp->adv_data_len + cp->scan_rsp_len)`，即使用精确长度匹配。如果 bluetoothd 发送了额外字节（如因自身 bug 导致多余尾部数据），内核会以 `MGMT_STATUS_INVALID_PARAMS` 拒绝命令。

### 变更后行为

MGMT_OP_ADD_EXT_ADV_DATA 仅检查 `expected_len > data_len`，即仅在期望长度大于实际数据长度（会导致越界访问）时拒绝。如果 `data_len` 大于 `expected_len`（存在额外尾部字节），多余字节被静默忽略，命令正常继续执行。

### 兼容性影响

内核 MGMT 协议对长度校验从严格精确匹配放宽为上限检查。之前由于内核提交 `d3f7d17960ed` 引入的严格长度校验导致与带有尾部多余字节的 bluetoothd 不兼容；本补丁将校验放宽，使得 bluetoothd 发送的带有额外字节的 `MGMT_OP_ADD_EXT_ADV_DATA` 命令可以正常处理，恢复与旧版本 bluetoothd 的向后兼容性。

### 证据

```diff
-	expected_len = struct_size(cp, data, cp->adv_data_len + cp->scan_rsp_len);
-	if (expected_len != data_len)
+	expected_len = struct_size(cp, data, cp->adv_data_len +
+				   cp->scan_rsp_len);
+	if (expected_len > data_len)
```

MGMT 命令表注册（net/bluetooth/mgmt.c:9534-9535）：
```c
	{ add_ext_adv_data,        MGMT_ADD_EXT_ADV_DATA_SIZE,
						HCI_MGMT_VAR_LEN },
```

### 静态调用链

```
MGMT_OP_ADD_EXT_ADV_DATA handler table dispatch -> add_ext_adv_data
```

### 复核建议

验证 bluetoothd 发送 MGMT_OP_ADD_EXT_ADV_DATA 时是否确实带有额外字节，确认旧版 bluetoothd 在新内核上正常工作。

### 测试建议

使用 bluetoothd 或模拟 MGMT 客户端发送 MGMT_OP_ADD_EXT_ADV_DATA 命令：
1. `data_len` 精确匹配时正常执行
2. `data_len` 带有少量额外字节时不再返回 `MGMT_STATUS_INVALID_PARAMS`，而是正常处理
3. `data_len` 小于 `expected_len` 时（越界风险）仍应返回 `MGMT_STATUS_INVALID_PARAMS`

建议同时验证 `hci_cmd_sync_queue` 异步路径通过 `add_ext_adv_data_sync` 和 `add_ext_adv_data_complete` 的完整生命周期。
