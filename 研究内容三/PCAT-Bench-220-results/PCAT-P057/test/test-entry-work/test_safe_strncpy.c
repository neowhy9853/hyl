#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

/* Prototype matching dnsmasq's safe_strncpy */
void safe_strncpy(char *dest, const char *src, size_t size);

volatile int crashed = 0;

void sigsegv_handler(int sig) {
    crashed = 1;
}

int main(int argc, char **argv) {
    char buf[256];
    int test_num = 0;
    int passed = 0;
    int failed = 0;

    /* Install signal handler for crash detection */
    signal(SIGSEGV, sigsegv_handler);

    /* Test 1: Normal src (non-NULL, short string) */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, "hello", 256);
    if (crashed) {
        printf("FAIL Test %d (normal src): CRASHED\n", test_num);
        failed++;
    } else if (strcmp(buf, "hello") != 0 || buf[255] != '\0') {
        printf("FAIL Test %d (normal src): wrong result '%s', term=%d\n", test_num, buf, buf[255] == '\0');
        failed++;
    } else {
        printf("PASS Test %d (normal src): result='%s'\n", test_num, buf);
        passed++;
    }

    /* Test 2: Empty src ("") */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, "", 256);
    if (crashed) {
        printf("FAIL Test %d (empty src): CRASHED\n", test_num);
        failed++;
    } else if (buf[0] != '\0' || buf[255] != '\0') {
        printf("FAIL Test %d (empty src): buf[0]=%d, term=%d\n", test_num, buf[0], buf[255] == '\0');
        failed++;
    } else {
        printf("PASS Test %d (empty src): first byte zeroed, terminated\n", test_num);
        passed++;
    }

    /* Test 3: NULL src (the crash scenario!) */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, NULL, 256);
    if (crashed) {
        printf("FAIL Test %d (NULL src): CRASHED - binary is not patched\n", test_num);
        failed++;
    } else if (buf[0] != '\0' || buf[255] != '\0') {
        printf("FAIL Test %d (NULL src): buf[0]=%d, term=%d\n", test_num, buf[0], buf[255] == '\0');
        failed++;
    } else {
        printf("PASS Test %d (NULL src): NULL handled gracefully, empty string returned\n", test_num);
        passed++;
    }

    /* Test 4: size=0 (edge case) */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, "hello", 0);
    if (crashed) {
        printf("FAIL Test %d (size=0): CRASHED\n", test_num);
        failed++;
    } else if (buf[0] != 'X') {
        printf("FAIL Test %d (size=0): buffer modified! buf[0]=%d\n", test_num, buf[0]);
        failed++;
    } else {
        printf("PASS Test %d (size=0): no modification, correct\n", test_num);
        passed++;
    }

    /* Test 5: size=1 with NULL src */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, NULL, 1);
    if (crashed) {
        printf("FAIL Test %d (size=1 NULL): CRASHED\n", test_num);
        failed++;
    } else if (buf[0] != '\0') {
        printf("FAIL Test %d (size=1 NULL): buf[0]=%d (expected 0)\n", test_num, buf[0]);
        failed++;
    } else {
        printf("PASS Test %d (size=1 NULL): buf[0] zeroed, correct\n", test_num);
        passed++;
    }

    /* Test 6: size=1 with normal src */
    test_num++;
    memset(buf, 'X', sizeof(buf));
    crashed = 0;
    safe_strncpy(buf, "hello", 1);
    if (crashed) {
        printf("FAIL Test %d (size=1 normal): CRASHED\n", test_num);
        failed++;
    } else if (buf[0] != '\0') {
        printf("FAIL Test %d (size=1 normal): buf[0]=%d (expected 0)\n", test_num, buf[0]);
        failed++;
    } else {
        printf("PASS Test %d (size=1 normal): buf[0] zeroed, correct\n", test_num);
        passed++;
    }

    printf("\n=== RESULTS: %d passed, %d failed ===\n", passed, failed);
    return failed > 0 ? 1 : 0;
}
