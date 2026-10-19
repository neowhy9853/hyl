# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/openldap`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/_worktrees/patched`
- Patch ID: `fbf682a6c684db5e0b6928b511f8fc57d6c8eb7c`
- Base ref: `fbf682a6c684db5e0b6928b511f8fc57d6c8eb7c^`
- Base commit: `bb64b0b55b5aa77fae077209f26b015f6a86275f`
- Patch apply status: `applied`
- Profile: `openldap`
- Effective profile: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 5
- Candidate hunks: 8
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 8617 |
| `patch_lines` | 257 |
| `raw_hunks` | 10 |
| `candidate_hunks` | 8 |
| `changed_files` | 5 |
| `churn` | 145 |
| `candidate_context_bytes` | 20534 |
| `candidates_json_bytes` | 53844 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/openldap show bb64b0b55b5aa77fae077209f26b015f6a86275f:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis.json`.

## Candidate Hunks

- `HUNK-0003` `servers/slapd/acl.c` old `545-550` new `545-564` symbol `slap_acl_get, a, acl_op, slap_restrictop_t, restrictop, SLAP_OP2RESTRICT, assert` surface `persistence_state, libldap_api, protocol_behavior, config_schema`
- `HUNK-0004` `servers/slapd/aclparse.c` old `1691-1696` new `1691-1741` symbol `parse_acl, strcasecmp, left, control, oid, oidm_find, snprintf, Debug` surface `user_visible_output, libldap_api, protocol_behavior, config_schema`
- `HUNK-0005` `servers/slapd/aclparse.c` old `2196-2204` new `2241-2251` symbol `acl_usage, t, op, opspec, control, oid` surface `protocol_behavior, config_schema`
- `HUNK-0006` `servers/slapd/aclparse.c` old `2394-2399` new `2441-2453` symbol `acl_free, BER_BVISNULL, a, acl_controlval, free, bv_val, ber_memfree` surface `libldap_api, protocol_behavior, config_schema`
- `HUNK-0007` `servers/slapd/aclparse.c` old `2815-2820` new `2869-2888` symbol `berval, BER_BVISNULL, a, acl_opval, to, ptr, ch_free` surface `user_visible_output, protocol_behavior, config_schema`
- `HUNK-0008` `servers/slapd/slap.h` old `1612-1617` new `1612-1624` symbol `AccessControl, slap_restrictop_t, acl_op, berval, acl_oid, acl_control, int` surface `public_headers, config_keys, network_protocol, persistence_state, protocol_behavior, config_schema`
- `HUNK-0009` `tests/data/slapd-acl.conf` old `131-136` new `131-142` symbol `access, to, dn, subtree, ou, Add` surface `tests, config_files, config_keys, config, persistence_state, protocol_behavior`
- `HUNK-0010` `tests/scripts/test006-acls` old `613-618` new `613-639` symbol `LDAPMODIFY, D, BABSDN, H, URI1, w` surface `tests, tools`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## Agent Adjudication Requirements

- This report is deterministic evidence, not the final compatibility decision.
- Start from analysis-context.json. It is the bounded context for agent adjudication and includes focused source excerpts.
- Do not reopen large source files to locate a changed function already present in analysis-context.json.
- Do not scan repo roots, patch-list directories, output directories, or profile trees.
- Final findings must include only confirmed compatibility changes.
- Every finding must include code line locations and at least one evidence snippet.
- In heavy mode, analyze each shard independently, then aggregate shard results with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/openldap/pca-results/fbf682/analysis.json`
