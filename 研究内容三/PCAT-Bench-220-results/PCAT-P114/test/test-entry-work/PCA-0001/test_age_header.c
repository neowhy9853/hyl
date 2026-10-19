#include "test-utils.h"
#include <stdlib.h>
#include <stdio.h>

static SoupCache *global_cache = NULL;

static void
age_test_server_callback (SoupServer *server, SoupMessage *msg,
                          const char *path, GHashTable *query,
                          SoupClientContext *context, gpointer data)
{
    const char *header;

    if (msg->method != SOUP_METHOD_GET) {
        soup_message_set_status (msg, SOUP_STATUS_NOT_IMPLEMENTED);
        return;
    }

    header = soup_message_headers_get_one (msg->request_headers, "Test-Set-Expires");
    if (header) {
        soup_message_headers_append (msg->response_headers, "Expires", header);
    }

    header = soup_message_headers_get_one (msg->request_headers,
                                           "If-Modified-Since");
    if (header) {
        const char *last_modified = soup_message_headers_get_one (
                msg->request_headers, "Test-Set-Last-Modified");
        if (last_modified) {
            SoupDate *date1, *date2;
            date1 = soup_date_new_from_string (last_modified);
            date2 = soup_date_new_from_string (header);
            if (date1 && date2 && soup_date_to_time_t (date1) <= soup_date_to_time_t (date2))
                soup_message_set_status (msg, SOUP_STATUS_NOT_MODIFIED);
            else
                soup_message_set_status (msg, SOUP_STATUS_OK);
            if (date1) soup_date_free (date1);
            if (date2) soup_date_free (date2);
        }
    }

    if (msg->status_code == SOUP_STATUS_OK || msg->status_code == 0) {
        soup_message_set_status (msg, SOUP_STATUS_OK);
        soup_message_set_response (msg, "text/plain", SOUP_MEMORY_COPY,
                                    "test-body", 10);
    }
}

static char *
do_age_test_request (SoupSession *session, SoupURI *base_uri,
                     const char *path, SoupMessageHeaders *response_headers)
{
    SoupRequestHTTP *req;
    SoupMessage *msg;
    GInputStream *stream;
    SoupURI *uri;
    char buf[256];
    gsize nread;
    GError *error = NULL;

    uri = soup_uri_new_with_base (base_uri, path);
    req = soup_session_request_http_uri (session, "GET", uri, NULL);
    soup_uri_free (uri);
    msg = soup_request_http_get_message (req);

    stream = soup_test_request_send (SOUP_REQUEST (req), NULL, 0, &error);
    if (!stream) {
        fprintf (stderr, "  request failed: %s\n", error ? error->message : "unknown");
        g_clear_error (&error);
        g_object_unref (req);
        g_object_unref (msg);
        return NULL;
    }

    if (response_headers) {
        soup_message_headers_foreach (msg->response_headers, copy_headers, response_headers);
    }

    g_object_unref (msg);
    g_input_stream_read_all (stream, buf, sizeof (buf) - 1, &nread, NULL, &error);
    g_clear_error (&error);
    soup_test_request_close_stream (SOUP_REQUEST (req), stream, NULL, &error);
    g_clear_error (&error);
    g_object_unref (stream);
    g_object_unref (req);

    soup_cache_flush (global_cache);
    return nread ? g_strndup (buf, nread) : g_strdup ("");
}

static void
copy_headers_cb (const char *name, const char *value, gpointer user_data)
{
    SoupMessageHeaders *headers = (SoupMessageHeaders *) user_data;
    soup_message_headers_append (headers, name, value);
}

int
main (int argc, char **argv)
{
    SoupServer *server;
    SoupURI *base_uri;
    SoupSession *session;
    SoupCache *cache;
    SoupMessageHeaders *headers;
    char *cache_dir;
    char *body;
    const char *age_header;
    int ret = 0;

    test_init (argc, argv, NULL);

    cache_dir = g_dir_make_tmp ("pca-age-test-XXXXXX", NULL);
    cache = soup_cache_new (cache_dir, SOUP_CACHE_SINGLE_USER);
    global_cache = cache;

    session = soup_test_session_new (SOUP_TYPE_SESSION_ASYNC,
                                      SOUP_SESSION_USE_THREAD_CONTEXT, TRUE,
                                      SOUP_SESSION_ADD_FEATURE, cache,
                                      NULL);

    server = soup_test_server_new (TRUE);
    soup_server_add_handler (server, NULL, age_test_server_callback, NULL, NULL);
    base_uri = soup_test_server_get_uri (server, "http", NULL);

    printf ("=== PCA Age Header Test ===\n");

    /* First request: populate cache */
    headers = soup_message_headers_new (SOUP_MESSAGE_HEADERS_RESPONSE);
    printf ("1. Initial request to populate cache...\n");
    body = do_age_test_request (session, base_uri, "/age-test", headers);
    g_free (body);
    soup_message_headers_free (headers);

    /* Second request: should hit cache */
    headers = soup_message_headers_new (SOUP_MESSAGE_HEADERS_RESPONSE);
    printf ("2. Second request (should be cached)...\n");
    body = do_age_test_request (session, base_uri, "/age-test", headers);
    g_free (body);

    /* Check for Age header */
    age_header = soup_message_headers_get_one (headers, "Age");
    if (age_header) {
        printf ("RESULT: Age header PRESENT: %s\n", age_header);
        printf ("BEHAVIOR: Age header is being added to cache responses.\n");
        ret = 1;
    } else {
        printf ("RESULT: Age header ABSENT\n");
        printf ("BEHAVIOR: No Age header in cache responses (patched behavior).\n");
        ret = 0;
    }

    soup_message_headers_foreach (headers, copy_headers_cb, NULL);
    soup_message_headers_free (headers);

    soup_test_session_abort_unref (session);
    g_object_unref (cache);
    g_free (cache_dir);

    soup_uri_free (base_uri);
    soup_test_server_quit_unref (server);

    test_cleanup ();

    if (ret == 0)
        printf ("\nPASS: Patch behavior confirmed - Age header NOT added to cache responses.\n");
    else
        printf ("\nFAIL: Age header IS present in cache responses.\n");

    return ret;
}
