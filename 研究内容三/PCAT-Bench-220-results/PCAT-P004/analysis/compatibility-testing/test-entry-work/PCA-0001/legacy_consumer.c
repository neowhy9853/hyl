#include <stddef.h>

#include <linux/sysctl.h>

_Static_assert(CTL_MAXNAME >= 9,
	       "legacy consumer requires at least nine sysctl path components");

int main(void)
{
	int name[CTL_MAXNAME];

	return sizeof(name) / sizeof(name[0]) < 9;
}
