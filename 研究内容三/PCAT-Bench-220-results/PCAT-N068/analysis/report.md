# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: f2c2c1f2e1e1f016f219f8a0b3fe84265f27b055^
**补丁**: f2c2c1f2e1e1f016f219f8a0b3fe84265f27b055
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 2 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析结论

此补丁仅修改 `src/cmd/compile/internal/ssa/generate_test.go`，一个测试文件。
两个 hunk 均为内部测试变更：

- **HUNK-0001**: 在 import 块中新增 `"io/fs"` 和 `"strings"` 导入，为 WalkDir 替代 Glob 做准备。
- **HUNK-0002**: 将 `filepath.Glob(filepath.Join(wd, "*.go"))`（仅顶级目录）替换为 `filepath.WalkDir(wd, ...)`（递归遍历，跳过 `_gen` 和 `testdata` 子目录），用于在子目录中查找生成的文件。

**无兼容性变更**。所有变更为内部测试代码的改动，不影响任何导出 API、CLI 行为、配置语义、错误契约或用户可见的输出。候选 surface 匹配（go_errors、go_commands、cli_options 等）来自测试函数中 `t.Fatalf` 和 `"run"` 字符串的模式匹配，属于误匹配，不代表实际的公共 API 变更。

`findings` 保持为空。无需进行定向动态测试。
