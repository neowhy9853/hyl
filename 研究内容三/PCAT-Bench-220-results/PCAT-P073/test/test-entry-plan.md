# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/lvm2`
- Analysis repo: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P073/compatibility-testing`
- Patch ID: `48291d27ac20`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `vgchange`
- Target: `tools/vgchange.c:1114-1120` `vgchange`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

