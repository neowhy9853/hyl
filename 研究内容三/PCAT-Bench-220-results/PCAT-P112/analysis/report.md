# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup
**基线**: becb3a0ab8aa986f829efb77a52d53e75419c413~1 (21e5e79b)
**补丁**: becb3a0ab8aa986f829efb77a52d53e75419c413
**Profile**: libsoup
**Commit Message**: Don't crash when a request is redirected to an invalid/non-http URI

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 6 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 输入契约变更 — HTTP 重定向 URL 合法性检查收紧

- **测试优先级**: HIGH
- **置信度**: 0.85
- **影响接口**: redirect_handler (SoupSession redirect pipeline)
- **旧代码位置**: libsoup/soup-session.c:887-893
- **新代码位置**: libsoup/soup-session.c:887-893
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为
当 HTTP 重定向的目标 Location header 指向非 HTTP URI（如 about:blank）时，soup_uri_new_with_base() 可能返回一个非 NULL 但没有 host 字段的 SoupURI 对象。旧代码仅检查 !new_uri，因此会通过该检查，继续执行 soup_message_set_uri 和 soup_session_requeue_message，最终可能在后续处理中因访问 NULL host 而崩溃（segfault）。

### 变更后行为
新代码增加了 !new_uri->host 检查，当 soup_uri_new_with_base() 返回的 URI 没有 host 字段时（例如 about:blank），会设置消息状态为 SOUP_STATUS_MALFORMED 并返回，拒绝执行该重定向。调用方的 SoupSession 将收到一个 MALFORMED 状态的消息，而不是崩溃。

### 兼容性影响
这是一项输入契约收紧（input contract tightening）变更。对于合法的 HTTP/HTTPS 重定向 URL，行为不变。对于非法的、无法解析出 host 的重定向 URL（如 about:blank、data: URI 等），行为从"未定义（可能导致崩溃）"变为"返回 SOUP_STATUS_MALFORMED 错误"。依赖 SoupSession 自动处理重定向的应用程序现在可以观察到新的错误状态码，而不是之前的崩溃行为。这是一个 bug 修复，将未定义行为转为明确定义的错误处理。

### 证据
```c
	/* Location is supposed to be an absolute URI, but some sites
	 * are lame, so we use soup_uri_new_with_base().
	 */
	new_uri = soup_uri_new_with_base (soup_message_get_uri (msg), new_loc);
	if (!new_uri || !new_uri->host) {
		soup_message_set_status_full (msg,
					      SOUP_STATUS_MALFORMED,
					      "Invalid Redirect URL");
		return;
	}
```

### 为何不是纯内部变更
虽然 redirect_handler 是一个 static 函数，但它是 SoupSession 内部重定向管道的核心部分。它通过 g_signal_connect 连接到 SoupMessage 的 restarted 信号，影响所有通过 SoupSession 发送 HTTP 请求的客户端代码。外部调用者通过 soup_session_send_message() API 触发请求后，自动重定向的行为由该函数控制，因此其行为变化对库用户是可观察的。

### 不确定因素
需要确认 soup_uri_new_with_base() 对于非 HTTP scheme（如 about:、data:、javascript:）的具体返回值行为。可能存在某些 non-HTTP URI scheme 返回的 URI 有 host 字段但未被 HTTP 层面正确处理的情况。此外，soup_uri_host_hash 和 soup_uri_host_equal 中添加的 g_return_val_if_fail 防御性检查在 release 构建中可能被 G_DISABLE_CHECKS 编译掉。

### 复核建议
建议验证以下场景：1) 使用不同类型的非 HTTP scheme（about:、data:、ftp:、file:、javascript:）作为重定向目标，确认行为一致；2) 确认 SOUP_STATUS_MALFORMED 被正确传递给 SoupSession 调用者的 SoupMessage 回调。

### 测试建议
建议执行以下测试：1) 使用 SoupSession 发送请求到返回 Location: about:blank 的重定向服务器，验证收到 SOUP_STATUS_MALFORMED 而非崩溃；2) 构造 HTTP 服务器返回各种非法重定向 URL（相对路径、空字符串、data: URI、非标准 scheme），验证 SoupSession 的行为一致性。

---

## 未纳入最终 findings 的候选说明

以下候选经分析判定不构成兼容性变更，留存在 candidates.json 中：

### HUNK-0002 / HUNK-0003: soup_uri_host_hash / soup_uri_host_equal (soup-uri.c)
这两个函数是公共 API（在 soup-uri.h 中声明），但变更仅为添加 g_return_val_if_fail 防御性 NULL 检查。对于传入合法 SoupURI 的调用者行为不变；对于非法 NULL 输入，行为从崩溃变为返回默认值。由于：
1. API 文档要求传入有效的 SoupURI 指针
2. g_return_val_if_fail 在 release 构建中可能被 G_DISABLE_CHECKS 禁用
3. 纯防御性变更，不改变合法输入路径的语义

判定为不构成兼容性变更。

### HUNK-0004 / HUNK-0005 / HUNK-0006: tests/redirect-test.c
测试文件变更，添加了 `final_status` 字段和新的 bad-no-host 测试用例。不涉及公共 API。

---

**分析产物目录**: /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P052/
**补丁后源码 worktree**: /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P052/_worktrees/patched (available)
