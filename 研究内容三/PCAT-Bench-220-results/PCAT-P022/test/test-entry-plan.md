# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/vim`
- Analysis repo: `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/e397c8/compatibility-testing`
- Patch ID: `e397c8`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `exported_function` `dict_extend_func / extend() / extendnew()`
- Target: `src/dict.c:1335-1340` `dict_extend_func`
- Entry kind: `return_value_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `exported_function` `list_extend_func / extend() / extendnew()`
- Target: `src/list.c:3014-3020` `list_extend_func`
- Entry kind: `return_value_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

