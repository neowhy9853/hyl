# Environment Setup Guide

## Contents

- Host-machine testing
- QEMU VM and kernel-module testing
- Daemon/service and network-packet testing
- GCC/Clang coverage instrumentation

## Host Machine Testing (User-Space C Tools)

For git, dnsmasq, and similar user-space C programs.

### Step 1: Clone Source and Apply Patch

```bash
# Clone the upstream repo
git clone https://github.com/<org>/<repo>.git /tmp/<project>-source

# Check out the base commit (from analysis.json)
git -C /tmp/<project>-source checkout <base_commit>

# Apply the patch
git -C /tmp/<project>-source am <patch_file>

# Or use worktrees for multiple patches
git -C <bare-repo> worktree add /tmp/<wt-name> <base_commit>
cd /tmp/<wt-name> && git am <patch_file>
```

### Step 2: Install Build Dependencies

```bash
# General C development
sudo apt install -y build-essential gcc make pkg-config autoconf automake

# Project-specific (check Makefile or configure.ac)
sudo apt install -y libssl-dev libcurl4-openssl-dev libexpat-dev gettext  # git
sudo apt install -y nettle-dev libgmp-dev                                  # dnsmasq
```

### Step 3: Build

```bash
# Standard autotools
./configure && make -j$(nproc)

# Custom Makefile (git: use NO_GETTEXT for faster build)
make -j$(nproc) NO_GETTEXT=YesPlease NO_TCLTK=YesPlease NO_ICONV=YesPlease

# dnsmasq with DNSSEC
make COPTS="-DHAVE_DNSSEC" -j$(nproc)
```

---

## QEMU VM Testing (Kernel Modules, Daemons Requiring Root)

### Step 1: Get Cloud Image

```bash
# Ubuntu 22.04 cloud image (~500MB)
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img \
    -O /tmp/qemu-vm/jammy.img
```

### Step 2: Create Cloud-Init Config

```yaml
# /tmp/qemu-vm/cloud-init.yml
#cloud-config
hostname: pcia-test
users:
  - name: tester
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa AAA...  # your SSH public key
packages:
  - build-essential
  - gcc
  - make
  - python3
  - python3-pip
  - nettle-dev
  - libgmp-dev
  - dnsutils
  - tcpdump
  - strace
  - socat
  - f2fs-tools
runcmd:
  - echo "VM ready for PCA testing" > /home/tester/READY
```

### Step 3: Boot VM

```bash
# Resize image
qemu-img resize /tmp/qemu-vm/jammy.img +10G

# Create cloud-init ISO
cloud-localds /tmp/qemu-vm/seed.img /tmp/qemu-vm/cloud-init.yml

# Boot (adjust RAM and CPU as needed)
qemu-system-x86_64 \
    -m 4096 -smp 4 \
    -drive file=/tmp/qemu-vm/jammy.img,format=qcow2 \
    -drive file=/tmp/qemu-vm/seed.img,format=raw \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device virtio-net-pci,netdev=net0 \
    -nographic -enable-kvm
```

### Step 4: Copy Test Artifacts into VM

```bash
# Copy patched source/build
scp -P 2222 -r /path/to/patched-source tester@localhost:/home/tester/
scp -P 2222 /path/to/test-scripts/* tester@localhost:/home/tester/

# SSH in and build
ssh -p 2222 tester@localhost
cd /home/tester/patched-source
make -j4
```

### Step 5: For Kernel Module Testing

```bash
# In VM: build kernel module
cd /path/to/kernel-source
make O=/tmp/kbuild defconfig
make O=/tmp/kbuild -j4 modules_prepare
make O=/tmp/kbuild M=fs/f2fs -j4

# Insert module
sudo insmod /tmp/kbuild/fs/f2fs/f2fs.ko

# Create test filesystem
dd if=/dev/zero of=/tmp/test.f2fs bs=1M count=64
sudo mkfs.f2fs /tmp/test.f2fs
sudo mkdir -p /mnt/f2fs-test
sudo mount -t f2fs -o loop /tmp/test.f2fs /mnt/f2fs-test

# Run the sysfs test
sudo bash run_f2fs_sysfs_u64_check.sh /sys/fs/f2fs/loop0
```

---

## Daemon/Service Testing

For dnsmasq, DHCPv6 servers, and other daemons.

### Pattern: Start → Test → Stop

```bash
#!/bin/bash
# Generic daemon test harness
DAEMON_BIN="/path/to/binary"
CONF_FILE="/tmp/test-daemon.conf"
PID_FILE="/tmp/test-daemon.pid"
LOG_FILE="/tmp/test-daemon.log"
PORT=1053  # Use non-privileged port

cleanup() {
    if [ -f "$PID_FILE" ]; then
        kill "$(cat "$PID_FILE")" 2>/dev/null || true
    fi
    rm -f "$PID_FILE" "$CONF_FILE" "$LOG_FILE"
}
trap cleanup EXIT

# Write config
cat > "$CONF_FILE" << EOF
port=$PORT
no-resolv
no-hosts
bind-interfaces
interface=lo
no-daemon
log-queries=extra
log-facility=$LOG_FILE
EOF

# Start daemon
"$DAEMON_BIN" -C "$CONF_FILE" --pid-file="$PID_FILE" 2>&1 &
sleep 1

if ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "FAIL: daemon failed to start"
    exit 1
fi

# Send test query
dig +tcp @127.0.0.1 -p $PORT test.local A

# Check results
grep "expected_pattern" "$LOG_FILE"
```

### Network Packet Testing (DHCPv6, DNS)

For protocol-level testing, use Python with raw sockets or scapy:

```python
# Minimal mock DNS server pattern
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 15353))

# Build DNS wire-format response manually
response = build_custom_response(query_data)
sock.sendto(response, client_addr)
```

---

## Coverage Instrumentation Setup

### GCC (gcov)

```bash
# Add to build command
CFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"
LDFLAGS="-lgcov --coverage"

# Clean before testing
find . -name "*.gcda" -delete

# After testing, collect coverage per file
gcov -o <obj_dir> <source_file>
```

### Clang (llvm-cov) — Alternative

```bash
# Build with coverage
CFLAGS="-fprofile-instr-generate -fcoverage-mapping -O0 -g"

# Set raw profile output directory
export LLVM_PROFILE_FILE="/tmp/profraw/%p_%m.profraw"

# After testing, merge profiles
llvm-profdata merge -o merged.profdata /tmp/profraw/*.profraw

# Export coverage
llvm-cov export <binary> -instr-profile=merged.profdata > coverage.json
```

### IMPORTANT: Clear Stale Coverage Between Inputs

For single-input isolation testing, clear coverage data before each input:

```bash
# gcov
find <project_dir> -name "*.gcda" -delete  # Clear GCNO data

# llvm-cov
rm -f /tmp/profraw/*.profraw  # Clear raw profiles
export LLVM_PROFILE_FILE="/tmp/profraw/input_%m.profraw"  # Isolate per-input
```

Then measure cumulative coverage after running ALL inputs (for the "total coverage" metric) and per-input coverage (for the "input impact" analysis).
