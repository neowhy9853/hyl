# PCA 兼容性变更分析报告

**仓库**: https://github.com/GNOME/libsoup
**基线**: a6d1d7aa49c264efc9d520ffe555299b7a92466e
**补丁**: a8982b0376885b5007b5c6bbbfedfde7bb941a54
**Profile**: c_project
**提交者**: Carlos Garcia Campos
**Bug**: https://bugzilla.gnome.org/show_bug.cgi?id=775882

## 概述

此补丁修复了 commit efcb377 引入的回归问题：`update_authorization_header()` 无条件移除 Authorization 头，
导致用户手动设置的 Authorization 头被忽略，在没有缓存凭证时认证失败。
补丁在 `libsoup/soup-auth-manager.c` 中修改 2 行逻辑，在 `tests/auth-test.c` 中新增 78 行测试代码。

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 4 |
| 兼容性变更 | 2 |
| 高优先级测试 | 1 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 条件性 Authorization 头移除

- **测试优先级**: HIGH
- **置信度**: 0.90
- **影响接口**: update_authorization_header (libsoup/soup-auth-manager.c)
- **旧代码位置**: libsoup/soup-auth-manager.c:446-452
- **新代码位置**: libsoup/soup-auth-manager.c:446-454
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
Authorization/Proxy-Authorization 头被无条件地从每条消息中移除，包括那些带有用户手动设置的 Authorization 头的消息。
没有缓存 auth 的消息其手动设置的 Authorization 头会被删除，导致在设置了 `SOUP_MESSAGE_DO_NOT_USE_AUTH_CACHE` 标志时认证失败。

### 变更后行为
Authorization/Proxy-Authorization 头仅在 `soup_message_get_auth(msg)` 返回非 NULL（即消息已有来自缓存凭证的关联 SoupAuth）时才被移除。
没有缓存 auth 的消息中，用户手动设置的 Authorization 头会被保留，确保手动认证可以成功。

### 兼容性影响
此变更修复了导致用户手动设置 Authorization 头被忽略的回归问题。依赖旧行为的消费者（原本预期 header 总是被移除）可能观察到差异，但此类消费者在旧版本中本身也面临认证失败的问题。

### 证据
```c
-	soup_message_headers_remove (msg->request_headers, authorization_header);
+	if (soup_message_get_auth (msg))
+		soup_message_headers_remove (msg->request_headers, authorization_header);
```

函数通过以下公共调用链可达：
- `soup_session_send_message()` → `request_queued` 信号 → `soup_auth_manager_request_queued()` → `auth_msg_starting()` → `update_authorization_header()`
- `auth_got_body()` / `proxy_auth_got_body()` → `update_authorization_header()`

### 测试建议
使用手动 Authorization 头的请求进行回归测试：在已认证 session 中清除 credentials 缓存后，用 `soup_message_headers_replace` 设置 Authorization 头并设置 `SOUP_MESSAGE_DO_NOT_USE_AUTH_CACHE` 标志，发送消息后验证 Authorization 头被保留且服务器正确响应。此场景已被 commit 中新增的测试覆盖。

---

## PCA-0002: Authorization 头 append → replace

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: update_authorization_header (libsoup/soup-auth-manager.c)
- **旧代码位置**: libsoup/soup-auth-manager.c:454-460
- **新代码位置**: libsoup/soup-auth-manager.c:456-462
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
使用 `soup_message_headers_append()` 将认证 token 追加到 Authorization 请求头。如果该头已存在值（例如用户手动设置的），会导致发送重复的 Authorization 头。

### 变更后行为
使用 `soup_message_headers_replace()` 将 Authorization 请求头中的任何现有值替换为新的认证 token，确保只有一个 Authorization 头被发送。

### 兼容性影响
从 append 到 replace 的语义变化影响 HTTP 请求头的最终构造。旧行为可能产生重复的 Authorization 头（某些 HTTP 中间件处理方式可能与预期不同），新行为保证单一值。在极端场景下，依赖旧行为发送特定重复 header 的 HTTP 服务器或中间件可能观察到差异。

### 证据
```c
-	soup_message_headers_append (msg->request_headers, authorization_header, token);
+	soup_message_headers_replace (msg->request_headers, authorization_header, token);
```

### 测试建议
针对同一 message 先后设置不同的 Authorization 值并触发认证刷新，验证最终发送的 HTTP 请求中 Authorization 头为单一最新值而非包含旧值和新值的重复头。

---
