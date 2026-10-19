# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/NetworkManager
**基线**: HEAD (4b63ae29a5)
**补丁**: fc49936904 - version: add 1.60 macros
**Profile**: networkmanager

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 2 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

本次补丁**不包含兼容性变更**。变更内容为新增版本 1.60 宏定义：

1. `src/libnm-core-public/nm-version-macros.h.in`: 新增 `NM_VERSION_1_60` 版本常量宏
2. `src/libnm-core-public/nm-version.h`: 新增 `NM_DEPRECATED_IN_1_60`、`NM_DEPRECATED_IN_1_60_FOR`、`NM_AVAILABLE_IN_1_60` 版本边界宏

所有变更均为纯粹新增，遵循与之前所有版本宏（0.9.8 至 1.58）完全相同的模式。无现有宏被修改或删除，不影响任何现有代码的兼容性。

`NM_AVAILABLE_IN_1_60` 在现有代码中展开为 `G_UNAVAILABLE(1, 60)`（因 `NM_VERSION_MAX_ALLOWED` 默认低于 1.60），这是新增版本 API 宏的预期行为，不构成破坏性变更。

## 产物位置

`/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/fc4993/`
