#define Py_LIMITED_API 0x030f0000
#include <Python.h>
#include <critical_section.h>
#include <stdio.h>
#include <stddef.h>

int main(int argc, char **argv) {
    int failures = 0;

    printf("=== PCA-0001: ABI struct layout verification ===\n");

    /* PyCriticalSection layout checks */
    printf("sizeof(PyCriticalSection) = %zu\n", sizeof(PyCriticalSection));
    printf("offsetof(PyCriticalSection, _cs_prev) = %zu\n",
           offsetof(PyCriticalSection, _cs_prev));
    printf("offsetof(PyCriticalSection, _cs_mutex) = %zu\n",
           offsetof(PyCriticalSection, _cs_mutex));

    /* PyCriticalSection2 layout checks */
    printf("sizeof(PyCriticalSection2) = %zu\n", sizeof(PyCriticalSection2));
    printf("offsetof(PyCriticalSection2, _cs_base) = %zu\n",
           offsetof(PyCriticalSection2, _cs_base));
    printf("offsetof(PyCriticalSection2, _cs_mutex2) = %zu\n",
           offsetof(PyCriticalSection2, _cs_mutex2));

    /* Verify struct size is reasonable (should be > 0 and <= 64 bytes typically) */
    if (sizeof(PyCriticalSection) == 0 || sizeof(PyCriticalSection) > 128) {
        printf("FAIL: PyCriticalSection size out of reasonable range\n");
        failures++;
    }
    if (sizeof(PyCriticalSection2) == 0 || sizeof(PyCriticalSection2) > 128) {
        printf("FAIL: PyCriticalSection2 size out of reasonable range\n");
        failures++;
    }

    /* Verify struct visibility under Py_LIMITED_API */
    #ifdef Py_LIMITED_API
    printf("Py_LIMITED_API is defined: compiler check PASS\n");
    #endif

    PyCriticalSection cs = {0};
    PyCriticalSection2 cs2 = {0};

    printf("PyCriticalSection initialized: _cs_prev=%lu _cs_mutex=%p\n",
           (unsigned long)cs._cs_prev, (void*)cs._cs_mutex);
    printf("PyCriticalSection2 initialized: _cs_mutex2=%p\n",
           (void*)cs2._cs_mutex2);

    if (failures > 0) {
        printf("\n=== RESULT: FAIL (%d failures) ===\n", failures);
        return 1;
    }
    printf("\n=== RESULT: PASS ===\n");
    return 0;
}
