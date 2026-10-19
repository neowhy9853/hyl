#include <stddef.h>
#include <stdio.h>
#include "tcpsrv.h"

int main(void)
{
    printf("sizeof(tcpLstnParams_t)=%zu\n", sizeof(tcpLstnParams_t));
    return 0;
}
