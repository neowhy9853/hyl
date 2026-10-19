# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/glib
**基线**: 59421091a (HEAD~1)
**补丁**: 3614d588fc168904ec31abee7ca63efa8fb2a25a — "gmarkup: Add another location api"
**Profile**: glib2 (effective: c_project + daemon_network)

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 15 |
| **兼容性变更** | **0** |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 结论

**本次补丁未发现兼容性变更。** 所有变更均为纯增量式，不影响现有公共 API 签名、ABI 布局或行为契约。

### 变更汇总

| 文件 | Hunk | 变更类型 | 判定 |
|------|------|----------|------|
| glib/gmarkup.c | HUNK-0001~0002 | `_GMarkupParseContext` 结构体新增字段 | 内部不透明结构体，对外无 ABI 影响 |
| glib/gmarkup.c | HUNK-0003~0004 | 新增字段初始化/释放 | 纯增量内部变更 |
| glib/gmarkup.c | HUNK-0005~0008 | static 函数行为增强 | 内部函数，非导出 API |
| glib/gmarkup.c | HUNK-0009 | 新增公共函数 `g_markup_parse_context_get_attribute_position` | **纯新增 API**（Since: 2.90），向后兼容 |
| glib/gmarkup.h | HUNK-0010 | 公共头文件新增函数声明 | 纯增量声明 |
| glib/tests/markup-parse.c | HUNK-0011~0015 | 测试增强 | 仅新增断言，不改已有测试行为 |

### 详细判定

1. **内部结构体变化（HUNK-0001 ~ HUNK-0002）**: `struct _GMarkupParseContext` 仅在 `gmarkup.c` 中定义，对外通过不透明指针 `GMarkupParseContext *` 使用。结构体布局变化为内部 ABI，不影响已编译的外部库消费者。

2. **内部函数增强（HUNK-0003 ~ HUNK-0008）**: 所有变更均在 `static` 或 `static inline` 函数内，未暴露给库外部消费者。`g_realloc` → `g_realloc_n` 行为等价。

3. **新增公共 API（HUNK-0009 ~ HUNK-0010）**: `g_markup_parse_context_get_attribute_position()` 是纯新增函数，标记 `GLIB_AVAILABLE_IN_2_90`（当前版本 2.89.2）。不修改任何已有的 API 签名、返回值或行为契约，完全向后兼容。

### 产物位置

`/home/soong/pca_benchmark/_repos/glib/pca-results/3614d5/`
