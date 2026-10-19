# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P052/compatibility-testing`
- Patch ID: `becb3a0ab8aa986f829efb77a52d53e75419c413`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `redirect_handler`
- Target: `libsoup/soup-session.c:890-890` `redirect_handler`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

