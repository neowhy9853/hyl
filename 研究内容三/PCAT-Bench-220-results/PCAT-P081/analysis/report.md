# PCA 兼容性变更分析报告

**仓库**: https://github.com/python/cpython
**基线**: b45319e13273ee17e84e6b8c459f03b141518289
**补丁**: c6fd7de64ac7591a9708c14a34737eb9baf050bc
**Profile**: c_project
**补丁描述**: gh-149083: use sentinel to fix _functools.reduce() signature

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 6 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 输出格式变更

- **测试优先级**: LOW
- **置信度**: 0.85
- **影响接口**: functools.reduce
- **旧代码位置**: Modules/clinic/_functoolsmodule.c.h:72
- **新代码位置**: Modules/clinic/_functoolsmodule.c.h:74-75
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为
`help(functools.reduce)` 显示 `initial=<unrepresentable>`；`inspect.signature(functools.reduce)` 无法生成有效签名（测试中 `reduce` 被标记为 `unsupported_signature`）。

### 变更后行为
`help(functools.reduce)` 显示 `initial=functools._initial_missing`，展示一个有意义的哨兵默认值；`inspect.signature(functools.reduce)` 现在可以正常返回包含 `initial` 参数的 Signature 对象。

### 兼容性影响
`functools.reduce` 的文档字符串（`help()` 输出）发生变化，从 `initial=<unrepresentable>` 变为 `initial=functools._initial_missing`。依赖解析 `help()` 输出的工具（如文档生成器、IDE 内省工具）可能会因输出格式差异而受影响。此外，`inspect.signature()` 对该函数的返回值从不完整变为完整，可能影响依赖签名内省的上游代码。

### 证据
```c
// Modules/clinic/_functoolsmodule.c.h
 PyDoc_STRVAR(_functools_reduce__doc__,
-"reduce($module, function, iterable, /, initial=<unrepresentable>)\n"
+"reduce($module, function, iterable, /,\n"
+"       initial=functools._initial_missing)\n"
```

```c
// Modules/_functoolsmodule.c
     function as func: object
     iterable as seq: object
     /
-    initial as result: object = NULL
+    initial as result: object(c_default="NULL") = functools._initial_missing
```

```python
# Lib/inspect.py
-        if isinstance(value, (str, int, float, bytes, bool, type(None))):
+        if isinstance(value, (str, int, float, bytes, bool, type(None),
+                              sentinel)):
```

### 复核建议
确认 IDE 和文档生成工具对 `functools.reduce` 签名展示是否从 `unrepresentable` 正确过渡到可读默认值。

### 测试建议
验证 `help(functools.reduce)` 和 `inspect.signature(functools.reduce)` 现在能正确返回包含 `initial=functools._initial_missing` 的有效输出，且 `functools.reduce` 的实际调用语义不变。
