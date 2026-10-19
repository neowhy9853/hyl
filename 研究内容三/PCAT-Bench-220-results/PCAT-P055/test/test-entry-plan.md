# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnf`
- Analysis repo: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/compatibility-testing`
- Patch ID: `eabf33aeeb486ec671f3e3fd2120bccc396d2326`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ERROR_EXCEPTION_CHANGE`
- API: `exported_function` `Base.package_import_key / dnf.exceptions.InvalidInstalledGPGKeyError`
- Target: `dnf/base.py:2665-2671` `Base._get_key_for_package`
- Entry kind: `error_or_exception_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `error_exception_stability` / `error`
- Observation: errno/error code, exception type, message, and failure mode
- Input axes: each error path, invalid input, missing resource, permission, fault injection

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `medium`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `cli_command` `BaseCli.gpgsigcheck`
- Target: `dnf/cli/cli.py:367-375` `BaseCli.gpgsigcheck`
- Entry kind: `golden_output_probe`
- Preferred artifact: single command line or regression test in the project's CLI test framework
- Trigger surface: run the command/option combination that exercises the changed behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

