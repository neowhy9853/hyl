# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Analysis repo: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/ef191c/compatibility-testing`
- Patch ID: `ef191c4`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `low`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `cli_parse_del_map`
- Target: `src/map.c:998-1009` `cli_parse_del_map`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

