# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/openldap`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/_worktrees/patched`
- Patch ID: `pca_openldap_60458c`
- Base ref: `HEAD`
- Base commit: `595e7ea6f36d5352af5a60eccef64c5cb3357fb2`
- Patch apply status: `already_applied`
- Profile: `openldap`
- Effective profile: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 4
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3301 |
| `patch_lines` | 81 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 4 |
| `changed_files` | 3 |
| `churn` | 30 |
| `candidate_context_bytes` | 9070 |
| `candidates_json_bytes` | 25196 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/openldap show 595e7ea6f36d5352af5a60eccef64c5cb3357fb2:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `servers/slapd/back-mdb/back-mdb.h` old `121-126` new `121-128` symbol `mdb_info, mi_pagesize` surface `public_headers, persistence_state, libldap_api, protocol_behavior, config_schema`
- `HUNK-0003` `servers/slapd/back-mdb/config.c` old `71-76` new `71-82` symbol `dbpagesize, size, ARG_UINT, ARG_OFFSET, offsetof, mdb_info` surface `config_keys, persistence_state, protocol_behavior, config_schema`
- `HUNK-0004` `servers/slapd/back-mdb/config.c` old `153-159` new `159-165` symbol `olcDbMultival, olcDbPageSize` surface `config_keys, persistence_state, protocol_behavior, config_schema`
- `HUNK-0005` `servers/slapd/back-mdb/init.c` old `126-131` new `126-142` symbol `mdb_db_open, mdb, mi_pagesize, rc, mdb_env_set_pagesize, mi_dbenv, Debug, LDAP_XSTRING` surface `user_visible_output, persistence_state, protocol_behavior, config_schema`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/openldap/pca-results/pca_op/analysis.json`
