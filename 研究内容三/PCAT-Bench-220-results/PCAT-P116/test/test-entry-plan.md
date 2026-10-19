# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P056/compatibility-testing`
- Patch ID: `8e14f88e25192080ac237cb64be452c592c1e4fe`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `SoupSession message lifecycle (queue_message, message_finished, connection_started_request)`
- Target: `libsoup/soup-session.c:1065-1094` `queue_message`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

