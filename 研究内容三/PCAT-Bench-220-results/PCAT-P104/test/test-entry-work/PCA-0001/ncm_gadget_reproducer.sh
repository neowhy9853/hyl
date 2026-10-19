#!/bin/bash
# PCA-0001 SIDE_EFFECT_CHANGE Reproducer: NCM gadget net_device lifecycle
#
# 测试patch前后NCM gadget的net_device在sysfs中的生命周期变化
#
# 用法: bash ncm_gadget_reproducer.sh <BEFORE_KERNEL_VM> <AFTER_KERNEL_VM>
# 或直接在目标VM中运行每个测试阶段。
#
# 前置条件:
#   - 两个VM分别运行baseline和patched内核
#   - CONFIG_USB_GADGET=y, CONFIG_USB_CONFIGFS=y, CONFIG_USB_CONFIGFS_NCM=y
#   - dummy_hcd.ko已加载 (modprobe dummy_hcd)
#   - libcomposite.ko, u_ether.ko, usb_f_ncm.ko已加载
#   - configfs已挂载: mount -t configfs none /sys/kernel/config

set -euo pipefail

BEFORE_DIR="${1:-}"
AFTER_DIR="${2:-}"
TEST_DIR="${TEST_DIR:-/tmp/ncm_gadget_test}"
IFACE_NAME="${IFACE_NAME:-usb0}"

log() { echo "[$(date +%H:%M:%S)] $*"; }

# ---- Phase 1: 环境准备 ----
setup_gadget() {
    log "Setting up NCM gadget via configfs..."
    mkdir -p "$TEST_DIR"
    
    cd /sys/kernel/config/usb_gadget
    mkdir -p g1
    cd g1
    
    echo "0x1d6b" > idVendor
    echo "0x0104" > idProduct
    echo "0x0100" > bcdDevice
    echo "0x0200" > bcdUSB
    
    mkdir -p strings/0x409
    echo "0123456789" > strings/0x409/serialnumber
    echo "Test" > strings/0x409/manufacturer
    echo "NCM Gadget" > strings/0x409/product
    
    mkdir -p functions/ncm.usb0
    mkdir -p configs/c.1
    ln -s functions/ncm.usb0 configs/c.1/
    
    echo "dummy_udc.0" > UDC
    sleep 2
    log "Gadget setup complete. Network interface should appear as $IFACE_NAME"
}

cleanup_gadget() {
    log "Cleaning up gadget..."
    cd /sys/kernel/config/usb_gadget/g1 2>/dev/null || return 0
    echo "" > UDC 2>/dev/null || true
    rm -f configs/c.1/ncm.usb0 2>/dev/null || true
    rmdir configs/c.1 2>/dev/null || true
    rmdir functions/ncm.usb0 2>/dev/null || true
    rmdir strings/0x409 2>/dev/null || true
    cd /sys/kernel/config/usb_gadget
    rmdir g1 2>/dev/null || true
}

# ---- Phase 2: 监控sysfs变化 ----
monitor_sysfs() {
    local stage="$1"
    log "=== $stage ==="
    
    if [ -L "/sys/class/net/$IFACE_NAME" ]; then
        log "Interface $IFACE_NAME exists"
        log "Device symlink: $(readlink /sys/class/net/$IFACE_NAME/device 2>/dev/null || echo 'N/A')"
        log "Uevent: $(cat /sys/class/net/$IFACE_NAME/device/uevent 2>/dev/null || echo 'N/A')"
    else
        log "Interface $IFACE_NAME does NOT exist"
    fi
    
    # 记录uevent事件(通过udevadm)
    log "Recent uevents for $IFACE_NAME:"
    udevadm info --query=path --name="$IFACE_NAME" 2>/dev/null || echo "No udev info"
}

# ---- Phase 3: bind/unbind循环测试 ----
test_bind_unbind_cycle() {
    log "Starting bind/unbind cycle test..."
    
    # Step 1: 首次bind(注册net_device)
    setup_gadget
    monitor_sysfs "AFTER_FIRST_BIND"
    
    # 验证net_device存在且正常
    if ! ip link show "$IFACE_NAME" >/dev/null 2>&1; then
        log "ERROR: $IFACE_NAME not found after bind"
        return 1
    fi
    
    # 记录初始设备路径
    DEV_PATH_BEFORE=$(readlink /sys/class/net/$IFACE_NAME/device 2>/dev/null || echo "NONE")
    log "Initial device path: $DEV_PATH_BEFORE"
    
    # Step 2: 解绑(unbind)
    echo "" > /sys/kernel/config/usb_gadget/g1/UDC 2>/dev/null || true
    sleep 1
    monitor_sysfs "AFTER_UNBIND"
    
    # 验证: net_device应该还存在(旧行为已销毁, 新行为持久存在)
    if ip link show "$IFACE_NAME" >/dev/null 2>&1; then
        log "PASS: $IFACE_NAME persists after unbind (new behavior)"
        DEV_PATH_AFTER_UNBIND=$(readlink /sys/class/net/$IFACE_NAME/device 2>/dev/null || echo "NONE")
        log "Device path after unbind: $DEV_PATH_AFTER_UNBIND"
        
        # 验证device路径已变更(不在gadget下, 应在/sys/devices/virtual/下)
        if [[ "$DEV_PATH_AFTER_UNBIND" != *"dummy_udc"* ]] && [[ "$DEV_PATH_AFTER_UNBIND" != *"gadget"* ]]; then
            log "PASS: Device moved back to /sys/devices/virtual/ (device_move to NULL)"
        else
            log "UNEXPECTED: Device still under gadget after unbind"
        fi
    else
        log "OLD_BEHAVIOR: $IFACE_NAME disappeared after unbind (old behavior, net_device destroyed)"
    fi
    
    # Step 3: 重新绑定
    echo "dummy_udc.0" > /sys/kernel/config/usb_gadget/g1/UDC 2>/dev/null || true
    sleep 2
    monitor_sysfs "AFTER_REBIND"
    
    DEV_PATH_AFTER_REBIND=$(readlink /sys/class/net/$IFACE_NAME/device 2>/dev/null || echo "NONE")
    log "Device path after rebind: $DEV_PATH_AFTER_REBIND"
    
    # 验证device已重新附着到gadget
    if [[ "$DEV_PATH_AFTER_REBIND" == *"dummy_udc"* ]] || [[ "$DEV_PATH_AFTER_REBIND" == *"gadget"* ]]; then
        log "PASS: Device re-attached to gadget (device_move to gadget device)"
    fi
    
    # 清理
    cleanup_gadget
    log "Bind/unbind cycle test complete."
}

# ---- Phase 4: uevent验证 ----
test_uevent_changes() {
    log "Starting uevent monitoring..."
    # 在另一个终端运行: udevadm monitor -k -p > /tmp/uevents.log
    # 然后执行bind/unbind, 检查KOBJ_MOVE事件
    
    log "Run this in another terminal before the bind/unbind test:"
    log "  udevadm monitor -k -p | grep -E '(KOBJ_|DEVNAME)' > /tmp/uevents.log"
    log ""
    log "After the bind/unbind cycle, check for KOBJ_MOVE events:"
    log "  grep -c 'KOBJ_MOVE' /tmp/uevents.log"
    log "  grep -c 'KOBJ_ADD' /tmp/uevents.log"
    log "  grep -c 'KOBJ_REMOVE' /tmp/uevents.log"
}

# ---- Main ----
main() {
    log "PCA-0001 NCM Gadget net_device lifecycle test"
    log "=============================================="
    
    # 检查configfs
    if ! mountpoint -q /sys/kernel/config 2>/dev/null; then
        log "Mounting configfs..."
        mount -t configfs none /sys/kernel/config || {
            log "ERROR: Cannot mount configfs. Need CONFIG_CONFIGFS_FS=y"
            exit 1
        }
    fi
    
    # 加载必要的内核模块
    modprobe dummy_hcd 2>/dev/null || log "WARNING: dummy_hcd not available"
    modprobe libcomposite 2>/dev/null || true
    modprobe u_ether 2>/dev/null || true
    
    test_uevent_changes
    echo ""
    test_bind_unbind_cycle
    
    log "Test complete."
}

main "$@"
