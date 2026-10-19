/* Exact copy of ib_umem_check_rereg() from patched umem.c:334-343.
 * This is the actual patched code under test.
 */
#include <errno.h>

int ib_umem_check_rereg(struct ib_umem *umem, int flags, int new_access_flags)
{
	if (!umem)
		return 0;

	if ((flags & IB_MR_REREG_ACCESS) && !(flags & IB_MR_REREG_TRANS))
		if (ib_access_writable(new_access_flags) && !umem->writable)
			return -EACCES;
	return 0;
}
