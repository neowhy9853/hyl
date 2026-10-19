# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/openldap`
- Analysis repo: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/f6ae8e/compatibility-testing`
- Patch ID: `f6ae8ef451f38e3f2f3ec6fc43cc8806ecfe125a`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `config_key` `lload_features / LLOAD_FEATURES_DEFAULT`
- Target: `servers/lloadd/lload.h:184-193` `LLOAD_FEATURES_DEFAULT`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

