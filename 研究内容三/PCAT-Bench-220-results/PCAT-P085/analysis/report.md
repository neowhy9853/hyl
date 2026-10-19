# PCA 兼容性变更分析报告

**仓库**: https://github.com/python/cpython
**基线**: 3a2b81e919103c0be3bc60a47aaa74d34fea6e9e^ (1516c26399)
**补丁**: 3a2b81e919103c0be3bc60a47aaa74d34fea6e9e
**Profile**: c_project

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 4 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 输入契约放宽 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.9
- **影响接口**: sysconfig.get_platform
- **旧代码位置**: Lib/sysconfig/__init__.py:694-704
- **新代码位置**: Lib/sysconfig/__init__.py:694-708
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为
在 32 位 ARM Android 运行于 64 位 ARM 内核的设备上，`os.uname().machine` 返回 `'armv8l'`。由于 `'armv8l'` 不在 `get_platform()` 内部 machine→ABI 映射字典中，`dict[machine]` 查找会引发 `KeyError`，导致该平台无法正确获取 platform 字符串。

### 变更后行为
`'armv8l'` 被新增到映射字典中，映射为 `'armeabi_v7a'`（与 `armv7l` 相同）。`get_platform()` 在 `armv8l` Android 设备上返回 `'android-<api_level>-armeabi_v7a'`，不再抛出 `KeyError`。

### 兼容性影响
这是一个公共 API 输入契约放宽变更：`get_platform()` 现在接受此前被拒的 machine 值 `'armv8l'`。该变更不破坏已有调用方（现有 `armv7l`/`x86_64`/`i686`/`aarch64` 行为完全不变），但会改变依赖 `get_platform()` 进行平台检测或 wheel tag 解析的下游代码在 `armv8l` 设备上的行为——从无法运行变为可以运行。该变更是向后兼容的 bug 修复。

### 证据
```python
# Lib/sysconfig/__init__.py:694-708
    if osname == "android" or sys.platform == "android":
        osname = "android"
        release = get_config_var("ANDROID_API_LEVEL")

        # Wheel tags use the ABI names from Android's own tools.
        # When Python is running on 32-bit ARM Android on a 64-bit ARM kernel,
        # 'os.uname().machine' is 'armv8l'. Such devices run the same userspace
        # code as 'armv7l' devices.
        machine = {
            "x86_64": "x86_64",
            "i686": "x86",
            "aarch64": "arm64_v8a",
            "armv7l": "armeabi_v7a",
            "armv8l": "armeabi_v7a",
        }[machine]
```

### 复核建议
确认 `armv8l` 与 `armv7l` 确实共享相同的 Android ABI (`armeabi_v7a`)，且不会有其他需要区分的场景。

### 测试建议
建议在 `armv8l` Android 设备上运行 `test_get_platform` 和 `test_android_ext_suffix` 测试用例，验证 platform 字符串和 EXT_SUFFIX 的正确性。

---
