#include "mock_grub.h"
#include <stdarg.h>

/* The mock secureboot mode for testing */
mock_sb_mode g_mock_secureboot_mode = GRUB_EFI_SECUREBOOT_MODE_DISABLED;

/* Minimal stub functions needed for the extracted code */
static int grub_strlen(const char *s) { return s ? strlen(s) : 0; }
static void *grub_utf16_to_utf8(void *dst, const void *src, int len) { 
  if (dst) *(char*)dst = 0; 
  return dst; 
}
static void efi_call_3(void *a, void *b, void *c, void *d) { (void)a; (void)b; (void)c; (void)d; }

/* EXTRACTED: The key changed code region.
   This is a simplified version showing the control flow change.
   BEFORE patch: uses grub_linuxefi_secure_validate() + rc-based branches
   AFTER patch: uses grub_efi_get_secureboot() with two-way branch
*/

/* Simulated grub_linuxefi_secure_validate (BEFORE behavior) */
static int grub_linuxefi_secure_validate(void *data, grub_uint32_t size) {
  (void)data; (void)size;
  /* Returns: >0 on secure validation success, 0 on no validation, <0 on error */
  if (g_mock_secureboot_mode == GRUB_EFI_SECUREBOOT_MODE_ENABLED)
    return 1;   /* SecureBoot ON -> validation passes */
  else
    return 0;   /* SecureBoot OFF -> no validation */
}

/* OLD behavior (BEFORE patch) */
static int chainloader_before_patch(void) {
  int rc;
  
  printf("=== BEFORE PATCH (old behavior) ===\n");
  printf("SecureBoot mode: %d\n", g_mock_secureboot_mode);
  
  rc = grub_linuxefi_secure_validate((void*)(unsigned long)1, 1024);
  grub_dprintf("chain", "linuxefi_secure_validate: %d\n", rc);
  
  if (rc > 0) {
    /* COVERAGE TARGET: old line ~1085 */
    printf("  -> Branch: rc > 0 (secureboot path via grub_secureboot_chainloader_boot)\n");
    printf("  -> TPM PCR extended TWICE (verifier + this explicit call)\n");
    return 1;
  } else if (rc == 0) {
    /* COVERAGE TARGET: old line ~1092 */
    printf("  -> Branch: rc == 0 (regular path via grub_chainloader_boot)\n");
    printf("  -> TPM PCR extended ONCE (verifier only)\n");
    return 0;
  }
  /* COVERAGE TARGET: old line ~1101 - fall-through to fail */
  printf("  -> Branch: rc < 0 (FAIL path)\n");
  return -1;
}

/* NEW behavior (AFTER patch) */
static int chainloader_after_patch(void) {
  printf("=== AFTER PATCH (new behavior) ===\n");
  printf("SecureBoot mode: %d\n", g_mock_secureboot_mode);
  
  if (grub_efi_get_secureboot() == GRUB_EFI_SECUREBOOT_MODE_ENABLED) {
    /* COVERAGE TARGET: new line ~1084 */
    printf("  -> Branch: SecureBoot ON (secureboot path via grub_secureboot_chainloader_boot)\n");
    printf("  -> TPM PCR extended ONCE (verifier only - no duplicate call)\n");
    return 1;
  } else {
    /* COVERAGE TARGET: new line ~1092 */
    printf("  -> Branch: SecureBoot OFF (regular path via grub_chainloader_boot)\n");
    printf("  -> TPM PCR extended ONCE (verifier only)\n");
    return 0;
  }
  /* NOTE: No fall-through fail path anymore */
}

int main(void) {
  int old_result, new_result;
  
  printf("========================================\n");
  printf("TEST 1: SecureBoot ENABLED\n");
  printf("========================================\n");
  g_mock_secureboot_mode = GRUB_EFI_SECUREBOOT_MODE_ENABLED;
  old_result = chainloader_before_patch();
  new_result = chainloader_after_patch();
  printf("Before result: %d, After result: %d\n", old_result, new_result);
  printf("PCR check: Before had EXPLICIT validate call + dprintf; After does not\n");
  
  printf("\n========================================\n");
  printf("TEST 2: SecureBoot DISABLED\n");
  printf("========================================\n");
  g_mock_secureboot_mode = GRUB_EFI_SECUREBOOT_MODE_DISABLED;
  old_result = chainloader_before_patch();
  new_result = chainloader_after_patch();
  printf("Before result: %d, After result: %d\n", old_result, new_result);
  printf("Path check: Both use regular path, but Before called grub_linuxefi_secure_validate first\n");
  
  printf("\n========================================\n");
  printf("SUMMARY\n");
  printf("========================================\n");
  printf("Key change 1: grub_linuxefi_secure_validate() call REMOVED\n");
  printf("  -> TPM PCR extended once instead of twice (SIDE_EFFECT_CHANGE)\n");
  printf("Key change 2: Condition changed from rc-based to SecureBoot-state-based\n");
  printf("  -> When SB=OFF+shim present, boot path may differ (SIDE_EFFECT_CHANGE)\n");
  printf("Key change 3: grub_dprintf debug output REMOVED\n");
  printf("  -> 'linuxefi_secure_validate: %%d' no longer printed (OUTPUT_FORMAT_CHANGE)\n");
  printf("Key change 4: Fall-through fail path REMOVED\n");
  printf("  -> No more explicit error path for validation failure (ERROR_EXCEPTION_CHANGE)\n");
  
  return 0;
}
