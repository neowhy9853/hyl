# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/b61737/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/libxml2`
- Analysis repo: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/b61737/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/b61737/compatibility-testing`
- Patch ID: `b61737679e1f5ce2aaf19d075784a40bd5f4938a`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `cli_command` `parseInteger (CLI integer argument parser)`
- Target: `xmllint.c:2497-2500` `parseInteger`
- Entry kind: `input_boundary_harness`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

