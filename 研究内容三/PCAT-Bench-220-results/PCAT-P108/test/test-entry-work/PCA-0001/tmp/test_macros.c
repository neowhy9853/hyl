#include <libsoup/soup-status.h>
#include <stdio.h>
#include <assert.h>

int main(void) {
    assert(SOUP_STATUS_IS_SUCCESSFUL(200));
    assert(SOUP_STATUS_IS_REDIRECTION(301));
    assert(SOUP_STATUS_IS_CLIENT_ERROR(404));
    assert(SOUP_STATUS_IS_SERVER_ERROR(500));
    assert(SOUP_STATUS_IS_TRANSPORT_ERROR(1));
    printf("All status class macros work correctly\n");
    return 0;
}
