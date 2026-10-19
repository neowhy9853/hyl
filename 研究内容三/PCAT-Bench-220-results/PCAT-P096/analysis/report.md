# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: 044c995af789121b9f5cef2206ef844ef6c8263b^
**补丁**: 044c995af789121b9f5cef2206ef844ef6c8263b
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 4 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析结论

**未检测到兼容性变更。**

该补丁对 Linux 内核版本字符串解析增加了对下划线后缀的容忍支持（修复 Synology 等嵌入式 Linux 平台），并将 `getKernelVersion()` 从不可恢复的 `throw()` 改为返回 `ok bool` 标记的优雅降级，在解析失败时回退到系统调用探测。

所有变更函数均位于 `src/runtime/` 包内，且均为小写字母开头（未导出）的内部函数：

| 函数 | 可见性 | 调用者 |
|------|--------|--------|
| `getKernelVersion()` | 未导出 | 仅 `os_linux32.go:configure64bitsTimeOn32BitsArchitectures` |
| `parseRelease()` | 未导出 | 仅 `os_linux.go:getKernelVersion` |
| `configure64bitsTimeOn32BitsArchitectures()` | 未导出 | 仅 `os_linux.go:osinit` |
| `probeFutexTime64()` | 未导出 | 仅 `os_linux32.go:configure64bitsTimeOn32BitsArchitectures` |

唯一的导出符号 `var ParseRelease` 位于 `export_linux_test.go`（_test.go 文件），仅在测试时编译。

### 各候选判定

- **HUNK-0001** (`export_linux_test.go`): 测试辅助变量导出。非兼容性变更。
- **HUNK-0002** (`os_linux.go`): `getKernelVersion` 签名变化（内部）；`parseRelease` 解析更宽容（叠加性变更，接受所有旧输入及新增下划线后缀输入）。非兼容性变更。
- **HUNK-0003** (`os_linux32.go`): 增加 `probeFutexTime64()` 回退探测（仅在 `getKernelVersion` 失败时触发，此前失败会导致 `throw` 崩溃）。非兼容性变更。
- **HUNK-0004** (`runtime_linux_test.go`): 新增测试函数 `TestParseRelease`。非兼容性变更。

### 影响面总结

此补丁为**纯 Bug 修复**：使 Go 运行时在 Synology 等使用下划线后缀的嵌入式 Linux 上正常启动（之前会崩溃 init）。不影响公共 API、ABI、CLI、配置、协议或外部输出格式。
