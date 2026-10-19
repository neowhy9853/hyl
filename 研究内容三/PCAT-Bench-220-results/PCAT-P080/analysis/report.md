# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/openldap`
- Patched analysis worktree: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/_worktrees/patched`
- Patch ID: `11ebc033d258da3b3f76b1be77bac750768ef2ae`
- Base ref: `f8ec414d7dad8fe5f235c4df2ddf98e111108adc`
- Base commit: `f8ec414d7dad8fe5f235c4df2ddf98e111108adc`
- Patch apply status: `applied`
- Profile: `openldap`
- Effective profile: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P080`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1423 |
| `patch_lines` | 43 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 2 |
| `churn` | 15 |
| `candidate_context_bytes` | 4886 |
| `candidates_json_bytes` | 11820 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/openldap show f8ec414d7dad8fe5f235c4df2ddf98e111108adc:<path>`.
- Rebuild worktree: `/usr/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/usr/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `libraries/liblmdb/lmdb.h` old `1177-1182` new `1177-1190` symbol `mdb_txn_env, brief, Retrieve, the, transaction, s, mdb_txn_begin` surface `public_headers, user_visible_output, network_protocol, persistence_state`
- `HUNK-0002` `libraries/liblmdb/mdb.c` old `3642-3647` new `3642-3654` symbol `mdb_txn_id, mdb_txn_flags, MDB_txn, txn, flags, EINVAL` surface `unknown`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/output_dir_rerun/PCAT-P080/analysis.json`
