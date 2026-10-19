# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: HEAD (commit bef396c3396fa7a31460cc4b892b90c5621e830f)
**补丁**: 10f7480a0e3c2e95d86d76df6eddbff0372a233f
**Profile**: golang
**分析模式**: heavy (3 shards)
**产物目录**: /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N034

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 7 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析结论

**未检测到兼容性变更。**

此补丁 (commit 10f7480a, "cmd/go: split build_overlay script test to improve parallelism") 是一个纯测试重构。它将 `build_overlay.txt` 测试脚本拆分为 3 个独立文件：

1. `build_overlay.txt` — 基础 overlay 测试（移除了 cgo 和 gccgo 相关部分）
2. `build_overlay_cgo.txt` — cgo overlay 测试（新建）
3. `build_overlay_gccgo.txt` — gccgo overlay 测试（新建）

所有 7 个候选 hunk 均位于 `src/cmd/go/testdata/script/` 目录下，属于 Go 内部测试脚本数据文件。变更内容仅涉及：
- 删除 `[cgo]` 标记的测试命令（移至新文件）
- 删除 gccgo 测试命令（移至新文件）
- 删除 cgo 测试辅助文件内容（移至新文件）
- 创建 `build_overlay_cgo.txt` 和 `build_overlay_gccgo.txt` 新测试文件

**无生产代码变更、无导出 API 变更、无 CLI 行为变更、无配置变更、无错误语义变更。** 测试逻辑完全保留，仅重新组织以提升并行度。

## 变更文件

| 文件 | 变更类型 |
|------|---------|
| `src/cmd/go/testdata/script/build_overlay.txt` | 修改（删除 cgo/gccgo 测试代码段） |
| `src/cmd/go/testdata/script/build_overlay_cgo.txt` | 新增（cgo overlay 测试） |
| `src/cmd/go/testdata/script/build_overlay_gccgo.txt` | 新增（gccgo overlay 测试） |

## 补丁指标

| 指标 | 值 |
|------|------|
| 补丁行数 | 556 |
| 新增行 | 338 |
| 删除行 | 132 |
| Churn | 470 |
| 原始 Hunk 数 | 7 |
| 候选 Hunk 数 | 7 |
