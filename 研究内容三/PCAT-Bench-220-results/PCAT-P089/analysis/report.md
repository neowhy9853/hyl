# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython
**基线**: f2521324e6bdf331460abec7c2a88e2d3736b91c~1 (5625b187)
**补丁**: f2521324e6bdf331460abec7c2a88e2d3736b91c
**Profile**: cpython
**补丁主题**: gh-119710: fix asyncio Process.wait() to finish on process exit and not wait for closing of pipes

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 9 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: asyncio.subprocess.Process.wait
- **旧代码位置**: Lib/asyncio/base_subprocess.py:242-250
- **新代码位置**: Lib/asyncio/base_subprocess.py:242-254
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
Process.wait() 仅在所有管道文件描述符断开连接（EOF到达）后才返回。如果孙进程继承了打开的管道，管道将永远不会关闭，导致 wait() 尽管已知 returncode 仍然无限期挂起。

### 变更后行为
Process.wait() 在子进程退出时立即返回（当 _process_exited 被调用），无论管道是否仍然打开。_exit_waiters 现在直接在 _process_exited 中被唤醒，而不是等待 _call_connection_lost 或 _try_finish 检测到所有管道断开。

### 兼容性影响
调用 Process.wait() 的代码现在会更快收到返回码，这是预期的修复。然而，任何隐式依赖 wait() 阻塞直到管道 EOF 的代码（例如，在继续之前确保所有 stdout/stderr 数据已被完全消费）现在可能在完全消费管道数据之前就继续执行。这是公共标准库 API 中的语义行为变更。

### 核心变更说明
此补丁将 _exit_waiters 的唤醒逻辑从两个位置（_try_finish 的 _pipes_connected==False 路径和 _call_connection_lost 的 finally 块）移动到 _process_exited。同时移除了私有属性 _pipes_connected。

- **HUNK-0001/0002**: 移除 `self._pipes_connected` 属性的设置（纯内部重构，非公共 API）
- **HUNK-0003**: 纯格式变更（空白行）
- **HUNK-0004**: 在 `_process_exited` 中新增 waiter 唤醒逻辑（**核心兼容性变更**）
- **HUNK-0005**: 在 `_try_finish` 中移除基于 `_pipes_connected` 的 waiter 唤醒回退路径
- **HUNK-0006**: 在 `_call_connection_lost` 的 finally 块中移除 waiter 唤醒逻辑
- **HUNK-0007/0008**: 测试变更（删除旧测试 test_proc_exited_no_invalid_state_error_on_exit_waiters，添加新测试 test_wait_even_if_pipe_is_open）
- **HUNK-0009**: NEWS 条目（文档）

### 证据
```python
# Lib/asyncio/base_subprocess.py:245-250 (新增)
        # gh-119710: Wake up futures waiting for wait() as soon as the process
        # exits.
        for waiter in self._exit_waiters:
            if not waiter.done():
                waiter.set_result(returncode)
        self._exit_waiters = None
```

```python
# Lib/asyncio/base_subprocess.py:274-279 (移除 waiter 唤醒后的 _call_connection_lost)
        try:
            self._protocol.connection_lost(exc)
        finally:
            self._loop = None
            self._proc = None
            self._protocol = None
```

```python
# Lib/asyncio/base_subprocess.py:264-271 (移除 _pipes_connected 检查后的 _try_finish)
        assert not self._finished
        if self._returncode is None:
            return
        if all(p is not None and p.disconnected
               for p in self._pipes.values()):
            self._finished = True
            self._call(self._call_connection_lost, None)
```

### 复核建议
审查任何调用 Process.wait() 然后从 stdout/stderr 管道读取数据的代码，确保管道数据在 wait() 返回前被消费。标准库自带的 Process.communicate() 方法已正确处理此问题。

### 测试建议
使用 stdout 管道被孙进程保持打开的子进程进行测试（如补丁中新测试 test_wait_even_if_pipe_is_open 所示）。验证 wait() 在进程退出后在超时时间内返回，即使管道从未到达 EOF。同时验证 Process.communicate() 继续正常工作，因为它在内部调用 wait()。

---

## 候选人排除说明

以下候选被评估为纯内部变更或测试/文档变更，不构成公共 API 兼容性变更：

- **HUNK-0001/0002**: `_pipes_connected` 属性（以 `_` 开头）是 Python 约定中的私有实现细节，其移除不构成公共 API 兼容性变更。
- **HUNK-0003**: 纯空白行格式变更。
- **HUNK-0005/0006**: `_try_finish` 和 `_call_connection_lost`（以 `_` 前缀，私有方法）的内部逻辑重构，外部行为变化通过 PCA-0001 已完全涵盖。
- **HUNK-0007/0008/0009**: 测试和文档文件，不构成兼容性变更。
