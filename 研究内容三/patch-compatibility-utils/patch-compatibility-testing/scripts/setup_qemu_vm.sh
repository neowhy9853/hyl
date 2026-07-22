#!/bin/bash
# =============================================================================
# setup_qemu_vm.sh — Create and boot a QEMU VM for patch testing
#
# Usage: setup_qemu_vm.sh <image_path> [cpu_count] [memory_mb] [ssh_port]
#
# Creates a QEMU VM from an Ubuntu cloud image with cloud-init for automated
# setup. Useful for kernel module testing, daemons requiring root, or isolated
# test environments.
#
# After boot, connect via: ssh -p <ssh_port> tester@localhost
# =============================================================================
set -euo pipefail

IMAGE="${1:-/tmp/qemu-vm/jammy.img}"
CPUS="${2:-4}"
MEMORY="${3:-4096}"
SSH_PORT="${4:-2222}"
WORKDIR="$(dirname "$IMAGE")"
VMNAME="pcia-test-vm"

mkdir -p "$WORKDIR"

# Step 1: Download cloud image if not present
if [ ! -f "$IMAGE" ]; then
    echo "=== Downloading Ubuntu 22.04 cloud image (~500MB) ==="
    wget -q --show-progress \
        https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img \
        -O "$IMAGE"
    qemu-img resize "$IMAGE" +10G
fi

# Step 2: Create cloud-init config
echo "=== Creating cloud-init config ==="
cat > "$WORKDIR/cloud-init.yml" << 'CLOUDEOF'
#cloud-config
hostname: pcia-test
manage_etc_hosts: true
users:
  - name: tester
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: $6$rounds=4096$test$test  # placeholder, SSH key preferred
    shell: /bin/bash
    ssh_authorized_keys: []
package_update: true
package_upgrade: false
packages:
  - build-essential
  - gcc
  - g++
  - make
  - pkg-config
  - git
  - python3
  - python3-pip
  - nettle-dev
  - libgmp-dev
  - dnsutils
  - tcpdump
  - strace
  - socat
  - f2fs-tools
  - gdb
  - lcov
runcmd:
  - echo "PCA test VM ready" > /home/tester/READY
final_message: "PCA test VM booted successfully"
CLOUDEOF

# Create cloud-init seed image
if command -v cloud-localds &>/dev/null; then
    cloud-localds "$WORKDIR/seed.img" "$WORKDIR/cloud-init.yml"
else
    echo "WARNING: cloud-localds not found. Install cloud-image-utils."
    echo "Skipping cloud-init. VM will need manual setup."
fi

# Step 3: Boot VM
echo "=== Booting QEMU VM ==="
echo "  Image:  $IMAGE"
echo "  CPUs:   $CPUS"
echo "  Memory: ${MEMORY}MB"
echo "  SSH:    localhost:$SSH_PORT"

if [ -f "$WORKDIR/seed.img" ]; then
    qemu-system-x86_64 \
        -name "$VMNAME" \
        -m "$MEMORY" -smp "$CPUS" \
        -drive file="$IMAGE",format=qcow2,if=virtio \
        -drive file="$WORKDIR/seed.img",format=raw,if=virtio \
        -netdev user,id=net0,hostfwd=tcp::${SSH_PORT}-:22 \
        -device virtio-net-pci,netdev=net0 \
        -nographic \
        -enable-kvm \
        ${QEMU_EXTRA_ARGS:-} &
    QEMU_PID=$!
    echo "QEMU PID: $QEMU_PID"
    echo ""
    echo "=== Waiting for VM to boot (cloud-init may take 1-2 min) ==="
    echo "Connect via: ssh -p $SSH_PORT tester@localhost"
    echo "Stop VM:     kill $QEMU_PID"
else
    qemu-system-x86_64 \
        -name "$VMNAME" \
        -m "$MEMORY" -smp "$CPUS" \
        -drive file="$IMAGE",format=qcow2,if=virtio \
        -netdev user,id=net0,hostfwd=tcp::${SSH_PORT}-:22 \
        -device virtio-net-pci,netdev=net0 \
        -nographic \
        -enable-kvm \
        ${QEMU_EXTRA_ARGS:-} &
    QEMU_PID=$!
    echo "QEMU PID: $QEMU_PID"
fi
