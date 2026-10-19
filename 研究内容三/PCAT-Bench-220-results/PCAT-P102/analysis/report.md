# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux
**基线**: 1e927a468500df5b39462c1c39c73e1f20b4fdb9^ (commit 214a2042b16b3c8d798a8b9ef9f36094f13a9859)
**补丁**: 1e927a468500df5b39462c1c39c73e1f20b4fdb9
**Profile**: kernel_6_6
**分析模式**: normal

## 补丁信息

| 项目 | 值 |
|------|-----|
| 标题 | tracing/probes: Point the error offset correctly for eprobe argument error |
| 作者 | Masami Hiramatsu (Google) |
| 上游 commit | 85e0f27dd1396307913ffc5745b0c05137e9beac |
| Fixes | 1b8b0cd754cd ("tracing/probes: Move event parameter fetching code to common parser") |
| 变更文件 | 2 |
| 补丁大小 | 54 行 (1 insertion, 3 deletions) |

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 2 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 错误异常行为变更 (ERROR_EXCEPTION_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.85
- **影响接口**: parse_probe_vars (tracefs error_log 错误位置输出)
- **旧代码位置**: kernel/trace/trace_probe.c:933-940
- **新代码位置**: kernel/trace/trace_probe.c:933-938
- **类型**: ERROR_EXCEPTION_CHANGE

### 变更前行为

当 eprobe 参数指定了不存在的事件字段且非 comm/COMM 时，`parse_probe_vars` 在进行错误报告前会执行 `ctx->offset = 0`（"backward compatibility"），导致错误位置始终指向参数串起始位置（offset 0），无法指出具体哪个变量无效。

### 变更后行为

移除了 `ctx->offset = 0` 的重置逻辑。错误位置保留 `parse_trace_event_arg` 或其他解析步骤已经设置的 `ctx->offset` 值，正确指向实际的无效参数位置。

### 兼容性影响

该变更改变了 tracefs error_log 中 eprobe 参数解析错误的错误位置输出。之前错误位置总是 0（参数起始位置），现在错误位置指向实际的错误变量处。编写到 dynamic_events 的用户和解析 error_log 的工具会观察到不同的错误位置数字。由于 error_log 是诊断接口而非稳定 ABI，且旧行为（始终 offset=0）本身是错误的，兼容性影响范围较小。对应的测试用例也已更新验证正确位置。

### 证据

**删除的旧代码 (kernel/trace/trace_probe.c:936-937)**:
```c
		/* backward compatibility */
		ctx->offset = 0;
```

**错误报告入口 (kernel/trace/trace_probe.c:1020-1022)**:
```c
inval:
	__trace_probe_log_err(ctx->offset, err);
	return -EINVAL;
```

**测试用例更新 (eprobes_syntax_errors.tc:22-23)**:
```
旧: check_error 'e:foo/bar syscalls/sys_enter_openat ^arg=$foo'	# BAD_ATTACH_ARG
新: check_error 'e:foo/bar syscalls/sys_enter_openat arg=^$foo'	# BAD_ATTACH_ARG
```

### 静态调用链

内部 static 调用链: `traceprobe_parse_probe_arg` -> `traceprobe_parse_probe_arg_body` -> `parse_probe_arg` -> `parse_probe_vars` -> `__trace_probe_log_err`

### 复核建议

确认无用户空间工具硬编码依赖 offset=0 的 eprobe 错误位置输出。

### 测试建议

通过 tracefs dynamic_events 接口写入无效参数验证 error_log 中错误位置能正确指向无效变量，并核对已有的 eprobes_syntax_errors.tc 测试通过。

---

## 候选变更（非兼容性变更）

- `tools/testing/selftests/ftrace/test.d/dynevent/eprobes_syntax_errors.tc`: 测试用例更新，将错误位置标记 `^` 从 `^arg=$foo` 移动到 `arg=^$foo`，以匹配修复后的正确错误位置。此为测试基础设施变更，无兼容性影响。
