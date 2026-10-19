# PCA 兼容性变更分析报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/gregkh/linux.git |
| 补丁 ID | c0b8e6eea1b2bc2252d4de8962e5b01e53e60eae |
| 基线 | 802e113cf120df7208e4c7e604950a85e87120a8 |
| Profile | kernel_6_6 |
| 补丁标题 | Documentation: ioctl-number: Extend "Include File" column width |
| 分析模式 | heavy (churn=464 >= 250) |

## 补丁内容

该补丁仅修改 `Documentation/userspace-api/ioctl/ioctl-number.rst` 文档文件，将 RST 表格中 "Include File" 列的宽度从 55 字符扩展到 57 字符，以容纳后续补丁中的长路径名。属于纯文档格式化变更。

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 (文档) |
| 候选变更 | 0 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 结论

**未检测到兼容性变更。** 该补丁仅涉及 RST 文档表格列宽调整，属于纯文档改动，不影响任何代码、API、ABI、系统调用、配置或运行时行为。无需进行定向测试。

## 产物目录

全部产物已写入: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N035/`
