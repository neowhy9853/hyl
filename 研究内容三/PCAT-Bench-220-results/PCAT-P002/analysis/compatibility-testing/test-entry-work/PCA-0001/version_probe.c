#include <stdio.h>

/* reproducer.sh force-includes the selected tree's uinput.h. */

int main(void)
{
	printf("%d\n", UINPUT_VERSION);
	return 0;
}
