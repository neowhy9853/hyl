#include <libsoup/soup-status.h>
#include <cstdio>

int main(void) {
    SoupKnownStatusCode status = SOUP_STATUS_OK;
    printf("status = %d\n", (int)status);
    return 0;
}
