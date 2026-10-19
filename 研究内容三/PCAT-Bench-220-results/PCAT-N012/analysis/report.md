# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/dnsmasq
**基线**: 65adc53130a774f84ea945f17030f3f0b07b3d78
**补丁**: Fix FTBFS with nettle 4.0 (4070a74862c3c956a676d2b931ff186e14f5d9f5)
**Profile**: dnsmasq

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 5 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

该补丁**不存在兼容性变更**。补丁目标为修复 nettle 4.0 的 FTBFS（build failure），属于上游库 API 演进的适应性修改。

### 变更摘要

| Hunk | 文件 | 变更类型 | 分析结论 |
|------|------|---------|---------|
| HUNK-0001/0002 | src/crypto.c | `null_hash_digest` 增加 `#if MIN_VERSION(4,0)` 条件编译 | **内部函数**（static），仅适配 nettle 4.0 的 digest 回调签名变化，无外部影响 |
| HUNK-0003 | src/crypto.c | 新增 `nettle_digest_wrapper()` 函数 | **新增公共函数，非破坏性**（additive），用于统一 digest 调用接口，跨 nettle 版本保持行为一致 |
| HUNK-0004 | src/dnsmasq.h | 新增 `nettle_digest_wrapper()` 声明 | **新增声明，非破坏性**，仅新增函数原型 |
| HUNK-0005 | src/dnssec.c | `validate_rrset()` 中 digest 调用改为 wrapper | **内部行为替换**，行为完全等价，`hash->digest_size` 与 `length` 参数值相同 |

### 判定依据

1. `null_hash_digest` 为 `static` 内部函数，仅通过函数指针转型后在 `null_hash` 结构体中使用，不构成公共 API。
2. `nettle_digest_wrapper` 为新增包装函数，保持完整向后兼容性：旧 nettle 版本路径使用旧 digest 签名，新 nettle 版本路径使用新签名。
3. `validate_rrset` 调用替换为 wrapper 后，传入参数完全相同（`hash->digest_size`），行为无变化。
4. 所有变更均为编译期条件编译，运行时行为在各自 nettle 版本内保持一致。

## 测试建议

由于已确认零兼容性变更，无需进行定向兼容性测试。

**产物已写入** `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/4070a7/`
