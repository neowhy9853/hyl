#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <linux/sysctl.h>

static int accepts_nlen(long nlen)
{
	return nlen >= 0 && nlen <= CTL_MAXNAME;
}

static int parse_nlen(const char *text, long *value)
{
	char *end = NULL;
	long parsed;

	errno = 0;
	parsed = strtol(text, &end, 10);
	if (errno != 0 || end == text || *end != '\0')
		return -1;
	*value = parsed;
	return 0;
}

int main(int argc, char **argv)
{
	int name[CTL_MAXNAME];
	long nlen;

	if (argc == 1 || (argc == 2 && strcmp(argv[1], "--describe") == 0)) {
		printf("CTL_MAXNAME=%d array_count=%zu array_bytes=%zu\n",
		       CTL_MAXNAME, sizeof(name) / sizeof(name[0]), sizeof(name));
		printf("accept[-1]=%d accept[0]=%d accept[8]=%d "
		       "accept[9]=%d accept[10]=%d accept[11]=%d\n",
		       accepts_nlen(-1), accepts_nlen(0), accepts_nlen(8),
		       accepts_nlen(9), accepts_nlen(10), accepts_nlen(11));
		return 0;
	}

	if (argc != 3 || strcmp(argv[1], "--nlen") != 0 ||
	    parse_nlen(argv[2], &nlen) != 0) {
		fprintf(stderr, "usage: %s [--describe | --nlen INTEGER]\n", argv[0]);
		return 2;
	}

	printf("nlen=%ld accepted=%d CTL_MAXNAME=%d\n",
	       nlen, accepts_nlen(nlen), CTL_MAXNAME);
	return accepts_nlen(nlen) ? 0 : 1;
}
