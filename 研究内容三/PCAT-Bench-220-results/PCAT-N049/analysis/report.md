# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/haproxy
**基线**: 2ff861747cd745f2698e3e74c7f10b64a656be0c^ (98b1fd4ff9a719f34131fa04cbd93f92c0c362f7)
**补丁**: 2ff861747cd745f2698e3e74c7f10b64a656be0c
**Profile**: haproxy
**分析模式**: normal
**分析日期**: 2026-07-23

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 3 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

**该补丁不存在兼容性变更问题。**

### 补丁摘要

`BUG/MINOR: server: fix add server with consistent hash balancing`

该补丁将 `cli_parse_add_server()` 中的 server ID 生成逻辑从 `srv_alloc_lb()` **之后**移至 **之前**。具体变更：

- **HUNK-0001**: 移除 `int next_id;` 局部变量声明（不再需要临时变量）
- **HUNK-0002**: 在 `srv_alloc_lb()` 调用前插入 server ID 生成代码
- **HUNK-0003**: 移除 `srv_alloc_lb()` 调用后的旧 ID 生成代码，替换为注释

### 行为分析

**变更前行为**:
1. `srv_alloc_lb()` → `chash_server_init()` → `chash_compute_server_key()` 在 `srv->puid == 0` 时被调用
2. 服务器默认 `hash-key id`，此时 `key = 0 * SRV_EWGHT_RANGE = 0`，lb_nodes 获得错误 key
3. 随后 `srv->puid` 被设置为正确值
4. 服务器启用时 `chash_queue_dequeue_srv()` 检测到 key 变化，重新计算

**变更后行为**:
1. 先生成 server ID（`srv->puid` 已设置）
2. `srv_alloc_lb()` → `chash_compute_server_key()` 获得正确 key
3. 服务器启用时 `chash_queue_dequeue_srv()` 检测到 key 未变化，无需重算

**最终外部可观察行为**: 变更前后完全一致。服务器启用后，lb_nodes 最终都使用正确的 key。

### 为何不是兼容性变更

1. **CLI 命令语法**: 未变化
2. **CLI 输出/错误信息**: 未变化（`ha_alert` 消息相同）
3. **返回值**: 未变化
4. **服务器最终状态**: 未变化（key 在启用时自动重算）
5. **中间状态不可观察**: `cli_parse_add_server()` 在线程隔离下运行，服务器以 disabled 状态创建，中间状态无法被外部观察到

### 证据位置

- 文件: `src/server.c`，函数: `cli_parse_add_server()`
- 变更涉及行: 旧 6221-6422 / 新 6221-6425

---

## 下一步

由于未发现兼容性变更问题，无需进行定向测试。
正在清理分析 worktree。
