# PCA-0003: OUTPUT_FORMAT_CHANGE - Stats Counter Addition

## Overview
4 new stats counters were added to every action: `ratelimit.allowed`, `ratelimit.dropped`, `ratelimit.paced`, `ratelimit.paced_usec`.

## Existing Tests (project-native)
The following existing tests already validate the stats output format and were updated in this patch:

- `tests/stats-cee.sh` - CEE format stats
- `tests/stats-json.sh` - JSON format stats
- `tests/stats-json-es.sh` - JSON ES format stats
- `tests/stats-cee-vg.sh` - CEE valgrind variant
- `tests/stats-json-vg.sh` - JSON valgrind variant

## Test Procedure
1. Build the patched binary
2. Run: `make check TESTS='tests/stats-cee.sh tests/stats-json.sh tests/stats-json-es.sh'`
3. Each test validates that the new counters appear with value 0 for an idle action.

## Expected Signal
The `custom_content_check` in each test script verifies the full stats JSON includes the new ratelimit.* counters.

## Setup
```bash
cd <analysis_repo>
./autogen.sh --enable-testbench --enable-imdiag
make -j$(nproc) check TESTS=''
# Then run specific tests
make check TESTS='tests/stats-cee.sh tests/stats-json.sh'
```
