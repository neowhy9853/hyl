/*
 * PCA-0001: ABI verification - SoupCookieJarClass struct layout change
 * Tests struct size and field offsets to verify ABI compatibility.
 */
#define LIBSOUP_DISABLE_DEPRECATED
#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
#include "../libsoup/soup-cookie-jar.h"
#include "../libsoup/soup-cookie.h"
#include "../libsoup/soup-date.h"

#define CHECK(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s\n", msg); return 1; } \
    else { printf("PASS: %s\n", msg); } \
} while(0)

int main() {
    printf("=== PCA-0001: ABI verification - SoupCookieJarClass vtable layout ===\n");

    /* Verify class struct has expected number of function pointers */
    size_t class_size = sizeof(SoupCookieJarClass);

    /* Expected: parent_class (GObjectClass) + save + changed + 3 reserved pointers */
    size_t expected_offset_save = G_STRUCT_OFFSET(SoupCookieJarClass, save);
    size_t expected_offset_changed = G_STRUCT_OFFSET(SoupCookieJarClass, changed);

    printf("SoupCookieJarClass size: %zu bytes\n", class_size);
    printf("Offset of save:    %zu\n", expected_offset_save);
    printf("Offset of changed: %zu\n", expected_offset_changed);

    CHECK(expected_offset_save == G_STRUCT_OFFSET(GObjectClass, _g_type_reserved0) + sizeof(gpointer),
          "save offset follows GObjectClass");

    CHECK(expected_offset_changed > expected_offset_save,
          "changed field exists after save");

    /* Verify the changed field is at the position previously held by _libsoup_reserved1 */
    CHECK(expected_offset_changed == expected_offset_save + sizeof(gpointer),
          "changed is directly after save (replaces reserved1 position)");

    /* Verify total slot count (save + changed + reserved1 + reserved2 + reserved3) = 5 */
    size_t slots_after_save = (class_size - expected_offset_save) / sizeof(gpointer);
    printf("Function pointer slots after save: %zu\n", slots_after_save);
    CHECK(slots_after_save == 5, "5 slots after save (save, changed, 3 reserved)");

    /* Verify SoupCookieJarClass exists and is linkable */
    GType t = soup_cookie_jar_get_type();
    CHECK(t != 0, "soup_cookie_jar_get_type() returns valid GType");

    printf("\n=== PCA-0001: PASSED ===\n");
    return 0;
}
