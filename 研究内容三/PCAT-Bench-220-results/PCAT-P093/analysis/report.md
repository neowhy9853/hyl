# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: 5d1cdacd7861acbfa5ff376ce8c0c4653902c86c
**补丁**: 16e8e067516c7c35f2affd8e9d58271707611575
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 4 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 错误/异常消息变更 (ERROR_EXCEPTION_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.95
- **影响接口**: runtime.PanicNilError.Error()
- **旧代码位置**: src/runtime/panic.go:794-794
- **新代码位置**: src/runtime/panic.go:794-794
- **类型**: ERROR_EXCEPTION_CHANGE

### 变更前行为
PanicNilError.Error() 返回字符串 "panic called with nil argument"，该错误消息不符合 Go 规范中对 runtime.Error 的约定——所有 runtime 错误应以 "runtime error:" 为前缀。panic(nil) 的完整输出为 "panic: panic called with nil argument"。

### 变更后行为
PanicNilError.Error() 返回字符串 "runtime error: panic called with nil argument"，添加了 "runtime error:" 前缀以正确符合 runtime.Error 接口约定。panic(nil) 的完整输出变为 "panic: runtime error: panic called with nil argument"。

### 兼容性影响
任何对 PanicNilError.Error() 返回值进行字符串精确匹配、子串匹配（如检查 "runtime error:" 前缀是否存在）或解析的代码都将受到影响。调用方如果比较错误消息以判断是否为 panic(nil) 错误，其断言将失败。Go 约定推荐使用类型断言和接口判断（而非字符串匹配）来处理错误，因此实际影响范围有限，但仍构成兼容性变更。

### 证据
```go
func (*PanicNilError) Error() string { return "runtime error: panic called with nil argument" }
```

### 静态调用链
无

### 复核建议
无需人工复核。此变更将 PanicNilError 的 Error() 输出对齐至 Go 规范要求的 runtime.Error 契约，是一个合规性修复。

### 测试建议
验证 panic(nil) 输出的错误消息包含 "runtime error:" 前缀；验证调用 panic(nil) 后 recover() 返回值实现 runtime.Error 接口；验证对 PanicNilError.Error() 的字符串包含检查在旧代码中可能失效的场景。
