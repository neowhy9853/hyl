#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <setjmp.h>

static jmp_buf crash_jmp;
static volatile int crashed = 0;

void sigsegv_handler(int sig) {
    crashed = 1;
    longjmp(crash_jmp, 1);
}

/* Old (before) version of safe_strncpy */
void safe_strncpy_old(char *dest, const char *src, size_t size)
{
  if (size != 0)
    {
      dest[size-1] = '\0';
      strncpy(dest, src, size-1);
    }
}

/* New (after) version of safe_strncpy */
void safe_strncpy_new(char *dest, const char *src, size_t size)
{
  if (size != 0)
    {
      dest[0] = dest[size-1] = '\0';
      if (src)
	strncpy(dest, src, size-1);
    }
}

int run_test(int test_num, const char *label,
             void (*func)(char *, const char *, size_t),
             const char *src, size_t size,
             int expect_crash, const char *expected_prefix) {
    char buf[256];
    struct sigaction sa, old;
    int result;

    memset(buf, 'Y', sizeof(buf));
    crashed = 0;

    /* Install handler that longjmps on SIGSEGV */
    sa.sa_handler = sigsegv_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGSEGV, &sa, &old);

    if (setjmp(crash_jmp) == 0) {
        func(buf, src, size);
        /* Normal return */
        sigaction(SIGSEGV, &old, NULL);
        if (expect_crash) {
            printf("FAIL Test %d (%s): expected crash but got clean return\n", test_num, label);
            return 0;
        }
        if (size > 0 && buf[size-1] != '\0') {
            printf("FAIL Test %d (%s): not null-terminated! buf[%zu]=%d\n",
                   test_num, label, size-1, buf[size-1]);
            return 0;
        }
        if (expected_prefix && size > 0 && strncmp(buf, expected_prefix, strlen(expected_prefix)) != 0) {
            printf("FAIL Test %d (%s): prefix mismatch. Got '%.20s', expected '%s'\n",
                   test_num, label, buf, expected_prefix);
            return 0;
        }
        printf("PASS Test %d (%s): result='%.20s'\n", test_num, label, buf);
        return 1;
    } else {
        /* Crashed - longjmp came here */
        sigaction(SIGSEGV, &old, NULL);
        if (expect_crash) {
            printf("PASS Test %d (%s): crashed as expected\n", test_num, label);
            return 1;
        } else {
            printf("FAIL Test %d (%s): UNEXPECTED CRASH\n", test_num, label);
            return 0;
        }
    }
}

int main(void) {
    int passed = 0, failed = 0, total = 0;

    printf("=== Testing INPUT_CONTRACT_CHANGE: safe_strncpy NULL handling ===\n\n");

    /* Test 1: Normal src with OLD version */
    total++; passed += run_test(total, "old:normal", safe_strncpy_old, "hello", 256, 0, "hello");
    /* Test 2: Empty src with OLD version */
    total++; passed += run_test(total, "old:empty", safe_strncpy_old, "", 256, 0, "");
    /* Test 3: NULL src with OLD version (should CRASH - no NULL check) */
    total++; passed += run_test(total, "old:NULL", safe_strncpy_old, NULL, 256, 1, NULL);
    /* Test 4: size=0 with OLD version */
    total++; passed += run_test(total, "old:size0", safe_strncpy_old, "hello", 0, 0, "");
    /* Test 5: size=1 with OLD + normal src */
    total++; passed += run_test(total, "old:size1+normal", safe_strncpy_old, "hello", 1, 0, "");

    printf("\n--- NEW (patched) version ---\n\n");

    /* Test 6: Normal src with NEW version */
    total++; passed += run_test(total, "new:normal", safe_strncpy_new, "hello", 256, 0, "hello");
    /* Test 7: Empty src with NEW version */
    total++; passed += run_test(total, "new:empty", safe_strncpy_new, "", 256, 0, "");
    /* Test 8: NULL src with NEW version (should NOT crash - NULL handled!) */
    total++; passed += run_test(total, "new:NULL", safe_strncpy_new, NULL, 256, 0, "");
    /* Test 9: size=0 with NEW version */
    total++; passed += run_test(total, "new:size0", safe_strncpy_new, "hello", 0, 0, "");
    /* Test 10: size=1 with NEW + NULL src */
    total++; passed += run_test(total, "new:size1+NULL", safe_strncpy_new, NULL, 1, 0, "");
    /* Test 11: size=1 with NEW + normal src */
    total++; passed += run_test(total, "new:size1+normal", safe_strncpy_new, "hello", 1, 0, "");

    printf("\n=== RESULTS: %d/%d passed, %d failed ===\n", passed, total, total-passed);
    return (passed == total) ? 0 : 1;
}
