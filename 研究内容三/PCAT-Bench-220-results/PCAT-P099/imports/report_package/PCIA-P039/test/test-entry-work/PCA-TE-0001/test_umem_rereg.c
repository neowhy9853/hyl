/* Test harness for ib_umem_check_rereg() compatibility contract verification.
 *
 * Compiles the exact patched ib_umem_check_rereg() function with mock headers.
 * Tests the INPUT_CONTRACT_CHANGE: RO umem + RW access request now returns -EACCES.
 */
#include <stdio.h>
#include <string.h>
#include "ib_umem_mock.h"

#define ERROR_MACRO(_err) (_err)

int ib_umem_check_rereg(struct ib_umem *umem, int flags, int new_access_flags);

/* ---- Exact copy of patched function from umem.c:330-344 ---- */
#include "umem_patched.c.inc"

static int tests_run = 0;
static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) do { tests_run++; printf("  TEST %s ... ", name); } while(0)
#define PASS() do { tests_passed++; printf("PASS\n"); } while(0)
#define FAIL(msg) do { tests_failed++; printf("FAIL: %s\n", msg); } while(0)
#define ASSERT_EQ(a, b, msg) do { \
    if ((a) != (b)) { \
        FAIL(msg); \
        printf("    expected %d, got %d\n", (int)(b), (int)(a)); \
    } else { PASS(); } \
} while(0)

int main(void) {
    struct ib_umem ro_umem = { .writable = 0 };
    struct ib_umem rw_umem = { .writable = 1 };
    struct ib_umem *null_umem = NULL;
    int ret;

    printf("=== ib_umem_check_rereg() Compatibility Contract Verification ===\n");
    printf("Patch: 09dc18894148381d3bfc550083b1236043870dce\n");
    printf("Finding: PCA-0001 INPUT_CONTRACT_CHANGE\n\n");

    /* --- Contract: NULL umem should succeed (no-op) --- */
    printf("--- NULL umem cases ---\n");
    TEST("null umem, no flags");
    ret = ib_umem_check_rereg(null_umem, 0, 0);
    ASSERT_EQ(ret, 0, "null umem should return 0");

    TEST("null umem, REREG_ACCESS only, writable request");
    ret = ib_umem_check_rereg(null_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_WRITE);
    ASSERT_EQ(ret, 0, "null umem should return 0 regardless of flags");

    /* --- Contract: Already-writable umem should always succeed --- */
    printf("\n--- Writable umem cases (should always succeed) ---\n");
    TEST("rw umem, no flags");
    ret = ib_umem_check_rereg(&rw_umem, 0, 0);
    ASSERT_EQ(ret, 0, "rw umem without flags should return 0");

    TEST("rw umem, REREG_ACCESS only, writable request");
    ret = ib_umem_check_rereg(&rw_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_WRITE);
    ASSERT_EQ(ret, 0, "rw umem REREG_ACCESS with writable request should succeed");

    TEST("rw umem, REREG_ACCESS only, read-only request");
    ret = ib_umem_check_rereg(&rw_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_READ);
    ASSERT_EQ(ret, 0, "rw umem REREG_ACCESS with read request should succeed");

    /* --- KEY COMPATIBILITY CHANGE: RO umem + RW access without REREG_TRANS now fails --- */
    printf("\n--- RO umem cases (COMPATIBILITY CHANGE) ---\n");

    TEST("ro umem, no flags → should succeed");
    ret = ib_umem_check_rereg(&ro_umem, 0, 0);
    ASSERT_EQ(ret, 0, "ro umem without flags should return 0");

    TEST("ro umem, REREG_ACCESS only, writable request → should FAIL with -EACCES");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_WRITE);
    ASSERT_EQ(ret, -13, "ro umem REREG_ACCESS + writable should return -EACCES (-13)");

    TEST("ro umem, REREG_ACCESS only, local write → should FAIL with -EACCES");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS, IB_ACCESS_LOCAL_WRITE);
    ASSERT_EQ(ret, -13, "ro umem REREG_ACCESS + local write should return -EACCES");

    TEST("ro umem, REREG_ACCESS only, remote atomic → should FAIL with -EACCES");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_ATOMIC);
    ASSERT_EQ(ret, -13, "ro umem REREG_ACCESS + remote atomic should return -EACCES");

    TEST("ro umem, REREG_ACCESS only, MW bind → should FAIL with -EACCES");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS, IB_ACCESS_MW_BIND);
    ASSERT_EQ(ret, -13, "ro umem REREG_ACCESS + MW bind should return -EACCES");

    /* --- BOTH flags set: REREG_ACCESS + REREG_TRANS should succeed --- */
    printf("\n--- REREG_ACCESS + REREG_TRANS cases (should succeed) ---\n");

    TEST("ro umem, REREG_ACCESS+REREG_TRANS, writable request → should succeed");
    ret = ib_umem_check_rereg(&ro_umem,
        IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS, IB_ACCESS_REMOTE_WRITE);
    ASSERT_EQ(ret, 0, "ro umem with both REREG flags should succeed (driver handles translation)");

    TEST("ro umem, REREG_TRANS only, writable request → should succeed");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_TRANS, IB_ACCESS_REMOTE_WRITE);
    ASSERT_EQ(ret, 0, "ro umem with only REREG_TRANS should succeed");

    /* --- ro umem + read-only access request should succeed --- */
    printf("\n--- RO umem with read-only access (should succeed) ---\n");

    TEST("ro umem, REREG_ACCESS only, read request → should succeed");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS, IB_ACCESS_REMOTE_READ);
    ASSERT_EQ(ret, 0, "ro umem REREG_ACCESS + read request should succeed");

    /* --- Mixed writable access flag combinations --- */
    printf("\n--- Mixed writable flag combinations ---\n");

    TEST("ro umem, REREG_ACCESS only, LOCAL_WRITE|REMOTE_READ → should FAIL with -EACCES");
    ret = ib_umem_check_rereg(&ro_umem, IB_MR_REREG_ACCESS,
        IB_ACCESS_LOCAL_WRITE | IB_ACCESS_REMOTE_READ);
    ASSERT_EQ(ret, -13, "local write + remote read should trigger -EACCES on RO");

    /* --- Summary --- */
    printf("\n========================================\n");
    printf("RESULTS: %d run, %d passed, %d failed\n", tests_run, tests_passed, tests_failed);
    printf("========================================\n");

    return tests_failed ? 1 : 0;
}
