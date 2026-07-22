# Kernel GCOV Coverage Collection Guide

## Contents

- Architecture and user-space differences
- Complete build, boot, execution, collection, and reporting workflow
- Coverage interpretation and troubleshooting
- Quick reference

Kernel coverage collection is fundamentally different from user-space. This guide covers the complete QEMU + kernel gcov workflow.

## Architecture Overview

```
Host Machine                          QEMU VM
┌──────────────┐                    ┌─────────────────────────┐
│ kernel source │                    │  debugfs                │
│ with .gcno    │                    │  /sys/kernel/debug/gcov/│
│    files      │                    │    ├── fs/f2fs/         │
└──────┬───────┘                    │    │   └── sysfs.gcda  │
       │                            │    ├── sound/soc/       │
       │ ① scp .gcda files          │    └── ...              │
       │    from VM to host         └─────────┬───────────────┘
       │                                      │
       ▼                                      │ ② reset + test
┌──────────────┐                              │    trigger module
│ gcov -o dir  │ ◄── ③ generate .gcov ───────┘
│ source.c     │
│ → .gcov file │
└──────────────┘
```

## Key Differences from User-Space

| Aspect | User-Space (git/dnsmasq) | Kernel (f2fs/drivers) |
|---|---|---|
| **Enable coverage** | `CFLAGS="-fprofile-arcs -ftest-coverage"` | `CONFIG_GCOV_KERNEL=y` + Makefile `GCOV_PROFILE_xxx.o := y` |
| **Optimization** | `-O0` works fine | `-O0` may cause build failures; use `-Og` as compromise |
| **Data location** | `.gcda` files next to `.o` files | `/sys/kernel/debug/gcov/<path>/` via debugfs |
| **Reset between tests** | `find . -name "*.gcda" -delete` | `echo 0 > /sys/kernel/debug/gcov/reset` |
| **Permissions** | User-owned files | Root-only debugfs (requires `sudo`) |
| **Execution env** | Host machine directly | QEMU VM |
| **Data extraction** | Direct file access | `sudo cp -r /sys/kernel/debug/gcov /tmp/` then scp |

## Complete Workflow

### Step 1: Enable Kernel GCOV

In the kernel source directory:

```bash
cd /path/to/linux-source

# Enable CONFIG_GCOV_KERNEL in .config
scripts/config -e GCOV_KERNEL

# OPTIONAL: Enable globally (large, slow; prefer per-subsystem)
# scripts/config -e GCOV_PROFILE_ALL

# Per-subsystem: add to the subsystem's Makefile
# Example for F2FS (fs/f2fs/Makefile):
echo 'GCOV_PROFILE_f2fs.o := y' >> fs/f2fs/Makefile
echo 'GCOV_PROFILE_sysfs.o := y' >> fs/f2fs/Makefile

# Example for a driver (sound/soc/fsl/Makefile):
echo 'GCOV_PROFILE_fsl_xcvr.o := y' >> sound/soc/fsl/Makefile
```

**Critical Kconfig options:**
```
CONFIG_GCOV_KERNEL=y           # REQUIRED: enables kernel gcov infrastructure
CONFIG_GCOV_PROFILE_ALL=y      # OPTIONAL: profiles EVERYTHING (massive data)
```

**Per-subsystem control (preferred):**
- `GCOV_PROFILE_<filename>.o := y` in the appropriate Makefile
- Only the specified object files are instrumented
- Much smaller data, faster build, less VM memory pressure

### Step 2: Build Kernel with Coverage

```bash
cd /path/to/linux-source

# IMPORTANT: Use -O0 or -Og for accurate line mapping
# WARNING: -O0 may cause kernel build failures in some subsystems
# If -O0 fails, try -Og or accept -O2 with potential line number skew

# Approach A: -O0 (best line accuracy, may fail on complex subsystems)
make -j$(nproc) KCFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"

# Approach B: -Og (good accuracy, more compatible)
make -j$(nproc) KCFLAGS="-fprofile-arcs -ftest-coverage -Og -g"

# Approach C: default -O2 (most compatible, accept line skew)
make -j$(nproc)
# (CONFIG_GCOV_KERNEL=y already adds the coverage flags)

echo "Build complete. Kernel: arch/x86/boot/bzImage"
```

**Optimization level tradeoffs:**

| Level | Line Accuracy | Build Success | Performance |
|---|---|---|---|
| `-O0` | Perfect — every source line maps 1:1 | May fail on some subsystems | Very slow |
| `-Og` | Good — most lines preserved | Works on most subsystems | Moderate |
| `-O2` | Poor — inlining/optimization shifts lines | Always works | Normal |

**Recommendation**: Start with `-O0`. If the build fails, try `-Og`. If that also fails (e.g., on complex drivers), fall back to `-O2` and accept that gcov line numbers may not match source exactly. Document which level was used in the coverage report.

### Step 3: Boot QEMU VM and Mount debugfs

```bash
# Boot VM with the newly built kernel
qemu-system-x86_64 \
    -kernel /path/to/linux-source/arch/x86/boot/bzImage \
    -append "console=ttyS0 root=/dev/sda1 rw" \
    -drive file=/tmp/qemu-vm/jammy.img,format=qcow2 \
    -m 4096 -smp 4 -nographic -enable-kvm

# Inside VM:
# Mount debugfs (REQUIRED — gcov data lives here)
sudo mount -t debugfs none /sys/kernel/debug

# Verify gcov is working
ls /sys/kernel/debug/gcov/
# Should show directory structure matching kernel source tree:
#   /sys/kernel/debug/gcov/fs/f2fs/sysfs.gcda
#   /sys/kernel/debug/gcov/sound/soc/fsl/fsl_xcvr.gcda
# If empty or missing, check:
#   - CONFIG_GCOV_KERNEL=y is set
#   - debugfs is mounted
#   - The module/subsystem is loaded
```

### Step 4: Load Module / Prepare Test Environment

```bash
# For built-in code (like filesystem code):
sudo mkdir -p /mnt/f2fs-test

# For loadable modules:
sudo modprobe f2fs   # or: sudo insmod /path/to/module.ko
lsmod | grep f2fs    # verify loaded

# Create test resources if needed:
dd if=/dev/zero of=/tmp/test.f2fs bs=1M count=64
sudo mkfs.f2fs /tmp/test.f2fs
sudo mount -t f2fs -o loop /tmp/test.f2fs /mnt/f2fs-test
```

### Step 5: Reset + Execute Test + Collect

This is the critical loop — for single-input isolation testing:

```bash
# === For EACH test input, do this sequence ===

# A. RESET coverage counters (isolates this input's coverage)
sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'

# B. EXECUTE the test input
sudo bash run_f2fs_sysfs_u64_check.sh /sys/fs/f2fs/loop0
# Or: echo 4294967297 | sudo tee /sys/fs/f2fs/loop0/atgc_age_threshold > /dev/null
# Or: sudo amixer cset ...  (for ALSA controls)

# C. COLLECT gcov data for this input
sudo cp -r /sys/kernel/debug/gcov /tmp/gcov_data_input1

# D. REPEAT for next input
sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'
# ... execute input 2 ...
sudo cp -r /sys/kernel/debug/gcov /tmp/gcov_data_input2
```

**Cumulative coverage (all inputs together):**
```bash
# Run ALL inputs without resetting
sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'   # reset once
<test_input_1>
<test_input_2>
<test_input_3>
sudo cp -r /sys/kernel/debug/gcov /tmp/gcov_data_cumulative
```

### Step 6: Export gcov Data to Host

```bash
# From HOST machine:
scp -P 2222 -r tester@localhost:/tmp/gcov_data_cumulative ./gcov_data/

# The directory structure mirrors the kernel source:
# ./gcov_data/fs/f2fs/sysfs.gcda
# ./gcov_data/fs/f2fs/f2fs.gcda
# etc.
```

### Step 7: Generate Coverage Reports

```bash
cd /path/to/linux-source

# Copy .gcda files to match .gcno locations in kernel source tree
for gcdafile in $(find ./gcov_data -name "*.gcda"); do
    # Extract relative path from gcov_data
    relpath="${gcdafile#./gcov_data/}"
    # Example: relpath = "fs/f2fs/sysfs.gcda"
    target_dir="$(dirname "$relpath")"
    # Example: target_dir = "fs/f2fs"
    cp "$gcdafile" "$target_dir/"
done

# Run gcov on the specific changed file
gcov -o fs/f2fs fs/f2fs/sysfs.c
# Output: fs/f2fs/sysfs.c.gcov

# Check specific lines
grep -E "^ *[0-9]+|#####" fs/f2fs/sysfs.c.gcov | head -30
```

### Step 8: Interpret Results

gcov output format for kernel code:
```
    -:    0:Source:fs/f2fs/sysfs.c         ← header
    -:    0:Graph:sysfs.gcno               ← graph data
    -:    0:Data:sysfs.gcda                ← profile data
    1:  286:static ssize_t __sbi_show...   ← executed 1 time
    #####:  290:    case 1:                ← NOT EXECUTED
    5:  293:    case 8:                    ← executed 5 times
    -:  295:    default:                   ← non-executable
```

**Important: line number skew with -O2**

When compiled with `-O2` (not `-O0`), gcov may report that line N was executed but the actual source line is N±3 due to compiler optimizations (inlining, code motion). Always verify with the source that the reported execution makes semantic sense.

**Signs of -O2 skew:**
- A comment line shows as "executed" (impossible — it was a nearby code line)
- A blank line shows as "executed" (same)
- A line that can't logically be reached shows a count

**Mitigation**: Always use `-O0` or `-Og` for kernel gcov testing. If `-O0` fails to build, document which optimization level was used in the coverage report.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `/sys/kernel/debug/gcov/` missing | debugfs not mounted | `sudo mount -t debugfs none /sys/kernel/debug` |
| `/sys/kernel/debug/gcov/` empty | `GCOV_PROFILE` not set | Add `GCOV_PROFILE_xxx.o := y` to Makefile |
| gcda files have 0 bytes | Module not loaded/used | `sudo modprobe <module>` or trigger the code path |
| `gcov` says "cannot open graph file" | `.gcno` not in expected location | Copy `.gcda` to match `.gcno` path, or use `gcov -o <obj_dir>` |
| Line numbers don't match source | `-O2` optimization skew | Rebuild with `-O0`; document if not possible |
| `echo 0 > reset` permission denied | Not root | Use `sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'` |
| Kernel build fails with `-O0` | Some subsystems require optimization | Use `-Og` or `KCFLAGS="-O0"` with `make SUBDIRS=fs/f2fs` |

## Quick Reference Card

```bash
# === ONE-TIME SETUP ===
scripts/config -e GCOV_KERNEL                    # Enable in .config
echo 'GCOV_PROFILE_f2fs.o := y' >> fs/f2fs/Makefile
make -j$(nproc) KCFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"

# === PER-TEST IN VM ===
sudo mount -t debugfs none /sys/kernel/debug     # First time only
sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'  # Before each test
<run_test>                                        # Execute test input
sudo cp -r /sys/kernel/debug/gcov /tmp/gcov_N    # Collect data

# === ON HOST ===
scp -r vm:/tmp/gcov_N ./gcov_data/
cp ./gcov_data/fs/f2fs/*.gcda fs/f2fs/
gcov -o fs/f2fs fs/f2fs/sysfs.c
grep -E "392:|393:|394:" fs/f2fs/sysfs.c.gcov
```
