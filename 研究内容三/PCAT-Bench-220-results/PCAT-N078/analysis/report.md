# Patch Compatibility Analyzer Report Draft

- Source repo: `/data7/wanghy/tmp/linux`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/_worktrees/patched`
- Patch ID: `8e655dbef4c9e56f125dc3545e52d5cf703751ca`
- Base ref: `8e655dbef4c9e56f125dc3545e52d5cf703751ca^`
- Base commit: `78da8e1be90c51d260cfb4442362bb3c9c4b49c9`
- Patch apply status: `applied`
- Profile: `kernel_6_6`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 6715 |
| `patch_lines` | 216 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 167 |
| `candidate_context_bytes` | 9430 |
| `candidates_json_bytes` | 20603 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/_worktrees/patched`.
- Pre-patch source read command: `git -C /data7/wanghy/tmp/linux show 78da8e1be90c51d260cfb4442362bb3c9c4b49c9:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N038/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tools/testing/selftests/bpf/progs/verifier_scalar_ids.c` old `47-52` new `47-118` symbol `linked_regs_bpf_k, Registers, r, share, same, ID, volatile` surface `unknown`
- `HUNK-0002` `tools/testing/selftests/bpf/progs/verifier_scalar_ids.c` old `280-285` new `346-447` symbol `precision_two_ids, SEC, socket, __success, __log_level, __flag, volatile` surface `unknown`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## Adjudication Result

**No compatibility changes detected.**

### Analysis

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 2 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

### 判定依据

补丁仅修改了 `tools/testing/selftests/bpf/progs/verifier_scalar_ids.c`，该文件位于 BPF 自测目录中，属于纯测试代码。变更内容为新增 5 个 `__naked` BPF 测试程序（linked_regs_bpf_x_src、linked_regs_bpf_x_dst、linked_regs_too_many_regs、linked_regs_broken_link_2、cjmp_no_linked_regs_trigger），用于验证 BPF 验证器精度跟踪的边界情况。

- **public_api_hunks: 0** — 两个候选 hunk 均不匹配任何公共 API surface（UAPI header、导出符号、syscall、ioctl、netlink、procfs、sysfs、sysctl、CLI/配置）
- **仅新增代码，无删除行** — 不修改任何已有接口的签名或行为
- **测试文件，非内核运行时代码** — 不影响内核对外接口

### Validation

analysis.json 已通过 validate_analysis.py 校验。优先级校准器确认 0 条 finding，无需调整。
