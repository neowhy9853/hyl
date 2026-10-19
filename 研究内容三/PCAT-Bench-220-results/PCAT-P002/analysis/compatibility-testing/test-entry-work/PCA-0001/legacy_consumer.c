/* reproducer.sh force-includes the selected tree's uinput.h. */

_Static_assert(UINPUT_VERSION == 5,
	       "downstream source expects uinput protocol version 5");

int main(void)
{
	return 0;
}
