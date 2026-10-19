# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/_worktrees/patched`
- Patch ID: `29ed28820a3bd8222d7b533e41ecd4809a2162f8`
- Base ref: `29ed28820a3bd8222d7b533e41ecd4809a2162f8~1`
- Base commit: `1468127018e1223ec87d7a56dd16270edf396b87`
- Patch apply status: `applied`
- Profile: `grub2`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 5
- Candidate hunks: 11
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 7616 |
| `patch_lines` | 200 |
| `raw_hunks` | 11 |
| `candidate_hunks` | 11 |
| `changed_files` | 5 |
| `churn` | 72 |
| `candidate_context_bytes` | 21427 |
| `candidates_json_bytes` | 59028 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2 show 1468127018e1223ec87d7a56dd16270edf396b87:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `grub-core/disk/cryptodisk.c` old `702-708` new `702-708` symbol `grub_cryptodisk_open, grub_uuidcasecmp, name, cryptouuid, dev, uuid, grub_error` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink, plugin_api, logging, module_api`
- `HUNK-0002` `grub-core/disk/cryptodisk.c` old `929-935` new `929-935` symbol `grub_cryptodisk_get_by_uuid, grub_uuidcasecmp, dev, uuid, grub_strcasecmp` surface `module_api`
- `HUNK-0003` `grub-core/disk/geli.c` old `305-311` new `305-311` symbol `configure_ciphers, cargs, search_uuid, NULL, grub_uuidcasecmp, uuid, grub_crypto_gcry_error` surface `config_keys, user_visible_output, config, module_api`
- `HUNK-0004` `grub-core/disk/luks.c` old `66-75` new `66-72` symbol `iptr, optr, uuid, header, configure_ciphers` surface `config_keys, user_visible_output, config, module_api, boot_protocol`
- `HUNK-0005` `grub-core/disk/luks.c` old `92-110` new `89-97` symbol `configure_ciphers, cargs, search_uuid, NULL, grub_uuidcasecmp, header, grub_dprintf` surface `config_keys, user_visible_output, config, logging, module_api`
- `HUNK-0006` `grub-core/disk/luks.c` old `123-129` new `110-116` symbol `configure_ciphers, grub_memcpy, newdev, uuid, header` surface `config_keys, user_visible_output, config, logging, module_api`
- `HUNK-0007` `grub-core/disk/luks.c` old `143-149` new `130-136` symbol `configure_ciphers, COMPILE_TIME_ASSERT, newdev, uuid, header, grub_free` surface `config_keys, user_visible_output, config, module_api`
- `HUNK-0008` `grub-core/disk/luks2.c` old `350-357` new `350-355` symbol `luks2_scan, uuid, header, grub_size_t, i, j` surface `user_visible_output, module_api`
- `HUNK-0009` `grub-core/disk/luks2.c` old `362-375` new `360-368` symbol `luks2_scan, cargs, search_uuid, NULL, grub_uuidcasecmp, header, grub_dprintf` surface `user_visible_output, module_api`
- `HUNK-0010` `grub-core/disk/luks2.c` old `377-384` new `370-377` symbol `luks2_scan, COMPILE_TIME_ASSERT, cryptodisk, uuid, header, grub_memcpy, grub_dprintf` surface `user_visible_output, module_api`
- `HUNK-0011` `include/grub/misc.h` old `290-295` new `290-325` symbol `grub_strncasecmp, Do, a, insensitive, compare, of` surface `public_headers, struct_layout, module_api, boot_protocol`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## Agent Adjudication Requirements

- This report is deterministic evidence, not the final compatibility decision.
- Start from analysis-context.json. It is the bounded context for agent adjudication and includes focused source excerpts.
- Do not reopen large source files to locate a changed function already present in analysis-context.json.
- Do not scan repo roots, patch-list directories, output directories, or profile trees.
- Final findings must include only confirmed compatibility changes.
- Every finding must include code line locations and at least one evidence snippet.
- In heavy mode, analyze each shard independently, then aggregate shard results with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis.json`
