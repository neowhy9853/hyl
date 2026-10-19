# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/compatibility-testing`
- Patch ID: `c090f1d17b280c98630914334d341a2fa3318117`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `RESOURCE_LIFETIME_CHANGE`
- API: `exported_function` `swap_to_tcp`
- Target: `src/dnsmasq.c:2262-2273` `swap_to_tcp`
- Entry kind: `resource_lifecycle_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `resource_lifetime_stability` / `exact`
- Observation: allocation/free, fd, lock, refcount, sanitizer, and cleanup manifest
- Input axes: normal cleanup, error cleanup, repetition, concurrency, cancellation

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `medium`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `sig_handler`
- Target: `src/dnsmasq.c:1335-1376` `sig_handler`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

