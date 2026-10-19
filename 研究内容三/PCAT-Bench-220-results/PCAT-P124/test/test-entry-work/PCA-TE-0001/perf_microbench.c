/*
 * PCA Performance Microbenchmark: grub_get_tsc() CPUID overhead
 *
 * This benchmark measures the performance overhead of adding a CPUID
 * serializing instruction after RDTSC in grub_get_tsc().
 *
 * Old pattern: cpuid; rdtsc
 * New pattern: cpuid; rdtsc; cpuid
 *
 * Patch: 531750f7bfc475332b2046dd516bab582ba7decf
 * File:  include/grub/i386/tsc.h
 * Lines: 47-57 (new), 47-52 (old)
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* ---- Assembly helpers matching GRUB's patterns ---- */

/* CPUID instruction - serializing, outputs to eax/ebx/ecx/edx */
static inline void do_cpuid(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d)
{
    asm volatile("cpuid"
                 : "=a"(*a), "=b"(*b), "=c"(*c), "=d"(*d)
                 : "0"(0));
}

/* RDTSC - read time stamp counter */
static inline uint64_t do_rdtsc(void)
{
    uint32_t lo, hi;
    asm volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

/*
 * Old grub_get_tsc() pattern (before patch):
 *   cpuid; rdtsc; return
 * This has CPUID before RDTSC but NOT after.
 */
static inline uint64_t old_grub_get_tsc(void)
{
    uint32_t a, b, c, d;
    uint32_t lo, hi;

    /* CPUID before RDTSC - serializes prior instructions */
    do_cpuid(&a, &b, &c, &d);
    /* RDTSC */
    asm volatile("rdtsc" : "=a"(lo), "=d"(hi));

    return ((uint64_t)hi << 32) | lo;
}

/*
 * New grub_get_tsc() pattern (after patch):
 *   cpuid; rdtsc; cpuid; return
 * This has CPUID both before AND after RDTSC for full serialization.
 */
static inline uint64_t new_grub_get_tsc(void)
{
    uint32_t a, b, c, d;
    uint32_t lo, hi;

    /* CPUID before RDTSC - serializes prior instructions */
    do_cpuid(&a, &b, &c, &d);
    /* RDTSC */
    asm volatile("rdtsc" : "=a"(lo), "=d"(hi));
    /* CPUID after RDTSC - ensures RDTSC completes before subsequent instructions */
    do_cpuid(&a, &b, &c, &d);

    return ((uint64_t)hi << 32) | lo;
}

/* ---- Timing infrastructure ---- */

static inline uint64_t time_call_new(uint64_t *dummy)
{
    uint64_t start, end;
    start = do_rdtsc();
    *dummy = new_grub_get_tsc();
    end = do_rdtsc();
    return end - start;
}

static inline uint64_t time_call_old(uint64_t *dummy)
{
    uint64_t start, end;
    start = do_rdtsc();
    *dummy = old_grub_get_tsc();
    end = do_rdtsc();
    return end - start;
}

/* ---- Main benchmark ---- */

int main(int argc, char **argv)
{
    long iterations = 1000000;
    int json_output = 0;
    int i;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc) {
            iterations = atol(argv[++i]);
        } else if (strcmp(argv[i], "--json") == 0) {
            json_output = 1;
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [--iterations N] [--json]\n", argv[0]);
            printf("  --iterations N   Number of warmup+measurement iterations (default 1000000)\n");
            printf("  --json           Output results as JSON\n");
            return 0;
        }
    }

    if (iterations <= 0) iterations = 1000000;

    /* Validate CPUID and RDTSC are available */
    uint32_t a, b, c, d;
    do_cpuid(&a, &b, &c, &d);
    if (a == 0 && b == 0 && c == 0 && d == 0) {
        fprintf(stderr, "ERROR: CPUID returned all zeros - test cannot run\n");
        return 1;
    }

    uint64_t dummy;
    uint64_t old_total = 0, new_total = 0;
    long warmup = iterations / 10;  /* 10% warmup */

    /* Warmup: old pattern */
    for (i = 0; i < warmup; i++) {
        dummy = old_grub_get_tsc();
    }

    /* Measure: old pattern */
    for (i = 0; i < iterations; i++) {
        old_total += time_call_old(&dummy);
    }

    /* Warmup: new pattern */
    for (i = 0; i < warmup; i++) {
        dummy = new_grub_get_tsc();
    }

    /* Measure: new pattern */
    for (i = 0; i < iterations; i++) {
        new_total += time_call_new(&dummy);
    }

    double old_avg = (double)old_total / iterations;
    double new_avg = (double)new_total / iterations;
    double overhead = new_avg - old_avg;
    double overhead_pct = old_avg > 0 ? (overhead / old_avg) * 100.0 : 0.0;
    int new_is_slower = new_avg > old_avg ? 1 : 0;

    if (json_output) {
        printf("{");
        printf("\"test_name\": \"grub_get_tsc_cpuid_overhead\",");
        printf("\"patch_id\": \"531750f7bfc475332b2046dd516bab582ba7decf\",");
        printf("\"compatibility_type\": \"PERFORMANCE_RESOURCE_SEMANTIC_CHANGE\",");
        printf("\"old_cycles_per_call\": %.2f,", old_avg);
        printf("\"new_cycles_per_call\": %.2f,", new_avg);
        printf("\"overhead_cycles\": %.2f,", overhead);
        printf("\"overhead_percent\": %.2f,", overhead_pct);
        printf("\"iterations\": %ld,", iterations);
        printf("\"new_pattern_is_slower\": %s,", new_is_slower ? "true" : "false");
        printf("\"old_pattern_description\": \"cpuid; rdtsc (no serialization after)\",");
        printf("\"new_pattern_description\": \"cpuid; rdtsc; cpuid (full serialization)\",");
        printf("\"arch\": \"%s\",",
#if defined(__x86_64__)
               "x86_64"
#elif defined(__i386__)
               "i386"
#else
               "unknown"
#endif
        );
        printf("\"nonsense_consumed_by_dummy\": \"%lu\"", (unsigned long)dummy);
        printf("}\n");
    } else {
        printf("=== grub_get_tsc() CPUID Serialization Overhead Benchmark ===\n");
        printf("Patch: 531750f7bfc475332b2046dd516bab582ba7decf\n");
        printf("Iterations: %ld\n\n", iterations);
        printf("Old pattern (cpuid; rdtsc):          %.2f cycles/call\n", old_avg);
        printf("New pattern (cpuid; rdtsc; cpuid):   %.2f cycles/call\n", new_avg);
        printf("Overhead:                             %.2f cycles (%.2f%%)\n",
               overhead, overhead_pct);
        printf("\nConclusion: new pattern is %s\n",
               new_is_slower ? "SLOWER (expected - added CPUID serialization)" :
               "FASTER (unexpected - measurement noise)");
    }

    return 0;
}
