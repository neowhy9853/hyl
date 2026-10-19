# PCA 兼容性变更分析报告

**仓库**: https://github.com/apache/httpd
**基线**: 4701f6f3cc47ac57053cf4151bfa60dd0b86a3a3 (parent of f02c7a9b)
**补丁**: f02c7a9b8ac443daafac8e7be5828b4010fb46d8
**Profile**: httpd
**分析模式**: heavy (8 shards)

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 16 |
| 兼容性变更 | 5 |
| 高优先级测试 | 4 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

**补丁主题**: mod_dav: Allow to disable lock discovery via an DAVLockDiscovery expression (per-request). PR 66313.

---

## PCA-0001: API 签名变化

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: dav_open_propdb
- **旧代码位置**: modules/dav/main/mod_dav.h:1691-1702
- **新代码位置**: modules/dav/main/mod_dav.h:1691-1705
- **类型**: API_SIGNATURE_CHANGE

### 变更前行为
函数签名为 `dav_open_propdb(request_rec *r, dav_lockdb *lockdb, const dav_resource *resource, int ro, apr_array_header_t *ns_xlate, dav_propdb **propdb)`，参数 `int ro` 用于表示是否以只读方式打开属性数据库。

### 变更后行为
函数签名为 `dav_open_propdb(request_rec *r, dav_lockdb *lockdb, const dav_resource *resource, int flags, apr_array_header_t *ns_xlate, dav_propdb **propdb)`，参数 `int flags` 改为标志位，支持 DAV_PROPDB_NONE(0)、DAV_PROPDB_RO(1)、DAV_PROPDB_DISABLE_LOCKDISCOVERY(2)。

### 兼容性影响
DAV_DECLARE 声明的公共导出函数签名变化。参数从 `int ro` 改为 `int flags`，虽然类型兼容（都是 int），但语义变化且新增标志位 DAV_PROPDB_DISABLE_LOCKDISCOVERY。调用此 API 的外部模块、第三方 DAV provider 必须在重新编译后适配。未重新编译的二进制将因参数语义不匹配可能出现未定义行为。

### 证据
```c
// modules/dav/main/mod_dav.h:1695-1701
DAV_DECLARE(dav_error *) dav_open_propdb(
    request_rec *r,
    dav_lockdb *lockdb,
    const dav_resource *resource,
    int flags,           // 旧参数为 int ro
    apr_array_header_t *ns_xlate,
    dav_propdb **propdb);
```

### 测试建议
编译一个调用 dav_open_propdb 的外部 DAV provider 模块，验证新签名可以正常编译和运行；检查 PROPPATCH 的 DAV_PROPDB_NONE 语义是否与旧的传 0 行为一致。

---

## PCA-0002: API 签名变化

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: dav_popen_propdb
- **旧代码位置**: modules/dav/main/mod_dav.h:1705-1711
- **新代码位置**: modules/dav/main/mod_dav.h:1708-1714
- **类型**: API_SIGNATURE_CHANGE

### 变更前行为
函数签名为 `dav_popen_propdb(apr_pool_t *p, request_rec *r, dav_lockdb *lockdb, const dav_resource *resource, int ro, apr_array_header_t *ns_xlate, dav_propdb **propdb)`，参数 `int ro` 表示只读标志。

### 变更后行为
函数签名为 `dav_popen_propdb(apr_pool_t *p, request_rec *r, dav_lockdb *lockdb, const dav_resource *resource, int flags, apr_array_header_t *ns_xlate, dav_propdb **propdb)`，参数改为 `int flags` 标志位。

### 兼容性影响
DAV_DECLARE 公共导出函数签名变化。这是 dav_open_propdb 调用的底层实现函数，同样暴露给外部调用方。外部模块直接调用此函数需要适配新签名和标志位语义。

### 证据
```c
// modules/dav/main/mod_dav.h:1708-1714
DAV_DECLARE(dav_error *) dav_popen_propdb(
    apr_pool_t *p,
    request_rec *r,
    dav_lockdb *lockdb,
    const dav_resource *resource,
    int flags,           // 旧参数为 int ro
    apr_array_header_t *ns_xlate,
    dav_propdb **propdb);
```

### 测试建议
如果一个模块同时使用了这两个函数的旧签名，编译和执行 PROPFIND/PROPPATCH 请求验证行为一致。

---

## PCA-0003: ABI 兼容性变化

- **测试优先级**: HIGH
- **置信度**: 0.90
- **影响接口**: DAV_PROPDB_NONE / DAV_PROPDB_RO / DAV_PROPDB_DISABLE_LOCKDISCOVERY
- **旧代码位置**: modules/dav/main/mod_dav.h:1691-1694
- **新代码位置**: modules/dav/main/mod_dav.h:1691-1697
- **类型**: ABI_CHANGE

### 变更前行为
dav_open_propdb 和 dav_popen_propdb 的参数 `int ro` 仅支持 0（读写）和 1（只读）。

### 变更后行为
新增三个标志宏：DAV_PROPDB_NONE=0, DAV_PROPDB_RO=1, DAV_PROPDB_DISABLE_LOCKDISCOVERY=2。参数改为 `int flags` 位掩码，可组合使用。

### 兼容性影响
公共头文件中新增宏定义并改变了公共 API 参数语义。旧二进制模块编译时不知晓 DAV_PROPDB_DISABLE_LOCKDISCOVERY 标志，运行时可能不会正确传递 flags 参数。虽然 DAV_PROPDB_NONE=0 和 DAV_PROPDB_RO=1 保持了值兼容性，但二进制 ABI 已变化（不兼容编译时需要重新编译）。

### 证据
```c
// modules/dav/main/mod_dav.h:1691-1697
#define DAV_PROPDB_NONE                  0 
#define DAV_PROPDB_RO                    1
#define DAV_PROPDB_DISABLE_LOCKDISCOVERY 2 

typedef struct dav_propdb dav_propdb;

DAV_DECLARE(dav_error *) dav_open_propdb(
    request_rec *r,
```

### 测试建议
使用旧版本编译的外部 DAV provider 模块链接到新版本 httpd，验证加载时是否有警告或错误，以及运行时 PROPFIND 请求是否正常工作。

---

## PCA-0004: 输出格式变化

- **测试优先级**: HIGH
- **置信度**: 0.85
- **影响接口**: dav_insert_coreprop / PROPFIND lockdiscovery 响应
- **旧代码位置**: modules/dav/main/props.c:351-356
- **新代码位置**: modules/dav/main/props.c:353-363
- **类型**: OUTPUT_FORMAT_CHANGE

### 变更前行为
PROPFIND 请求的 lockdiscovery 属性始终返回资源的实际锁信息（如果有锁）或空（如果无锁）。

### 变更后行为
当 DAVLockDiscovery 指令配置了表达式且表达式结果为 false 时，DAV_PROPDB_DISABLE_LOCKDISCOVERY 被设置。此时 dav_insert_coreprop 在 DAV_PROPID_CORE_lockdiscovery 分支中检测到该标志后，直接返回空字符串 `value = ""`，不查询实际的锁数据库。

### 兼容性影响
WebDAV 客户端通过 PROPFIND 获取的 lockdiscovery XML 内容可能在配置 DAVLockDiscovery 后发生变化。之前返回完整锁信息的响应现在可能返回空的 lockdiscovery 属性。

### 证据
```c
// modules/dav/main/props.c:353-363
case DAV_PROPID_CORE_lockdiscovery:
    if (propdb->flags & DAV_PROPDB_DISABLE_LOCKDISCOVERY) {
        value = "";       // 新增：禁用 lock discovery 时返回空
        break;
    }

    if (propdb->lockdb != NULL) {
```

### 测试建议
配置 DAVLockDiscovery expr=false 并对加锁资源执行 PROPFIND，对比 lockdiscovery 响应与未配置时的差异；验证默认（未配置）行为无变化。

---

## PCA-0005: 配置/CLI 行为变化

- **测试优先级**: MEDIUM
- **置信度**: 0.80
- **影响接口**: DAVLockDiscovery 配置指令
- **旧代码位置**: modules/dav/main/mod_dav.c:5220-5225
- **新代码位置**: modules/dav/main/mod_dav.c:5264-5274
- **类型**: CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为
mod_dav 没有 DAVLockDiscovery 配置指令，lock discovery 始终在 PROPFIND 响应中返回实际的锁信息。

### 变更后行为
新增 DAVLockDiscovery 配置指令，接受 Apache 表达式参数（如 `DAVLockDiscovery expr=...`）。该指令作用于 per-dir 和 per-server 配置，通过表达式求值动态决定是否禁用 lock discovery。

### 兼容性影响
新增配置指令本身是向后兼容的（未配置时行为不变）。指令引入了新的配置解析路径和可能的配置错误消息。

### 证据
```c
// modules/dav/main/mod_dav.c:5264-5274
AP_INIT_TAKE1("DAVLockDiscovery", dav_cmd_davlockdiscovery, NULL,
              ACCESS_CONF|RSRC_CONF,
              "allow lock discovery by PROPFIND requests"),
```

### 测试建议
在 Apache 配置中添加 DAVLockDiscovery expr=-R 10.0.0.0/8 等典型表达式，验证配置解析正确；验证未配置时的默认行为无变化。
