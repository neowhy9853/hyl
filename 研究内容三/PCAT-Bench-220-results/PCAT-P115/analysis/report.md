# PCA 兼容性变更分析报告

**仓库**: https://github.com/GNOME/libsoup
**基线**: 4e0fe0f16215b2f481356e879bc05661862ae4ad (71ca70a0f62c 的父提交)
**补丁**: 71ca70a0f62cfc30dfacfd2ee0952a86e2e64055
**Profile**: libsoup
**分析模式**: normal

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 7 |
| 兼容性变更 | 3 |
| 高优先级测试 | 3 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 补丁概述

**主题**: Enable ssl-use-system-ca-file on deprecated Sync and Async sessions

该补丁将 `priv->tlsdb_use_default = TRUE` 的设置从仅对 plain `SoupSession` 有效的 `if (type == SOUP_TYPE_SESSION)` 代码块内移出，使得该设置对通过 `soup_session_constructor` 构造的所有 session 类型均生效，包括已废弃但仍在广泛使用的 `SoupSessionAsync` 和 `SoupSessionSync`。补丁作者在提交信息中明确表示这是一次有意的兼容性破坏（"This is a break in behavior however the security concerns are important"），目的是为所有仍在使用旧 API 的下游项目提供基础级别的 TLS 安全性。

---

## PCA-0001: TLS 系统 CA 默认启用的副作用变更

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: soup_session_constructor (SoupSession GObject 构造器)
- **旧代码位置**: libsoup/soup-session.c:293-299
- **新代码位置**: libsoup/soup-session.c:279-280
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
`priv->tlsdb_use_default = TRUE` 仅在 `type == SOUP_TYPE_SESSION`（plain SoupSession）时执行。`SoupSessionAsync` 和 `SoupSessionSync` 子类在构造时不设置 `tlsdb_use_default`，因此其 `ssl-use-system-ca-file` 属性默认值为 `FALSE`，`tls-database` 属性默认值为 `NULL`。这意味着这些子类默认不会使用系统 CA 数据库验证 TLS 证书，HTTPS 连接即使遇到自签名或非公共 CA 签发的证书也会成功。

### 变更后行为
`priv->tlsdb_use_default = TRUE` 被移到 `if (type == SOUP_TYPE_SESSION)` 条件判断之前，对所有 session 类型均生效。所有 session 类型现在默认启用系统 CA 数据库进行 TLS 证书验证，`ssl-use-system-ca-file` 默认值为 `TRUE`，`tls-database` 默认指向系统 CA 数据库。

### 兼容性影响
任何使用 `SoupSessionAsync` 或 `SoupSessionSync` 且依赖旧默认行为（不验证证书）的应用，升级后 HTTPS 连接将默认启用证书验证。若目标服务器使用自签名证书或非公共 CA 签发的证书，连接将失败。影响面广泛：所有未显式配置 TLS 数据库的 `SoupSessionAsync`/`SoupSessionSync` 用户都将受到影响。

### 证据
```c
// libsoup/soup-session.c:272-280 (补丁后)
	GObject *object;
	SoupSession *session;
	SoupSessionPrivate *priv;

	object = G_OBJECT_CLASS (soup_session_parent_class)->constructor (...);
	session = SOUP_SESSION (object);
	priv = soup_session_get_instance_private (session);

	priv->tlsdb_use_default = TRUE;  // 新增：对所有 session 类型生效

	/* If this is a "plain" SoupSession, fix up the default ... */
	if (type == SOUP_TYPE_SESSION) {
		// 原 priv->tlsdb_use_default = TRUE 已从此代码块移除
```

### 复核建议
确认下游应用中是否有代码显式依赖 `SoupSessionAsync`/`SoupSessionSync` 的旧默认 TLS 行为。

### 测试建议
分别创建 `SoupSessionAsync` 和 `SoupSessionSync` 实例，不设置任何 TLS 相关属性，读取 `ssl-use-system-ca-file` 和 `tls-database` 属性，验证默认值均为启用状态。测试使用自签名证书的 HTTPS 连接是否正确失败。

---

## PCA-0002: HTTPS 连接错误状态变更

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: SoupSession (ssl-use-system-ca-file / tls-database GObject 属性)
- **旧代码位置**: libsoup/soup-session.c:293-299
- **新代码位置**: libsoup/soup-session.c:279-280
- **类型**: ERROR_EXCEPTION_CHANGE

### 变更前行为
使用 `SoupSessionAsync` 或 `SoupSessionSync` 创建的默认 session 中，TLS 证书验证默认关闭。应用可以连接任意 HTTPS 服务器而不会收到 SSL 验证失败错误。`SoupMessage` 的状态码不会出现 `SOUP_STATUS_SSL_FAILED`（除非用户显式启用了证书验证）。

### 变更后行为
所有 session 类型默认启用 TLS 证书验证。连接使用自签名证书或非系统 CA 信任链签发的 HTTPS 服务器时，`SoupMessage` 将收到 `SOUP_STATUS_SSL_FAILED` 状态码，连接将失败。

### 兼容性影响
用户可见的错误行为发生根本性变化：之前成功的 HTTPS 连接现在会失败。下游应用的消息处理回调中原本不会遇到的 `SOUP_STATUS_SSL_FAILED` 错误现在将成为可能。任何未处理此错误状态的代码路径可能产生未预期的行为。

### 证据
```c
// libsoup/soup-session.c:3480-3486 (property 文档)
 * Normally, if #SoupSession:tls-database is set (including if
 * it was set via #SoupSession:ssl-use-system-ca-file or
 * #SoupSession:ssl-ca-file), then libsoup will reject any
 * certificate that is invalid (ie, expired) or that is not
 * signed by one of the given CA certificates, and the
 * #SoupMessage will fail with the status
 * %SOUP_STATUS_SSL_FAILED.
```

### 复核建议
建议下游应用维护者检查所有使用 `SoupSessionAsync`/`SoupSessionSync` 的代码路径，确认是否正确处理了 `SOUP_STATUS_SSL_FAILED` 错误。

### 测试建议
使用默认构造的 `SoupSessionAsync` 和 `SoupSessionSync` 向自签名证书 HTTPS 端点发起请求，验证返回 `SOUP_STATUS_SSL_FAILED`。对比补丁前后的行为差异。

---

## PCA-0003: GObject 属性默认值契约变更

- **测试优先级**: HIGH
- **置信度**: 0.90
- **影响接口**: SoupSession:ssl-use-system-ca-file / SoupSession:tls-database
- **旧代码位置**: libsoup/soup-session.c:293-299
- **新代码位置**: libsoup/soup-session.c:279-280
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为
`SoupSessionAsync` 和 `SoupSessionSync` 构造完成后，`g_object_get(session, "ssl-use-system-ca-file", ...)` 返回 `FALSE`；`g_object_get(session, "tls-database", ...)` 返回 `NULL`。

### 变更后行为
所有 session 类型构造完成后，`ssl-use-system-ca-file` 默认返回 `TRUE`，`tls-database` 默认指向系统 CA 数据库对象（非 NULL）。

### 兼容性影响
GObject 属性的默认值契约发生了不兼容变化。任何在构造后读取这些属性并根据其值决定后续行为的代码都会受到影响。开发者不能再依赖 `tls-database == NULL` 作为判断是否需要配置 TLS 的条件。

### 证据
```c
// tests/no-ssl-test.c:75-76 (测试断言更新以反映新契约)
	soup_test_assert (use_system, "ssl-use-system-ca-file defaults to FALSE");
	soup_test_assert (tlsdb != NULL, "tls-database not set by default");
```

### 复核建议
检查下游应用中在 `SoupSessionAsync`/`SoupSessionSync` 构造后通过 `g_object_get` 读取这些属性的代码。

### 测试建议
构造 session 实例后立即通过 `g_object_get` 读取属性值，验证是否符合新默认值。

---

## 非兼容性候选说明

以下候选被保留在 `candidates.json` 中，但未确认为兼容性变更：

| Hunk | 文件 | 说明 |
|------|------|------|
| HUNK-0003 | libsoup/soup-session.c:3413-3422 | `ssl-use-system-ca-file` 属性的 GTK-Doc 注释更新，仅反映行为变更，非独立兼容性问题 |
| HUNK-0004 | libsoup/soup-session.c:3453-3459 | `tls-database` 属性的 GTK-Doc 注释更新，仅反映行为变更 |
| HUNK-0005 | tests/no-ssl-test.c:72-79 | 测试断言更新，仅反映预期行为变化 |
| HUNK-0006 | tests/ssl-test.c:174-183 | 测试断言更新，仅反映预期行为变化 |
| HUNK-0007 | tests/ssl-test.c:195-201 | `g_assert_true(tlsdb_changed)` → `g_assert_false(tlsdb_changed)`，反映 tls-database 默认已有值的事实 |
