# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/openldap`
- Analysis repo: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/compatibility-testing`
- Patch ID: `fbf682a6c684db5e0b6928b511f8fc57d6c8eb7c`
- Task count: 2

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `CONFIG_CLI_BEHAVIOR_CHANGE`
- API: `config_key` `slapd.conf / cn=config ACL syntax`
- Target: `servers/slapd/aclparse.c:1691-1741` `parse_acl`
- Entry kind: `config_cli_precedence_matrix`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `config_cli_behavior_stability` / `exact`
- Observation: acceptance, default, precedence, exit status, output, and resulting state
- Input axes: default, explicit setting, legacy alias, invalid value, CLI/config/env precedence

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0004 / PCA-0004

- Priority: `high`
- Type: `INPUT_CONTRACT_CHANGE`
- API: `exported_function` `slap_acl_get ACL evaluation`
- Target: `servers/slapd/acl.c:545-564` `slap_acl_get`
- Entry kind: `input_boundary_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `backward_input_acceptance` / `acceptance`
- Observation: accept/reject result at old and new validation boundaries
- Input axes: old-valid, old-invalid, exact boundary, null/empty, maximum

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

