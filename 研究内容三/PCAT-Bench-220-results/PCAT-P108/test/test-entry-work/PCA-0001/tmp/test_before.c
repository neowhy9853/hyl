#include "soup-status-old.h"
#include <stdio.h>

int main(void) {
    SoupKnownStatusCode status = SOUP_STATUS_OK;
    printf("Before patch: SoupKnownStatusCode OK = %d\n", (int)status);
    return 0;
}
