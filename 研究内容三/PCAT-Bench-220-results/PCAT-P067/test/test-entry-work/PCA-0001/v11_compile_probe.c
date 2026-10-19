#include "net.h"

#if netCURR_IF_VERSION != 11
#error "unchanged v11 consumer cannot use this net interface version"
#endif

int main(void)
{
    return 0;
}
