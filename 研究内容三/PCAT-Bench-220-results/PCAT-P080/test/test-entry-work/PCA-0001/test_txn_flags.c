#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "lmdb.h"

int main(int argc, char *argv[]) {
    int rc;
    MDB_env *env;
    MDB_txn *txn;
    unsigned int flags;
    int errors = 0;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <db_path>\n", argv[0]);
        return 1;
    }

    rc = mdb_env_create(&env);
    if (rc != 0) { fprintf(stderr, "mdb_env_create: %s\n", mdb_strerror(rc)); return 1; }

    rc = mdb_env_set_mapsize(env, 1048576);
    if (rc != 0) { fprintf(stderr, "mdb_env_set_mapsize: %s\n", mdb_strerror(rc)); return 1; }

    rc = mdb_env_open(env, argv[1], MDB_CREATE, 0644);
    if (rc != 0) { fprintf(stderr, "mdb_env_open(%s): %s\n", argv[1], mdb_strerror(rc)); return 1; }

    /* Test 1: Write transaction - flags should NOT have MDB_RDONLY */
    rc = mdb_txn_begin(env, NULL, 0, &txn);
    if (rc != 0) { fprintf(stderr, "mdb_txn_begin(write): %s\n", mdb_strerror(rc)); errors++; }
    else {
        rc = mdb_txn_flags(txn, &flags);
        if (rc != MDB_SUCCESS) { fprintf(stderr, "FAIL: mdb_txn_flags(write) returned %d\n", rc); errors++; }
        else if (flags & MDB_RDONLY) { fprintf(stderr, "FAIL: Write txn flags has MDB_RDONLY (flags=0x%x)\n", flags); errors++; }
        else { printf("PASS: Write txn flags=0x%x (no MDB_RDONLY)\n", flags); }
        mdb_txn_abort(txn);
    }

    /* Test 2: Read-only transaction - flags should have MDB_RDONLY */
    rc = mdb_txn_begin(env, NULL, MDB_RDONLY, &txn);
    if (rc != 0) { fprintf(stderr, "mdb_txn_begin(rdonly): %s\n", mdb_strerror(rc)); errors++; }
    else {
        rc = mdb_txn_flags(txn, &flags);
        if (rc != MDB_SUCCESS) { fprintf(stderr, "FAIL: mdb_txn_flags(rdonly) returned %d\n", rc); errors++; }
        else if (!(flags & MDB_RDONLY)) { fprintf(stderr, "FAIL: Rdonly txn missing MDB_RDONLY (flags=0x%x)\n", flags); errors++; }
        else { printf("PASS: Read-only txn flags=0x%x (MDB_RDONLY set)\n", flags); }
        mdb_txn_abort(txn);
    }

    /* Test 3: NULL txn - should return EINVAL */
    rc = mdb_txn_flags(NULL, &flags);
    if (rc == EINVAL) { printf("PASS: NULL txn returns EINVAL\n"); }
    else { fprintf(stderr, "FAIL: NULL txn returned %d (expected EINVAL=%d)\n", rc, EINVAL); errors++; }

    mdb_env_close(env);
    printf("\n%d error(s)\n", errors);
    return errors > 0 ? 1 : 0;
}
