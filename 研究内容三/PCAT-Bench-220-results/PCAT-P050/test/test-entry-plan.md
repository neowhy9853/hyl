# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Analysis repo: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/900f55/compatibility-testing`
- Patch ID: `96cab112a257`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `SIDE_EFFECT_CHANGE`
- API: `daemon_handler` `send_ra`
- Target: `src/core/ndisc/nm-lndp-ndisc.c:532-540` `send_ra`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

