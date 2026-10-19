# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/cpython`
- Analysis repo: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/compatibility-testing`
- Patch ID: `1d4e965829eef4cdb089a984fda21ca465a1f534`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `public_method` `sys.lazy_modules`
- Target: `Python/import.c:275-281` `_PyImport_InitLazyModules`
- Entry kind: `api_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, and limitations.

