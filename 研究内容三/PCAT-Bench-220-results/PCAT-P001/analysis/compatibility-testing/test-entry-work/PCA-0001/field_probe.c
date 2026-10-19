#include <stddef.h>
#include <stdio.h>

int main(void)
{
    printf("compat_reserved_offset=%zu\n",
           offsetof(struct input_event, compat_reserved));
    return 0;
}
