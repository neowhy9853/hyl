# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P040/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P040/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P040/compatibility-testing`
- Patch ID: `ba760c38b38b4fc5377f30bea492deba5f17df60`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `daemon_handler` `MGMT_OP_ADD_EXT_ADV_DATA`
- Target: `net/bluetooth/mgmt.c:9147-9149` `add_ext_adv_data`
- Entry kind: `input_boundary_harness`
- Preferred artifact: kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists
- Trigger surface: drive the externally reachable subsystem path that reaches the changed line
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

