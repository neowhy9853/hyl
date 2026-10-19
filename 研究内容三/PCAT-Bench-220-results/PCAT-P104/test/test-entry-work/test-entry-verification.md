# PCA Test Entry Verification Report

## Summary

| Status | Count |
|--------|-------|
| runnable_verified | 0 |
| ran_expected_signal_mismatch | 0 |
| static_valid_not_run | 1 |
| needs_refinement | 0 |
| needs_env | 0 |
| unsafe_not_run | 0 |

## PCA-TE-0001 / PCA-0001 — SIDE_EFFECT_CHANGE (static_valid_not_run)

**Entry**: `test-entry-work/PCA-0001/ncm_gadget_reproducer.sh`
**Type**: synthetic_harness (shell script for kernel VM testing)

**Reason for not running**: Kernel VM testing requires a QEMU VM environment with:
- Two kernel builds (baseline at `d68b621bb5a48051932f1017a6e1bc9b18f854d0` and patched at `36c41e9724c9a7a7cda37f5a4e9d94f25c8031c4`)
- Kernel config: `CONFIG_USB_GADGET=y`, `CONFIG_USB_CONFIGFS=y`, `CONFIG_USB_CONFIGFS_NCM=y`
- `dummy_hcd.ko` module for USB gadget emulation
- `libcomposite.ko`, `u_ether.ko`, `usb_f_ncm.ko` modules
- configfs mounted at `/sys/kernel/config`
- root privileges for gadget operations and udev monitoring

**Entry validity**: The reproducer script is structurally valid:
- Defines setup/cleanup for NCM gadget via configfs
- Monitors sysfs path changes during bind/unbind cycles
- Validates net_device persistence
- Provides uevent monitoring instructions
- Has proper error handling and logging

**Required infrastructure to execute**: QEMU VM + kernel builds + USB gadget emulation
