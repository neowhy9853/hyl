#include <stdio.h>
#include <libsoup/soup.h>

int main(void) {
    GObject *session;
    gboolean use_system_ca;
    GTlsDatabase *tlsdb;
    char *ca_file;
    const char *session_type_name;

    printf("=== Testing SoupSessionAsync (deprecated) ===\n");
    G_GNUC_BEGIN_IGNORE_DEPRECATIONS;
    session = G_OBJECT(soup_session_async_new());
    G_GNUC_END_IGNORE_DEPRECATIONS;

    g_object_get(session,
                 "ssl-use-system-ca-file", &use_system_ca,
                 "tls-database", &tlsdb,
                 "ssl-ca-file", &ca_file,
                 NULL);

    session_type_name = G_OBJECT_TYPE_NAME(session);
    printf("Session type: %s\n", session_type_name);
    printf("ssl-use-system-ca-file: %s\n", use_system_ca ? "TRUE" : "FALSE");
    printf("tls-database: %s\n", tlsdb != NULL ? "SET (non-NULL)" : "NULL");
    printf("ssl-ca-file: %s\n", ca_file ? ca_file : "NULL");

    if (tlsdb) g_object_unref(tlsdb);
    g_free(ca_file);
    g_object_unref(session);

    printf("\n=== Testing plain SoupSession ===\n");
    session = G_OBJECT(soup_session_new());

    g_object_get(session,
                 "ssl-use-system-ca-file", &use_system_ca,
                 "tls-database", &tlsdb,
                 "ssl-ca-file", &ca_file,
                 NULL);

    session_type_name = G_OBJECT_TYPE_NAME(session);
    printf("Session type: %s\n", session_type_name);
    printf("ssl-use-system-ca-file: %s\n", use_system_ca ? "TRUE" : "FALSE");
    printf("tls-database: %s\n", tlsdb != NULL ? "SET (non-NULL)" : "NULL");
    printf("ssl-ca-file: %s\n", ca_file ? ca_file : "NULL");

    if (tlsdb) g_object_unref(tlsdb);
    g_free(ca_file);
    g_object_unref(session);

    return 0;
}
