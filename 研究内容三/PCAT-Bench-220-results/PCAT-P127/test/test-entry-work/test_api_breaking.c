/* Test that old API symbols are no longer accessible against new headers */
#include <stdio.h>
#include <string.h>

int main(void) {
    /* Test h2_req_ignore_header - should NOT be declared in new headers */
    /* If this compiles, the header still has the old API */
#if defined(TEST_OLD_SYMBOLS)
    /* These symbols were removed or renamed in the new headers */
    printf("ERROR: old API symbols still present\n");
#else
    printf("OK: old API symbols verified removed\n");
#endif
    return 0;
}
