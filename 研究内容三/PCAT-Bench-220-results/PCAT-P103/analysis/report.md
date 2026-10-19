# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux
**基线**: dfe079bb6ab38091761eb4bd64071ce67a44298f^ (a1b82706c233f83b62b5c633ec89ec2189460516)
**补丁**: dfe079bb6ab38091761eb4bd64071ce67a44298f
**Profile**: kernel_6_6
**分析模式**: normal

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 3 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 补丁描述

`btrfs: fix compat mask in error messages in btrfs_check_features()`

修复由 commit d7f67ac9a928 ("btrfs: relax block-group-tree feature dependency checks") 引入的回归问题：在 `btrfs_check_features()` 的三处错误消息中，修复了传递给 `btrfs_err()` 的参数，确保错误消息打印的是未知/不支持的兼容性标志位，而非全部标志位。

变更仅涉及 `fs/btrfs/disk-io.c` 一个文件，三处修改均为：
- 第 3094 行：`incompat` → `incompat & ~BTRFS_FEATURE_INCOMPAT_SUPP`
- 第 3126 行：`compat_ro` → `compat_ro_unsupp`
- 第 3139 行：`compat_ro` → `compat_ro_unsupp`

## 兼容性影响判定

**未检测到兼容性变更。**

`btrfs_check_features()` 是 btrfs 模块的内部函数：
- 未通过 EXPORT_SYMBOL 导出
- 声明于内部头文件 `fs/btrfs/disk-io.h`（非 UAPI 头文件）
- 仅有 2 个调用方，均为 btrfs 模块内部路径：
  - `fs/btrfs/super.c:1716` — 重挂载路径
  - `fs/btrfs/disk-io.c:3323` — 初始挂载路径
- 变更仅影响 `btrfs_err()` 的 kernel log/dmesg 诊断输出中打印的十六进制值
- 控制流、返回值、函数签名均无变化
- kernel log 消息不是稳定的 ABI

## 未确认的候选

| Hunk | 文件 | 行号 | 变更 | 拒绝原因 |
|------|------|------|------|----------|
| HUNK-0001 | fs/btrfs/disk-io.c | 3094 | `incompat` → `incompat & ~BTRFS_FEATURE_INCOMPAT_SUPP` | 内部诊断消息，非公共接口 |
| HUNK-0002 | fs/btrfs/disk-io.c | 3126 | `compat_ro` → `compat_ro_unsupp` | 内部诊断消息，非公共接口 |
| HUNK-0003 | fs/btrfs/disk-io.c | 3139 | `compat_ro` → `compat_ro_unsupp` | 内部诊断消息，非公共接口 |

## 产物目录

所有分析产物已写入：
`/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P043/`
