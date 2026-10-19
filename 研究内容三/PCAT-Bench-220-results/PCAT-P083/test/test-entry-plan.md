# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/libsoup`
- Analysis repo: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/compatibility-testing`
- Patch ID: `04d0a30ca93c`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `soup_message_headers_append_common`
- Target: `libsoup/soup-message-headers.c:297-310` `soup_message_headers_append_common`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

