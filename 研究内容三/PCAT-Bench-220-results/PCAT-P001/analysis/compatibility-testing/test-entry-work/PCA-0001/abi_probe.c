#include <stddef.h>
#include <stdio.h>

int main(void)
{
    struct input_event records[2];

    printf("%zu %zu %zu %zu %zu %zu\n",
           sizeof(struct input_event),
           _Alignof(struct input_event),
           offsetof(struct input_event, type),
           offsetof(struct input_event, code),
           offsetof(struct input_event, value),
           (size_t)((unsigned char *)&records[1] -
                    (unsigned char *)&records[0]));
    return 0;
}
