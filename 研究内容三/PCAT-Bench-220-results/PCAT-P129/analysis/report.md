# PCA 兼容性变更分析报告

**仓库**: https://github.com/apache/httpd
**基线**: 8ffa19a1f7eb03b156e6bdbda65b3d2a2de9dfe8
**补丁**: dee1eb37d787d34cb37df7eab535240e1774293a
**Profile**: httpd

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 4 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: SSL_CTX_set_dh_auto (通过 ssl_init_server_certs)
- **代码位置**: modules/ssl/ssl_engine_init.c:1622-1628 (新)
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为

当 certfile 存在且不为 engine ID 时（`if (certfile && !modssl_is_engine_id(certfile))` 为 true），即使无法从证书文件中加载 DH 参数（局部变量 `done` 保持为 0），`else` 分支匹配的是外层 `if` 条件，导致 `SSL_CTX_set_dh_auto()` 不会被调用，DH 密码套件被实际禁用。只有当 certfile 不存在或是 engine ID 时，`else` 才会执行并启用 DH 自动选择。

### 变更后行为

将局部变量 `done` 替换为函数作用域的 `custom_dh_done`，并将 `else` 改为独立的 `if (!custom_dh_done)` 检查。现在无论 certfile 是否存在或是否能从中读取 DH 参数，只要没有成功加载自定义 DH 参数（custom_dh_done == 0），`SSL_CTX_set_dh_auto()` 都会被调用以启用 DH 参数自动选择，恢复 DH 密码套件功能。

### 兼容性影响

该变更修复了一个回归缺陷（PR 68863），恢复了 TLS 握手期间的 DH 密码套件自动协商功能。虽然修改的是 `static` 函数，但其副作用——通过 `SSL_CTX_set_dh_auto()` 修改 SSL_CTX 的 DH 参数协商行为——直接影响所有 HTTPS 客户端的 TLS 握手过程。SSL/TLS 密码套件协商是公开的安全协议接口，任何客户端的连接行为都可能受此变更影响。

### 证据

**补丁后代码（DH 自动选择逻辑）：**
```c
// modules/ssl/ssl_engine_init.c:1622-1628
#if !MODSSL_USE_OPENSSL_PRE_1_1_API
    if (!custom_dh_done) {
        /* If no parameter is manually configured, enable auto
         * selection. */
        SSL_CTX_set_dh_auto(mctx->ssl_ctx, 1);
    }
#endif
```

**补丁前代码（DH 自动选择逻辑）：**
```c
// modules/ssl/ssl_engine_init.c (before patch)
#if !MODSSL_USE_OPENSSL_PRE_1_1_API
    else {
        /* If no parameter is manually configured, enable auto
         * selection. */
        SSL_CTX_set_dh_auto(mctx->ssl_ctx, 1);
    }
#endif
```

**函数作用域新增变量：**
```c
// modules/ssl/ssl_engine_init.c:1418-1419
    EVP_PKEY *pkey;
    int custom_dh_done = 0;
```

**DH 参数加载位置的 `done` → `custom_dh_done` 替换：**
```c
// modules/ssl/ssl_engine_init.c:1594-1602
    if (certfile && !modssl_is_engine_id(certfile)) {
        int num_bits = 0;
        // ... OpenSSL < 3.0 branch ...
            custom_dh_done = 1;  // was: done = 1
        // ... OpenSSL >= 3.0 branch ...
                custom_dh_done = 1;  // was: done = 1
```

### 静态调用链

未生成（include_call_chain 未开启）。

### 复核建议

1. 确认 `SSL_CTX_set_dh_auto()` 在 OpenSSL < 1.1 版本下已被 `#if !MODSSL_USE_OPENSSL_PRE_1_1_API` 正确保护。
2. 验证在有 certfile 但无 DH 参数、无 certfile、certfile 为 engine ID 三种场景下 DH 参数设置行为。
3. 检查是否有配置显式设置了 DH 参数但仍因 `SSL_CTX_set_dh_auto` 被覆盖的边缘情况。

### 测试建议

1. 配置 SSL vhost 但不设置 DH 参数文件，验证 DH 密码套件在 TLS 握手中可用。
2. 在 certfile 中嵌入 DH 参数，验证自定义参数优先于 `SSL_CTX_set_dh_auto()` 的自动选择。
3. 使用 `openssl s_client -cipher 'DHE'` 连接并验证 DH 密码套件协商结果。
4. 检查服务器日志中 `Custom DH parameters` 日志输出是否按预期出现。

---
