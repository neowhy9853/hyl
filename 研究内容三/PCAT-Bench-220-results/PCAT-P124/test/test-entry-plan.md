# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P064/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repos/grub2`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P064/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P064/compatibility-testing`
- Patch ID: `531750f7bfc475332b2046dd516bab582ba7decf`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `PERFORMANCE_RESOURCE_SEMANTIC_CHANGE`
- API: `exported_function` `grub_get_tsc`
- Target: `include/grub/i386/tsc.h:47-57` `grub_get_tsc`
- Entry kind: `timeout_retry_resource_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `performance_resource_semantics` / `numeric_tolerance`
- Observation: JSON numeric measurements for timeout, retries, limits, ordering, and resource use
- Input axes: idle, nominal load, boundary limit, timeout, retry, contention

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

