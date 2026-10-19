# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P051/compatibility-testing`
- Patch ID: `324f7af5655a48841a079ac761fedef2ab3d1180`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `soup_session_send_message / soup_session_queue_message`
- Target: `libsoup/soup-session.c:845-853` `redirect_handler`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

