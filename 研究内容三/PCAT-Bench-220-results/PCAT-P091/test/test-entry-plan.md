# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P031/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P031/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/fn_rerun_20260724_155026/PCIA-P031/compatibility-testing`
- Patch ID: `efbecbbb465c99ed608b06d72fa1982122382d00`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `SIDE_EFFECT_CHANGE`
- API: `struct_type` `ConnectionState.LocalCertificate`
- Target: `src/crypto/tls/common.go:325-335` `ConnectionState`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

