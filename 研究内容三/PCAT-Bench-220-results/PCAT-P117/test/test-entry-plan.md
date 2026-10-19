# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P057/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P057/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P057/compatibility-testing`
- Patch ID: `204a6ddfb3bb456929e7c364e1e8d6ee1928b471`
- Task count: 5

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct linux_kernel_params`
- Target: `include/grub/i386/linux.h:190-506` `linux_kernel_params`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct grub_boot_e820_entry (原 grub_e820_mmap)`
- Target: `include/grub/i386/linux.h:207-212` `grub_boot_e820_entry`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct grub_screen_info (新增), struct grub_apm_bios_info (新增), struct grub_setup_header (新增) 等子结构体`
- Target: `include/grub/i386/linux.h:129-398` `grub_screen_info`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0004 / PCA-0004

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `struct linux_i386_kernel_header`
- Target: `include/grub/i386/linux.h:153-204` `linux_i386_kernel_header`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0005 / PCA-0005

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `grub_linux_setup_video`
- Target: `grub-core/loader/i386/linux.c:234-340` `grub_linux_setup_video`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

