# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: 06bc6592c3336596ec8904357efb333203d05170 (7db85e388c5e^)
**补丁**: 7db85e388c5e36db3c03c4146e6674cc98bd714d
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 3 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析结论

**未检测到兼容性变更。** 该补丁为纯增量变更，在 `go/parser` 包中新增了已标记为 `Deprecated` 的导出函数 `ResolveFile(*ast.File)`。

### 补丁变更内容

1. **`src/go/parser/resolver.go`**: 新增导出函数 `ResolveFile` 和未导出变量 `resolveOnces`。`ResolveFile` 对 `SkipObjectResolution` 模式解析的文件执行事后标识符解析，具有幂等性和并发安全性。

2. **`api/next/79802.txt`**: Go API 元数据跟踪文件，记录新增的公共 API 签名。

3. **`src/go/parser/resolver_test.go`**: 新增测试函数 `TestResolveFile`，验证 `ResolveFile` 的功能和幂等性。

### 兼容性判定依据

- **纯增量变更**：补丁仅新增代码（126行新增，0行删除），未修改任何已有 API 签名、返回值语义、错误契约或行为逻辑。
- **Go 1 兼容性承诺**：在 Go 语言中，向现有包添加新的导出标识符是完全向后兼容的操作，不会破坏已有代码的编译或运行时行为。
- **已标记 Deprecated**：`ResolveFile` 从引入起即标记为 `Deprecated`，文档明确建议新设计使用 `go/types` 包。该函数仅作为从旧 `ast.Object` 解析机制迁移的辅助工具。
- **未修改已有行为**：已有的 `resolveFile`（未导出）函数、`SkipObjectResolution` 模式标志、以及整个解析流程的行为均未被改动。
- **内部实现隔离**：新增的 `resolveOnces sync.Map` 为未导出变量，不对外暴露。

### 候选排除说明

| 候选 | 文件 | 判定 | 原因 |
|------|------|------|------|
| HUNK-0001 | `api/next/79802.txt` | 非兼容性变更 | API 元数据跟踪文件，非功能代码 |
| HUNK-0003 | `src/go/parser/resolver.go` | 非兼容性变更 | 纯增量变更，新增导出函数不破坏已有 API |
| HUNK-0004 | `src/go/parser/resolver_test.go` | 非兼容性变更 | 测试代码，非公共接口 |
