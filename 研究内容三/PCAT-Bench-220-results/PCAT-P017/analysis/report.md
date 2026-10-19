# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/libxml2
**基线**: 47f416a5829356f55efa6f48a7e668c8de359e5a
**补丁**: b61737679e1f5ce2aaf19d075784a40bd5f4938a
**Profile**: libxml2

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## PCA-0001: 输入契约变更 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 1.0
- **影响接口**: parseInteger (CLI integer argument parser) — 影响 `--maxmem`, `--pretty`, `--max-ampl`
- **旧代码位置**: xmllint.c:2496-2496
- **新代码位置**: xmllint.c:2497-2500
- **类型**: INPUT_CONTRACT_CHANGE, CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为
parseInteger() 直接将输入字符串传给 strtoul()，后者将负号开头的有符号值静默转换为无符号大数。例如 `--max-ampl -1` 将放大因子设为 ULONG_MAX，实际上禁用了放大保护；`--maxmem -1` 同样分配了一个极大的内存限制。

### 变更后行为
parseInteger() 在调用 strtoul() 前检查字符串是否以 '-' 开头。如果检测到负值，向 errStream 输出错误消息 (`<context>: value not allowed: <value>`) 并返回 -1，拒绝该输入。

### 兼容性影响
CLI 选项 `--maxmem`、`--pretty`、`--max-ampl` 使用 parseInteger() 解析参数。之前负值通过 strtoul() 绕行被静默接受，现在被拒绝并报错。任何依赖向这些选项传递负值的脚本、封装工具或用户将观察到行为变化——命令现在会报错退出而非静默执行。

### 证据
```c
    if (str != NULL && *str == '-') {
        fprintf(errStream, "%s: value not allowed: %s\n", ctxt, str);
        return(-1);
    }
```

### 静态调用链
未生成（在分析阶段不自动生成，测试阶段按需生成）

### 复核建议
检查所有向 --maxmem、--pretty 或 --max-ampl 传递负值的脚本或测试套件。这些调用现在将报错退出。

### 测试建议
验证 xmllint --maxmem -1、xmllint --pretty -1、xmllint --max-ampl -1 均输出错误消息并以非零状态退出。验证正值和零值继续正常工作。测试边界值（如 --maxmem 0、--maxmem 1、--maxmem <实际限制>）。

---

*分析产物目录: /home/soong/pca_benchmark/_repos/libxml2/pca-results/b61737/*
