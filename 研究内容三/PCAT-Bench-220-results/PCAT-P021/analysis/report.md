# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/vim
**基线**: 203210e48b75e8af501c4f40f91671c4a8556f28
**补丁**: 16f562b4e (patch 9.2.0817: crash when building a stacktrace during an autocommand)
**Profile**: vim

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 2 |
| 兼容性变更 | 2 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 2 |

---

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.7
- **影响接口**: estack_sfile — `<sfile>` expansion in ESTACK_SCRIPT context
- **旧代码位置**: src/scriptfile.c:166-175
- **新代码位置**: src/scriptfile.c:166-176
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
在 ESTACK_SCRIPT 路径下遍历执行栈时，如果遇到 es_info.aucmd == NULL 的 ETYPE_AUCMD 条目（尚未匹配模式的自动命令），调用 acp_script_ctx(entry->es_info.aucmd) 会解引用空指针，导致 Vim 崩溃。

### 变更后行为
在调用 acp_script_ctx() 之前先检查 entry->es_info.aucmd != NULL；如果为 NULL，def_ctx 被设为 NULL，随后的 def_ctx != NULL 守卫使得函数返回 NULL 而非崩溃。

### 兼容性影响
这是一个崩溃修复。旧行为（崩溃）不是有效契约。新行为在特定边界条件下优雅返回 NULL。不破坏向后兼容性：所有正常调用方不受影响。

### 证据
```c
sctx_T *def_ctx = entry->es_type == ETYPE_UFUNC
              ? &entry->es_info.ufunc->uf_script_ctx
              : entry->es_info.aucmd != NULL
                  ? acp_script_ctx(entry->es_info.aucmd) : NULL;

return def_ctx != NULL && def_ctx->sc_sid > 0
           ? vim_strsave(SCRIPT_ITEM(def_ctx->sc_sid)->sn_name)
           : NULL;
```

### 静态调用链
无（未开启调用链分析）

### 复核建议
无需人工复核。这是一个直接的 NULL 守卫添加，修复了崩溃问题。

### 测试建议
使用 test_stacktrace.vim 中新增的 Test_getstacktrace_during_autocmd_prompt 测试。额外测试 expand('<sfile>') 在相同自动命令场景下的行为。

---

## PCA-0002: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.7
- **影响接口**: stacktrace_create — getstacktrace() 函数和 v:stacktrace 变量
- **旧代码位置**: src/scriptfile.c:322-332
- **新代码位置**: src/scriptfile.c:323-337
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
在 stacktrace_create() 中处理 ETYPE_AUCMD 条目时，无条件解引用 entry->es_info.aucmd。如果 aucmd 为 NULL（尚未匹配模式的自动命令），导致空指针解引用崩溃。

### 变更后行为
先检查 entry->es_info.aucmd != NULL 再调用 acp_script_ctx()。如果为 NULL，sctx 设为 NULL，filepath 设为空字符串 ""，不增加 lnum。栈回溯条目仍然推入列表但使用空 filepath 和基础 lnum。

### 兼容性影响
这是一个崩溃修复。getstacktrace() / v:stacktrace 现在在未匹配自动命令场景下优雅返回数据而非崩溃。不破坏向后兼容性：之前场景无法恢复（崩溃），现在产生有效输出。

### 证据
```c
// The autocmd may not have a matching pattern yet, in which case
// es_info.aucmd is still NULL.
sctx_T *sctx = entry->es_info.aucmd != NULL
                   ? acp_script_ctx(entry->es_info.aucmd) : NULL;
char_u *filepath = sctx != NULL && sctx->sc_sid > 0 ?
                       get_scriptname(sctx->sc_sid) : (char_u *)"";

if (sctx != NULL)
    lnum += sctx->sc_lnum;
stacktrace_push_item(l, NULL, entry->es_name, lnum, filepath);
```

### 静态调用链
无（未开启调用链分析）

### 复核建议
无需人工复核。直接的 NULL 守卫添加修复了崩溃问题。新增的 Test_getstacktrace_during_autocmd_prompt 测试覆盖了报告的场景。

### 测试建议
运行 test_stacktrace.vim 中的 Test_getstacktrace_during_autocmd_prompt 测试。同时运行现有的 Test_getstacktrace、Test_getstacktrace_event、Test_vstacktrace 和 Test_stacktrace_vim9 测试以确保无回归。

---

## 测试结果摘要

测试在 disposable worktree 中进行，使用 `--with-features=huge --enable-terminal --disable-gui` 配置，`-O0 -g --coverage` 编译选项。

### 补丁后构建
- 全部 5 个 test_stacktrace 测试通过（0 失败，耗时 1.53s）
- PCA-0002 (stacktrace_create) 变更代码行：100% gcov 覆盖
- PCA-0001 (estack_sfile) ESTACK_SCRIPT 路径：现有测试未覆盖（需要特定触发条件）

### 基线对比
- 原始 4 个测试在基线和补丁后构建均通过
- 基线构建在新测试 Test_getstacktrace_during_autocmd_prompt 上失败（RunVimInTerminal 失败）

### 产物位置
- 分析产物：/home/soong/pca_benchmark/_repos/vim/pca-results/16f562/
- 测试产物：/home/soong/pca_benchmark/_repos/vim/pca-results/16f562/compatibility-testing/
- Worktree 状态：已清理
