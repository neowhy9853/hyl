# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/cpython
**基线**: 9c23f3452df96dede49d82d7f957343364182b35
**补丁**: PCAT-N016 — gh-149156: Fix perf trampoline crash after fork
**Profile**: cpython

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 4 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

本次补丁**不引入任何外部可见兼容性变更**。补丁修复了 perf trampoline 在 `os.fork()` 后的间歇性崩溃问题（gh-149156）。

### 变更摘要

| Hunk | 文件 | 判定 | 原因 |
|------|------|------|------|
| HUNK-0001 | `Misc/NEWS.d/.../...rst` | 非兼容性变更 | 纯文档（NEWS 条目） |
| HUNK-0002 | `Python/perf_trampoline.c` | 非兼容性变更 | 内部重构：提取 `perf_trampoline_clear_code_watcher()`，均为 `static` 函数 |
| HUNK-0003 | `Python/perf_trampoline.c` | 非兼容性变更 | `perf_trampoline_reset_state()` 新定义，`static` 函数 |
| HUNK-0004 | `Python/perf_trampoline.c` | 非兼容性变更 | Bug fix：`_PyPerfTrampoline_AfterFork_Child()` 中不再释放 code arenas |

### 关键判定依据（HUNK-0004）

1. **函数定位**：`_PyPerfTrampoline_AfterFork_Child` 声明在 `Include/internal/pycore_ceval.h`（**内部头文件**），`_Py` 前缀在 CPython 惯例中标识内部/私有 API。
2. **Profile 忽略规则**：cpython profile 的 `ignore_patterns` 明确排除：
   - `_ prefixed symbols unless explicitly exported`
   - `static functions in .c files unless reachable from a public surface`
   - `private/internal headers unless installed or included by public headers`
3. **变更本质**：Bug fix — fork 后子进程不再调用 `free_code_arenas()`，保留旧 arenas 映射，因为子进程可能需要通过 fork() 时 C 栈上的 trampoline frames 返回。彻底清除 code watcher 后重新 Init。
4. **Surface 误报说明**：`user_visible_output` surface 在 HUNK-0004 上为模式匹配误报（`PyStatus_Error` 含 "error" 模式）。实际变更不涉及任何输出逻辑。

### 跳过测试的原因

最终 findings 为空（0 兼容性变更），按规则不执行定向测试。不得为测试虚构 finding。

---

*分析工具：PCA patch-compatibility-analysis (cpython profile)*
*补丁标识：9989a54a5333a4ce8d7893d3468d8187e6e3b13b*
*产物目录: /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max-rerun-20260722/PCAT-N016*
