#include <stdio.h>
#include <stddef.h>
#include <string.h>

#define __packed __attribute__((packed))
typedef unsigned char grub_uint8_t;
typedef unsigned short grub_uint16_t;
typedef unsigned int grub_uint32_t;
typedef unsigned long long grub_uint64_t;

#define GRUB_PACKED __attribute__((packed))
#define GRUB_E820_MAX_ENTRIES_ZEROPAGE 128
#define EDDMAXNR 6
#define EDD_MBR_SIG_MAX 16

struct grub_screen_info {
  grub_uint8_t orig_x;
  grub_uint8_t orig_y;
  grub_uint16_t ext_mem_k;
  grub_uint16_t orig_video_page;
  grub_uint8_t orig_video_mode;
  grub_uint8_t orig_video_cols;
  grub_uint8_t flags;
  grub_uint8_t unused2;
  grub_uint16_t orig_video_ega_bx;
  grub_uint16_t unused3;
  grub_uint8_t orig_video_lines;
  grub_uint8_t orig_video_isVGA;
  grub_uint16_t orig_video_points;
  grub_uint16_t lfb_width;
  grub_uint16_t lfb_height;
  grub_uint16_t lfb_depth;
  grub_uint32_t lfb_base;
  grub_uint32_t lfb_size;
  grub_uint16_t cl_magic, cl_offset;
  grub_uint16_t lfb_linelength;
  grub_uint8_t red_size;
  grub_uint8_t red_pos;
  grub_uint8_t green_size;
  grub_uint8_t green_pos;
  grub_uint8_t blue_size;
  grub_uint8_t blue_pos;
  grub_uint8_t rsvd_size;
  grub_uint8_t rsvd_pos;
  grub_uint16_t vesapm_seg;
  grub_uint16_t vesapm_off;
  grub_uint16_t pages;
  grub_uint16_t vesa_attributes;
  grub_uint32_t capabilities;
  grub_uint32_t ext_lfb_base;
  grub_uint8_t _reserved[2];
} GRUB_PACKED;

struct grub_boot_e820_entry {
  grub_uint64_t addr;
  grub_uint64_t size;
  grub_uint32_t type;
} GRUB_PACKED;

struct grub_setup_header {
  grub_uint8_t setup_sects;
  grub_uint16_t root_flags;
  grub_uint32_t syssize;
  grub_uint16_t ram_size;
  grub_uint16_t vid_mode;
  grub_uint16_t root_dev;
  grub_uint16_t boot_flag;
  grub_uint16_t jump;
  grub_uint32_t header;
  grub_uint16_t version;
  grub_uint32_t realmode_swtch;
  grub_uint16_t start_sys;
  grub_uint16_t kernel_version;
  grub_uint8_t type_of_loader;
  grub_uint8_t loadflags;
  grub_uint16_t setup_move_size;
  grub_uint32_t code32_start;
  grub_uint32_t ramdisk_image;
  grub_uint32_t ramdisk_size;
  grub_uint32_t bootsect_kludge;
  grub_uint16_t heap_end_ptr;
  grub_uint8_t ext_loader_ver;
  grub_uint8_t ext_loader_type;
  grub_uint32_t cmd_line_ptr;
  grub_uint32_t initrd_addr_max;
  grub_uint32_t kernel_alignment;
  grub_uint8_t relocatable_kernel;
  grub_uint8_t min_alignment;
  grub_uint16_t xloadflags;
  grub_uint32_t cmdline_size;
  grub_uint32_t hardware_subarch;
  grub_uint64_t hardware_subarch_data;
  grub_uint32_t payload_offset;
  grub_uint32_t payload_length;
  grub_uint64_t setup_data;
  grub_uint64_t pref_address;
  grub_uint32_t init_size;
  grub_uint32_t handover_offset;
  grub_uint32_t kernel_info_offset;
} GRUB_PACKED;

struct linux_kernel_params {
  struct grub_screen_info screen_info;
  grub_uint8_t _pad1[0x40 - sizeof(struct grub_screen_info)];
  grub_uint16_t apm_version;
  grub_uint16_t apm_code_segment;
  grub_uint32_t apm_entry;
  grub_uint16_t apm_16bit_code_segment;
  grub_uint16_t apm_data_segment;
  grub_uint16_t apm_flags;
  grub_uint32_t apm_code_len;
  grub_uint16_t apm_data_len;
  grub_uint8_t _pad2[0x60 - 0x54];
  grub_uint32_t ist_signature;
  grub_uint32_t ist_command;
  grub_uint32_t ist_event;
  grub_uint32_t ist_perf_level;
  grub_uint64_t acpi_rsdp_addr;
  grub_uint8_t _pad3[0x80 - 0x78];
  grub_uint8_t hd0_info[16];
  grub_uint8_t hd1_info[16];
  grub_uint16_t rom_config_len;
  grub_uint8_t _pad4[0xb0 - 0xa2];
  grub_uint32_t ofw_signature;
  grub_uint32_t ofw_num_items;
  grub_uint32_t ofw_cif_handler;
  grub_uint32_t ofw_idt;
  grub_uint8_t _pad5[0x1b8 - 0xc0];
  grub_uint32_t efi_system_table;
  grub_uint32_t padding_1bc;
  grub_uint32_t efi_loader_signature;
  grub_uint32_t efi_memdesc_size;
  grub_uint32_t efi_memdesc_version;
  grub_uint32_t efi_memmap_size;
  grub_uint32_t efi_memmap;
  grub_uint32_t alt_mem_k;
  grub_uint32_t scratch;
  grub_uint8_t e820_entries;
  grub_uint8_t eddbuf_entries;
  grub_uint8_t edd_mbr_sig_buf_entries;
  grub_uint8_t kbd_status;
  grub_uint8_t secure_boot;
  grub_uint8_t _pad6[2];
  grub_uint8_t sentinel;
  grub_uint8_t _pad7[1];
  struct grub_setup_header hdr;
  grub_uint8_t _pad8[0x290 - 0x1f1 - sizeof(struct grub_setup_header)];
  struct grub_boot_e820_entry e820_table[GRUB_E820_MAX_ENTRIES_ZEROPAGE];
} GRUB_PACKED;

static int failed = 0;

#define CHECK_SIZE(type, expected) do { \
  size_t sz = sizeof(type); \
  if (sz != expected) { \
    printf("FAIL: sizeof(" #type ") = %zu, expected %zu\n", sz, (size_t)(expected)); \
    failed = 1; \
  } else { \
    printf("OK: sizeof(" #type ") = %zu\n", sz); \
  } \
} while(0)

#define CHECK_OFFSET(type, field, expected) do { \
  size_t off = offsetof(type, field); \
  if (off != expected) { \
    printf("FAIL: offsetof(" #type ", " #field ") = %zu, expected %zu\n", off, (size_t)(expected)); \
    failed = 1; \
  } else { \
    printf("OK: offsetof(" #type ", " #field ") = %zu\n", off); \
  } \
} while(0)

int main(void) {
  printf("=== GRUB2 Linux Boot Parameter ABI Verification ===\n\n");

  printf("--- struct grub_screen_info ---\n");
  CHECK_SIZE(struct grub_screen_info, 0x40);
  CHECK_OFFSET(struct grub_screen_info, orig_x, 0x00);
  CHECK_OFFSET(struct grub_screen_info, orig_y, 0x01);
  CHECK_OFFSET(struct grub_screen_info, ext_mem_k, 0x02);
  CHECK_OFFSET(struct grub_screen_info, lfb_width, 0x12);
  CHECK_OFFSET(struct grub_screen_info, lfb_height, 0x14);
  CHECK_OFFSET(struct grub_screen_info, lfb_depth, 0x16);
  CHECK_OFFSET(struct grub_screen_info, lfb_base, 0x18);
  CHECK_OFFSET(struct grub_screen_info, lfb_linelength, 0x24);
  CHECK_OFFSET(struct grub_screen_info, red_size, 0x26);
  CHECK_OFFSET(struct grub_screen_info, red_pos, 0x27);
  CHECK_OFFSET(struct grub_screen_info, green_size, 0x28);
  CHECK_OFFSET(struct grub_screen_info, green_pos, 0x29);
  CHECK_OFFSET(struct grub_screen_info, blue_size, 0x2a);
  CHECK_OFFSET(struct grub_screen_info, blue_pos, 0x2b);
  CHECK_OFFSET(struct grub_screen_info, rsvd_size, 0x2c);
  CHECK_OFFSET(struct grub_screen_info, rsvd_pos, 0x2d);
  CHECK_OFFSET(struct grub_screen_info, capabilities, 0x36);
  CHECK_OFFSET(struct grub_screen_info, ext_lfb_base, 0x3a);
  CHECK_OFFSET(struct grub_screen_info, orig_video_isVGA, 0x0f);

  printf("\n--- struct grub_boot_e820_entry ---\n");
  CHECK_SIZE(struct grub_boot_e820_entry, 20);
  CHECK_OFFSET(struct grub_boot_e820_entry, addr, 0);
  CHECK_OFFSET(struct grub_boot_e820_entry, size, 8);
  CHECK_OFFSET(struct grub_boot_e820_entry, type, 16);

  printf("\n--- struct grub_setup_header ---\n");
  CHECK_OFFSET(struct grub_setup_header, setup_sects, 0);
  CHECK_OFFSET(struct grub_setup_header, boot_flag, 14);
  CHECK_OFFSET(struct grub_setup_header, header, 18);
  CHECK_OFFSET(struct grub_setup_header, version, 22);
  CHECK_OFFSET(struct grub_setup_header, type_of_loader, 32);
  CHECK_OFFSET(struct grub_setup_header, loadflags, 33);
  CHECK_OFFSET(struct grub_setup_header, ext_loader_ver, 42);
  CHECK_OFFSET(struct grub_setup_header, ext_loader_type, 43);
  CHECK_OFFSET(struct grub_setup_header, cmd_line_ptr, 44);
  CHECK_OFFSET(struct grub_setup_header, initrd_addr_max, 48);
  CHECK_OFFSET(struct grub_setup_header, kernel_alignment, 52);
  CHECK_OFFSET(struct grub_setup_header, relocatable_kernel, 56);
  CHECK_OFFSET(struct grub_setup_header, cmdline_size, 60);
  CHECK_OFFSET(struct grub_setup_header, kernel_info_offset, 88);

  printf("\n--- struct linux_kernel_params ---\n");
  CHECK_OFFSET(struct linux_kernel_params, screen_info, 0);
  CHECK_OFFSET(struct linux_kernel_params, apm_version, 0x40);
  CHECK_OFFSET(struct linux_kernel_params, ist_signature, 0x60);
  CHECK_OFFSET(struct linux_kernel_params, acpi_rsdp_addr, 0x70);
  CHECK_OFFSET(struct linux_kernel_params, hd0_info, 0x80);
  CHECK_OFFSET(struct linux_kernel_params, ofw_signature, 0xb0);
  CHECK_OFFSET(struct linux_kernel_params, efi_system_table, 0x1b8);
  CHECK_OFFSET(struct linux_kernel_params, efi_loader_signature, 0x1c0);
  CHECK_OFFSET(struct linux_kernel_params, alt_mem_k, 0x1e0);
  CHECK_OFFSET(struct linux_kernel_params, e820_entries, 0x1e8);
  CHECK_OFFSET(struct linux_kernel_params, secure_boot, 0x1ec);
  CHECK_OFFSET(struct linux_kernel_params, hdr, 0x1f1);
  CHECK_OFFSET(struct linux_kernel_params, e820_table, 0x2d0);

  printf("\n=== Result: %s ===\n", failed ? "FAILED" : "PASSED");
  return failed;
}
