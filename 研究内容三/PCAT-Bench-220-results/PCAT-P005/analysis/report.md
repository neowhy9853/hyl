# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/_worktrees/patched`
- Patch ID: `42d960748efa79a31e72cc36d983aca244dc167e`
- Base ref: `558057cf4f43ea3b28c5e0b1b2250cab362f1a6a`
- Base commit: `558057cf4f43ea3b28c5e0b1b2250cab362f1a6a`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 7
- Candidate hunks: 14
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 11043 |
| `patch_lines` | 301 |
| `raw_hunks` | 14 |
| `candidate_hunks` | 14 |
| `changed_files` | 7 |
| `churn` | 105 |
| `candidate_context_bytes` | 22616 |
| `candidates_json_bytes` | 59556 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/42d960/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 558057cf4f43ea3b28c5e0b1b2250cab362f1a6a:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `line-log.c` old `13-19` new `13-18` symbol `include, log, tree, h` surface `unknown`
- `HUNK-0002` `line-log.c` old `1004-1032` new `1003-1020` symbol `line_log_data, line_log_queue_pairs, rev_info, rev, commit, range, free` surface `user_visible_output, logging`
- `HUNK-0003` `line-log.h` old `46-52` new `46-52` symbol `rev_info, line_log_queue_pairs, rev, commit, line_log_print, line_log_process_ranges_arbitrary_commit` surface `user_visible_output, logging, public_library_headers`
- `HUNK-0004` `log-tree.c` old `1105-1110` new `1105-1116` symbol `rev_info, opt, line_level_traverse, line_log_queue_pairs, commit, log_tree_diff_flush, log_tree_diff` surface `user_visible_output, logging`
- `HUNK-0005` `log-tree.c` old `1179-1188` new `1185-1190` symbol `rev_info, NEEDSWORK, no, restoring, of, no_free, log_tree_commit` surface `user_visible_output, logging, commands`
- `HUNK-0006` `revision.c` old `3179-3186` new `3179-3188` symbol `rev_info, revs, full_diff, diffopt, output_format, DIFF_FORMAT_PATCH, die` surface `user_visible_output, logging`
- `HUNK-0007` `t/t4211-line-log.sh` old `368-374` new `368-373` symbol `unknown` surface `tests`
- `HUNK-0008` `t/t4211-line-log.sh` old `377-383` new `376-381` symbol `unknown` surface `tests`
- `HUNK-0009` `t/t4211-line-log.sh` old `433-439` new `431-436` symbol `Z` surface `tests`
- `HUNK-0010` `t/t4211-line-log.sh` old `445-451` new `442-447` symbol `ZZ` surface `tests`
- `HUNK-0011` `t/t4211-line-log.sh` old `494-516` new `490-506` symbol `test_expect_success, L, G, should, filter, commits` surface `tests`
- `HUNK-0012` `t/t4211-line-log.sh` old `711-714` new `701-741` symbol `test_expect_success, L, with, diff, filter, M` surface `tests`
- `HUNK-0013` `t/t4211/sha1/expect.parallel-change-f-to-main` old `5-11` new `5-10` symbol `unknown` surface `tests`
- `HUNK-0014` `t/t4211/sha256/expect.parallel-change-f-to-main` old `5-11` new `5-10` symbol `unknown` surface `tests`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/42d960/analysis.json`
