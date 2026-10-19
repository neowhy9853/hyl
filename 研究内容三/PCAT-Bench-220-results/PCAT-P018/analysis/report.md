# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/libxml2
**基线**: 6be0acd2afb3f55af3c721e1e35ac6675df3057a
**补丁**: d3352554e4c1f052b914cda7b415d06b7eab5dfa (xmllint: Fix the `--maxmem` command option)
**Profile**: libxml2

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: CLI 选项行为变更 (CONFIG_CLI_BEHAVIOR_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: xmllintMain --maxmem
- **旧代码位置**: xmllint.c:3075-3082
- **新代码位置**: xmllint.c:3075-3083
- **类型**: CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为
当使用 `--maxmem` 指定非零值 N 时，`xmllintMaxmem` 被错误地设为 0 而非 N。自定义内存分配器中的检查 `xmlMemUsed() + size > xmllintMaxmem` 因 `xmllintMaxmem=0` 导致每次分配都立即超过限制，使 `--maxmem` 完全不可用（首条分配立即 OOM）。

### 变更后行为
`xmllintMaxmem` 在 `if` 块之前初始化为 0。当 `--maxmem` 指定非零值 N 时，`xmllintMaxmem` 被正确设为 N。自定义内存分配器现在正确执行预期的内存限制，`--maxmem` 按文档工作。

### 兼容性影响
`--maxmem` CLI 选项的行为从完全损坏（立即 OOM）变为正确工作。任何之前使用过 `--maxmem` 的用户都会遇到立即 OOM 错误；修复后选项实际限制内存使用。从未使用 `--maxmem` 的用户不受影响。这是一个恢复文档化行为的 bug 修复。

### 证据
\`\`\`c
    xmllintMaxmem = 0;
    if (lint->maxmem != 0) {
        xmllintMaxmem = lint->maxmem;
        xmllintMaxmemReached = 0;
        xmllintOom = 0;
        xmlMemSetup(myFreeFunc, myMallocFunc, myReallocFunc, myStrdupFunc);
    }
\`\`\`

### 静态调用链
无（CLI 主入口点）

### 复核建议
验证 `--maxmem` 现在正确执行内存限制，使用各种正整数值测试，并确认 OOM 在预期阈值触发。

### 测试建议
使用值 1、100、1000000 和 0（无限制/默认）测试 `--maxmem`。验证当内存低于限制时处理成功，超限时失败并 OOM。同时验证不传递 `--maxmem` 时行为不变（不安装自定义分配器）。

---

## 产物位置

分析产物已写入 /home/soong/pca_benchmark/_repos/libxml2/pca-results/d33525/

发现 1 个兼容性变更: PCA-0001 (CONFIG_CLI_BEHAVIOR_CHANGE, 中优先级)
