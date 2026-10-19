#ifndef MOCK_GRUB_H
#define MOCK_GRUB_H
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int grub_err_t;
typedef int grub_command_t;
typedef int grub_file_t;
typedef int grub_device_t;
typedef int grub_efi_device_path_t;
typedef int grub_efi_status_t;
typedef int grub_efi_boot_services_t;
typedef int grub_efi_loaded_image_t;
typedef int grub_efi_char16_t;
typedef unsigned int grub_efi_uintn_t;
typedef uint32_t grub_efi_uint32_t;
typedef uint64_t grub_size_t;
typedef uint64_t grub_uint64_t;
typedef uint32_t grub_uint32_t;
typedef uint16_t grub_uint16_t;
typedef uint8_t grub_uint8_t;

#define GRUB_ERR_BAD_ARGUMENT 1
#define GRUB_ERR_BAD_OS 2
#define GRUB_ERR_OUT_OF_MEMORY 3
#define GRUB_EFI_SUCCESS 0
#define N_(x) x
#define __attribute__(x)

typedef enum {
  GRUB_EFI_SECUREBOOT_MODE_UNKNOWN = 0,
  GRUB_EFI_SECUREBOOT_MODE_DISABLED = 1,
  GRUB_EFI_SECUREBOOT_MODE_ENABLED = 2,
} grub_efi_secureboot_mode_t;

/* Mock globals */
static void *address = 0;
static grub_efi_device_path_t *file_path = 0;
static int image_handle = 0;
static int dev_handle = 0;
static grub_size_t fsize = 0;
static grub_size_t pages = 0;
static int my_mod = 0;

/* Mock function declarations with coverage tracking */
typedef enum {
  SECUREBOOT_MODE_ENABLED = 2,
  SECUREBOOT_MODE_DISABLED = 1,
} mock_sb_mode;

extern mock_sb_mode g_mock_secureboot_mode;

/* Function stubs */
static inline void grub_dl_ref(int mod) { (void)mod; }
static inline void grub_dl_unref(int mod) { (void)mod; }
static inline grub_err_t grub_error(int code, const char *fmt, ...) {
  fprintf(stderr, "GRUB ERROR %d: ", code);
  va_list ap;
  va_start(ap, fmt);
  vfprintf(stderr, fmt, ap);
  va_end(ap);
  fprintf(stderr, "\n");
  return code;
}
static inline void grub_file_close(grub_file_t f) { (void)f; }
static inline void grub_device_close(grub_device_t d) { (void)d; }
static inline void grub_free(void *p) { free(p); }
static inline void *grub_malloc(grub_size_t sz) { return malloc(sz); }
static inline void grub_efi_free_pages(void *addr, grub_size_t pgs) { (void)addr; (void)pgs; }

static inline int grub_efi_get_secureboot(void) {
  return g_mock_secureboot_mode;
}

static inline void grub_loader_set(void *boot, void *unload, int flags) {
  (void)boot; (void)unload; (void)flags;
  printf("grub_loader_set called\n");
}

static inline void grub_load_and_start_image(void *boot_image) {
  (void)boot_image;
  printf("grub_load_and_start_image called\n");
}

static inline int grub_cpu_to_le32(int x) { return x; }

/* grub_dprintf stub */
#define grub_dprintf(cat, fmt, ...) printf("[DEBUG " cat "] " fmt, ##__VA_ARGS__)

#endif /* MOCK_GRUB_H */
