# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/git`
- Analysis repo: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/compatibility-testing`
- Patch ID: `pca_patch_e61190`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `git-gui usage string`
- Target: `git-gui.sh:3130-3130` `usage`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

