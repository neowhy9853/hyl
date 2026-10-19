# PCA 兼容性变更分析报告

**仓库**: https://github.com/python/cpython
**基线**: 71cf3130c6e5dd903837b6871af99156c799fd1e (07ae6f133ad7a4e7ed506f6a511809b1fc3d1465^)
**补丁**: 07ae6f133ad7a4e7ed506f6a511809b1fc3d1465
**Profile**: c_project

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 4 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 补丁说明

补丁 GH-150208 修复了 `sysconfigdata` 变量中字符串值被双重引号包裹的问题。来自 `pyconfig.h` 的字符串值在渲染到 `sysconfigdata` 时保留了引号，该补丁在 `parse_config_h()` 中添加了引号剥离逻辑。

---

## PCA-0001: 输出格式变更 (OUTPUT_FORMAT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: `sysconfig.parse_config_h`（公共 API，间接影响 `get_config_vars` / `get_config_var`）
- **旧代码位置**: Lib/sysconfig/__init__.py:437-450
- **新代码位置**: Lib/sysconfig/__init__.py:437-453
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为

`parse_config_h()` 解析 config.h 文件时，对于被双引号包裹的字符串值（如 `#define FOO "bar"`），直接保留引号存入返回字典，例如 `vars['FOO'] = '"bar"'`。这些值通过 `_sysconfigdata_*` 模块最终暴露给 `sysconfig.get_config_vars()`，导致运行时 `get_config_var()` 返回带引号的字符串。

### 变更后行为

`parse_config_h()` 新增 `quoted_re` 正则表达式，解析时先检查值是否被双引号包围，若是则剥离引号后存入字典。例如 `#define FOO "bar"` → `vars['FOO'] = 'bar'`（无引号）。

### 兼容性影响

`parse_config_h()` 是 sysconfig 模块 `__all__` 中列出的公共 API，其返回值在 CPython 构建期间通过 `Lib/sysconfig/__main__.py` 写入 `_sysconfigdata_*` 模块，最终经 `sysconfig.get_config_vars()` 暴露给所有运行时消费者。任何依赖 `get_config_var()` 返回带引号字符串的代码在升级后将获得不带引号的值，可能导致断言失败、字符串匹配错误或下游逻辑异常。

### 证据

```python
# Lib/sysconfig/__init__.py (lines 437-440 — 新增 quoted_re 编译)
    import re
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n")
+    quoted_re = re.compile('^"(.*)"$')
```

```python
# Lib/sysconfig/__init__.py (lines 446-450 — 新增引号剥离逻辑)
        if m:
            n, v = m.group(1, 2)
+            if mq := quoted_re.match(v):
+                v = mq.group(1)
            try:
```

```python
# Lib/test/test_sysconfig.py (lines 579-583 — 新增测试验证无引号)
+    @unittest.skipIf(sysconfig.get_config_var('PY_BUILTIN_HASHLIB_HASHES') is None,
+                     'PY_BUILTIN_HASHLIB_HASHES required for this test')
+    def test_PY_BUILTIN_HASHLIB_HASHES_in_vars(self):
+        vars = sysconfig.get_config_vars()
+        self.assertFalse(vars['PY_BUILTIN_HASHLIB_HASHES'].startswith('"'))
```

### 复核建议

确认 `_ALWAYS_STR` 集合（Lib/sysconfig/__init__.py:23）中的所有 key 对应的值在变更后是否正确（原本带引号的字符串现在不带引号）。复核 CPython 生态中是否有其他工具（如 pip、setuptools）依赖 `get_config_var()` 返回带引号字符串。

### 测试建议

1. 运行现有测试套件 `Lib/test/test_sysconfig.py` 确认新增 `test_PY_BUILTIN_HASHLIB_HASHES_in_vars` 通过
2. 对 `parse_config_h()` 构造包含引号字符串的 config.h 输入，验证返回值中引号已被剥离
3. 对 `parse_config_h()` 构造不带引号的数值输入（如 `#define FOO 42`），验证 int 转换行为未受影响
4. 对 `parse_config_h()` 传入包含 `_ALWAYS_STR` 成员的输入，验证字符串值正确且无引号残留

---
