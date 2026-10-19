# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnf`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/compatibility-testing`
- Patch ID: `de9c5c5b597bf97aa03145de129fb579b5a0e953`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `rpm2py_format`
- Target: `dnf/cli/commands/repoquery.py:68-74` `rpm2py_format`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

