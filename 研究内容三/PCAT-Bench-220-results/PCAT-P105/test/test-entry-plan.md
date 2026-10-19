# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P045/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux-stable`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P045/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P045/compatibility-testing`
- Patch ID: `8a3cd890fd2a7d016a821a1c9dfd8a84d45ad320`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `__ksmbd_override_fsids`
- Target: `fs/smb/server/smb_common.c:761-778` `__ksmbd_override_fsids`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

