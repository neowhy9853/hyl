# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux
**基线**: 48b91ed7e22bb82571c34f8b80b6ecdc90a6fab8
**补丁**: 7536ebe0473d9c1781710730d6e2f951ec640e07
**Profile**: kernel_6_6

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 5 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 补丁概述

该补丁是一个 Revert，回退了 commit 59ac47a0275f（upstream 26285e689c6c），该提交在 selftest 工具 `testptp` 中添加了时间戳事件队列掩码测试功能。

变更的文件：`tools/testing/selftests/ptp/testptp.c`

变更内容：
1. 移除 `-F` CLI 选项的 usage 文档
2. 移除 `channel` 局部变量声明
3. 从 getopt 字符串中移除 `F:`
4. 移除 `case 'F':` 分支处理代码
5. 移除使用 `PTP_MASK_CLEAR_ALL` / `PTP_MASK_EN_SINGLE` ioctl 的测试代码块

## 兼容性判定

**结论：无兼容性变更**

所有 5 个候选 hunk 均为非兼容性变更，理由如下：

1. **所有变更位于 selftest 工具中** (`tools/testing/selftests/ptp/testptp.c`)。kernel_6_6 profile 的 `tests` API surface 标记为 `public: false`，明确说明 selftest 不构成公共 API。

2. **被移除的代码引用不存在的 UAPI 常量**。`PTP_MASK_CLEAR_ALL` 和 `PTP_MASK_EN_SINGLE` ioctl 命令号在目标内核分支的 UAPI 头文件中未定义，导致原代码无法编译。该补丁是一个构建修复，而非功能性回归。

3. **CLI 选项 `-F` 从未在目标内核树中可用**。由于缺少所需的 ioctl 定义，即使用户调用 `testptp -F <chan>`，也无法正常工作。该选项的移除使工具与实际可用的内核接口保持一致。

4. **该 selftest 被视为测试基础设施**，而非面向最终用户的工具或库。profile 中 `ignore_patterns` 包含 `tools/**`（userspace tools）。

## 产物

- analysis.json: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N036/analysis.json`
- candidates.json: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N036/candidates.json`
- patch.diff: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N036/patch.diff`
