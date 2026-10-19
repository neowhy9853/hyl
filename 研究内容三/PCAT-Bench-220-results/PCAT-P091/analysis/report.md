# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: efbecbbb465c99ed608b06d72fa1982122382d00^ (5005a206)
**补丁**: efbecbbb465c99ed608b06d72fa1982122382d00
**Profile**: golang
**补丁标题**: crypto/tls: add LocalCertificate to ConnectionState
**修复 issues**: #24673

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 8 |
| 候选变更 | 9 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 副作用变更 — ConnectionState 新增 LocalCertificate 字段

- **测试优先级**: MEDIUM
- **置信度**: 0.95
- **影响接口**: crypto/tls.ConnectionState.LocalCertificate
- **旧代码位置**: src/crypto/tls/common.go:325-330
- **新代码位置**: src/crypto/tls/common.go:325-335
- **类型**: SIDE_EFFECT_CHANGE
- **影响面**: go_exported_api, stdlib

### 变更前行为

`ConnectionState` 结构体不包含 `LocalCertificate` 字段。调用者通过 `Conn.ConnectionState()` 获取连接状态后，无法获知本端在 TLS 握手过程中向对端出示了哪个证书链。

### 变更后行为

`ConnectionState` 新增公开导出字段 `LocalCertificate [][]byte`。TLS 握手期间（TLS 1.0—1.3，客户端与服务端双向）会将本端向对端出示的证书链（DER 编码）记录到该字段。该字段仅在非恢复连接（DidResume 为 false）时填充；恢复连接中 `LocalCertificate` 为 nil。

该变更涉及的代码路径：
- `src/crypto/tls/handshake_client.go:731` — TLS 1.2 客户端全握手
- `src/crypto/tls/handshake_client_tls13.go:759` — TLS 1.3 客户端证书发送
- `src/crypto/tls/handshake_server.go:283` — TLS 1.2 服务端握手处理
- `src/crypto/tls/handshake_server_tls13.go:496` — TLS 1.3 服务端证书挑选

### 兼容性影响

`crypto/tls.ConnectionState` 是 Go 标准库公开导出结构体。新增字段 `LocalCertificate` 改变了结构体布局，并使 TLS 握手产生新的外部可观察副作用。该变更属于纯增量变更（pure additive change），不影响既有字段语义，旧代码编译和执行均不受影响，但与之前版本相比公开 API surface 发生了变化。

### 证据

```go
// src/crypto/tls/common.go:325-335
	// HelloRetryRequest indicates whether we sent a HelloRetryRequest if we
	// are a server, or if we received a HelloRetryRequest if we are a client.
	HelloRetryRequest bool

	// LocalCertificate is the certificate chain presented to the peer, if any,
	// during the handshake. This field is only populated for connections which
	// are not resumed (DidResume is false).
	LocalCertificate [][]byte

	// ekm is a closure exposed via ExportKeyingMaterial.
	ekm func(label string, context []byte, length int) ([]byte, error)
```

```go
// src/crypto/tls/conn.go:1622-1629
	state.PeerCertificates = c.peerCertificates
	state.LocalCertificate = c.localCertificate
	state.VerifiedChains = c.verifiedChains
	state.SignedCertificateTimestamps = c.scts
	state.OCSPResponse = c.ocspResponse
```

### 复核建议

无需人工复核。纯增量 API 添加，与 Go 1 兼容性承诺一致。

### 测试建议

验证 `ConnectionState.LocalCertificate` 在以下场景均正确填充：
- TLS 1.0 / 1.1 / 1.2 / 1.3 各版本
- 客户端侧与服务器侧
- 通过 `Config.Certificates` 直接配置与通过 `Config.GetCertificate`/`Config.GetClientCertificate` 回调两种方式
- 验证恢复连接（DidResume=true）时 `LocalCertificate` 为 nil

补丁中已包含覆盖以上场景的测试 (`TestLocalCertificate`, `TestLocalCertificateResumption`)。

---

*分析产物目录: /data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P031/*
*Worktree 状态: available*
