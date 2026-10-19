# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux/pca-results/09dc18/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux/pca-results/09dc18/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux/pca-results/09dc18/compatibility-testing`
- Patch ID: `09dc18894148381d3bfc550083b1236043870dce`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `rereg_user_mr (ibv_rereg_mr via uverbs)`
- Target: `drivers/infiniband/core/umem.c:326-344` `ib_umem_check_rereg`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

