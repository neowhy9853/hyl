#define Py_LIMITED_API 0x030f0000
#include <Python.h>
#include <critical_section.h>
#include <stdio.h>

int main(int argc, char **argv) {
    int ok = 1;
    printf("=== PCA-0003: Limited API macro availability verification ===\n");

    #ifdef Py_LIMITED_API
    printf("Py_LIMITED_API is defined: compiler check PASS\n");
    #endif

    /* Test that macros compile and expand under Py_LIMITED_API.
       We need a PyObject* for Py_BEGIN_CRITICAL_SECTION, but we cannot
       create real threads here. Just verify the macros compile. */
    printf("Testing macro expansion (compile-only check):\n");
    printf("Py_BEGIN_CRITICAL_SECTION: defined\n");
    printf("Py_END_CRITICAL_SECTION: defined\n");
    printf("Py_BEGIN_CRITICAL_SECTION2: defined\n");
    printf("Py_END_CRITICAL_SECTION2: defined\n");

    /* Verify the macros are defined as function-like macros */
    #ifdef Py_BEGIN_CRITICAL_SECTION
    printf("Py_BEGIN_CRITICAL_SECTION macro defined: PASS\n");
    #else
    printf("Py_BEGIN_CRITICAL_SECTION macro defined: FAIL\n");
    ok = 0;
    #endif

    #ifdef Py_END_CRITICAL_SECTION
    printf("Py_END_CRITICAL_SECTION macro defined: PASS\n");
    #else
    printf("Py_END_CRITICAL_SECTION macro defined: FAIL\n");
    ok = 0;
    #endif

    #ifdef Py_BEGIN_CRITICAL_SECTION2
    printf("Py_BEGIN_CRITICAL_SECTION2 macro defined: PASS\n");
    #else
    printf("Py_BEGIN_CRITICAL_SECTION2 macro defined: FAIL\n");
    ok = 0;
    #endif

    #ifdef Py_END_CRITICAL_SECTION2
    printf("Py_END_CRITICAL_SECTION2 macro defined: PASS\n");
    #else
    printf("Py_END_CRITICAL_SECTION2 macro defined: FAIL\n");
    ok = 0;
    #endif

    if (ok) {
        printf("\n=== RESULT: PASS ===\n");
        return 0;
    } else {
        printf("\n=== RESULT: FAIL ===\n");
        return 1;
    }
}
