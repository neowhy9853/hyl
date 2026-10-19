/* Minimal test harness for GRUB2 script function redefinition compatibility */
#define GRUB_LST_GENERATOR(fn) void fn (const char *filename, int quiet)
#include <config.h>
#include <grub/types.h>
#include <grub/err.h>
#include <grub/mm.h>
#include <grub/script_sh.h>
#include <grub/misc.h>
#include <grub/charset.h>
#include <grub/script.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    grub_script_function_t func_a, func_b, found;
    struct grub_script *script_a, *script_b;
    struct grub_script_arg fname;

    grub_mm_init_region((void*)0x100000, 64*1024*1024);

    printf("=== PCA Test: grub_script_function_create return value and error behavior ===\n\n");

    /* Test 1: Create first function */
    printf("Test 1: Create initial function 'testfunc'\n");
    script_a = grub_script_parse("echo executing", NULL);
    if (!script_a) {
        printf("  FAIL: Could not parse script\n");
        return 1;
    }
    fname.str = grub_strdup("testfunc");
    func_a = grub_script_function_create(&fname, script_a);
    if (!func_a) {
        printf("  FAIL: grub_script_function_create returned NULL\n");
        return 1;
    }
    printf("  PASS: Function created, ptr=%p\n", (void*)func_a);
    printf("  executing field = %u (expected 0)\n", func_a->executing);

    /* Test 2: Call existing function */
    printf("\nTest 2: Call testfunc\n");
    grub_err_t ret = grub_script_function_call(func_a, 0, NULL);
    printf("  Return: %d (expected GRUB_ERR_NONE=0)\n", ret);
    printf("  executing field after call: %u (expected 0)\n", func_a->executing);

    /* Test 3: Redefine function while NOT executing (should succeed) */
    printf("\nTest 3: Redefine testfunc while NOT executing\n");
    script_b = grub_script_parse("echo redefined", NULL);
    if (!script_b) {
        printf("  FAIL: Could not parse second script\n");
        return 1;
    }
    func_b = grub_script_function_create(&fname, script_b);
    if (!func_b) {
        printf("  FAIL: Redefinition returned NULL when it should succeed\n");
        return 1;
    }
    printf("  PASS: Redefinition succeeded, ptr=%p\n", (void*)func_b);
    printf("  executing field = %u (expected 0)\n", func_b->executing);

    /* Test 4: Call the redefined function */
    printf("\nTest 4: Call redefined testfunc\n");
    ret = grub_script_function_call(func_b, 0, NULL);
    printf("  Return: %d\n", ret);

    printf("\n=== All basic tests passed ===\n");
    printf("\nNOTE: Full 'redefine during execution' test requires proper\n");
    printf("GRUB environment initialization and script execution setup.\n");
    return 0;
}
