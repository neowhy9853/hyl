# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P048/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P048/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P048/compatibility-testing`
- Patch ID: `7f9c7c8731821149ff42971fad18e2a9abbb4c10`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `enum_type` `SoupKnownStatusCode`
- Target: `libsoup/soup-status.h:97-97` `SoupKnownStatusCode`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

