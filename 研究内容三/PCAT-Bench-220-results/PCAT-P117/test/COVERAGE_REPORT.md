# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `204a6ddfb3bb456929e7c364e1e8d6ee1928b471` |
| 仓库 | `/data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2` |
| 基线 | `6b64f297e5906feb295dcc6fb5046368f5f3e95b` |
| Profile | `grub2` |
| 执行状态 | `partial` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：5个高优先级兼容性发现均已执行静态ABI布局验证。4个通过（PCA-0002/3/4/5），1个部分通过（PCA-0001）。linux_kernel_params结构体完全重构，字段从扁平布局移至嵌套子结构，字段名变更（lfb_width→screen_info.lfb_width, have_vga→screen_info.orig_video_isVGA等）。sizeof/offsetof验证确认新布局与Linux内核v6.13.7 boot_params一致，但该变更与旧版Linux内核不兼容，属于破坏性启动协议变更。gcov行级覆盖率不适用于纯头文件结构体定义。动态运行时测试受限于QEMU环境不可用，无法执行完整的内核启动验证。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 6 |
| 测试 findings | 5 |
| 规划入口 | 5 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 1 |
| 执行输入 | 1 |
| 契约通过 | 4 |
| 契约违约 | 1 |
| 契约跳过 | 0 |
| 补丁可执行行 | 0 |
| 已覆盖行 | 0 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (GCC) 14.2.1` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Build environment lacks QEMU for runtime boot testing
- Static ABI layout verification performed via sizeof/offsetof checks against real GRUB headers
- Full grub2 build not performed due to platform-specific target requirements (i386-pc)

## Finding 测试结果

### PCA-0001: ABI_CHANGE

- **优先级**: `high`
- **状态**: `partial`
- **目标**: `include/grub/i386/linux.h:190-506 (linux_kernel_params)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | passed | `test-entry-work/abi_verify_real` | `./test-entry-work/abi_verify_real` | PASSED (linux_kernel_params key offsets verified) | offsetof results printed for all key fields |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| binary_abi_compatibility | breached | linux_kernel_params struct layout completely restructured: flat fields moved to sub-structs (screen_info, apm_bios_info, ist_info, olpc_ofw_header, hdr). Verified key offsets: screen_info@0, apm_bios_info@0x40, ist_info@0x60, acpi_rsdp_addr@0x70, olpc_ofw_header@0xb0, edid_info@0x140, efi_info@0x1b8, hdr@0x1f1, e820_table@0x2d0. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- Header-only struct definition: line-level gcov not applicable
- Static offsetof verification confirms new struct layout matches Linux kernel 6.13.7 boot_params
- Runtime validation requires QEMU with bootable Linux kernel

### PCA-0002: ABI_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `include/grub/i386/linux.h:207-212 (grub_boot_e820_entry)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0002 | passed | `test-entry-work/abi_verify_real` | `./test-entry-work/abi_verify_real` | sizeof(grub_boot_e820_entry)=20, offsets ok | grub_boot_e820_entry sizeof/offsetof printed |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| binary_abi_compatibility | passed | grub_boot_e820_entry layout correct: sizeof=20, addr@0 (8B), size@8 (8B), type@16 (4B). Matches Linux kernel boot_e820_entry. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- Struct renamed from grub_e820_mmap to grub_boot_e820_entry
- Field names addr/size/type preserved, only type name changed
- e820_map -> e820_table field rename in linux_kernel_params also confirmed

### PCA-0003: ABI_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `include/grub/i386/linux.h:129-398 (grub_screen_info)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0003 | passed | `test-entry-work/abi_verify_real` | `./test-entry-work/abi_verify_real` | grub_screen_info layout matches kernel upstream | grub_screen_info offsetof results printed |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| binary_abi_compatibility | passed | grub_screen_info verified: sizeof=64=0x40. Key offsets: orig_video_isVGA@15, lfb_width@0x12, lfb_height@0x14, lfb_depth@0x16, lfb_base@0x18, lfb_size@0x1c, lfb_linelength@0x24, red_size@0x26, capabilities@0x36, ext_lfb_base@0x3a. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- grub_screen_info is new sub-struct type added to public header
- All offsets verified against Linux kernel screen_info struct expectations

### PCA-0004: ABI_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `include/grub/i386/linux.h:153-204 (linux_i386_kernel_header)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0004 | passed | `test-entry-work/abi_verify_real` | `./test-entry-work/abi_verify_real` | Compatibility detection: struct field changes verified | grub_setup_header offsetof results showing field layout changes |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| binary_abi_compatibility | passed | grub_setup_header (linux_i386_kernel_header) layout change confirmed: sizeof=123. New fields: ext_loader_ver/ext_loader_type (replaces old pad1), relocatable_kernel (renamed from relocatable), kernel_info_offset (new addition). Old pad1(2B) split into two 1B fields. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- pad1(grub_uint16_t) replaced by ext_loader_ver(grub_uint8_t)+ext_loader_type(grub_uint8_t)
- relocatable renamed to relocatable_kernel
- kernel_info_offset field added at end of struct

### PCA-0005: SIDE_EFFECT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `grub-core/loader/i386/linux.c:234-340 (grub_linux_setup_video)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0005 | passed | `test-entry-work/abi_verify_real` | `./test-entry-work/abi_verify_real` | linux_kernel_params field offsets confirmed changed from flat to nested layout | offsetof results confirm screen_info.* sub-struct field locations |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| side_effect_manifest_stability | passed | Confirmed: grub_linux_setup_video now writes to screen_info.lfb_width (offset 18 from linux_kernel_params start) instead of old params->lfb_width (different old offset). Video info fields now inside screen_info sub-struct, changing the memory locations where boot parameters are written. |

- **覆盖率**: 0/0 (0.00%)
- **未覆盖行**: -
- grub_linux_setup_video's writes target different memory offsets in linux_kernel_params
- Old flat field params->lfb_width, params->have_vga no longer exist
- New screen_info.lfb_width, screen_info.orig_video_isVGA at different offsets
- Dynamic runtime verification requires QEMU boot test

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-0001 | QEMU system emulator not available in host environment. Full runtime boot testing requires booting Linux kernel via GRUB in a VM. | Set up QEMU VM with disk image, install patched GRUB, boot Linux kernel to verify boot parameter transfer |
| build | BLOCKER-0002 | Full grub2 build requires autotools bootstrap, configure for i386-pc target, and platform toolchain. Not performed as build was not the primary test goal for header-only ABI changes. | Run ./bootstrap && ./configure --target=i386 --with-platform=pc && make to build patched GRUB with gcov instrumentation |
| finding | BLOCKER-0003 | PCA-0006 (LINUX_LOADER_ID_* macros) not targeted for testing as medium priority. New macro definitions are additive and non-breaking. | No action required; medium priority finding deferred |

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `phase4_execution/contract_verification.json` |
| coverage_data | `test-entry-work/abi_verify_real.c.gcov` |
| execution_results | `phase4_execution/abi_verify_output.txt` |
| impact_map | `phase1_impact/impact_map.json` |
| report | `COVERAGE_REPORT.md` |
| test_entries | `test-entry-work/test-entries.json` |
| test_entry_tasks | `test-entry-tasks.json` |
| test_inputs | `phase3_inputs/test_inputs.json` |

## 建议

- 在QEMU环境中执行完整GRUB构建和Linux内核启动测试
- 使用pahole逐字节比较struct linux_kernel_params与内核struct boot_params
- 在i386-pc和x86_64-efi平台验证启动参数传递
- 验证grub_linux_setup_video在新布局下正确填充所有screen_info字段
- 与旧版Linux内核进行回归测试，确认不兼容范围
