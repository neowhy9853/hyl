# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/_worktrees/patched`
- Patch ID: `0cd2255e64b4775520a6acbbb1868437fc26662d`
- Base ref: `HEAD`
- Base commit: `ea97ad8d017de0c9037451a78008a0fd60abea0c`
- Patch apply status: `applied_3way`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 5
- Candidate hunks: 16
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 15057 |
| `patch_lines` | 418 |
| `raw_hunks` | 19 |
| `candidate_hunks` | 16 |
| `changed_files` | 5 |
| `churn` | 188 |
| `candidate_context_bytes` | 35136 |
| `candidates_json_bytes` | 92417 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/0cd225/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show ea97ad8d017de0c9037451a78008a0fd60abea0c:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis.json`.

## Candidate Hunks

- `HUNK-0004` `builtin/multi-pack-index.c` old `16-26` new `16-28` symbol `refs, snapshot, path, no, write, chain` surface `cli_options, config_keys, config, commands`
- `HUNK-0005` `builtin/multi-pack-index.c` old `63-68` new `65-71` symbol `incremental_base` surface `cli_options, config, commands`
- `HUNK-0006` `builtin/multi-pack-index.c` old `151-156` new `154-161` symbol `cmd_multi_pack_index_write, OPT_STRING, base, opts, incremental_base, N_` surface `proc_sys_consumers, cli_options, config_keys, config, commands`
- `HUNK-0007` `builtin/multi-pack-index.c` old `190-195` new `195-207` symbol `cmd_multi_pack_index_write, opts, incremental_base, flags, MIDX_WRITE_NO_CHAIN, error, usage_with_options` surface `cli_options, config_keys, user_visible_output, config, commands`
- `HUNK-0008` `builtin/multi-pack-index.c` old `201-207` new `213-220` symbol `cmd_multi_pack_index_write, opts, refs_snapshot, incremental_base, flags, read_packs_from_stdin` surface `cli_options, config_keys, user_visible_output, config, commands`
- `HUNK-0009` `builtin/multi-pack-index.c` old `229-234` new `242-249` symbol `cmd_multi_pack_index_compact, OPT_STRING, base, opts, incremental_base, N_` surface `cli_options, config_keys, user_visible_output, config, commands`
- `HUNK-0010` `builtin/multi-pack-index.c` old `290-296` new `305-312` symbol `cmd_multi_pack_index_compact, ret, write_midx_file_compact, source, from_midx, to_midx, die` surface `cli_options, user_visible_output, config, commands`
- `HUNK-0011` `midx-write.c` old `1247-1252` new `1247-1253` symbol `write_midx_opts, incremental_base, hashcmp` surface `config_keys, config`
- `HUNK-0012` `midx-write.c` old `1330-1340` new `1331-1362` symbol `write_midx_opts, compacted, MIDX, will, share, the, warning` surface `user_visible_output`
- `HUNK-0013` `midx-write.c` old `1827-1833` new `1849-1856` symbol `write_midx_opts, refs_snapshot, flags, write_midx_file` surface `user_visible_output`
- `HUNK-0014` `midx-write.c` old `1842-1854` new `1865-1880` symbol `odb_source, refs_snapshot, incremental_base, flags, write_midx_file_only` surface `user_visible_output`
- `HUNK-0015` `midx-write.c` old `1858-1869` new `1884-1897` symbol `odb_source, incremental_base, write_midx_file_compact` surface `user_visible_output`
- `HUNK-0016` `midx.h` old `132-141` new `132-144` symbol `odb_source, refs_snapshot, incremental_base, flags, write_midx_file` surface `public_library_headers`
- `HUNK-0017` `t/t5334-incremental-multi-pack-index.sh` old `113-118` new `113-148` symbol `test_expect_success, write, MIDX, layer, with, base` surface `tests, config_keys`
- `HUNK-0018` `t/t5335-compact-multi-pack-index.sh` old `304-309` new `304-310` symbol `base, nth_line, midx_chain` surface `tests, cli_options, config_keys, cli`
- `HUNK-0019` `t/t5335-compact-multi-pack-index.sh` old `326-329` new `327-406` symbol `test_expect_success, MIDX, compaction, with, base, git` surface `tests, cli_options, config_keys, cli`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/0cd225/analysis.json`
