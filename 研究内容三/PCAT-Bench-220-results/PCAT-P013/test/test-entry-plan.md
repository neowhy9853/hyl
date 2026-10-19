# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/cpython`
- Analysis repo: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P013/compatibility-testing`
- Patch ID: `07ae6f133ad7a4e7ed506f6a511809b1fc3d1465`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `RETURN_CONTRACT_CHANGE`
- API: `exported_function` `sysconfig.parse_config_h`
- Target: `Lib/sysconfig/__init__.py:437-453` `parse_config_h`
- Entry kind: `return_value_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `return_contract_stability` / `exit_code`
- Observation: return value, exit status, output value, and ownership convention
- Input axes: success, failure, boundary, null result, partial result

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

