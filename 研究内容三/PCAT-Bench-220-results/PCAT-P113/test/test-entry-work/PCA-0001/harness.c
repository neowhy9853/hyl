/*
 * PCA-0001 Test Harness: Conditional Authorization Header Removal
 *
 * This program validates that user-provided Authorization headers on a
 * SoupMessage are preserved when no cached credentials exist (the fix
 * for GNOME bug 775882 / commit a8982b03).
 *
 * It tests the behavioral change in update_authorization_header() where:
 *   Before: Authorization header ALWAYS removed
 *   After:  Authorization header only removed when soup_message_get_auth(msg)
 *           returns non-NULL
 *
 * Build (requires libsoup-2.4-dev, glib-2.0-dev):
 *   gcc -Wall -O0 -g -fprofile-arcs -ftest-coverage \
 *       $(pkg-config --cflags libsoup-2.4 glib-2.0) \
 *       -o auth-header-test harness.c \
 *       $(pkg-config --libs libsoup-2.4 glib-2.0) \
 *       -lgcov --coverage
 *
 * This is a synthetic harness (entry source #6).
 */

#include <libsoup/soup.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void
on_authenticate(SoupSession *session, SoupMessage *msg,
                SoupAuth *auth, gboolean retrying, gpointer user_data)
{
    gboolean *authenticate_called = (gboolean *)user_data;
    *authenticate_called = TRUE;
    soup_auth_authenticate(auth, "testuser", "testpass");
}

static void
on_server_request(SoupServer *server, SoupMessage *msg,
                  const char *path, GHashTable *query,
                  SoupClientContext *client, gpointer user_data)
{
    const char *auth_header;

    auth_header = soup_message_headers_get_one(msg->request_headers, "Authorization");
    if (!auth_header) {
        /* No auth - return 401 with WWW-Authenticate */
        soup_message_set_status(msg, SOUP_STATUS_UNAUTHORIZED);
        soup_message_headers_append(msg->response_headers,
                                     "WWW-Authenticate",
                                     "Basic realm=\"TestRealm\"");
        soup_message_set_response(msg, "text/plain", SOUP_MEMORY_STATIC,
                                   "Unauthorized", 12);
    } else {
        /* Auth provided - echo back the auth type */
        soup_message_set_status(msg, SOUP_STATUS_OK);
        soup_message_set_response(msg, "text/plain", SOUP_MEMORY_COPY,
                                   auth_header, strlen(auth_header));
    }
}

static void
test_auth_header_preservation(SoupSession *session, const char *base_uri)
{
    SoupMessage *msg;
    gboolean authenticate_called = FALSE;
    char *uri;

    uri = g_strdup_printf("%s/protected", base_uri);

    /* Test 1: Send request with manually set Authorization header,
     * no cached credentials. The header should be preserved. */
    printf("TEST 1: Manual Authorization header without cached credentials\n");
    msg = soup_message_new("GET", uri);
    soup_message_headers_replace(msg->request_headers,
                                  "Authorization", "Basic dGVzdDp0ZXN0");

    /* Send synchronously */
    g_signal_connect(session, "authenticate",
                     G_CALLBACK(on_authenticate), &authenticate_called);

    soup_session_send_message(session, msg);

    printf("  Status: %u (%s)\n",
           msg->status_code, msg->reason_phrase);
    printf("  Authenticate callback called: %s\n",
           authenticate_called ? "YES" : "NO");

    /* The auth header should have been preserved (not stripped) */
    const char *sent_auth = soup_message_headers_get_one(
        msg->request_headers, "Authorization");

    if (sent_auth != NULL && strstr(sent_auth, "Basic dGVzdDp0ZXN0")) {
        printf("  PASS: Authorization header was preserved\n");
    } else {
        printf("  BREACH: Authorization header was %s\n",
               sent_auth ? "modified" : "removed/stripped");
    }

    g_object_unref(msg);
    g_free(uri);
    printf("\n");
}

int main(int argc, char **argv)
{
    SoupSession *session;
    SoupServer *server;
    char *base_uri;
    GMainLoop *loop;

    printf("=== PCA-0001 Test Harness: Authorization Header Preservation ===\n");
    printf("Target: libsoup/soup-auth-manager.c:446-454\n");
    printf("Bug: https://bugzilla.gnome.org/show_bug.cgi?id=775882\n\n");

    /* Start an in-process SoupServer for testing */
    server = soup_server_new(SOUP_SERVER_PORT, 0, NULL);
    g_signal_connect(server, "request-started",
                     G_CALLBACK(on_server_request), NULL);
    soup_server_listen_all(server, 0, SOUP_SERVER_LISTEN_IPV4_ONLY, NULL);

    GUri *srv_uri = soup_server_get_uris(server)->data;
    base_uri = g_uri_to_string(srv_uri);

    printf("Test server listening on: %s\n\n", base_uri);

    /* Create session */
    session = soup_test_session_new(SOUP_TYPE_SESSION, NULL);

    test_auth_header_preservation(session, base_uri);

    /* Cleanup */
    soup_test_session_abort_unref(session);
    g_object_unref(server);
    g_free(base_uri);

    printf("=== Test Complete ===\n");
    return 0;
}
