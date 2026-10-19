# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/git`
- Analysis repo: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/git/pca-results/3fbef1/compatibility-testing`
- Patch ID: `3fbef193c7e49e8edb5a4421c465df67de944da6`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `cli_command` `git gui browser|blame argument parsing`
- Target: `git-gui.sh:2999-3103` `selected_paths`
- Entry kind: `input_boundary_harness`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

