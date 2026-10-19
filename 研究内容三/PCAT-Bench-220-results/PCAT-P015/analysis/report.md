# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/cpython
**基线**: d8ff4f8e56217133be6e22592aa60a1fab331d8e
**补丁**: 24c6bbc92b6dd0ce9b7ff799049498299f70f97d — gh-84353: Preserve non-UTF-8 filenames when appending to ZipFile
**Profile**: cpython

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 5 |
| 兼容性变更 | 2 |
| 高优先级测试 | 1 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: OUTPUT_FORMAT_CHANGE — `_encodeFilenameFlags` 编码行为变更

- **测试优先级**: HIGH
- **置信度**: 0.92
- **影响接口**: ZipInfo._encodeFilenameFlags (通过 FileHeader() 公开)
- **旧代码位置**: Lib/zipfile/__init__.py:566-573
- **新代码位置**: Lib/zipfile/__init__.py:566-577
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为

在 `flag_bits` 未设置 `_MASK_UTF_FILENAME` 时，始终尝试 ascii 编码。对非 ASCII 文件名触发 `UnicodeEncodeError` 后回退到 UTF-8 编码并设置 UTF-8 标志位。导致原始 cp437 编码文件名在重写中央目录时被转换为 UTF-8。

### 变更后行为

在 `flag_bits` 未设置 `_MASK_UTF_FILENAME` 时使用 cp437 编码；设置时使用 ascii 编码。编码成功时清除 UTF-8 标志位 (`flag_bits & ~_MASK_UTF_FILENAME`)。使得 cp437 编码的文件名在重写时保持 cp437 编码不变。

### 兼容性影响

`ZipInfo.FileHeader()` 是公开 API，其输出 bytes 格式发生变化：对于无 UTF-8 标志位的 `ZipInfo` 对象且文件名为 cp437 可编码时，返回的文件名字节从 UTF-8 编码变为 cp437 编码，且 `flag_bits` 中的 UTF-8 标志位被清除。依赖 `FileHeader()` 输出的 ZIP 生成/解析工具可能观察到字节差异。

### 证据

```python
def _encodeFilenameFlags(self):
    if self.flag_bits & _MASK_UTF_FILENAME:
        encoding = "ascii"
    else:
        encoding = "cp437"
    try:
        return self.filename.encode(encoding), self.flag_bits & ~_MASK_UTF_FILENAME
    except UnicodeEncodeError:
        return self.filename.encode("utf-8"), self.flag_bits | _MASK_UTF_FILENAME
```

### 复核建议

确认 `FileHeader()` 输出的 bytes 变化是否被任何外部解析器或测试断言所依赖。验证 cp437→UTF-8 转换回退路径仍正确处理 cp437 不可编码的极端 Unicode 字符。

### 测试建议

创建含非 ASCII cp437 可编码文件名的 ZIP，读取后调用 `ZipInfo.FileHeader()` 比较 old/new 输出 bytes。验证 append 模式下中央目录文件名编码是否保持原始编码而非被转换为 UTF-8。

---

## PCA-0002: SIDE_EFFECT_CHANGE — `_open_to_write` 默认 flag_bits 变更

- **测试优先级**: MEDIUM
- **置信度**: 0.80
- **影响接口**: ZipFile 写入操作链
- **旧代码位置**: Lib/zipfile/__init__.py:1812-1818
- **新代码位置**: Lib/zipfile/__init__.py:1816-1822
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为

新写入 ZIP 条目的 `flag_bits` 初始化为 `0x00`，表示不使用 UTF-8 文件名标志位。随后在 `_encodeFilenameFlags` 中通过 ascii→utf-8 回退机制处理编码。

### 变更后行为

新写入 ZIP 条目的 `flag_bits` 初始化为 `_MASK_UTF_FILENAME` (0x800)，明确声明文件名使用 UTF-8 编码。随后在 `_encodeFilenameFlags` 中通过 ascii 编码处理，编码成功后清除 UTF-8 标志位。

### 兼容性影响

虽然 `_open_to_write` 是私有方法，但它是所有 `ZipFile` 写入操作的核心路径。`flag_bits` 的默认值变化结合 `_encodeFilenameFlags` 的逻辑变更（PCA-0001），影响新创建 ZIP 文件中条目的通用标志位初态。

### 证据

```python
zinfo.flag_bits = _MASK_UTF_FILENAME
if zinfo.compress_type == ZIP_LZMA:
    zinfo.flag_bits |= _MASK_COMPRESS_OPTION_1
if not self._seekable:
    zinfo.flag_bits |= _MASK_USE_DATA_DESCRIPTOR
```

### 复核建议

验证新创建的 ZIP 中 ASCII 文件名的 `flag_bits` 仍为 0，非 ASCII 文件名的 `flag_bits` 正确设置为 UTF-8 标志。确认其他标志位运算不受影响。

### 测试建议

创建含 ASCII 和非 ASCII 文件名的 ZIP，解析文件头验证 `flag_bits` 值。对比 old/new 创建的文件头字节序列。

---

## 分析结论

该补丁修复了 zipfile 模块在 append 模式下重写中央目录时，非 UTF-8 编码文件名被损坏的问题（gh-84353）。核心变更在 `_encodeFilenameFlags` 方法中根据 `flag_bits` 的 UTF-8 标志位选择编码方式，以及 `_open_to_write` 中为新条目默认设置 UTF-8 标志位。两项变更均改变了对 ZIP 文件头中文件名字段的编码输出，属于兼容性变更。

产物已写入 `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max-rerun-20260722/PCAT-P015/`
