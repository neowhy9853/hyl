# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/3a052d/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/3a052d/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/3a052d/compatibility-testing`
- Patch ID: `3a052d55fbfca49d8d435cdd2110fb2667594c61`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `SIDE_EFFECT_CHANGE`
- API: `daemon_handler` `tcp_request`
- Target: `src/forward.c:2570-2576` `tcp_request`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

