# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/go
**基线**: 1c3a1bac8b14c866d70b330e0229e5555670f577~1
**补丁**: 1c3a1bac8b14c866d70b330e0229e5555670f577
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 7 |
| 候选变更 | 8 |
| 兼容性变更 | 3 |
| 高优先级测试 | 1 |
| 中优先级测试 | 1 |
| 低优先级测试 | 1 |

---

## PCA-0001: 配置/CLI 行为变更 — 代理环境变量优先级反转

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: ProxyFromEnvironment / DefaultTransport / DefaultClient
- **旧代码位置**: src/vendor/golang.org/x/net/http/httpproxy/proxy.go:112-114
- **新代码位置**: src/vendor/golang.org/x/net/http/httpproxy/proxy.go:93-95
- **类型**: CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为

`getEnvAny("HTTP_PROXY", "http_proxy")` 优先返回大写环境变量的值；`getEnvAny("HTTPS_PROXY", "https_proxy")` 优先返回大写环境变量的值；`getEnvAny("NO_PROXY", "no_proxy")` 优先返回大写环境变量的值。即大写形式优先级高于小写形式。

### 变更后行为

`getEnvAny("http_proxy", "HTTP_PROXY")` 优先返回小写环境变量的值；`getEnvAny("https_proxy", "HTTPS_PROXY")` 优先返回小写环境变量的值；`getEnvAny("no_proxy", "NO_PROXY")` 优先返回小写环境变量的值。即小写形式优先级高于大写形式。

### 兼容性影响

当 `$HTTP_PROXY` 与 `$http_proxy` 同时设置且值不同时（如 CGI 环境中两者均可能被设置），旧版使用大写值，新版使用小写值，代理解析结果发生变化。该变更影响 `http.DefaultTransport`、`http.DefaultClient` 以及所有直接调用 `http.ProxyFromEnvironment` 的代码。根据 #79656 的文档说明，此变更旨在使 Go 的行为与业界惯例一致（小写形式优先）。

### 证据

```go
// 文件: src/vendor/golang.org/x/net/http/httpproxy/proxy.go
// 行号: 93-95 (新), 112-114 (旧)

// 新代码:
HTTPProxy:  getEnvAny("http_proxy", "HTTP_PROXY"),
HTTPSProxy: getEnvAny("https_proxy", "HTTPS_PROXY"),
NoProxy:    getEnvAny("no_proxy", "NO_PROXY"),

// 旧代码:
// HTTPProxy:  getEnvAny("HTTP_PROXY", "http_proxy"),
// HTTPSProxy: getEnvAny("HTTPS_PROXY", "https_proxy"),
// NoProxy:    getEnvAny("NO_PROXY", "no_proxy"),

// getEnvAny 的实现（同文件第 100-107 行）:
func getEnvAny(names ...string) string {
	for _, n := range names {
		if val := os.Getenv(n); val != "" {
			return val
		}
	}
	return ""
}
```

```go
// 文件: src/net/http/transport.go
// 行号: 1040-1044
// ProxyFromEnvironment 调用链最终到达 getEnvAny

func envProxyFunc() func(*url.URL) (*url.URL, error) {
	envProxyOnce.Do(func() {
		envProxyFuncValue = httpproxy.FromEnvironment().ProxyFunc()
	})
	return envProxyFuncValue
}
```

### 复核建议

建议审查 CGI 环境下的代理行为，因为 CGI 规范要求 `HTTP_PROXY` 必须设置为大写形式，同时某些 CGI 服务端可能也设置小写形式。

### 测试建议

测试应在设置 `HTTP_PROXY=http://up:8080` 和 `http_proxy=http://low:8080` 两种不同值的情况下，验证 Go HTTP 客户端实际使用小写值 `http://low:8080`。同理测试 `HTTPS_PROXY`/`https_proxy` 和 `NO_PROXY`/`no_proxy` 的组合。还需验证仅设置一种形式时行为不变。

---

## PCA-0002: 副作用变更 — Endpoint.Close 资源清理路径统一

- **测试优先级**: MEDIUM
- **置信度**: 0.90
- **影响接口**: Endpoint.Close
- **旧代码位置**: src/vendor/golang.org/x/net/quic/endpoint.go:149-153
- **新代码位置**: src/vendor/golang.org/x/net/quic/endpoint.go:149-156
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为

当 `Close()` 通过 `e.closec` 正常完成时（非超时路径），不调用 `conn.exit()` 清理连接，返回 `nil`。仅在 `ctx.Done()` 超时路径才调用 `conn.exit()` 并返回 `ctx.Err()`。

### 变更后行为

无论 `Close()` 通过 `e.closec` 正常完成还是 `ctx.Done()` 超时，始终对每个连接调用 `c.exit()` 进行清理，并始终返回 `ctx.Err()`（正常完成时 `ctx.Err()` 返回 `nil`，与原 `nil` 返回等价）。

### 兼容性影响

该变更修复了一个 bug：正常关闭路径未调用 `c.exit()` 进行连接清理。同时返回值从固定 `nil` 改为 `ctx.Err()`，当 context 未超时时 `ctx.Err()` 返回 `nil`，行为等价；但当 context 已被取消时，返回值从 `nil` 变更为非 `nil` 错误。对于依赖 `Close()` 返回 `nil` 判断关闭成功的调用方，此为可观察的行为变化。

### 证据

```go
// 文件: src/vendor/golang.org/x/net/quic/endpoint.go
// 行号: 149-156 (新)

select {
case <-e.closec:
case <-ctx.Done():
}
for _, c := range conns {
	c.exit()
}
return ctx.Err() // nil if context hasn't expired
```

### 复核建议

确认 Go 标准库内部所有 `Endpoint.Close` 的调用方是否依赖返回 `nil` 来判断关闭成功，以及是否已正确处理 `ctx.Err()` 返回值。

### 测试建议

测试 `Endpoint.Close` 在正常关闭（context 未取消）和 context 已取消两种场景下的 conn exit 调用和返回值。验证正常关闭时返回 `nil`（`ctx.Err()`），并确认所有连接都已清理。

---

## PCA-0003: 输入契约变更 — Config.Clone nil receiver 安全处理

- **测试优先级**: LOW
- **置信度**: 0.85
- **影响接口**: Config.Clone
- **旧代码位置**: src/vendor/golang.org/x/net/quic/config.go:110-115
- **新代码位置**: src/vendor/golang.org/x/net/quic/config.go:112-118
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为

调用 `(*Config)(nil).Clone()` 时，执行 `n := *c` 会解引用 nil 指针导致 panic。

### 变更后行为

调用 `(*Config)(nil).Clone()` 时，先检查 `c == nil` 并安全返回 `nil`，不会 panic。

### 兼容性影响

输入契约放宽：原先对 nil receiver 的 `Clone()` 调用会 panic，现在安全返回 nil。这是一个向后兼容的变更——所有此前正常工作的代码继续正常工作，同时新增了对 nil receiver 的安全处理。属于 additive behavior，不破坏现有正确调用。

### 证据

```go
// 文件: src/vendor/golang.org/x/net/quic/config.go
// 行号: 112-118 (新)

func (c *Config) Clone() *Config {
	if c == nil {
		return nil
	}
	n := *c
	return &n
}
```

### 复核建议

无需人工复核，此变更是标准的安全加固。

### 测试建议

测试 `Config.Clone` 在 nil receiver 和非 nil receiver 场景下的行为，确认 nil receiver 返回 nil 且不 panic。
