#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

typedef unsigned char grub_uint8_t;
#ifdef __LP64__
typedef unsigned long long grub_size_t;
#else
typedef unsigned int grub_size_t;
#endif

static inline int grub_tolower (int c) {
  if (c >= 'A' && c <= 'Z') return c - 'A' + 'a';
  return c;
}

static inline int grub_uuidcasecmp (const char *uuid1, const char *uuid2, grub_size_t n) {
  if (n == 0) return 0;
  while (*uuid1 && *uuid2 && --n) {
    while ('-' == *uuid1) ++uuid1;
    while ('-' == *uuid2) ++uuid2;
    if (grub_tolower ((grub_uint8_t) *uuid1) != grub_tolower ((grub_uint8_t) *uuid2))
      break;
    uuid1++; uuid2++;
  }
  return (int) grub_tolower ((grub_uint8_t) *uuid1) - (int) grub_tolower ((grub_uint8_t) *uuid2);
}

static inline int grub_strcasecmp (const char *s1, const char *s2) {
  while (*s1 && *s2) {
    if (grub_tolower ((grub_uint8_t) *s1) != grub_tolower ((grub_uint8_t) *s2)) break;
    s1++; s2++;
  }
  return (int) grub_tolower ((grub_uint8_t) *s1) - (int) grub_tolower ((grub_uint8_t) *s2);
}

static void strip_dashes(const char *src, char *dst, size_t dst_size) {
  size_t j = 0;
  for (size_t i = 0; src[i] && j < dst_size - 1; i++)
    if (src[i] != '-') dst[j++] = src[i];
  dst[j] = '\0';
}

static int old_behavior_compare(const char *search_uuid, const char *header_uuid) {
  char stripped[128];
  strip_dashes(header_uuid, stripped, sizeof(stripped));
  return grub_strcasecmp(search_uuid, stripped);
}

int test_count = 0, pass_count = 0;

void s(const char *n, int exp_sign, const char *u1, const char *u2, grub_size_t sz) {
  test_count++;
  int r = grub_uuidcasecmp(u1, u2, sz);
  int sign = (r > 0) - (r < 0);
  if (sign == exp_sign) {
    printf("  PASS: %s (u1='%s', u2='%s', n=%llu, r=%d)\n", n, u1, u2, (unsigned long long)sz, r);
    pass_count++;
  } else {
    printf("  FAIL: %s (u1='%s', u2='%s', n=%llu, exp_sign=%d, r=%d)\n", n, u1, u2, (unsigned long long)sz, exp_sign, r);
  }
}

void e(const char *n, int exp, int act) {
  test_count++;
  if (exp == act) {
    printf("  PASS: %s (exp=%d, got=%d)\n", n, exp, act);
    pass_count++;
  } else {
    printf("  FAIL: %s (exp=%d, got=%d)\n", n, exp, act);
  }
}

int main(void) {
  printf("=== grub_uuidcasecmp Unit & Contract Tests ===\n\n");

  /* Standard UUID: 32 hex chars, 8-4-4-4-12 format with dashes */
  const char *std_dashed  = "12345678-1234-5678-90ab-cdef12345678";
  const char *std_no_dash = "123456781234567890abcdef12345678";
  const char *std_diff    = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
  const char *std_diff2   = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
  const char *std_upper   = "FEDCBA98-7654-3210-ABCD-EF0123456789";
  const char *std_lower   = "fedcba98-7654-3210-abcd-ef0123456789";
  const char *std_lower_nodash = "fedcba9876543210abcdef0123456789";
  const char *std_mixed   = "a1B2c3D4-5678-90Ab-CdEf-0123456789ab";
  const char *std_mixed2  = "A1b2C3d4567890aBcDeF0123456789AB";

  /* -- BASIC MATCHING -- */
  printf("--- Basic matching ---\n");
  e("same dashed", 0, grub_uuidcasecmp(std_dashed, std_dashed, 32));
  e("same no-dash", 0, grub_uuidcasecmp(std_no_dash, std_no_dash, 32));
  e("dashed vs no-dash (same hex)", 0, grub_uuidcasecmp(std_dashed, std_no_dash, 32));
  e("case insensitive", 0, grub_uuidcasecmp(std_upper, std_lower, 32));
  e("mixed case match", 0, grub_uuidcasecmp(std_mixed, std_mixed2, 32));

  /* -- DASH VARIATIONS -- */
  printf("\n--- Dash position invariance ---\n");
  e("extra dashes in s1", 0, grub_uuidcasecmp("12-34-56-78-12-34-56-78-90-ab-cd-ef-12-34-56-78", std_no_dash, 32));
  e("single dash", 0, grub_uuidcasecmp("12345678-1234567890abcdef12345678", std_dashed, 32));

  /* -- NON-MATCH -- */
  printf("\n--- Non-matching ---\n");
  s("completely different", -1, std_diff, std_diff2, 32);
  s("last char differs", -1, "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaA", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaB", 32);

  /* -- EDGE CASES -- */
  printf("\n--- Edge cases ---\n");
  e("n=0 returns 0", 0, grub_uuidcasecmp(std_dashed, "00000000-0000-0000-0000-000000000000", 0));
  s("empty s1", -1, "", "1234", 4);
  s("empty s2", 1, "1234", "", 4);
  e("both empty", 0, grub_uuidcasecmp("", "", 4));
  s("s1 all dashes", -1, "----", "1234", 4);
  s("s2 all dashes", 1, "1234", "----", 4);
  e("both all dashes", 0, grub_uuidcasecmp("----", "----", 4));

  /* -- PARTIAL n (compare first N significant chars) -- */
  printf("\n--- Partial n comparison ---\n");
  e("n=8 prefix match", 0, grub_uuidcasecmp("12345678-abcd-ef01-2345-6789abcdef01", "12345678-ffff-ffff-ffff-ffffffffffff", 8));
  s("n=8 prefix mismatch", 1, "23456789-abcd-ef01-2345-6789abcdef01", "12345678-ffff-ffff-ffff-ffffffffffff", 8);

  /* -- CONTRACT: backward compatibility verification -- */
  printf("\n--- Backward compatibility contract ---\n");
  const char *hd = "12345678-1234-1234-1234-123456789abc";
  const char *df = "12345678123412341234123456789abc";

  int old_df = old_behavior_compare(df, hd);
  int old_hd = old_behavior_compare(hd, hd);
  int new_df = grub_uuidcasecmp(df, hd, 32);
  int new_hd = grub_uuidcasecmp(hd, hd, 32);

  printf("  OLD(dash-free input vs dashed UUID) -> %s\n", old_df==0?"MATCH":"NO MATCH");
  printf("  OLD(dashed input   vs dashed UUID) -> %s\n", old_hd==0?"MATCH":"NO MATCH");
  printf("  NEW(dash-free input vs dashed UUID) -> %s\n", new_df==0?"MATCH":"NO MATCH");
  printf("  NEW(dashed input   vs dashed UUID) -> %s\n", new_hd==0?"MATCH":"NO MATCH");

  test_count++;
  if (old_df == 0) {
    printf("  PASS: old code accepts dash-free input with stripped UUID\n"); pass_count++;
  } else {
    printf("  FAIL: old code should accept dash-free input\n");
  }
  test_count++;
  if (old_hd != 0) {
    printf("  PASS: old code rejects dashed input (no dash stripping on input)\n"); pass_count++;
  } else {
    printf("  FAIL: old code matched dashed input when it shouldn't\n");
  }
  test_count++;
  if (new_df == 0) {
    printf("  PASS: new code preserves backward compat (dash-free still works)\n"); pass_count++;
  } else {
    printf("  FAIL: new code broke dash-free input\n");
  }
  test_count++;
  if (new_hd == 0) {
    printf("  PASS: new code accepts dashed input (new behavior)\n"); pass_count++;
  } else {
    printf("  FAIL: new code doesn't accept dashed input\n");
  }

  /* -- LUKS FORMATS -- */
  printf("\n--- LUKS UUID variations ---\n");
  e("LUKS upper vs lower", 0, grub_uuidcasecmp(std_upper, std_lower, 32));
  e("LUKS dashed vs dash-free lower", 0, grub_uuidcasecmp(std_lower, std_lower_nodash, 32));
  e("LUKS upper dashed vs dash-free lower", 0, grub_uuidcasecmp(std_upper, std_lower_nodash, 32));
  e("LUKS2 mixed format", 0, grub_uuidcasecmp(std_mixed, std_mixed2, 32));

  printf("\n=== %d/%d PASSED ===\n", pass_count, test_count);
  return pass_count == test_count ? 0 : 1;
}
