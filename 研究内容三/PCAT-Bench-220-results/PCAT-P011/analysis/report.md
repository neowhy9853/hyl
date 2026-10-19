# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/dnsmasq
**基线**: 1eab169173fc4c8579a3db61186096fe117e6aca
**补丁**: 3a052d55fbfca49d8d435cdd2110fb2667594c61
**Profile**: dnsmasq

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 5 |
| 兼容性变更 | 2 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 1 |

---

## PCA-0001: 非 QUERY TCP 请求转发行为变更

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: tcp_request (daemon_handler)
- **旧代码位置**: src/forward.c:2568-2574
- **新代码位置**: src/forward.c:2570-2576
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
非 QUERY DNS TCP 请求（如 NOTIFY、UPDATE）在 m=0 且 ede=EDE_UNSET 时，即使 flags 已设为 F_RCODE（来自 OPCODE != QUERY 分支），仍会进入 forwarding 逻辑，导致这些请求被错误地转发到上游服务器。

### 变更后行为
非 QUERY DNS TCP 请求在 flags 设为 F_RCODE（非零）后，新增的 `!flags` 守卫条件阻止其进入 forwarding 逻辑。这些请求将收到 RCODE 拒绝响应，而不再被转发。

### 兼容性影响
向 dnsmasq 发送非 QUERY TCP 请求（NOTIFY、UPDATE 等）的 DNS 客户端将收到 RCODE 拒绝响应，而不是将请求转发到上游服务器。这恢复了 729c16a 之前回归的正确行为，但依赖错误转发行为的客户端将观察到不同响应。

### 证据
```c
      if (!flags && m == 0 && ede == EDE_UNSET)
	{
	  struct server *master;
	  int start;
```
```c
	  if (OPCODE(header) != QUERY)
	    {
	      log_query_mysockaddr((auth_dns ? F_NOERR : 0) |  F_QUERY | F_FORWARD | F_CONFIG, NULL, &peer_addr, NULL, OPCODE(header));
	      gotname = 0;
	      flags = F_RCODE;
	    }
```

### 静态调用链
（未启用）

### 复核建议
确认没有基础设施依赖 dnsmasq 将非 QUERY TCP 请求（NOTIFY、UPDATE）转发到上游服务器。

### 测试建议
向 dnsmasq 发送非 QUERY DNS 请求（如 DNS NOTIFY）并验证它们收到 RCODE 响应，而不是被转发。比较补丁前后的行为变化。

---

## PCA-0002: 非 QUERY TCP 请求获得 EDNS0 处理

- **测试优先级**: LOW
- **置信度**: 0.70
- **影响接口**: tcp_request (daemon_handler)
- **旧代码位置**: src/forward.c:2461-2466
- **新代码位置**: src/forward.c:2461-2475
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
add_edns0_config()、buffer memset() 和 query memcpy() 仅在 QUERY 处理分支内（OPCODE != QUERY 检查通过后）执行。非 QUERY TCP 请求不接收 EDNS0 OPT 记录处理，也不准备输出缓冲区。

### 变更后行为
add_edns0_config()、buffer memset() 和 query memcpy() 现在在 OPCODE 检查之前对所有 TCP 请求执行。非 QUERY TCP 请求现在也会在其 header 缓冲区中添加 EDNS0 OPT 记录，并准备输出缓冲区。

### 兼容性影响
非 QUERY 请求的 EDNS0 处理修改了内存中的数据包缓冲区（添加 OPT 记录）并准备了输出缓冲区。虽然非 QUERY 路径不使用这些修改进行 DNS 处理，但检查修改后缓冲区的日志或诊断可能会显示非 QUERY 请求的不同内容。

### 证据
```c
	  /* Add edns0 pheader to query */
	  size = add_edns0_config(header, size, ((unsigned char *) header) + daemon->edns_pktsz, &peer_addr, now, &cacheable);

	  /* Clear buffer to avoid risk of information disclosure. */
	  memset(bigbuff->iov_base, 0, bigbuff->iov_len);
	  /* Copy query into output buffer for local answering */
	  memcpy(out_header, header, size);
```

### 静态调用链
（未启用）

### 复核建议
验证 add_edns0_config() 处理非 QUERY 操作码时没有副作用，且修改后的 header 缓冲区不影响非 QUERY 处理。

### 测试建议
发送非 QUERY DNS 请求并验证响应是正确的 RCODE 拒绝。比较补丁前后 EDNS0 OPT 记录在缓冲区中的存在情况。

---

## 测试交接

补丁兼容性分析已完成，共发现 **2 个兼容性变更**（1 个 MEDIUM 优先级，1 个 LOW 优先级）。产物目录：`/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/3a052d/`
