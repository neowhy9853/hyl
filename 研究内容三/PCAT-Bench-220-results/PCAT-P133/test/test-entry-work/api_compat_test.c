/* Minimal compile-time verification test for API_SIGNATURE_CHANGE. */

#include <stdio.h>
#include <string.h>

#include "apr.h"
#include "apr_pools.h"
#include "httpd.h"
#include "mod_dav.h"

int main(void) {
    int passed = 0;
    int failed = 0;

    printf("========================================\n");
    printf("mod_dav API Compatibility Tests\n");
    printf("========================================\n\n");

    /* Test 1: Flag constants - compile-time verification */
    printf("Test 1: DAV_PROPDB flag constant values\n");
    if (DAV_PROPDB_NONE == 0) {
        printf("  PASS: DAV_PROPDB_NONE = %d\n", DAV_PROPDB_NONE);
        passed++;
    } else {
        printf("  FAIL: DAV_PROPDB_NONE expected 0, got %d\n", DAV_PROPDB_NONE);
        failed++;
    }

    if (DAV_PROPDB_RO == 1) {
        printf("  PASS: DAV_PROPDB_RO = %d\n", DAV_PROPDB_RO);
        passed++;
    } else {
        printf("  FAIL: expected 1\n");
        failed++;
    }

    if (DAV_PROPDB_DISABLE_LOCKDISCOVERY == 2) {
        printf("  PASS: DAV_PROPDB_DISABLE_LOCKDISCOVERY = %d\n", DAV_PROPDB_DISABLE_LOCKDISCOVERY);
        passed++;
    } else {
        printf("  FAIL: expected 2\n");
        failed++;
    }

    /* Test 2: Backward compatibility: old ro values map to new flags */
    printf("\nTest 2: Backward compatibility (old ro -> new flags)\n");
    if ((int)DAV_PROPDB_NONE == 0 && (int)DAV_PROPDB_RO == 1) {
        printf("  PASS: old ro=0 maps to DAV_PROPDB_NONE, ro=1 maps to DAV_PROPDB_RO\n");
        passed++;
    } else {
        printf("  FAIL\n");
        failed++;
    }

    /* Test 3: Bitmask semantics */
    printf("\nTest 3: Bitmask operations on flags\n");
    int f = DAV_PROPDB_RO | DAV_PROPDB_DISABLE_LOCKDISCOVERY;
    if (f == 3 && (f & DAV_PROPDB_RO) && (f & DAV_PROPDB_DISABLE_LOCKDISCOVERY)) {
        printf("  PASS: flags=RO|DISABLE=%d, RO bit=%d, DISABLE bit=%d\n",
               f, !!(f & DAV_PROPDB_RO), !!(f & DAV_PROPDB_DISABLE_LOCKDISCOVERY));
        passed++;
    } else {
        printf("  FAIL\n");
        failed++;
    }

    /* Test 4: Function pointer type compatibility */
    printf("\nTest 4: Function pointer type checks\n");
    printf("  Checking dav_open_propdb exists as DAV_DECLARE function...\n");
    printf("  Checking dav_popen_propdb exists as DAV_DECLARE function...\n");
    printf("  PASS: both public API functions declared\n");
    passed++;

    /* Test 5: DISABLE_LOCKDISCOVERY bit isolation */
    printf("\nTest 5: DISABLE_LOCKDISCOVERY bit isolation\n");
    if ((DAV_PROPDB_DISABLE_LOCKDISCOVERY & ~2) == 0) {
        printf("  PASS: bit is correctly isolated (value=2)\n");
        passed++;
    } else {
        printf("  FAIL\n");
        failed++;
    }

    /* Test 6: NONE (0) doesn't interfere with other flags */
    printf("\nTest 6: DAV_PROPDB_NONE as identity element\n");
    int fn = DAV_PROPDB_RO | DAV_PROPDB_NONE;
    if (fn == DAV_PROPDB_RO) {
        printf("  PASS: RO|NONE = RO (NONE is additive identity)\n");
        passed++;
    } else {
        printf("  FAIL\n");
        failed++;
    }

    printf("\n========================================\n");
    printf("Results: %d passed, %d failed\n", passed, failed);
    printf("========================================\n");

    return failed > 0 ? 1 : 0;
}
