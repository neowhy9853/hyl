# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/git`
- Analysis repo: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/compatibility-testing`
- Patch ID: `0cd2255e64b4775520a6acbbb1868437fc26662d`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `write_midx_file_only / write_midx_file_compact`
- Target: `midx.h:132-145` `write_midx_file_only, write_midx_file_compact`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

