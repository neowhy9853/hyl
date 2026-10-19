# PCA 兼容性变更分析报告

**仓库**: https://github.com/GNOME/libsoup
**基线**: 824a60e614bb7ea57f59c09b819a8f1dcb2f5b11^ (71aed93e)
**补丁**: 824a60e614bb7ea57f59c09b819a8f1dcb2f5b11
**Profile**: c_project

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 2 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: SIDE_EFFECT_CHANGE - soup_cache_send_response 不再自动添加 Age 头

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: soup_cache_send_response (exported_function, C)
- **旧代码位置**: libsoup/soup-cache.c:704-716
- **新代码位置**: libsoup/soup-cache.c:703-708
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
调用 soup_cache_send_response 从缓存发送响应时，自动计算当前 Age 值并通过 soup_message_headers_replace 将 "Age" 头添加到 msg->response_headers 中。所有缓存响应（包括重新验证后的一手响应）都包含 Age 头。

### 变更后行为
调用 soup_cache_send_response 从缓存发送响应时，不再自动添加 "Age" 头到响应消息中。缓存响应不再携带 Age 头信息。

### 兼容性影响
该变更移除了 soup_cache_send_response 中的自动 Age 头添加逻辑。HTTP Age 头曾被 RFC 2616 强制要求用于缓存响应，但 RFC 7234 已移除此要求。旧行为对通过重新验证获得的一手响应也错误地添加了 Age 头，导致下游客户端进行不必要的条件请求。变更后 HTTP 响应头发生变化，依赖 Age 头进行缓存新鲜度计算的下游 HTTP 客户端或中间代理可能受到影响。soup-session.c 在两个位置调用此函数（第 3006 行和第 3064 行），意味着所有通过 libsoup 缓存层的 HTTP 响应都会受此变更影响。

### 证据
```diff
-	/* Add 'Age' header with the current age */
-	current_age = g_strdup_printf ("%d", soup_cache_entry_get_current_age (entry));
-	soup_message_headers_replace (msg->response_headers,
-				      "Age",
-				      current_age);
-	g_free (current_age);
```

函数声明（libsoup/cache/soup-cache-private.h:38-39）：
```c
GInputStream      *soup_cache_send_response                   (SoupCache   *cache,
							 SoupMessage *msg);
```

调用方1（libsoup/soup-session.c:3006）：
```c
		stream = soup_cache_send_response (data->cache, data->item->msg);
```

调用方2（libsoup/soup-session.c:3064）：
```c
		stream = soup_cache_send_response (cache, item->msg);
```

### 复核建议
确认 soup_cache_entry_get_current_age 仍然是可访问的 API 函数，以便需要 Age 头的调用者可以自行获取该值。检查是否有已安装的公共头文件暴露了该函数。

### 测试建议
测试缓存响应的 HTTP 头输出：使用 libsoup 缓存功能发送请求，验证 1) 缓存命中时响应中不再包含 Age 头；2) soup_cache_entry_get_current_age 仍然可被调用以获取当前 Age 值。测试 soup-session.c 中两处 soup_cache_send_response 调用路径（第 3006 行正常路径，第 3064 行条件缓存路径）的响应头完整集合。
