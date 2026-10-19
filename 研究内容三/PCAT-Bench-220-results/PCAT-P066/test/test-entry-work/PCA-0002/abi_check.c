/*
 * PCA-0002: ABI_CHANGE - struct layout verification for action_s and ratelimit_shared_s
 *
 * This program checks the sizes and field offsets of the changed structs.
 * Print offsets for the fields that shifted due to the insertion of new fields.
 *
 * Build (requires librsyslog built from analysis_repo):
 *   gcc -I<analysis_repo> -I<analysis_repo>/runtime -o abi_check abi_check.c -L<build_dir>/runtime/.libs -lrsyslog
 *
 *  Expected output (NEW layout):
 *   sizeof(action_s) = <new_size>
 *   offsetof(action_s.pszRatelimitName) = <offset_after_pszName>
 *   offsetof(action_s.ratelimiter) = <offset_after_pszRatelimitName>
 *   offsetof(ratelimit_shared_s.scope) = <offset_after_name>
 *   offsetof(ratelimit_shared_s.output_mode) = <offset_after_scope>
 *   offsetof(ratelimit_shared_s.output_pace_forbidden) = <offset_after_output_mode>
 *   offsetof(ratelimit_shared_s.interval) = <shifted_offset>
 *
 * Reachability signal:
 *   Program runs and prints struct layout info.
 */

#include <stdio.h>
#include <stddef.h>
#include "action.h"
#include "ratelimit.h"

int main(void) {
    printf("=== action_s struct layout (patched) ===\n");
    printf("sizeof(action_s) = %zu\n", sizeof(action_t));
    printf("offsetof(pszName) = %zu\n", offsetof(action_t, pszName));
    printf("offsetof(pszRatelimitName) = %zu\n", offsetof(action_t, pszRatelimitName));
    printf("offsetof(ratelimiter) = %zu\n", offsetof(action_t, ratelimiter));
    printf("offsetof(ctrProcessed) = %zu\n", offsetof(action_t, ctrProcessed));
    printf("offsetof(ctrRateLimitAllowed) = %zu\n", offsetof(action_t, ctrRateLimitAllowed));
    printf("offsetof(ctrRateLimitDropped) = %zu\n", offsetof(action_t, ctrRateLimitDropped));
    printf("offsetof(ctrRateLimitPaced) = %zu\n", offsetof(action_t, ctrRateLimitPaced));
    printf("offsetof(ctrRateLimitPacedUsec) = %zu\n", offsetof(action_t, ctrRateLimitPacedUsec));

    printf("\n=== ratelimit_shared_s struct layout (patched) ===\n");
    printf("sizeof(ratelimit_shared_t) = %zu\n", sizeof(ratelimit_shared_t));
    printf("offsetof(name) = %zu\n", offsetof(ratelimit_shared_t, name));
    printf("offsetof(scope) = %zu\n", offsetof(ratelimit_shared_t, scope));
    printf("offsetof(output_mode) = %zu\n", offsetof(ratelimit_shared_t, output_mode));
    printf("offsetof(output_pace_forbidden) = %zu\n", offsetof(ratelimit_shared_t, output_pace_forbidden));
    printf("offsetof(interval) = %zu\n", offsetof(ratelimit_shared_t, interval));

    return 0;
}
