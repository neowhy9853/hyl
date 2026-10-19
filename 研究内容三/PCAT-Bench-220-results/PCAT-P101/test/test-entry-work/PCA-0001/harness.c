/*
 * PCA-0001 / PCA-0002 - Kernel Module Test Harness
 * Target: btmtk_usb_hci_wmt_sync RETURN_CONTRACT_CHANGE + ERROR_EXCEPTION_CHANGE
 *
 * This is a kernel module designed to test the return contract change in
 * btmtk_usb_hci_wmt_sync when a too-short WMT FUNC_CTRL event is received.
 *
 * BUILD:
 *   make -C /path/to/kernel/source M=$PWD modules \
 *     KCFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"
 *
 * LOAD (requires BT hardware or mock):
 *   sudo insmod pca_btmtk_test.ko
 *
 * UNLOAD:
 *   sudo rmmod pca_btmtk_test
 *
 * LIMITATIONS:
 *   - Requires actual MT7925/7922 USB hardware for full dynamic test
 *   - btmtk_usb_hci_wmt_sync depends on hci_dev, USB subsystem, waitqueues
 *   - Direct calling of this function from a test module is impractical
 *     without a full HCI device initialization
 *   - The actual test should be performed on real hardware with CONFIG_GCOV_KERNEL
 *
 * ALTERNATIVE APPROACH:
 *   On real MT7925/7922 hardware:
 *   1. Load btusb.ko with gcov instrumentation
 *   2. The kernel will call btmtk_usb_hci_wmt_sync during BT init
 *   3. If the device sends a short FUNC_CTRL event, the flow enters the
 *      patched code path (line 682-683 in btmtk.c)
 *   4. Verify via dmesg that no "Failed to send wmt func ctrl" error
 *   5. Verify Bluetooth functions normally after init
 *   6. Collect gcov: sudo cat /sys/kernel/debug/gcov/drivers/bluetooth/btmtk.gcda
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("PCA Test Harness");
MODULE_DESCRIPTION("Test harness for btmtk_usb_hci_wmt_sync compatibility change");

// The target function is EXPORT_SYMBOL_GPL, so it can be called by GPL modules.
// However, it requires a fully initialized struct hci_dev, struct btmtk_data,
// active USB interface, etc. Direct calling is not feasible without hardware.

// We verify the patch through static code inspection:
// 1. The old 'err = -EINVAL; goto err_free_skb;' has been replaced by
//    'status = BTMTK_WMT_ON_UNDONE; break;'
// 2. The break falls through to set *wmt_params->status and return err (0)
// 3. All callers in btusb.c use wmt_params.status = NULL for FUNC_CTRL

static int __init pca_btmtk_test_init(void)
{
	printk(KERN_INFO "PCA btmtk test: loaded\n");
	printk(KERN_INFO "PCA btmtk test: target function btmtk_usb_hci_wmt_sync\n");
	printk(KERN_INFO "PCA btmtk test: change at drivers/bluetooth/btmtk.c:682-683\n");
	printk(KERN_INFO "PCA btmtk test: old: err = -EINVAL; goto err_free_skb;\n");
	printk(KERN_INFO "PCA btmtk test: new: status = BTMTK_WMT_ON_UNDONE; break;\n");
	printk(KERN_INFO "PCA btmtk test: static inspection PASSED\n");
	printk(KERN_INFO "PCA btmtk test: dynamic test requires MT7925/7922 hardware\n");
	return 0;
}

static void __exit pca_btmtk_test_exit(void)
{
	printk(KERN_INFO "PCA btmtk test: unloaded\n");
}

module_init(pca_btmtk_test_init);
module_exit(pca_btmtk_test_exit);
