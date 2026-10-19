# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Analysis repo: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/9c0f64/compatibility-testing`
- Patch ID: `9c0f64303f61a7ce5247831afe546146073046f3`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `ratelimitAddConfig`
- Target: `runtime/ratelimit.h:121-135` `ratelimitAddConfig`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `exported_function` `action_s / ratelimit_shared_s`
- Target: `runtime/action.h:97-130` `action_s`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

