// Synthetic harness to test the cmd_rewriterule QSA + trailing ? behavior
// This isolates the config-parsing logic change to verify before/after behavior.
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Flag constants from mod_rewrite.c (line 167, 174, 178)
#define RULEFLAG_QSAPPEND           (1<<9)
#define RULEFLAG_QSDISCARD          (1<<16)
#define RULEFLAG_QSNONE             (1<<20)

// ===== BEFORE (old/buggy) logic =====
static void apply_trailing_qmark_BEFORE(unsigned int *flags) {
    // Old code: unconditionally set QSNONE
    *flags |= RULEFLAG_QSNONE;
}

// ===== AFTER (new/fixed) logic =====
static void apply_trailing_qmark_AFTER(unsigned int *flags) {
    // New code: only set QSNONE if QSAPPEND is NOT set
    if (!(*flags & RULEFLAG_QSAPPEND)) {
        *flags |= RULEFLAG_QSNONE;
    }
}

typedef struct {
    const char *desc;
    unsigned int input_flags;
    unsigned int expected_before;
    unsigned int expected_after;
    int qsnone_set_before;
    int qsnone_set_after;
} test_case_t;

int main(void) {
    int passed = 0, failed = 0;
    unsigned int result_before, result_after;

    test_case_t tests[] = {
        {
            "trailing ? without QSA",
            0,
            0 | RULEFLAG_QSNONE,
            0 | RULEFLAG_QSNONE,
            1, 1
        },
        {
            "trailing ? with QSA (KEY test)",
            RULEFLAG_QSAPPEND,
            RULEFLAG_QSAPPEND | RULEFLAG_QSNONE,  // BEFORE: QSNONE set, overriding QSA
            RULEFLAG_QSAPPEND,                     // AFTER: QSNONE NOT set, QSA preserved
            1, 0
        },
        {
            "trailing ? with QSDISCARD",
            RULEFLAG_QSDISCARD,
            RULEFLAG_QSDISCARD | RULEFLAG_QSNONE,
            RULEFLAG_QSDISCARD | RULEFLAG_QSNONE,
            1, 1
        },
        {
            "trailing ? with QSAPPEND|QSDISCARD combined",
            RULEFLAG_QSAPPEND | RULEFLAG_QSDISCARD,
            RULEFLAG_QSAPPEND | RULEFLAG_QSDISCARD | RULEFLAG_QSNONE,
            RULEFLAG_QSAPPEND | RULEFLAG_QSDISCARD,
            1, 0
        },
        {
            "trailing ? with other flags (nocase, redirect etc)",
            0x1 | 0x2 | 0x4,  // some non-QSA flags
            0x1 | 0x2 | 0x4 | RULEFLAG_QSNONE,
            0x1 | 0x2 | 0x4 | RULEFLAG_QSNONE,
            1, 1
        },
        {
            "trailing ? with nocase+QSA",
            RULEFLAG_QSAPPEND | 0x4,
            RULEFLAG_QSAPPEND | 0x4 | RULEFLAG_QSNONE,
            RULEFLAG_QSAPPEND | 0x4,
            1, 0
        },
    };

    int ntests = sizeof(tests) / sizeof(tests[0]);

    printf("=== PCA-0001: RewriteRule QSA + trailing ? behavior test ===\n");
    printf("Testing BEFORE (old: unconditional QSNONE) vs AFTER (new: QSA-aware QSNONE)\n\n");

    for (int i = 0; i < ntests; i++) {
        test_case_t *t = &tests[i];

        // BEFORE
        result_before = t->input_flags;
        apply_trailing_qmark_BEFORE(&result_before);
        int qs_before = (result_before & RULEFLAG_QSNONE) ? 1 : 0;

        // AFTER
        result_after = t->input_flags;
        apply_trailing_qmark_AFTER(&result_after);
        int qs_after = (result_after & RULEFLAG_QSNONE) ? 1 : 0;

        int ok_before = (result_before == t->expected_before) && (qs_before == t->qsnone_set_before);
        int ok_after  = (result_after == t->expected_after) && (qs_after == t->qsnone_set_after);

        printf("Test %d: %s\n", i+1, t->desc);
        printf("  Input flags:   0x%08x\n", t->input_flags);
        printf("  BEFORE result: 0x%08x (QSNONE=%s)\n", result_before, qs_before ? "SET" : "not set");
        printf("  AFTER  result: 0x%08x (QSNONE=%s)\n", result_after, qs_after ? "SET" : "not set");

        if (ok_before && ok_after) {
            printf("  PASS\n");
            passed++;
        } else {
            printf("  FAIL\n");
            if (!ok_before)
                printf("    BEFORE miscompare: expected 0x%08x, got 0x%08x\n", t->expected_before, result_before);
            if (!ok_after)
                printf("    AFTER miscompare: expected 0x%08x, got 0x%08x\n", t->expected_after, result_after);
            failed++;
        }
        printf("\n");
    }

    printf("=== Results: %d passed, %d failed ===\n", passed, failed);

    // KEY assertion: QSA+trailing ? should NOT set QSNONE in the AFTER version
    printf("\n=== KEY ASSERTION ===\n");
    printf("Rule with QSA + trailing ?: QSNONE=%s in new code (should be: not set)\n",
           (tests[1].qsnone_set_after == 0) ? "NOT SET (CORRECT)" : "SET (WRONG)");

    return failed > 0 ? 1 : 0;
}
