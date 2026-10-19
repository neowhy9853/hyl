# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Analysis repo: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/98b1fd/compatibility-testing`
- Patch ID: `98b1fd4ff9a719f34131fa04cbd93f92c0c362f7`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `daemon_handler` `h3_rcv_buf`
- Target: `src/h3.c:2074-2079` `h3_rcv_buf`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

