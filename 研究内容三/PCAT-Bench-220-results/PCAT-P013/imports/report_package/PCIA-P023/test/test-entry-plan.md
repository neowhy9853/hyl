# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P023/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P023/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P023/compatibility-testing`
- Patch ID: `07ae6f133ad7a4e7ed506f6a511809b1fc3d1465`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `exported_function` `parse_config_h / get_config_vars / get_config_var`
- Target: `Lib/sysconfig/__init__.py:437-453` `parse_config_h`
- Entry kind: `golden_output_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

