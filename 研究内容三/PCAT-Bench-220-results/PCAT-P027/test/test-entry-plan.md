# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/git`
- Analysis repo: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/git/pca-results/e21647/compatibility-testing`
- Patch ID: `e2164742`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `cli_option` `add_negotiation_tips/--negotiation-restrict`
- Target: `builtin/fetch.c:1535-1563` `add_negotiation_tips`
- Entry kind: `input_boundary_harness`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `negotiate_using_fetch`
- Target: `fetch-pack.h:94-101` `negotiate_using_fetch`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

