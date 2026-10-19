# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/vim`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/_worktrees/patched`
- Patch ID: `4692bb7af4dd`
- Base ref: `6f02e5cd7c27fc098d0b8dfec99542c7663a807e`
- Base commit: `6f02e5cd7c27fc098d0b8dfec99542c7663a807e`
- Patch apply status: `applied`
- Profile: `vim`
- Effective profile: `/home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3330 |
| `patch_lines` | 104 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 56 |
| `candidate_context_bytes` | 5975 |
| `candidates_json_bytes` | 16533 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/vim show 6f02e5cd7c27fc098d0b8dfec99542c7663a807e:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/analysis.json`.

## Candidate Hunks

- `HUNK-0003` `src/move.c` old `1560-1565` new `1560-1575` symbol `textpos2screenpos, ifdef, FEAT_RIGHTLEFT, wp, w_p_rl, row, getvcol` surface `ex_commands, vimscript, ui_behavior`
- `HUNK-0004` `src/testdir/test_cursor_func.vim` old `216-221` new `216-259` symbol `Test_screenpos, func, Test_screenpos_rightleft, CheckFeature, rightleft, rightbelow` surface `tests, ex_commands, options, ui_behavior`
- `HUNK-0005` `src/version.c` old `759-764` new `759-766` symbol `init_longVersion` surface `ex_commands, ui_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/vim/pca-results/dcd5b5/analysis.json`
