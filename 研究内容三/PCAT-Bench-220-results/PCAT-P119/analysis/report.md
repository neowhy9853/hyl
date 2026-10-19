# PCA 兼容性变更分析报告

**仓库**: https://github.com/rhboot/grub2
**基线**: ad0386bd7c2075a5fc72f99bb99f9380519d20a4
**补丁**: e2a1a337e21d28dcd1d9d7fe25aff62f4e3bdf98
**Profile**: grub2

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 4 |
| 兼容性变更 | 4 |
| 高优先级测试 | 2 |
| 中优先级测试 | 1 |
| 低优先级测试 | 1 |

## 补丁摘要

本补丁修改 `grub-core/loader/efi/chainloader.c` 中的 `grub_cmd_chainloader` 函数，移除对 `grub_linuxefi_secure_validate()` 的显式调用，改为仅通过 `grub_efi_get_secureboot()` 检查 SecureBoot 状态来决定启动路径。主要目的是避免 chainloader 镜像被 shim-lock verifier 重复校验，消除双重 TPM PCR 测量。

---

## PCA-0001: TPM PCR 测量行为变化

- **测试优先级**: HIGH
- **置信度**: 0.95
- **类型**: SIDE_EFFECT_CHANGE
- **影响接口**: grub_cmd_chainloader (CLI command)
- **旧代码位置**: grub-core/loader/efi/chainloader.c:1082-1090
- **新代码位置**: grub-core/loader/efi/chainloader.c:1081-1087

### 变更前行为
调用 `grub_linuxefi_secure_validate()` 对已加载的 chainloader 镜像进行第二次 shim-lock verify 校验，导致 TPM PCR 被扩展两次（一次由 verifier 框架在 `grub_file_open` 时触发，一次由该显式调用触发）。

### 变更后行为
完全移除 `grub_linuxefi_secure_validate()` 显式调用，chainloader 镜像的 shim-lock verify 仅由 verifier 框架在 `grub_file_open()` 时执行一次，TPM PCR 仅被扩展一次。

### 兼容性影响
PCR TPM 事件日志发生变化。依赖 TPM 远程证明（remote attestation）或测量启动（measured boot）的系统将对 chainloader 镜像观察到不同的 PCR 值，可能破坏既有的 PCR 策略和完整性校验逻辑。

### 证据
```c
-  rc = grub_linuxefi_secure_validate((void *)(unsigned long)address, fsize);
-  grub_dprintf ("chain", "linuxefi_secure_validate: %d\n", rc);
-  if (rc > 0)
+  if (grub_efi_get_secureboot () == GRUB_EFI_SECUREBOOT_MODE_ENABLED)
```

### 测试建议
在启用 SecureBoot 的 QEMU/VM 环境中执行 chainloader 命令加载 EFI 镜像，捕获并对比修复前后的 TPM 事件日志（PCR 扩展记录），验证 PCR 值的变化符合预期。

---

## PCA-0002: 启动路径选择标准变化

- **测试优先级**: HIGH
- **置信度**: 0.90
- **类型**: SIDE_EFFECT_CHANGE
- **影响接口**: grub_cmd_chainloader (CLI command)
- **旧代码位置**: grub-core/loader/efi/chainloader.c:1082-1098
- **新代码位置**: grub-core/loader/efi/chainloader.c:1081-1095

### 变更前行为
启动路径选择依据 `grub_linuxefi_secure_validate()` 的返回值：rc > 0 时使用 `grub_secureboot_chainloader_boot`（调用 `handle_image` 进行 PE 校验和重定位，然后 `start_image`）；rc == 0 时使用 `grub_chainloader_boot`（先 `LoadImage` 再 `start_image`）。当 SecureBoot 关闭但 shim 存在时，shim 可能仍验证成功返回 rc > 0，导致使用 `handle_image` 路径。

### 变更后行为
启动路径选择仅依据 SecureBoot 状态：SecureBoot 开启时使用 `grub_secureboot_chainloader_boot`，否则始终使用 `grub_chainloader_boot`。不再调用 `grub_linuxefi_secure_validate()`。

### 兼容性影响
当 SecureBoot 关闭但 shim 仍安装时，旧代码可能选择 `grub_secureboot_chainloader_boot` 路径（调用 `handle_image` + `LoadImage` + `StartImage`），新代码始终选择 `grub_chainloader_boot` 路径（直接 `LoadImage` + `StartImage`）。`handle_image` 额外进行 PE 头部校验、重定位等处理，其缺失可能影响某些非标准 EFI 镜像的启动行为。

### 证据
```c
-  rc = grub_linuxefi_secure_validate((void *)(unsigned long)address, fsize);
-  grub_dprintf ("chain", "linuxefi_secure_validate: %d\n", rc);
-  if (rc > 0)
+  if (grub_efi_get_secureboot () == GRUB_EFI_SECUREBOOT_MODE_ENABLED)
     {
       ...
       grub_loader_set (grub_secureboot_chainloader_boot, ...);
       return 0;
     }
-  else if (rc == 0)
+  else
     {
       ...
       grub_loader_set (grub_chainloader_boot, ...);
```

### 测试建议
在 SecureBoot OFF + shim 安装环境中测试 chainloader 启动多种 EFI 镜像，观察启动行为是否与修复前一致。

> **需要人工复核**: 是

---

## PCA-0003: 错误处理路径简化

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **类型**: ERROR_EXCEPTION_CHANGE
- **影响接口**: grub_cmd_chainloader (CLI command)
- **旧代码位置**: grub-core/loader/efi/chainloader.c:1092-1107
- **新代码位置**: grub-core/loader/efi/chainloader.c:1089-1103

### 变更前行为
`grub_linuxefi_secure_validate()` 返回负值时，代码通过 fall-through 进入 `fail` 标签，执行资源清理和错误返回。三段分支：rc > 0 安全启动路径、rc == 0 常规路径、rc < 0 失败路径。

### 变更后行为
二段分支：SecureBoot 开启走安全启动路径，否则走常规路径。依赖 verifier 框架在 `grub_file_open()` 阶段截获加载失败。

### 兼容性影响
虽然 commit 声称在 SecureBoot 下该错误路径已不可达，但代码的契约语义已发生变化。如果将来存在非标准 verifier 模块配置，缺少显式错误路径可能导致行为不同。

### 证据
```c
-  else if (rc == 0)
+  else
     { ... }
-  // -1 fall-through to fail
```

---

## PCA-0004: 调试日志输出移除

- **测试优先级**: LOW
- **置信度**: 0.95
- **类型**: OUTPUT_FORMAT_CHANGE
- **影响接口**: grub_cmd_chainloader (CLI command)
- **旧代码位置**: grub-core/loader/efi/chainloader.c:1082-1090
- **新代码位置**: grub-core/loader/efi/chainloader.c:1081-1087

### 变更前行为
输出 `grub_dprintf` 调试日志 `"linuxefi_secure_validate: %d\n"`，包含验证返回值。

### 变更后行为
该调试日志被完全移除。

### 兼容性影响
依赖该调试日志进行启动故障排查的开发者或自动化脚本可能受到影响。

### 证据
```c
-  grub_dprintf ("chain", "linuxefi_secure_validate: %d\n", rc);
```

---
