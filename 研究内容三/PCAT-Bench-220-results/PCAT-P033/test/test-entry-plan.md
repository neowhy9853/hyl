# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/ruby`
- Analysis repo: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/compatibility-testing`
- Patch ID: `23c056c83cebad03f716c7af490c8bec9753ec90`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `API_SIGNATURE_CHANGE`
- API: `public_method` `Integer#bit_count`
- Target: `numeric.c:6656-6656` `Integer#bit_count`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

