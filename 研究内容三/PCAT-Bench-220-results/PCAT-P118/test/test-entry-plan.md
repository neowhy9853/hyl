# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P058/compatibility-testing`
- Patch ID: `29ed28820a3bd8222d7b533e41ecd4809a2162f8`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `grub_cryptodisk_open`
- Target: `grub-core/disk/cryptodisk.c:702-708` `grub_cryptodisk_open`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `cli_command` `configure_ciphers / luks2_scan (search_uuid matching)`
- Target: `grub-core/disk/geli.c:305-311` `configure_ciphers`
- Entry kind: `input_boundary_harness`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

