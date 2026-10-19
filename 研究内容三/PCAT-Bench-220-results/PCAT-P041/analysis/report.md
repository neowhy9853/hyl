# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/glib
**基线**: 91adfd09b
**补丁**: 407349aa255a5c2b49caa52847aca1b8311c98b2
**Profile**: glib2

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 9 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 输入契约变更 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.75
- **影响接口**: `_g_dbus_auth_run_server` (reachable via GDBusServer/GDBusConnection public API)
- **旧代码位置**: gio/gdbusauth.c:314-324
- **新代码位置**: gio/gdbusauth.c:344-365
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为
读取D-Bus认证行时没有长度限制，客户端可以发送任意长度的行，服务器会一直读取直到收到\r\n。内存消耗不受控，存在OOM风险。

### 变更后行为
新增max_line_length参数和长度检查：当读取行超过max_line_length+2字节时，立即停止读取，设置G_IO_ERROR_FAILED并返回NULL，拒绝该连接。

### 兼容性影响
GDBusServer/GDBusConnection认证过程中对客户端输入增加了行长度限制。发送过长的AUTH/DATA/BEGIN行的客户端连接会被拒绝（errno: G_IO_ERROR_FAILED）。正常D-Bus客户端行为不受影响，但之前被接受的非标准/恶意超长输入现在被拒绝。

### 证据
```c
g_assert (max_line_length <= SIZE_MAX - 2);
...
if (str->len >= max_line_length + 2  /* allow for \r\n */)
{
  g_set_error_literal (error,
                       G_IO_ERROR,
                       G_IO_ERROR_FAILED,
                       _("Malformed D-Bus authentication line"));
  goto fail;
}
```

### 静态调用链
未生成

### 复核建议
确认MAX_DATA_PAYLOAD_LENGTH_BYTES=4096对于所有使用场景是否足够。检查是否有已知的D-Bus扩展机制需要更长的认证行。

### 测试建议
运行gio/tests/gdbus-auth.c中的test_auth_server_read_limit测试用例验证超长行被拒绝。建议额外验证正常长度（边界附近）的认证行能正常通过。
