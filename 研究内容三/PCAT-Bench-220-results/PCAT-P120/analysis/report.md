# PCA 兼容性变更分析报告

**仓库**: https://github.com/rhboot/grub2
**基线**: 1162f7afb
**补丁**: bacb99f6b (fs/xfs: Fix XFS directory extent parsing)
**Profile**: grub2

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 5 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析摘要

本补丁修复了 GRUB2 中 XFS 文件系统目录 extent 解析的两个问题：

1. **多 extent 目录解析错误**：之前的代码假设所有目录都使用单一 extent，当 `/boot/grub/<arch>` 目录跨越多个 extent 时，解析器会错误地触发 "invalid XFS directory entry" 错误。修复后正确区分单 extent 和多 extent 情况。

2. **边界检查修正**：旧的边界检查使用 `filename + direntry->len - 1` 与 `tail` 比较，仅检查文件名本身是否越界，忽略了文件名后的 filetype/tag 字节。修正后使用 `filename + direntry->len + 1` 与 `end`（正确排除 leaf 区域后的边界）比较。

**变更范围**：所有变更均位于 `grub-core/fs/xfs.c` 文件内的 `static` 函数 `grub_xfs_iterate_dir` 中。该函数通过 `GRUB_MOD_INIT(xfs)` → `grub_fs_register(&grub_xfs_fs)` → `grub_xfs_fs.dir` → `grub_xfs_iterate_dir` 链路被调用，属于 GRUB 文件系统驱动模块内部实现。

**兼容性判定**：未检测到兼容性变更。理由如下：

- 所有 5 个候选均为 `static` 函数内的内部实现细节，不触及公共 API/ABI 接口
- 新结构体 `grub_xfs_dir_leaf_entry` 仅在 `.c` 文件内定义，不在任何 public header 中
- 无 CLI 选项、配置文件、环境变量、导出符号、协议或系统接口变更
- 边界检查从 `-1` 收紧到 `+1` 仅影响损坏文件系统的检测行为（正确拒绝原本会被错误接受的 corrupt entry），对合法 XFS 文件系统无任何差异
- 多 extent 修复使原本无法工作的功能恢复正常，属于缺陷修复而非行为变更
- 有效 profile (`grub2`) 明确排除了 "static functions in .c files unless reachable from a public surface" 和 "purely internal refactors without exported, CLI, config, protocol, or test-reachable behavior"
- 虽然该 static 函数可通过模块注册链路被到达，但其行为变更不构成可观察的外部兼容性风险
