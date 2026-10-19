# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/lvm2
**基线**: 7af75425ac7c735fb7713fe2b51db48e2a318a3a (629cc2a35^)
**补丁**: 629cc2a - "CI: fix compile-all.sh script"
**Profile**: lvm2
**分析模式**: normal

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 变更摘要

**文件**: `ci/compile-all.sh` (第15行)
**变更**: `TARGET=${2:-"main"}` → `TARGET=${2:-"origin/main"}`

此补丁修改 CI 脚本 `ci/compile-all.sh` 中第2个位置参数的默认值，将默认目标分支从 `"main"` 改为 `"origin/main"`。该脚本是内部 CI 基础设施的一部分，用于测试分支中所有尚未合入目标分支的提交能否通过编译。

## 判定结果: ❌ 非兼容性变更

**理由**:
- `ci/compile-all.sh` 位于 `ci/` 目录，是 CI 辅助脚本，不属于 lvm2 发布的 CLI 工具、库 API、配置格式或守护进程协议
- lvm2 profile 的 `ignore_patterns` 包含 `scripts/**`，明确标记脚本类文件为非公共接口
- 变更仅影响不传第二个参数调用脚本时的默认行为，而 CI 脚本通常由 CI 系统显式指定参数调用
- 外部用户/消费者不依赖于该脚本的默认参数行为
- 不存在对公共 API、ABI、CLI、配置、协议、syscall/ioctl/procfs/sysfs/sysctl 的表面变更

## 证据

```bash
# ci/compile-all.sh (第15行)
-TARGET=${2:-"main"}
+TARGET=${2:-"origin/main"}
```

## 产物目录

所有分析产物已写入: `/home/soong/pca_benchmark/_repos/lvm2/pca-results/629cc2/`
