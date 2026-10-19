#define Py_LIMITED_API 0x030f0000
#include <Python.h>
#include <critical_section.h>
#include <stdio.h>

int main(int argc, char **argv) {
    printf("=== PCA-0002: Limited API function signature verification ===\n");

    /* Test that function declarations are accessible under Py_LIMITED_API */
    /* Declare function pointers to verify signatures */
    void (*fn_begin)(PyCriticalSection *, PyObject *) = PyCriticalSection_Begin;
    void (*fn_end)(PyCriticalSection *) = PyCriticalSection_End;
    void (*fn_begin2)(PyCriticalSection2 *, PyObject *, PyObject *) = PyCriticalSection2_Begin;
    void (*fn_end2)(PyCriticalSection2 *) = PyCriticalSection2_End;

    printf("PyCriticalSection_Begin function pointer: %p\n", (void*)fn_begin);
    printf("PyCriticalSection_End function pointer: %p\n", (void*)fn_end);
    printf("PyCriticalSection2_Begin function pointer: %p\n", (void*)fn_begin2);
    printf("PyCriticalSection2_End function pointer: %p\n", (void*)fn_end2);

    #ifdef Py_LIMITED_API
    printf("Py_LIMITED_API is defined: compiler check PASS\n");
    #endif

    /* Verify linkage resolves */
    if (fn_begin == NULL || fn_end == NULL || fn_begin2 == NULL || fn_end2 == NULL) {
        printf("\n=== RESULT: FAIL (NULL function pointers) ===\n");
        return 1;
    }

    printf("\n=== RESULT: PASS ===\n");
    return 0;
}
