# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/dnf
**基线**: HEAD~1 (1f9f3e99cf70b2431ae95796512d69086fc2ff7b)
**补丁**: aeb975e5486fa3bb5cd7db9d35af1eebd4bc8e64
**Profile**: dnf

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 2 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 输入契约变更 / 配置行为变更

- **测试优先级**: HIGH
- **置信度**: 1.0
- **影响接口**: usr_drift_protected_paths (config_key)
- **旧代码位置**: dnf/cli/cli.py:254-256
- **新代码位置**: dnf/cli/cli.py:255-257
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为

`usr_drift_protected_paths` 配置值被当作路径前缀处理。对于每个包文件路径，代码检查 `pkg_file_path.startswith("/<path>/") or pkg_file_path == <path>`。例如 `/usr/lib` 会匹配 `/usr/lib/foo`、`/usr/lib/bar` 以及 `/usr/lib` 本身。

### 变更后行为

`usr_drift_protected_paths` 配置值被当作 glob 模式通过 `fnmatch()` 处理。不带通配符的值（如 `/usr/lib`）只精确匹配 `/usr/lib`。要匹配 `/usr/lib/` 下的文件，用户现在必须使用 `/usr/lib/*`。glob 特殊字符（`*`、`?`、`[]`）现在具有模式语义。

### 兼容性影响

配置选项 `usr_drift_protected_paths` 的语义契约从"路径前缀匹配"更改为"glob 模式匹配"。依赖前缀匹配的现有配置（如使用 `/usr/lib` 保护 `/usr/lib/` 下所有文件）在补丁后将不再匹配这些路径。这可能导致 bootc 事务中原本应被检测并阻止的文件修改不再被检测到（漏报）。fnmatch() 函数在不含通配符时执行精确匹配，比原有的前缀或精确匹配范围更窄。

### 证据

```python
# Old (prefix matching):
for protected_path in self.conf.usr_drift_protected_paths:
    if pkg_file_path.startswith("%s/" % protected_path) or pkg_file_path == protected_path:

# New (glob matching):
for protected_pattern in self.conf.usr_drift_protected_paths:
    if fnmatch(pkg_file_path, protected_pattern):
```

### 静态调用链

未启用

### 复核建议

审查现有的 `usr_drift_protected_paths` 配置，判断是否依赖前缀匹配行为。使用裸目录路径（如 `/usr/lib`、`/usr/local`、`/opt`）且不带通配符的配置，将不再匹配子目录内容。应将它们更新为 `/usr/lib/*`、`/usr/local/*` 或 `/opt/*` 以保持原有的保护范围。同时检查路径中是否包含 `*`、`?` 或 `[` 作为字面字符的配置。

### 测试建议

使用多种 `usr_drift_protected_paths` 值进行测试：
1. 不带通配符的裸路径（如 `/usr/lib`）—— 验证 `/usr/lib/` 下的文件是否**不再**被匹配（行为变更）
2. 带通配符后缀的路径（如 `/usr/lib/*`）—— 验证 `/usr/lib/` 下的文件是否**被**匹配（获取旧行为的新方式）
3. 包含 glob 元字符的路径（如 `/usr/local/*/bin`）—— 验证 glob 匹配正常工作
4. 精确路径匹配（如 `/etc/os-release`）—— 验证精确文件仍被匹配（未变更行为）
5. 验证 `--setopt=usr_drift_protected_paths=` 覆盖选项仍有效

---
