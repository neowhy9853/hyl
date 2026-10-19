# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/openldap
**基线**: HEAD (595e7ea6f3)
**补丁**: ebbb93d54b (ITS#10543 slapd-read: plug leak)
**Profile**: openldap

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 分析结论

**无兼容性变更。**

该补丁是 OpenLDAP ITS#10543 的内存泄漏修复，变更仅涉及 `tests/progs/slapd-read.c` 中的一行：

```diff
-		free( values );
+		ldap_charray_free( values );
```

### 变更分析

- **文件位置**: `tests/progs/slapd-read.c`（测试工具，非发布二进制/库）
- **变更内容**: `values` 是一个 `char **` 数组，其元素由 `ldap_get_dn()` 分配的 DN 字符串填充。原代码使用 `free(values)` 只释放外层数组，导致每个 DN 字符串泄漏。替换为 `ldap_charray_free(values)` 后正确释放数组及所有元素。
- **API 影响**: 无。该文件是测试程序，不导出任何公共 API。
- **ABI 影响**: 无。
- **CLI/配置影响**: 无。
- **协议影响**: 无。
- **输出格式影响**: 无（标准错误输出不变）。

### 结论

这是一次纯内部的 bugfix，没有任何外部可观察的兼容性影响。无需进行定向动态测试。

## 产物目录

- 产物已写入 `/home/soong/pca_benchmark/_repos/openldap/pca-results/ebbb93/`
