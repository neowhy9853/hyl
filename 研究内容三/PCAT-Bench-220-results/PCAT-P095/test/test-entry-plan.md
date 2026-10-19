# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P035/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P035/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P035/compatibility-testing`
- Patch ID: `10981ef1378830f88ff1efba68a98c56a1a33d6f`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `go test (package list mode, non-verbose, non-JSON output)`
- Target: `src/cmd/go/internal/test/test.go:1736-1742` `func (r *runTestActor) Act`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

