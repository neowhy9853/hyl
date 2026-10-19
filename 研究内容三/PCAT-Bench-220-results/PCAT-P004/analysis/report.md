# PCA 兼容性变更分析报告

**仓库**: `/home/soong/pca_benchmark/_repos/kernel`  
**基线**: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`  
**补丁**: `c6d4181a1e8281b4e446ba83aa8eb06021cafdc7`（seeded patch 标识，不作为可解析 commit 使用）  
**Profile**: `kernel_6_6`  
**补丁状态**: 已从基线创建隔离 worktree 并成功应用 `patch.patch`

## 概要

| 指标 | 数量 |
|---|---:|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 确认兼容性变更 | 1 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## PCA-0001：公开 sysctl 输入上限收紧

- **类型**: `INPUT_CONTRACT_CHANGE`
- **测试优先级**: HIGH
- **置信度**: 0.99
- **影响接口**: `CTL_MAXNAME`
- **位置**: `include/uapi/linux/sysctl.h:30-33`

### 变更前行为

用户态源码包含 `<linux/sysctl.h>` 时得到 `CTL_MAXNAME == 10`。相邻公开注释将其定义为 `struct __sysctl_args.nlen` 可接受的最大路径分量数。

### 变更后行为

同一源码针对补丁后安装头文件重编译时得到 `CTL_MAXNAME == 8`。依赖该宏的数组容量、长度边界检查和编译期断言随之从 10 收紧为 8。

### 兼容性影响

该宏位于稳定的 `include/uapi/**` 公共接口中。既有消费者原先可以依据公开常量处理 9 或 10 个路径分量，重编译后会拒绝、截断这些输入，或因静态断言失败而无法编译。因此这是公开输入契约收紧，而不是纯内核内部实现变化。

补丁后精确符号检索仅找到该头文件定义，没有发现内核执行代码引用 `CTL_MAXNAME`。因此本分析只确认编译期/重编译消费者可观察的契约变化，不宣称已构建二进制或当前内核运行时的 sysctl 系统调用结果发生变化。

### 证据

```c
-#define CTL_MAXNAME 10        /* how many path components do we allow in a
+#define CTL_MAXNAME 8         /* how many path components do we allow in a
                                   call to sysctl?   In other words, what is
                                   the largest acceptable value for the nlen
                                   member of a struct __sysctl_args to have? */
```

### 静态调用链

`static_call_chains` 为 `[]`。C AST 依赖检查确认当前环境缺少 `tree_sitter`，且目标是宏声明而非函数；按分析规则未回退到 grep/正则构造调用链。

### 复核与测试建议

分别执行 before/after `headers_install`，使用两套安装头文件编译同一 C 探针，比较宏值、由宏决定的数组容量和 8/9/10 边界判断；另用要求 `CTL_MAXNAME >= 9` 的既有消费者静态断言验证源码兼容性。宏声明不是可执行行，不应虚构 runtime gcov 命中。
