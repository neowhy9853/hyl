#define _GNU_SOURCE
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

#include "/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P057/_worktrees/patched/include/grub/i386/linux.h"

static int failed = 0;

#define CHECK_SIZE(type, expected) do { \
  size_t sz = sizeof(type); \
  printf("sizeof(" #type ") = %3zu  (expected %3zu) %s\n", sz, (size_t)(expected), (sz == expected) ? "OK" : "FAIL"); \
  if (sz != expected) failed = 1; \
} while(0)

#define CHECK_OFFSET(type, field, expected) do { \
  size_t off = offsetof(type, field); \
  printf("offsetof(" #type ", %-30s) = %3zu  (expected %3zu) %s\n", #field, off, (size_t)(expected), (off == expected) ? "OK" : "FAIL"); \
  if (off != (size_t)(expected)) failed = 1; \
} while(0)

int main(void) {
  printf("=== GRUB2 Linux Boot Parameter ABI Verification (Real Headers) ===\n\n");

  printf("--- struct grub_screen_info (size=%zu) ---\n", sizeof(struct grub_screen_info));
  CHECK_OFFSET(struct grub_screen_info, orig_x, 0);
  CHECK_OFFSET(struct grub_screen_info, ext_mem_k, 2);
  CHECK_OFFSET(struct grub_screen_info, orig_video_isVGA, 15);
  CHECK_OFFSET(struct grub_screen_info, lfb_width, 0x12);
  CHECK_OFFSET(struct grub_screen_info, lfb_height, 0x14);
  CHECK_OFFSET(struct grub_screen_info, lfb_depth, 0x16);
  CHECK_OFFSET(struct grub_screen_info, lfb_base, 0x18);
  CHECK_OFFSET(struct grub_screen_info, lfb_linelength, 0x24);
  CHECK_OFFSET(struct grub_screen_info, red_size, 0x26);
  CHECK_OFFSET(struct grub_screen_info, capabilities, 0x36);
  CHECK_OFFSET(struct grub_screen_info, ext_lfb_base, 0x3a);

  printf("\n--- struct grub_boot_e820_entry (size=%zu) ---\n", sizeof(struct grub_boot_e820_entry));
  CHECK_OFFSET(struct grub_boot_e820_entry, addr, 0);
  CHECK_OFFSET(struct grub_boot_e820_entry, size, 8);
  CHECK_OFFSET(struct grub_boot_e820_entry, type, 16);

  printf("\n--- struct grub_setup_header (size=%zu) ---\n", sizeof(struct grub_setup_header));
  CHECK_OFFSET(struct grub_setup_header, setup_sects, 0);
  CHECK_OFFSET(struct grub_setup_header, boot_flag, 14);
  CHECK_OFFSET(struct grub_setup_header, jump, 16);
  CHECK_OFFSET(struct grub_setup_header, header, 18);
  CHECK_OFFSET(struct grub_setup_header, version, 22);
  CHECK_OFFSET(struct grub_setup_header, type_of_loader, 32);
  CHECK_OFFSET(struct grub_setup_header, loadflags, 33);
  CHECK_OFFSET(struct grub_setup_header, cmd_line_ptr, 44);
  CHECK_OFFSET(struct grub_setup_header, initrd_addr_max, 48);

  printf("\n--- struct linux_kernel_params ---\n");
  CHECK_OFFSET(struct linux_kernel_params, screen_info, 0);
  CHECK_OFFSET(struct linux_kernel_params, apm_bios_info, 0x40);
  CHECK_OFFSET(struct linux_kernel_params, ist_info, 0x60);
  CHECK_OFFSET(struct linux_kernel_params, acpi_rsdp_addr, 0x70);
  CHECK_OFFSET(struct linux_kernel_params, olpc_ofw_header, 0xb0);
  CHECK_OFFSET(struct linux_kernel_params, edid_info, 0x140);
  CHECK_OFFSET(struct linux_kernel_params, efi_info, 0x1b8);
  CHECK_OFFSET(struct linux_kernel_params, e820_entries, 0x1e8);
  CHECK_OFFSET(struct linux_kernel_params, secure_boot, 0x1ec);
  CHECK_OFFSET(struct linux_kernel_params, hdr, 0x1f1);
  CHECK_OFFSET(struct linux_kernel_params, e820_table, 0x2d0);

  /* Verify the struct layout is consistent with Linux kernel boot_params 6.13.7 */
  /* screen_info starts at offset 0 */
  /* edid_info at 0x140 (inline byte array, not struct) */
  /* efi_info union at 0x1b8 */
  /* hdr (setup_header) at 0x1f1 */
  /* e820_table at 0x2d0 */

  printf("\n=== Result: %s ===\n", failed ? "FAILED" : "PASSED");
  return failed;
}
