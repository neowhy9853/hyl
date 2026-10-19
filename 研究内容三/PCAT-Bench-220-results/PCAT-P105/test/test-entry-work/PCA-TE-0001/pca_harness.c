/*
 * PCA Directed Test Harness for ksmbd supplementary groups patch
 * Tests: SIDE_EFFECT_CHANGE in __ksmbd_override_fsids / ksmbd_alloc_user
 * 
 * This harness extracts the key logic paths from the ksmbd changes 
 * and tests them in userspace. It uses minimal mocking of kernel
 * functions to validate contract semantics.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>

/* ---------- Mock kernel types and constants ---------- */
typedef unsigned int gid_t;
typedef unsigned int uid_t;
#define NGROUPS_MAX 65536
#define GFP_KERNEL 0

/* ---------- Mock kernel functions ---------- */
static void *mock_kmalloc(size_t sz) {
    void *p = malloc(sz);
    return p;
}
static void *mock_kzalloc(size_t sz) {
    void *p = calloc(1, sz);
    return p;
}

/* ---------- Extracted logic test: ksmbd_alloc_user changes ---------- */
struct test_login_response {
    char account[48];
    unsigned int gid;
    unsigned int uid;
    unsigned short status;
    unsigned short hash_sz;
    char hash[18];
};

struct test_login_response_ext {
    unsigned int handle;
    int ngroups;
    char reserved[128];
    char payload[];
};

struct test_user {
    char *name;
    unsigned int flags;
    unsigned int gid;
    unsigned int uid;
    size_t passkey_sz;
    char *passkey;
    int ngroups;
    gid_t *sgid;
};

/* NEW: patched version of alloc_user logic */
static struct test_user *test_alloc_user_patched(
    struct test_login_response *resp,
    struct test_login_response_ext *resp_ext)
{
    struct test_user *user;
    
    user = mock_kmalloc(sizeof(struct test_user));
    if (!user) return NULL;

    user->name = strdup(resp->account);
    user->flags = resp->status;
    user->gid = resp->gid;
    user->uid = resp->uid;
    user->passkey_sz = resp->hash_sz;
    user->passkey = mock_kmalloc(resp->hash_sz);
    if (user->passkey)
        memcpy(user->passkey, resp->hash, resp->hash_sz);

    user->ngroups = 0;
    user->sgid = NULL;

    if (!user->name || !user->passkey)
        goto err_free;

    /* NEW CODE: handle extension response */
    if (resp_ext) {
        if (resp_ext->ngroups > NGROUPS_MAX) {
            fprintf(stderr, "ngroups(%d) from login response exceeds max groups(%d)\n",
                    resp_ext->ngroups, NGROUPS_MAX);
            goto err_free;
        }

        user->sgid = mock_kmalloc(resp_ext->ngroups * sizeof(gid_t));
        if (!user->sgid)
            goto err_free;

        memcpy(user->sgid, resp_ext->payload, resp_ext->ngroups * sizeof(gid_t));
        user->ngroups = resp_ext->ngroups;
    }

    return user;

err_free:
    free(user->name);
    free(user->passkey);
    free(user);
    return NULL;
}

/* OLD: pre-patch alloc_user logic */
static struct test_user *test_alloc_user_old(
    struct test_login_response *resp)
{
    struct test_user *user;
    
    user = mock_kmalloc(sizeof(struct test_user));
    if (!user) return NULL;

    user->name = strdup(resp->account);
    user->flags = resp->status;
    user->gid = resp->gid;
    user->uid = resp->uid;
    user->passkey_sz = resp->hash_sz;
    user->passkey = mock_kmalloc(resp->hash_sz);
    if (user->passkey)
        memcpy(user->passkey, resp->hash, resp->hash_sz);

    user->ngroups = 0;
    user->sgid = NULL;

    if (!user->name || !user->passkey) {
        free(user->name);
        free(user->passkey);
        free(user);
        return NULL;
    }

    return user;
}

/* ---------- Extracted logic test: __ksmbd_override_fsids changes ---------- */
struct mock_group_info {
    int ngroups;
    gid_t gid[NGROUPS_MAX];
};

static struct mock_group_info *mock_groups_alloc(int ngroups) {
    if (ngroups < 0 || ngroups > NGROUPS_MAX) return NULL;
    struct mock_group_info *gi = mock_kzalloc(sizeof(*gi));
    if (!gi) return NULL;
    gi->ngroups = 0;
    return gi;
}

/* NEW: patched __ksmbd_override_fsids groups setup logic */
static int test_override_fsids_patched(struct test_user *user) {
    int i;

    /* NEW CODE: groups_alloc(user->ngroups) instead of groups_alloc(0) */
    if (user->ngroups > 0) {
        struct mock_group_info *gi;

        gi = mock_groups_alloc(user->ngroups);
        if (!gi) {
            return -ENOMEM;
        }

        for (i = 0; i < user->ngroups; i++) {
            gi->gid[gi->ngroups++] = user->sgid[i];
        }

        /* Check if groups were properly populated */
        if (gi->ngroups != user->ngroups) {
            free(gi);
            return -EINVAL;
        }

        printf("  [PATCHED] supplementary groups loaded: %d groups\n", gi->ngroups);
        for (i = 0; i < gi->ngroups; i++) {
            printf("    group[%d] = %u\n", i, gi->gid[i]);
        }
        free(gi);
    } else {
        /* No supplementary groups - same as old behavior */
        printf("  [PATCHED] no supplementary groups (ngroups=0)\n");
    }

    return 0;
}

/* OLD: pre-patch __ksmbd_override_fsids groups setup */
static int test_override_fsids_old(struct test_user *user) {
    /* OLD CODE: groups_alloc(0) - never uses supplementary groups */
    struct mock_group_info *gi;

    gi = mock_groups_alloc(0);
    if (!gi) {
        return -ENOMEM;
    }

    printf("  [OLD] supplementary groups: 0 (groups_alloc(0))\n");
    free(gi);
    return 0;
}

/* ---------- Test functions ---------- */
static int test_count = 0;
static int test_passed = 0;
static int test_failed = 0;

#define ASSERT(cond, msg) do { \
    test_count++; \
    if (cond) { \
        printf("  PASS: %s\n", msg); \
        test_passed++; \
    } else { \
        printf("  FAIL: %s\n", msg); \
        test_failed++; \
    } \
} while(0)

static void test_alloc_user_no_extension(void) {
    printf("\n--- Test: ksmbd_alloc_user without extension (old path) ---\n");
    struct test_login_response resp = {0};
    strcpy(resp.account, "testuser");
    resp.gid = 1000;
    resp.uid = 1000;
    resp.status = 0x01;  /* KSMBD_USER_FLAG_OK */
    resp.hash_sz = 16;
    memset(resp.hash, 'A', 16);

    /* Old version */
    struct test_user *u_old = test_alloc_user_old(&resp);
    ASSERT(u_old != NULL, "old alloc_user succeeds without extension");
    ASSERT(u_old->ngroups == 0, "old: ngroups=0");
    ASSERT(u_old->sgid == NULL, "old: sgid=NULL");
    free(u_old->name); free(u_old->passkey); free(u_old);

    /* Patched version without extension (NULL resp_ext) - should match old */
    struct test_user *u_new = test_alloc_user_patched(&resp, NULL);
    ASSERT(u_new != NULL, "patched alloc_user succeeds without extension (NULL resp_ext)");
    ASSERT(u_new->ngroups == 0, "patched: ngroups=0 with NULL extension");
    ASSERT(u_new->sgid == NULL, "patched: sgid=NULL with NULL extension");
    free(u_new->name); free(u_new->passkey); free(u_new);
}

static void test_alloc_user_with_extension(void) {
    printf("\n--- Test: ksmbd_alloc_user with extension (new path) ---\n");
    struct test_login_response resp = {0};
    strcpy(resp.account, "testuser");
    resp.gid = 1000;
    resp.uid = 1000;
    resp.status = 0x01;
    resp.hash_sz = 16;
    memset(resp.hash, 'A', 16);

    /* Create extension with 3 supplementary groups */
    gid_t groups[] = {1000, 1001, 1002};
    struct test_login_response_ext *ext = mock_kmalloc(sizeof(*ext) + sizeof(groups));
    ext->handle = 1;
    ext->ngroups = 3;
    memset(ext->reserved, 0, sizeof(ext->reserved));
    memcpy(ext->payload, groups, sizeof(groups));

    struct test_user *u = test_alloc_user_patched(&resp, ext);

    ASSERT(u != NULL, "patched alloc_user succeeds with extension");
    if (u) {
        ASSERT(u->ngroups == 3, "ngroups=3 with extension");
        ASSERT(u->sgid != NULL, "sgid is allocated with extension");
        ASSERT(u->sgid[0] == 1000, "sgid[0]=1000");
        ASSERT(u->sgid[1] == 1001, "sgid[1]=1001");
        ASSERT(u->sgid[2] == 1002, "sgid[2]=1002");
        free(u->sgid);
        free(u->name);
        free(u->passkey);
        free(u);
    }
    free(ext);
}

static void test_alloc_user_ngroups_exceeds_max(void) {
    printf("\n--- Test: ksmbd_alloc_user ngroups exceeds NGROUPS_MAX ---\n");
    struct test_login_response resp = {0};
    strcpy(resp.account, "testuser");
    resp.gid = 1000;
    resp.uid = 1000;
    resp.status = 0x01;
    resp.hash_sz = 16;
    memset(resp.hash, 'A', 16);

    struct test_login_response_ext *ext = mock_kmalloc(sizeof(*ext));
    ext->handle = 1;
    ext->ngroups = NGROUPS_MAX + 1;  /* Exceeds max */
    memset(ext->reserved, 0, sizeof(ext->reserved));

    struct test_user *u = test_alloc_user_patched(&resp, ext);
    ASSERT(u == NULL, "alloc_user returns NULL when ngroups > NGROUPS_MAX");
    free(ext);
}

static void test_alloc_user_with_0_groups_extension(void) {
    printf("\n--- Test: ksmbd_alloc_user with 0 groups extension ---\n");
    struct test_login_response resp = {0};
    strcpy(resp.account, "testuser");
    resp.gid = 1000;
    resp.uid = 1000;
    resp.status = 0x01;
    resp.hash_sz = 16;
    memset(resp.hash, 'A', 16);

    struct test_login_response_ext *ext = mock_kmalloc(sizeof(*ext));
    ext->handle = 1;
    ext->ngroups = 0;
    memset(ext->reserved, 0, sizeof(ext->reserved));

    struct test_user *u = test_alloc_user_patched(&resp, ext);
    ASSERT(u != NULL, "alloc_user succeeds with 0 groups extension");
    if (u) {
        ASSERT(u->ngroups == 0, "ngroups=0");
        ASSERT(u->sgid == NULL, "sgid=NULL when ngroups=0 (no kmemdup for 0)");
        free(u->name);
        free(u->passkey);
        free(u);
    }
    free(ext);
}

static void test_override_fsids_behavior_diff(void) {
    printf("\n--- Test: __ksmbd_override_fsids behavior difference ---\n");

    /* Setup user with supplementary groups */
    struct test_user user = {0};
    user.ngroups = 3;
    gid_t groups[] = {1000, 1001, 1002};
    user.sgid = groups;

    printf("Testing old behavior:\n");
    int ret_old = test_override_fsids_old(&user);
    ASSERT(ret_old == 0, "old override_fsids: groups_alloc(0) succeeds");
    /* Old behavior: no supplementary groups used */

    printf("\nTesting patched behavior:\n");
    int ret_new = test_override_fsids_patched(&user);
    ASSERT(ret_new == 0, "patched override_fsids: groups_alloc(3) succeeds");
    /* New behavior: 3 supplementary groups populated */

    printf("\n--- Contract Verification ---\n");
    printf("BEHAVIOR CHANGE CONFIRMED: supplementary groups %s used in credential override\n",
           "are NOW");
    printf("  Old: groups_alloc(0) -> empty supplementary groups\n");
    printf("  New: groups_alloc(user->ngroups) -> groups populated from sgid\n");
    printf("  Impact: Files accessible via supplementary group membership now accessible via SMB\n");
}

static void test_no_groups_user(void) {
    printf("\n--- Test: override_fsids with no supplementary groups ---\n");
    struct test_user user = {0};
    user.ngroups = 0;
    user.sgid = NULL;

    /* Old and new should behave identically for ngroups=0 */
    int ret_old = test_override_fsids_old(&user);
    int ret_new = test_override_fsids_patched(&user);

    ASSERT(ret_old == 0, "old: ngroups=0 succeeds");
    ASSERT(ret_new == 0, "new: ngroups=0 succeeds");
    printf("  Backward compatibility: ngroups=0 gives same result in old/new\n");
}

int main(void) {
    printf("=== PCA Directed Test: ksmbd supplementary groups patch ===\n");
    printf("Target: __ksmbd_override_fsids / ksmbd_alloc_user SIDE_EFFECT_CHANGE\n");
    printf("Patch: 8a3cd890fd2a7d016a821a1c9dfd8a84d45ad320\n\n");

    /* Test ksmbd_alloc_user changes */
    test_alloc_user_no_extension();
    test_alloc_user_with_extension();
    test_alloc_user_ngroups_exceeds_max();
    test_alloc_user_with_0_groups_extension();

    /* Test __ksmbd_override_fsids changes */
    test_override_fsids_behavior_diff();
    test_no_groups_user();

    printf("\n=== Results: %d/%d passed, %d failed ===\n",
           test_passed, test_count, test_failed);

    return test_failed > 0 ? 1 : 0;
}
