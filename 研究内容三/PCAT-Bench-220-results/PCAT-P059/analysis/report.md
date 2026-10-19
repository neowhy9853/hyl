# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/dnsmasq
**基线**: c090f1d
**补丁**: f603a4f920e6953b11667d424956fd47373870e9
**Profile**: dnsmasq

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 17 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.75
- **影响接口**: dnssec_validate_reply (DNSSEC wildcard validation)
- **旧代码位置**: src/dnssec.c:2238-2280
- **新代码位置**: src/dnssec.c:2237-2279
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
当查询 wildcard 名称本身（如 *.example.com）且存在通配符记录时，`validate_rrset()` 返回 `STAT_SECURE_WILDCARD`，触发 `prove_non_existence()` 检查展开后的名称是否存在实际记录。这种对 wildcard 名称本身的 non-existence 检查是错误的，可能导致 DNSSEC 验证失败（BOGUS → SERVFAIL）。

### 变更后行为
`validate_rrset()` 现在直接返回 `STAT_SECURE`（`STAT_SECURE_WILDCARD` 已移除）。通配符展开状态通过 `wild_offset`（int 类型）传递。新增保护性检查：当名称已经是通配符模式（`name_labels - labels == 1 && name_start[0] == '*' && name_start[1] == '.'`）时，跳过通配符展开处理。在 `dnssec_validate_reply()` 中，当 `wild_offset == 0` 时正确跳过 non-existence 检查。

### 兼容性影响
对 wildcard 名称本身的 DNSSEC 验证结果发生变化：之前可能因错误的 non-existence 检查返回 BOGUS/SERVFAIL，现在正确验证为 SECURE。这是一个 RFC 4035 合规性 bug fix。

### 证据
```c
// src/dnsmasq.h: STAT_SECURE_WILDCARD removed, values shifted
#define STAT_OK                 0x70000
#define STAT_ABANDONED          0x80000
#define STAT_ASYNC              0x90000
```

```c
// src/dnssec.c: New guard in validate_rrset()
/* If the name is already the wildcard, we are not going to change it. */
if (labels < name_labels &&
    !(name_labels - labels == 1 && name_start[0] == '*' && name_start[1] == '.'))
```

```c
// src/dnssec.c: Return code simplified
if (verify(...))
  return STAT_SECURE;
```

```c
// src/dnssec.c: wild_offset check instead of STAT_SECURE_WILDCARD
if (wild_offset != 0 &&
    ((rc_nsec = prove_non_existence(...))) != 0)
  return (rc_nsec & DNSSEC_FAIL_WORK) ? STAT_ABANDONED : (STAT_BOGUS | rc_nsec);
```

### 静态调用链
- dnssec_validate_reply() → validate_rrset() [wildcard guard]
- dnssec_validate_reply() → prove_non_existence() [wild_offset check]
- prove_non_existence() → prove_non_existence_nsec3() [wild_offset parameter]

### 复核建议
验证修复正确处理：(1) *.example.com 的通配符查询，(2) 存在实际 a.example.com 记录时的通配符查询，(3) 不存在 a.example.com 记录时的通配符查询。

### 测试建议
构建支持 DNSSEC 的 dnsmasq，配置双签名的测试域名和通配符记录，分别查询 *.example.com 和 a.example.com 验证 DNSSEC 验证行为。

---

## 测试结果

测试产物目录: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/f603a4f9/compatibility-testing/`

- STATUS: **partial** (DNSSEC wildcard 验证需要受控 DNSSEC 测试环境)
- Before/After 二进制均构建成功，基本转发模式行为一致
- gcov: dnssec.c 总体覆盖率 10.27% (114/1110 行)
- 补丁行覆盖率: 0% (需要 DNSSEC 签名响应触发)
- 完整 DNSSEC 验证测试需要搭建 BIND/Knot 权威服务器并配置 trust-anchor

产物已写入 `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/f603a4f9/`。
