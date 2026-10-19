# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/haproxy
**基线**: a7c64a5b12f8f205b5e0b7f044052d9993e21fa7
**补丁**: 667645ed2b7e0a78f7bbd640440af900703cce35 (DEV: patchbot: prepare for new version 3.5-dev)
**Profile**: haproxy

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 2 |
| 兼容性变更 | **0** |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

本补丁**不包含兼容性变更**。

### 补丁内容

该 commit 在两个 **纯文本 prompt 文件**，位于 `dev/patchbot/prompts/` 目录下：

1. `dev/patchbot/prompts/prompt15-3.5-mist7bv2-pfx.txt` — AI 助手（patchbot）的前缀 prompt，包含 HAProxy 开发流程上下文和任务描述
2. `dev/patchbot/prompts/prompt15-3.5-mist7bv2-sfx.txt` — AI 助手的后缀 prompt，包含回传判定指令格式

### 判定理由

- 两个文件均位于 `dev/` 目录，是 **开发工具内部资源**，不参与 HAProxy 运行时
- 文件后缀为 `.txt`，是 **纯文本 prompt 内容**，非可执行代码、配置文件、头文件或脚本
- 无任何 haproxy 源码变更（`src/`、`include/` 等核心目录未修改）
- Profile ignore_patterns 明确包含 `dev/**`
- 不涉及 API/ABI、CLI、配置、协议、proc/sys、系统接口或任何运行时行为变化

### 候选分析

| Hunk | 文件 | 是否兼容性变更 | 原因 |
|------|------|---------------|------|
| HUNK-0001 | dev/patchbot/prompts/prompt15-3.5-mist7bv2-pfx.txt | 否 | dev/ 目录纯文本 prompt |
| HUNK-0002 | dev/patchbot/prompts/prompt15-3.5-mist7bv2-sfx.txt | 否 | dev/ 目录纯文本 prompt |

---

## 下一步

补丁兼容性分析已完成，无需进行定向测试。所有任务完成后将清除 worktree。
