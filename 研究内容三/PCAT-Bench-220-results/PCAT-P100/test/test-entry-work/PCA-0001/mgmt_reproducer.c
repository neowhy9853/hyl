/*
 * PCA-0001: Bluetooth MGMT INPUT_CONTRACT_CHANGE reproducer
 *
 * Tests the MGMT_OP_ADD_EXT_ADV_DATA input length validation change:
 *   Before patch: expected_len != data_len  -> MGMT_STATUS_INVALID_PARAMS
 *   After patch:  expected_len >  data_len  -> MGMT_STATUS_INVALID_PARAMS
 *
 * The patch relaxes the check so extra trailing bytes (data_len > expected_len)
 * are accepted instead of rejected — restoring backward compatibility with
 * bluetoothd versions that send extra bytes.
 *
 * Build:
 *   gcc -O0 -g -Wall -o mgmt_reproducer mgmt_reproducer.c
 *
 * Prerequisites:
 *   - Kernel with CONFIG_BT=y, CONFIG_BT_MGMT=y
 *   - A Bluetooth HCI device (or hci_vhci for virtual testing)
 *   - CAP_NET_ADMIN (root) to open HCI_CHANNEL_CONTROL socket
 *
 * Run:
 *   sudo ./mgmt_reproducer
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <sys/select.h>
#include <sys/time.h>

/* Bluetooth HCI socket constants (from <bluetooth/bluetooth.h>, <bluetooth/mgmt.h>) */
#ifndef AF_BLUETOOTH
#define AF_BLUETOOTH 31
#endif

#ifndef BTPROTO_HCI
#define BTPROTO_HCI 1
#endif

#ifndef HCI_CHANNEL_CONTROL
#define HCI_CHANNEL_CONTROL 3
#endif

#ifndef HCI_DEV_NONE
#define HCI_DEV_NONE 0xffff
#endif

/* MGMT command constants (from include/net/bluetooth/mgmt.h) */
#define MGMT_INDEX_NONE          0xFFFF
#define MGMT_HDR_SIZE            6

#define MGMT_OP_ADD_EXT_ADV_DATA 0x0055
#define MGMT_ADD_EXT_ADV_DATA_SIZE 3
#define MGMT_STATUS_SUCCESS      0x00
#define MGMT_STATUS_INVALID_PARAMS 0x0d

struct mgmt_hdr {
    uint16_t opcode;
    uint16_t index;
    uint16_t len;
} __attribute__((packed));

struct mgmt_cp_add_ext_adv_data {
    uint8_t instance;
    uint8_t adv_data_len;
    uint8_t scan_rsp_len;
    uint8_t data[];
} __attribute__((packed));

struct mgmt_ev_cmd_complete {
    uint16_t opcode;
    uint8_t  status;
    uint8_t  data[];
} __attribute__((packed));

struct mgmt_ev_cmd_status {
    uint16_t opcode;
    uint8_t  status;
} __attribute__((packed));

#define MGMT_EV_CMD_COMPLETE 0x0001
#define MGMT_EV_CMD_STATUS   0x0002

static int mgmt_send_cmd(int sock, uint16_t opcode, uint16_t index,
                         const void *param, uint16_t param_len)
{
    char buf[1024];
    struct mgmt_hdr *hdr = (struct mgmt_hdr *)buf;
    struct iovec iov[2];
    int ret;

    if (param_len > sizeof(buf) - MGMT_HDR_SIZE) {
        fprintf(stderr, "param too large\n");
        return -1;
    }

    hdr->opcode = opcode;
    hdr->index  = index;
    hdr->len    = param_len;

    iov[0].iov_base = hdr;
    iov[0].iov_len  = MGMT_HDR_SIZE;
    iov[1].iov_base = (void *)param;
    iov[1].iov_len  = param_len;

    ret = writev(sock, iov, 2);
    if (ret < 0) {
        perror("writev");
        return -1;
    }
    return 0;
}

static int mgmt_recv_event(int sock, uint16_t *opcode_out, uint8_t *status_out,
                           int timeout_ms)
{
    char buf[1024];
    struct timeval tv;
    fd_set rfds;
    int ret;
    uint16_t event;

    FD_ZERO(&rfds);
    FD_SET(sock, &rfds);

    tv.tv_sec  = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    ret = select(sock + 1, &rfds, NULL, NULL, &tv);
    if (ret <= 0) {
        if (ret == 0)
            fprintf(stderr, "timeout waiting for response\n");
        else
            perror("select");
        return -1;
    }

    ret = read(sock, buf, sizeof(buf));
    if (ret < 0) {
        perror("read");
        return -1;
    }

    event = ((uint16_t)buf[0]) | ((uint16_t)buf[1] << 8);

    if (event == MGMT_EV_CMD_COMPLETE) {
        struct mgmt_ev_cmd_complete *ev =
            (struct mgmt_ev_cmd_complete *)(buf + 2);
        *opcode_out = ev->opcode;
        *status_out = ev->status;
    } else if (event == MGMT_EV_CMD_STATUS) {
        struct mgmt_ev_cmd_status *ev =
            (struct mgmt_ev_cmd_status *)(buf + 2);
        *opcode_out = ev->opcode;
        *status_out = ev->status;
    } else {
        fprintf(stderr, "unexpected event 0x%04x\n", event);
        *opcode_out = 0;
        *status_out = 0xff;
    }
    return ret;
}

/*
 * Test scenario: send MGMT_OP_ADD_EXT_ADV_DATA with various data_len values.
 * expected_len = struct_size(cp, data, adv_data_len + scan_rsp_len)
 *              = 3 + adv_data_len + scan_rsp_len
 *
 * We use: instance=1, adv_data_len=2, scan_rsp_len=1 => expected_len = 6
 */
static int test_length(int sock, int data_len, const char *desc)
{
    char param[256];
    struct mgmt_cp_add_ext_adv_data *cp =
        (struct mgmt_cp_add_ext_adv_data *)param;
    uint16_t opcode;
    uint8_t status;
    int ret;

    memset(param, 0xAA, sizeof(param));
    cp->instance     = 1;
    cp->adv_data_len = 2;
    cp->scan_rsp_len = 1;
    /* data[] already filled with 0xAA */

    printf("  %-55s ", desc);
    fflush(stdout);

    ret = mgmt_send_cmd(sock, MGMT_OP_ADD_EXT_ADV_DATA, MGMT_INDEX_NONE,
                        param, (uint16_t)data_len);
    if (ret < 0) {
        printf("SEND FAILED\n");
        return -1;
    }

    ret = mgmt_recv_event(sock, &opcode, &status, 3000);
    if (ret < 0) {
        printf("RECV FAILED\n");
        return -1;
    }

    if (status == MGMT_STATUS_SUCCESS)
        printf("ACCEPTED (status=0x%02x)\n", status);
    else if (status == MGMT_STATUS_INVALID_PARAMS)
        printf("REJECTED  (status=MGMT_STATUS_INVALID_PARAMS 0x%02x)\n", status);
    else
        printf("OTHER     (status=0x%02x)\n", status);

    return (status == MGMT_STATUS_SUCCESS) ? 0 : 1;
}

int main(void)
{
    struct sockaddr_hci {
        sa_family_t hci_family;
        unsigned short hci_dev;
        unsigned short hci_channel;
    } addr;
    int sock;
    int passed = 0, failed = 0;

    sock = socket(AF_BLUETOOTH, SOCK_RAW | SOCK_CLOEXEC | SOCK_NONBLOCK,
                  BTPROTO_HCI);
    if (sock < 0) {
        perror("socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)");
        fprintf(stderr, "Cannot open MGMT socket. Requires:\n");
        fprintf(stderr, "  - CONFIG_BT=y, CONFIG_BT_MGMT=y\n");
        fprintf(stderr, "  - CAP_NET_ADMIN (run as root)\n");
        fprintf(stderr, "  - An HCI device or hci_vhci loaded\n");
        return 77; /* SKIP exit code */
    }

    memset(&addr, 0, sizeof(addr));
    addr.hci_family  = AF_BLUETOOTH;
    addr.hci_dev     = HCI_DEV_NONE;
    addr.hci_channel = HCI_CHANNEL_CONTROL;

    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind(HCI_CHANNEL_CONTROL)");
        close(sock);
        return 77;
    }

    /* Clear O_NONBLOCK for select-based receive */
    {
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags & ~O_NONBLOCK);
    }

    printf("PCA-0001: Bluetooth MGMT INPUT_CONTRACT_CHANGE reproducer\n");
    printf("Testing MGMT_OP_ADD_EXT_ADV_DATA with adv_data_len=2, scan_rsp_len=1\n");
    printf("expected_len = 3 + 2 + 1 = 6 bytes\n\n");

    printf("Test 1 - exact match (data_len=6):\n");
    printf("  Expected: ACCEPTED in both before and after versions\n");
    if (test_length(sock, 6, "exact_len=6") == 0)
        passed++;
    else
        failed++;

    printf("\nTest 2 - extra bytes (data_len=7):\n");
    printf("  BEFORE patch: REJECTED (INVALID_PARAMS, != check rejects extra bytes)\n");
    printf("  AFTER  patch: ACCEPTED (extra bytes tolerated, > check only catches undersize)\n");
    printf("  COMPATIBILITY: input contract relaxed, old bluetoothd works again\n");
    if (test_length(sock, 7, "extra_len=7") == 0)
        passed++;
    else
        failed++;

    printf("\nTest 3 - too short (data_len=5):\n");
    printf("  Expected: REJECTED in both versions (would cause OOB access)\n");
    if (test_length(sock, 5, "short_len=5") != 0)
        passed++;
    else
        failed++;

    printf("\nTest 4 - zero data (data_len=3, min struct size):\n");
    printf("  Expected: ACCEPTED (adv_data_len=2 + scan_rsp_len=1 in struct header)\n");
    if (test_length(sock, 3, "min_len=3") == 0)
        passed++;
    else
        failed++;

    close(sock);

    printf("\nResults: %d passed, %d failed\n", passed, failed);
    return (failed > 0) ? 1 : 0;
}
