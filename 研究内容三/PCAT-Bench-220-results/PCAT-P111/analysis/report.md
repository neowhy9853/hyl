# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup
**基线**: 324f7af5655a48841a079ac761fedef2ab3d1180^ (ec7911a3)
**补丁**: 324f7af5655a48841a079ac761fedef2ab3d1180
**Profile**: c_project
**分析模式**: normal

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 2 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 副作用变化 (SIDE_EFFECT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.95
- **影响接口**: soup_session_send_message / soup_session_queue_message
- **旧代码位置**: libsoup/soup-session.c:845-851
- **新代码位置**: libsoup/soup-session.c:845-853
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
POST 请求遇到 HTTP 301 (Moved Permanently) 响应时不会被自动重定向。请求完成但不会跟随重定向。

### 变更后行为
POST 请求遇到 HTTP 301 响应时会被自动重定向——请求方法从 POST 改为 GET（POST 请求体被丢弃）。

### 兼容性影响
使用 libsoup 发送 POST 请求到返回 HTTP 301 的 URL 时，现在会观察到完全不同的行为：POST 被静默转换为 GET 请求并发送到重定向目标。依赖旧行为（不跟随 POST+301 重定向）的应用程序将被破坏——包括 POST 数据丢失和请求语义变化（非幂等到幂等转换）。

### 证据
```c
/* libsoup/soup-session.c:848-850 */
     !SOUP_METHOD_IS_SAFE (msg->method)) ||
    (msg->status_code == SOUP_STATUS_MOVED_PERMANENTLY &&
     msg->method == SOUP_METHOD_POST)) {
```

### 静态调用链
未生成（include_call_chain=false）。

### 复核建议
确认 POST 转 GET 的 301 重定向行为不违反 HTTP/1.1 规范（RFC 2616 10.3.2），并与常见 HTTP 客户端（浏览器、curl、wget）行为一致。注意 libsoup 版本中同时存在 SOUP_MESSAGE_NO_REDIRECT 标志可作为应用的退路。

### 测试建议
验证 POST+301 自动重定向为 GET 的行为正确，确保重定向目标收到 GET 请求。同时验证 POST+307 (Temporary Redirect) 不跟随重定向（因为 307 必须保持原 HTTP 方法），确保不存在回归。关注 soup-session.c:859 的 else-if 分支中 SOUP_STATUS_MOVED_PERMANENTLY 仍存在，需确认 GET+301 的正常重定向未受影响。
