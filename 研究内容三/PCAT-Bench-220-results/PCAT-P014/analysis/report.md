# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/cpython
**基线**: 776573c9f08f70ae9cb2327a905a42f265b331a6
**补丁**: 7de4fcd44585f572acbcee23f5c7018b2b3f0983
**Profile**: cpython

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 3 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: itertext() 不再输出 Comment/PI 元素的文本 (OUTPUT_FORMAT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.95
- **影响接口**: `xml.etree.ElementTree.Element.itertext`
- **旧代码位置**: `Modules/_elementtree.c:2297-2303`
- **新代码位置**: `Modules/_elementtree.c:2297-2307`
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为
当 `elementiter_next` 以 `gettext=1` 调用时（即来自 `Element.itertext()`），函数无条件调用 `element_get_text()` 并 yield 文本。对于 Comment 和 ProcessingInstruction 元素（其 tag 字段为函数对象，而非 None 或 Unicode 字符串），会错误地将其文本内容作为 itertext() 的一部分返回。

### 变更后行为
在 `element_get_text()` 调用前新增了守卫检查：如果 `elem->tag` 不是 `Py_None` 且不是 Unicode 字符串，则跳过该元素（`Py_DECREF` + `continue`）。这使 C 实现与 Python 回退实现保持一致，Comment 和 PI 元素不再参与 itertext() 输出。

### 兼容性影响
`Element.itertext()` 是 Python 标准库的公共方法。C 实现此前会输出 Comment/PI 的文本，而 Python 实现已跳过。此补丁修复了一致性问题，但改变了可观察行为：依赖 `itertext()` 获取 Comment/PI 文本的用户代码将得到不同结果（这些文本现在被跳过）。

### 证据
```c
        if (it->gettext) {
            if (elem->tag != Py_None && !PyUnicode_Check(elem->tag)) {
                Py_DECREF(elem);
                continue;
            }
            text = element_get_text(elem);
            goto gettext;
        }
```

```python
    def itertext(self):
        tag = self.tag
        if not isinstance(tag, str) and tag is not None:
            return
        t = self.text
        if t:
            yield t
        for e in self:
            yield from e.itertext()
            t = e.tail
            if t:
                yield t
```

### 静态调用链
（未启用）

### 复核建议
确认新增守卫条件 (`elem->tag != Py_None && !PyUnicode_Check(elem->tag)`) 能正确识别所有 Comment/PI 元素类型，不会误跳 tag 为非常规对象的合法元素。

### 测试建议
运行 `test_xml_etree::ElementIterTest::test_comment` 和 `test_processinginstruction`。验证包含 Comment/PI 子元素的元素上 `itertext()` 不再返回其文本。运行 `test_xml_etree` 全量测试确认无回归。
