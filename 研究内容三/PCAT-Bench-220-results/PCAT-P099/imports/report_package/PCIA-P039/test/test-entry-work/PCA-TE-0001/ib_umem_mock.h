/* Mock header for standalone testing of ib_umem_check_rereg() */
#ifndef _IB_UMEM_MOCK_H
#define _IB_UMEM_MOCK_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Mirrors include/rdma/ib_verbs.h definitions */
#define IB_ACCESS_LOCAL_WRITE    (1 << 0)
#define IB_ACCESS_REMOTE_WRITE   (1 << 1)
#define IB_ACCESS_REMOTE_READ    (1 << 2)
#define IB_ACCESS_REMOTE_ATOMIC  (1 << 3)
#define IB_ACCESS_MW_BIND        (1 << 4)

#define IB_MR_REREG_TRANS        (1 << 0)
#define IB_MR_REREG_PD           (1 << 1)
#define IB_MR_REREG_ACCESS       (1 << 2)

/* Mirrors include/rdma/ib_umem.h struct ib_umem (relevant fields) */
struct sg_append_table {
    /* stub - not needed for ib_umem_check_rereg */
    void *dummy;
};

struct ib_umem {
    void *ibdev;
    void *owning_mm;
    uint64_t iova;
    size_t length;
    unsigned long address;
    unsigned int writable : 1;
    unsigned int is_odp : 1;
    unsigned int is_dmabuf : 1;
    struct sg_append_table sgt_append;
};

static inline bool ib_access_writable(int access_flags)
{
    return access_flags &
        (IB_ACCESS_LOCAL_WRITE | IB_ACCESS_REMOTE_WRITE |
         IB_ACCESS_REMOTE_ATOMIC | IB_ACCESS_MW_BIND);
}

#endif /* _IB_UMEM_MOCK_H */
