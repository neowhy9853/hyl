# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/compatibility-testing`
- Patch ID: `8839fe2a8962`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `dhcp6_maybe_relay`
- Target: `src/rfc3315.c:113-130` `dhcp6_maybe_relay`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `low`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `dhcp6_maybe_relay`
- Target: `src/rfc3315.c:241-248` `dhcp6_maybe_relay`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

