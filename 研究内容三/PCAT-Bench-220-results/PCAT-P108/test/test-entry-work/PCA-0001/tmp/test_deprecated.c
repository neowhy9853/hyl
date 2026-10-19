#include <libsoup/soup-status.h>
#include <stdio.h>

int main(void) {
    SoupKnownStatusCode status = SOUP_KNOWN_STATUS_CODE_OK;
    printf("Deprecated SoupKnownStatusCode OK = %d\n", (int)status);
    return 0;
}
