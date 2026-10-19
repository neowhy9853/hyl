/*
 * PCA-0001: API_SIGNATURE_CHANGE - ratelimitAddConfig signature change
 *
 * This test harness verifies that the old 13-parameter signature of
 * ratelimitAddConfig no longer compiles against the new header.
 *
 * Expected behavior:
 * - Compilation with the OLD signature (13 params): FAILS with
 *   "too few arguments to function" or similar error.
 * - Compilation with the NEW signature (15 params): SUCCEEDS.
 *
 * Build (requires librsyslog built from analysis_repo):
 *   gcc -I<analysis_repo> -I<analysis_repo>/runtime ... -c reproducer.c
 *
 * Reachability signal:
 *   Compile error on line calling the old signature.
 */

#include "ratelimit.h"
#include "rsconf.h"

/* Old 13-parameter call (will fail with new header) */
int test_old_signature(void) {
    rsconf_t *conf = NULL;
    const char *name = "test";
    unsigned int interval = 60;
    unsigned int burst = 10;
    int severity = 5;
    const char *policy_file = NULL;
    sbool policy_watch = 0;
    const char *policy_watch_debounce = NULL;
    sbool per_source_enabled = 0;
    const char *per_source_policy_file = NULL;
    const char *per_source_key_tpl_name = NULL;
    unsigned int per_source_max_states = 0;
    unsigned int per_source_topn = 0;

    /* OLD signature - missing has_inline_policy_params, has_legacy_per_source_params */
    rsRetVal ret = ratelimitAddConfig(
        conf, name, interval, burst, severity,
        policy_file, policy_watch, policy_watch_debounce,
        per_source_enabled, per_source_policy_file,
        per_source_key_tpl_name, per_source_max_states,
        per_source_topn
    );

    return (ret == RS_RET_OK) ? 0 : 1;
}

/* New 15-parameter call (should succeed) */
int test_new_signature(void) {
    rsconf_t *conf = NULL;
    const char *name = "test";
    unsigned int interval = 60;
    unsigned int burst = 10;
    int severity = 5;
    const char *policy_file = NULL;
    sbool policy_watch = 0;
    const char *policy_watch_debounce = NULL;
    sbool per_source_enabled = 0;
    const char *per_source_policy_file = NULL;
    const char *per_source_key_tpl_name = NULL;
    unsigned int per_source_max_states = 0;
    unsigned int per_source_topn = 0;

    /* NEW signature - includes both new params */
    rsRetVal ret = ratelimitAddConfig(
        conf, name, interval, burst, severity,
        policy_file, policy_watch, policy_watch_debounce,
        per_source_enabled, per_source_policy_file,
        per_source_key_tpl_name, per_source_max_states,
        per_source_topn,
        0,  /* has_inline_policy_params */
        0   /* has_legacy_per_source_params */
    );

    return (ret == RS_RET_OK) ? 0 : 1;
}

int main(void) {
    /* Only test_new_signature should compile with the new header */
    return test_new_signature();
}
