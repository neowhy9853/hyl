#include <libsoup/soup-status.h>
#include <stdio.h>
#include <assert.h>

int main(void) {
    assert(SOUP_STATUS_OK == SOUP_KNOWN_STATUS_CODE_OK);
    assert(SOUP_STATUS_NOT_FOUND == SOUP_KNOWN_STATUS_CODE_NOT_FOUND);
    assert(SOUP_STATUS_CANCELLED == SOUP_KNOWN_STATUS_CODE_CANCELLED);
    assert(SOUP_STATUS_INTERNAL_SERVER_ERROR == SOUP_KNOWN_STATUS_CODE_INTERNAL_SERVER_ERROR);
    printf("All enum values match between SoupStatus and SoupKnownStatusCode\n");
    return 0;
}
