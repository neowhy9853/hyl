# PCA 兼容性变更分析报告

- Source repo: `/home/soong/pca_benchmark/_repos/linux`
- Patched analysis worktree: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/_worktrees/patched`
- Patch ID: `3310153e66dddd35668e409c053cb72e3ae224ce`
- Base ref: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`
- Base commit: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`
- Patch apply status: `applied`
- Profile: `kernel_6_6`
- Effective profile: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 501 |
| `patch_lines` | 18 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 2 |
| `candidate_context_bytes` | 1937 |
| `candidates_json_bytes` | 6220 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/linux show ffc253263a1375a65fa6c9f62a893e9767fbebfa:<path>`.
- Rebuild worktree: `/home/soong/miniconda3/bin/python3 /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/miniconda3/bin/python3 /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P002/analysis/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `include/uapi/linux/uinput.h` old `43-49` new `43-49` symbol `define, UINPUT_VERSION` surface `public_headers, ioctl_netlink_consumers, uapi, ioctl`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## 最终判定

- 确认兼容性变化：1
- 类型：`ABI_CHANGE`
- 测试优先级：`high`
- 影响接口：`UINPUT_VERSION`
- 位置：`include/uapi/linux/uinput.h:46`

### 变更前行为

包含 `<linux/uinput.h>` 的用户态 C 代码在编译时得到 `UINPUT_VERSION == 5`。

### 变更后行为

包含 `<linux/uinput.h>` 的用户态 C 代码在编译时得到 `UINPUT_VERSION == 6`。

### 兼容性影响

`UINPUT_VERSION` 位于稳定的 `include/uapi/**` 公共接口面。宏值变化会改变既有用户态源码的编译期常量、静态断言和版本分支选择，因此属于 UAPI 宏契约的 `ABI_CHANGE`。

### 测试建议

分别针对补丁前后头文件编译并运行最小 C 探针，比较宏值，并用旧值为 5 的编译期断言验证下游源码兼容性。
