#include "ratelimit.h"
#include "rsconf.h"

int main(void) {
    /* New 15-parameter call - should compile cleanly */
    rsRetVal ret = ratelimitAddConfig(
        NULL, "test", 60, 10, 5,
        NULL, 0, NULL,
        0, NULL, NULL, 0, 0,
        0,  /* has_inline_policy_params */
        0   /* has_legacy_per_source_params */
    );
    return 0;
}
