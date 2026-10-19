# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/vim`
- Analysis repo: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/compatibility-testing`
- Patch ID: `0001-patch`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `SIDE_EFFECT_CHANGE`
- API: `exported_function` `complete_check()`
- Target: `src/insexpand.c:6408-6417` `ins_compl_check_keys`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

