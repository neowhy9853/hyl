#include "midx.h"

/*
 * Test to verify API signature compatibility.
 * 
 * write_midx_file_only() gained a new `const char *incremental_base`
 * parameter (before flags).
 * write_midx_file_compact() gained the same parameter.
 * 
 * Compiling with the new header means callers must pass 6 and 5
 * arguments respectively instead of 5 and 4.
 */

/* write_midx_file_only with new signature (6 params) */
int test_write_midx_file_only(void) {
    return write_midx_file_only(NULL, NULL, NULL, NULL, NULL, 0);
}

/* write_midx_file_compact with new signature (5 params) */
int test_write_midx_file_compact(void) {
    return write_midx_file_compact(NULL, NULL, NULL, NULL, 0);
}

/* write_midx_file (unchanged - 4 params) */
int test_write_midx_file(void) {
    return write_midx_file(NULL, NULL, NULL, 0);
}

int main(void) {
    int ret = 0;
    ret += test_write_midx_file_only();
    ret += test_write_midx_file_compact();
    ret += test_write_midx_file();
    return ret ? 1 : 0;
}
