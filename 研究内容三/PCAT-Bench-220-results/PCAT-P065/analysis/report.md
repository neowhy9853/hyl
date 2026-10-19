# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/haproxy
**基线**: ef191c46d7569712c538e93031fb3a6dca88defa~1 (b9fa07bd205ddd993c84e29d5b0324a84d032578)
**补丁**: ef191c4 - BUG/MINOR: acl: report "ACL" not "map" in ACL ID lookup failures
**Profile**: haproxy

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 输出格式变更 (OUTPUT_FORMAT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.9
- **影响接口**: cli_parse_del_map (CLI command)
- **旧代码位置**: src/map.c:998-1005
- **新代码位置**: src/map.c:998-1009
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为
当通过 CLI 命令 `del map` 或 `del acl` 删除条目时，如果标识符无效，错误消息总是显示 "Unknown map identifier. Please use #<id> or <file>."，无论操作的是 map 还是 ACL。

### 变更后行为
错误消息现在根据上下文区分：如果操作的是 map (PAT_REF_MAP)，显示 "Unknown map identifier."；如果操作的是 ACL (PAT_REF_ACL)，正确显示 "Unknown ACL identifier."。

### 兼容性影响
用户可见的 CLI 错误消息文本在 ACL 删除路径上发生了变化。任何解析 HAProxy CLI 错误输出来检测 "Unknown map identifier" 的脚本或自动化工具，在处理 ACL 时将无法匹配到该文本。

### 证据
```c
/* Lookup the reference in the maps. */
ctx->ref = pat_ref_lookup_ref(args[2]);
if (!ctx->ref ||
    !(ctx->ref->flags & ctx->display_flags)) {
    if (ctx->display_flags == PAT_REF_MAP)
        return cli_err(appctx, "Unknown map identifier. Please use #<id> or <file>.\n");
    else
        return cli_err(appctx, "Unknown ACL identifier. Please use #<id> or <file>.\n");
}
```

### 静态调用链
未生成（LOW 优先级，不强制）

### 复核建议
确认没有自动化或监控工具通过解析 HAProxy CLI 错误消息文本来检测 ACL 操作失败。

### 测试建议
通过 HAProxy CLI 验证：
1. `del acl` 使用无效标识符时产生 "Unknown ACL identifier"
2. `del map` 使用无效标识符时仍产生 "Unknown map identifier"

---

## 产物

- analysis.json: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/analysis.json`
- patch.diff: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/patch.diff`
- candidates.json: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/candidates.json`
