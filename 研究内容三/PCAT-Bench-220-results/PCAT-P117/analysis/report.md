# Patch Compatibility Analyzer Report Draft

- Source repo: `/data7/wanghy/tmp/opencode/grub2`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/_worktrees/patched`
- Patch ID: `204a6ddfb3bb456929e7c364e1e8d6ee1928b471`
- Base ref: `6b64f297e`
- Base commit: `6b64f297e5906feb295dcc6fb5046368f5f3e95b`
- Patch apply status: `applied`
- Profile: `grub2`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; patch_lines=1066 >= 1000; candidates_json_bytes=224374 >= 180000
- Changed files: 2
- Candidate hunks: 27
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 39757 |
| `patch_lines` | 1066 |
| `raw_hunks` | 27 |
| `candidate_hunks` | 27 |
| `changed_files` | 2 |
| `churn` | 726 |
| `candidate_context_bytes` | 84727 |
| `candidates_json_bytes` | 224374 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/shards`
- Shard count: 11

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `cli_options` | 5 | 1 | 11842 | `shards/shard-0001.json` |
| `SHARD-0002` | `cli_options` | 2 | 1 | 5288 | `shards/shard-0002.json` |
| `SHARD-0003` | `config` | 1 | 1 | 3303 | `shards/shard-0003.json` |
| `SHARD-0004` | `module_api` | 2 | 1 | 3816 | `shards/shard-0004.json` |
| `SHARD-0005` | `plugin_api` | 1 | 1 | 1447 | `shards/shard-0005.json` |
| `SHARD-0006` | `public_headers` | 3 | 1 | 11401 | `shards/shard-0006.json` |
| `SHARD-0007` | `public_headers` | 3 | 1 | 19031 | `shards/shard-0007.json` |
| `SHARD-0008` | `public_headers` | 3 | 1 | 13217 | `shards/shard-0008.json` |
| `SHARD-0009` | `user_visible_output` | 3 | 1 | 6894 | `shards/shard-0009.json` |
| `SHARD-0010` | `user_visible_output` | 3 | 1 | 6961 | `shards/shard-0010.json` |
| `SHARD-0011` | `user_visible_output` | 1 | 1 | 1527 | `shards/shard-0011.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/_worktrees/patched`.
- Pre-patch source read command: `git -C /data7/wanghy/tmp/opencode/grub2 show 6b64f297e5906feb295dcc6fb5046368f5f3e95b:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `grub-core/loader/i386/linux.c` old `124-130` new `124-130` symbol `find_mmap_size, mmap_size, count, grub_boot_e820_entry, grub_e820_mmap, grub_mmap_iterate` surface `plugin_api, module_api, boot_protocol`
- `HUNK-0002` `grub-core/loader/i386/linux.c` old `212-231` new `212-231` symbol `allocate_pages, grub_e820_add_region, grub_boot_e820_entry, e820_entry, e820_num, n, free_pages` surface `user_visible_output, config, module_api, boot_protocol`
- `HUNK-0003` `grub-core/loader/i386/linux.c` old `253-295` new `253-295` symbol `linux_kernel_params, params, screen_info, lfb_width, mode_info, width, grub_linux_setup_video` surface `config, module_api, boot_protocol`
- `HUNK-0004` `grub-core/loader/i386/linux.c` old `307-313` new `307-313` symbol `linux_kernel_params, params, screen_info, orig_video_isVGA, GRUB_VIDEO_LINUX_TYPE_SIMPLE, have_vga, grub_linux_setup_video` surface `module_api, boot_protocol`
- `HUNK-0005` `grub-core/loader/i386/linux.c` old `332-340` new `332-340` symbol `linux_kernel_params, params, screen_info, red_size, green_size, blue_size, grub_linux_setup_video` surface `module_api, boot_protocol`
- `HUNK-0006` `grub-core/loader/i386/linux.c` old `391-397` new `391-397` symbol `grub_linux_boot_mmap_fill, grub_e820_add_region, ctx, params, e820_table, e820_num` surface `user_visible_output, config, module_api, boot_protocol`
- `HUNK-0007` `grub-core/loader/i386/linux.c` old `423-432` new `423-432` symbol `grub_linux_boot, linux_params, olpc_ofw_header, ofw_magic, GRUB_LINUX_OFW_SIGNATURE, ofw_version` surface `user_visible_output, config, module_api, boot_protocol`
- `HUNK-0008` `grub-core/loader/i386/linux.c` old `471-489` new `471-489` symbol `grub_linux_boot, linux_params, screen_info, orig_video_isVGA, GRUB_VIDEO_LINUX_TYPE_TEXT, orig_video_mode, grub_puts_` surface `user_visible_output, module_api, boot_protocol`
- `HUNK-0009` `grub-core/loader/i386/linux.c` old `494-512` new `494-512` symbol `grub_linux_boot, linux_params, screen_info, orig_x, pos, x, FOR_ACTIVE_TERM_OUTPUTS` surface `user_visible_output, module_api, boot_protocol`
- `HUNK-0010` `grub-core/loader/i386/linux.c` old `517-524` new `517-524` symbol `grub_linux_boot, cl_offset, grub_size_t, linux_params, hdr, setup_sects, FOR_ACTIVE_TERM_OUTPUTS` surface `user_visible_output, module_api, boot_protocol`
- `HUNK-0011` `grub-core/loader/i386/linux.c` old `567-583` new `567-583` symbol `grub_linux_boot, ctx, params, hdr, cmd_line_ptr, real_mode_target, grub_dprintf` surface `user_visible_output, module_api, boot_protocol`
- `HUNK-0012` `grub-core/loader/i386/linux.c` old `596-637` new `596-637` symbol `grub_linux_boot, grub_le_to_cpu16, ctx, params, hdr, version, grub_dprintf` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0013` `grub-core/loader/i386/linux.c` old `641-647` new `641-647` symbol `grub_linux_boot, state, eip, ctx, params, hdr, grub_relocator64_efi_boot` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0014` `grub-core/loader/i386/linux.c` old `791-797` new `791-797` symbol `grub_cmd_linux, grub_memcpy, linux_params, hdr, setup_sects, lh, grub_error` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0015` `grub-core/loader/i386/linux.c` old `805-866` new `805-866` symbol `grub_cmd_linux, linux_params, hdr, code32_start, prot_mode_target, lh, grub_memcpy` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0016` `grub-core/loader/i386/linux.c` old `999-1005` new `999-1005` symbol `grub_cmd_linux, linux_params, hdr, loadflags, GRUB_LINUX_FLAG_QUIET, grub_free` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0017` `grub-core/loader/i386/linux.c` old `1074-1082` new `1074-1082` symbol `grub_cmd_initrd, grub_le_to_cpu16, linux_params, hdr, version, addr_max, grub_error` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0018` `grub-core/loader/i386/linux.c` old `1139-1147` new `1139-1147` symbol `grub_cmd_initrd, linux_params, hdr, ramdisk_image, initrd_mem_target, ramdisk_size, grub_dprintf` surface `cli_options, user_visible_output, cli, module_api, boot_protocol, cli_commands`
- `HUNK-0019` `include/grub/i386/linux.h` old `51-56` new `51-59` symbol `Number, of, edd_info, structs, starting, at, Copyright` surface `public_headers, struct_layout, module_api, boot_protocol`
- `HUNK-0020` `include/grub/i386/linux.h` old `87-122` new `90-181` symbol `define, GRUB_E820_MAX_ENTRIES_ZEROPAGE, grub_screen_info, grub_uint8_t, orig_x, orig_y, Copyright` surface `public_headers, callbacks, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0021` `include/grub/i386/linux.h` old `124-140` new `183-188` symbol `linux_i386_kernel_header, define, LINUX_LOADER_ID_LILO, LINUX_LOADER_ID_LOADLIN, LINUX_LOADER_ID_BOOTSECT, LINUX_LOADER_ID_SYSLINUX, Copyright` surface `public_headers, callbacks, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0022` `include/grub/i386/linux.h` old `142-155` new `190-204` symbol `linux_i386_kernel_header, grub_uint8_t, ext_loader_ver, Extended, loader, version, Copyright` surface `public_headers, callbacks, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0023` `include/grub/i386/linux.h` old `158-299` new `207-368` symbol `linux_i386_kernel_header, grub_uint32_t, kernel_info_offset, grub_boot_e820_entry, grub_uint64_t, addr, Copyright` surface `public_headers, callbacks, cli_options, config_keys, cli, config, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0024` `include/grub/i386/linux.h` old `301-310` new `370-376` symbol `linux_kernel_params, grub_uint16_t, boot_flag, magic, number, grub_uint8_t, Copyright` surface `public_headers, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0025` `include/grub/i386/linux.h` old `312-317` new `378-394` symbol `linux_kernel_params, define, LINUX_LOADER_ID_LILO, LINUX_LOADER_ID_LOADLIN, LINUX_LOADER_ID_BOOTSECT, LINUX_LOADER_ID_SYSLINUX, Copyright` surface `public_headers, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0026` `include/grub/i386/linux.h` old `319-333` new `396-409` symbol `linux_kernel_params, grub_uint16_t, pad1, Unused, grub_uint32_t, initrd_addr_max, Copyright` surface `public_headers, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`
- `HUNK-0027` `include/grub/i386/linux.h` old `336-346` new `412-506` symbol `linux_kernel_params, GRUB_PACKED, Boot, parameters, Linux, based, Copyright` surface `public_headers, cli_options, cli, plugin_api, struct_layout, module_api, boot_protocol`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P057/analysis.json`
