#include <libsoup/soup-status.h>
#include <stdio.h>

int main(void) {
    SoupStatus status = SOUP_STATUS_OK;
    printf("SoupStatus OK = %d\n", (int)status);
    printf("SOUP_STATUS_NOT_FOUND = %d\n", (int)SOUP_STATUS_NOT_FOUND);
    printf("SOUP_STATUS_INTERNAL_SERVER_ERROR = %d\n", (int)SOUP_STATUS_INTERNAL_SERVER_ERROR);
    return 0;
}
