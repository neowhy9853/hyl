# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Analysis repo: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/compatibility-testing`
- Patch ID: `7d5fbe7da380135a70ab7b7f3f117cc870207503`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `exported_function` `add_edns0_config / add_mac / add_dns_client`
- Target: `src/edns0.c:265-279` `edns0_needs_mac`
- Entry kind: `golden_output_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

