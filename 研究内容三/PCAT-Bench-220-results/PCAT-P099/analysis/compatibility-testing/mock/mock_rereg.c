/*
 * PCAT-P099 standalone compatibility harness.
 *
 * The PATCHED implementation of ib_umem_check_rereg() is copied from
 * drivers/infiniband/core/umem.c:334-343 at patched commit
 * 09dc18894148381d3bfc550083b1236043870dce.  The CONFIG_USER_MEM=n return
 * is copied from include/rdma/ib_umem.h:208-212.  Driver wrappers model only
 * the ordering around the newly added call sites; hardware APIs are controlled
 * mocks whose invocation sequence is recorded in struct state.effects.
 */

#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef PATCHED
#define PATCHED 1
#endif

#ifndef CONFIG_USER_MEM
#define CONFIG_USER_MEM 1
#endif

enum {
	IB_MR_REREG_TRANS = 1,
	IB_MR_REREG_PD = 1 << 1,
	IB_MR_REREG_ACCESS = 1 << 2,
	IB_MR_REREG_SUPPORTED = (IB_MR_REREG_ACCESS << 1) - 1,
};

enum {
	IB_ACCESS_LOCAL_WRITE = 1 << 0,
	IB_ACCESS_REMOTE_WRITE = 1 << 1,
	IB_ACCESS_REMOTE_ATOMIC = 1 << 2,
	IB_ACCESS_MW_BIND = 1 << 3,
};

#define RXE_MR_REREG_SUPPORTED (IB_MR_REREG_PD | IB_MR_REREG_ACCESS)
#define INVALID_REREG_FLAG (1 << 8)

struct ib_umem {
	bool writable;
};

struct state {
	int mailbox_alloc;
	int hw_dereg;
	int mpt_get;
	int umr;
	int pd_put;
	int pd_get;
	int mr_access_writes;
	int mr_pd_writes;
	int trans_updates;
	int access;
	int pd;
	char effects[256];
};

static int failures;

static bool ib_access_writable(int access_flags)
{
	return access_flags &
	       (IB_ACCESS_LOCAL_WRITE | IB_ACCESS_REMOTE_WRITE |
		IB_ACCESS_REMOTE_ATOMIC | IB_ACCESS_MW_BIND);
}

#if PATCHED
static int ib_umem_check_rereg(struct ib_umem *umem, int flags,
			       int new_access_flags)
{
#if CONFIG_USER_MEM
	if (!umem)
		return 0;

	if ((flags & IB_MR_REREG_ACCESS) && !(flags & IB_MR_REREG_TRANS))
		if (ib_access_writable(new_access_flags) && !umem->writable)
			return -EACCES;
	return 0;
#else
	/* Harness-only warning suppression; the kernel inline stub omits these. */
	(void)umem;
	(void)flags;
	(void)new_access_flags;
	return -EOPNOTSUPP;
#endif
}
#else
/* The helper did not exist before the patch; wrappers do not call this shim. */
static int ib_umem_check_rereg(struct ib_umem *umem, int flags,
			       int new_access_flags)
{
	(void)umem;
	(void)flags;
	(void)new_access_flags;
	return 0;
}
#endif

static void effect(struct state *s, const char *name)
{
	if (s->effects[0])
		strcat(s->effects, ",");
	strcat(s->effects, name);
}

static int patch_guard(struct ib_umem *umem, int flags, int access)
{
#if PATCHED
	return ib_umem_check_rereg(umem, flags, access);
#else
	(void)umem;
	(void)flags;
	(void)access;
	return 0;
#endif
}

static int hns_wrapper(struct ib_umem *umem, int flags, int access,
		       struct state *s)
{
	int ret = patch_guard(umem, flags, access);
	if (ret)
		return ret;
	s->mailbox_alloc++;
	effect(s, "mailbox_alloc");
	s->hw_dereg++;
	effect(s, "hw_dereg");
	if (flags & IB_MR_REREG_PD) {
		s->mr_pd_writes++;
		s->pd = 2;
		effect(s, "mr_pd");
	}
	if (flags & IB_MR_REREG_ACCESS) {
		s->mr_access_writes++;
		s->access = access;
		effect(s, "mr_access");
	}
	if (flags & IB_MR_REREG_TRANS) {
		s->trans_updates++;
		effect(s, "trans");
	}
	return 0;
}

static int irdma_wrapper(struct ib_umem *umem, int flags, int access,
			 struct state *s)
{
	int ret;

	if (flags & ~IB_MR_REREG_SUPPORTED)
		return -EOPNOTSUPP;
	ret = patch_guard(umem, flags, access);
	if (ret)
		return ret;
	s->hw_dereg++;
	effect(s, "hw_dereg");
	if (flags & IB_MR_REREG_ACCESS) {
		s->mr_access_writes++;
		s->access = access;
		effect(s, "mr_access");
	}
	if (flags & IB_MR_REREG_PD) {
		s->mr_pd_writes++;
		s->pd = 2;
		effect(s, "mr_pd");
	}
	if (flags & IB_MR_REREG_TRANS) {
		s->trans_updates++;
		effect(s, "trans");
	}
	return 0;
}

static int mlx4_wrapper(struct ib_umem *umem, int flags, int access,
			struct state *s)
{
	int ret = patch_guard(umem, flags, access);
	if (ret)
		return ret;
	s->mpt_get++;
	effect(s, "mpt_get");
	if (flags & IB_MR_REREG_PD) {
		s->mr_pd_writes++;
		s->pd = 2;
		effect(s, "mr_pd");
	}
	/* Retained mlx4 check: ACCESS|TRANS is still rejected after MPT get. */
	if ((flags & IB_MR_REREG_ACCESS) && ib_access_writable(access) &&
	    umem && !umem->writable)
		return -EPERM;
	if (flags & IB_MR_REREG_ACCESS) {
		s->mr_access_writes++;
		s->access = access;
		effect(s, "mr_access");
	}
	if (flags & IB_MR_REREG_TRANS) {
		s->trans_updates++;
		effect(s, "trans");
	}
	return 0;
}

static int mlx5_wrapper(struct ib_umem *umem, int flags, int access,
			struct state *s)
{
	int ret;

#if !CONFIG_USER_MEM
	return -EOPNOTSUPP;
#endif
	if (flags & ~IB_MR_REREG_SUPPORTED)
		return -EOPNOTSUPP;
	ret = patch_guard(umem, flags, access);
	if (ret)
		return ret;
	s->umr++;
	effect(s, "umr");
	if (flags & IB_MR_REREG_PD) {
		s->mr_pd_writes++;
		s->pd = 2;
		effect(s, "mr_pd");
	}
	if (flags & IB_MR_REREG_ACCESS) {
		s->mr_access_writes++;
		s->access = access;
		effect(s, "mr_access");
	}
	if (flags & IB_MR_REREG_TRANS) {
		s->trans_updates++;
		effect(s, "trans");
	}
	return 0;
}

static int rxe_wrapper(struct ib_umem *umem, int flags, int access,
		       struct state *s)
{
	int ret;

	if (flags & ~RXE_MR_REREG_SUPPORTED)
		return -EOPNOTSUPP;
	ret = patch_guard(umem, flags, access);
	if (ret)
		return ret;
	if (flags & IB_MR_REREG_PD) {
		s->pd_put++;
		effect(s, "pd_put");
		s->pd_get++;
		effect(s, "pd_get");
		s->mr_pd_writes++;
		s->pd = 2;
		effect(s, "mr_pd");
	}
	if (flags & IB_MR_REREG_ACCESS) {
		s->mr_access_writes++;
		s->access = access;
		effect(s, "mr_access");
	}
	return 0;
}

struct driver {
	const char *name;
	int (*run)(struct ib_umem *, int, int, struct state *);
};

static const struct driver drivers[] = {
	{ "hns", hns_wrapper },
	{ "irdma", irdma_wrapper },
	{ "mlx4", mlx4_wrapper },
	{ "mlx5", mlx5_wrapper },
	{ "rxe", rxe_wrapper },
};

static int uverbs_dispatch(const struct driver *d, struct ib_umem *umem,
			   int flags, int access, struct state *s)
{
	if (!flags)
		return -EINVAL;
	if (flags & ~IB_MR_REREG_SUPPORTED)
		return -EOPNOTSUPP;
	return d->run(umem, flags, access, s);
}

static void expect_int(const char *label, int got, int want)
{
	if (got != want) {
		fprintf(stderr, "ASSERT label=%s got=%d want=%d\n", label, got,
			want);
		failures++;
	}
}

static void expect_empty_effects(const char *label, const struct state *s)
{
	if (s->effects[0]) {
		fprintf(stderr, "ASSERT label=%s unexpected_effects=%s\n", label,
			s->effects);
		failures++;
	}
}

static void print_result(const char *driver, const char *case_name, int ret,
			 const struct state *s)
{
	printf("{\"version\":\"%s\",\"config_user_mem\":%d,"
	       "\"driver\":\"%s\",\"case\":\"%s\",\"ret\":%d,"
	       "\"errno\":%d,\"access\":%d,\"pd\":%d,"
	       "\"effects\":\"%s\",\"mailbox\":%d,\"hw_dereg\":%d,"
	       "\"mpt_get\":%d,\"umr\":%d,\"pd_put\":%d,\"pd_get\":%d}\n",
	       PATCHED ? "after" : "before", CONFIG_USER_MEM, driver,
	       case_name, ret, ret < 0 ? -ret : 0, s->access, s->pd, s->effects,
	       s->mailbox_alloc, s->hw_dereg, s->mpt_get, s->umr, s->pd_put,
	       s->pd_get);
}

static void helper_case(const char *name, struct ib_umem *umem, int flags,
			int access, int expected)
{
	int ret = ib_umem_check_rereg(umem, flags, access);
	printf("{\"version\":\"%s\",\"config_user_mem\":%d,"
	       "\"helper_case\":\"%s\",\"ret\":%d}\n",
	       PATCHED ? "after" : "before", CONFIG_USER_MEM, name, ret);
	expect_int(name, ret, expected);
}

static void run_helper_matrix(void)
{
	struct ib_umem ro = { .writable = false };
	struct ib_umem rw = { .writable = true };
#if CONFIG_USER_MEM
	int deny = PATCHED ? -EACCES : 0;
	helper_case("umem_null", NULL, IB_MR_REREG_ACCESS,
		    IB_ACCESS_LOCAL_WRITE, 0);
	helper_case("ro_new_readonly", &ro, IB_MR_REREG_ACCESS, 0, 0);
	helper_case("ro_new_local_write", &ro, IB_MR_REREG_ACCESS,
		    IB_ACCESS_LOCAL_WRITE, deny);
	helper_case("ro_new_remote_write", &ro, IB_MR_REREG_ACCESS,
		    IB_ACCESS_REMOTE_WRITE, deny);
	helper_case("ro_new_remote_atomic", &ro, IB_MR_REREG_ACCESS,
		    IB_ACCESS_REMOTE_ATOMIC, deny);
	helper_case("ro_no_rereg_access", &ro, IB_MR_REREG_PD,
		    IB_ACCESS_LOCAL_WRITE, 0);
	helper_case("ro_access_trans", &ro,
		    IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS,
		    IB_ACCESS_LOCAL_WRITE, 0);
	helper_case("rw_new_local_write", &rw, IB_MR_REREG_ACCESS,
		    IB_ACCESS_LOCAL_WRITE, 0);
#else
	helper_case("stub_null", NULL, IB_MR_REREG_ACCESS,
		    IB_ACCESS_LOCAL_WRITE, -EOPNOTSUPP);
	helper_case("stub_ro", &ro, IB_MR_REREG_ACCESS, 0, -EOPNOTSUPP);
	helper_case("stub_rw", &rw, IB_MR_REREG_ACCESS,
		    IB_ACCESS_LOCAL_WRITE, -EOPNOTSUPP);
#endif
}

static void driver_case(const struct driver *d, const char *name,
			struct ib_umem *umem, int flags, int access,
			int expected_ret, bool expect_no_effect)
{
	struct state s = { .access = -1, .pd = 1 };
	int ret = uverbs_dispatch(d, umem, flags, access, &s);
	char label[128];

	snprintf(label, sizeof(label), "%s/%s", d->name, name);
	print_result(d->name, name, ret, &s);
	expect_int(label, ret, expected_ret);
	if (expect_no_effect)
		expect_empty_effects(label, &s);
}

static void run_driver_matrix(void)
{
	struct ib_umem ro = { .writable = false };
	struct ib_umem rw = { .writable = true };
	size_t i;

	for (i = 0; i < sizeof(drivers) / sizeof(drivers[0]); i++) {
		const struct driver *d = &drivers[i];
		int ro_to_rw;

#if !CONFIG_USER_MEM
		ro_to_rw = -EOPNOTSUPP;
#elif PATCHED
		ro_to_rw = -EACCES;
#else
		ro_to_rw = strcmp(d->name, "mlx4") == 0 ? -EPERM : 0;
#endif
		driver_case(d, "ro_to_local_write", &ro, IB_MR_REREG_ACCESS,
			    IB_ACCESS_LOCAL_WRITE, ro_to_rw, PATCHED);
		driver_case(d, "keep_readonly", &ro, IB_MR_REREG_ACCESS, 0, 0,
			    false);
		driver_case(d, "original_writable", &rw, IB_MR_REREG_ACCESS,
			    IB_ACCESS_LOCAL_WRITE, 0, false);
		driver_case(d, "pd_only_no_access", &ro, IB_MR_REREG_PD,
			    IB_ACCESS_LOCAL_WRITE, 0, false);
		driver_case(d, "pd_access_readonly", &ro,
			    IB_MR_REREG_PD | IB_MR_REREG_ACCESS, 0, 0, false);
		driver_case(d, "invalid_flag", &ro, INVALID_REREG_FLAG, 0,
			    -EOPNOTSUPP, true);
		driver_case(d, "zero_flags", &ro, 0, 0, -EINVAL, true);

		if (strcmp(d->name, "rxe") == 0)
			driver_case(d, "access_trans", &ro,
				    IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS,
				    IB_ACCESS_LOCAL_WRITE, -EOPNOTSUPP, true);
		else if (strcmp(d->name, "mlx4") == 0)
			driver_case(d, "access_trans", &ro,
				    IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS,
				    IB_ACCESS_LOCAL_WRITE, -EPERM, false);
		else
			driver_case(d, "access_trans", &ro,
				    IB_MR_REREG_ACCESS | IB_MR_REREG_TRANS,
				    IB_ACCESS_LOCAL_WRITE, 0, false);
	}
}

int main(int argc, char **argv)
{
	bool helper = true;
	bool drivers_mode = true;

	if (argc == 2) {
		helper = strcmp(argv[1], "--drivers") != 0;
		drivers_mode = strcmp(argv[1], "--helper") != 0;
	}
	if (helper)
		run_helper_matrix();
	if (drivers_mode)
		run_driver_matrix();
	printf("PCAT_P099_MOCK_DONE failures=%d version=%s config_user_mem=%d\n",
	       failures, PATCHED ? "after" : "before", CONFIG_USER_MEM);
	return failures ? EXIT_FAILURE : EXIT_SUCCESS;
}
