# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/vim`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/_worktrees/patched`
- Patch ID: `0001-patch`
- Base ref: `27865e206ce6bba7cd5fe5ba379ce245e447bc92`
- Base commit: `27865e206ce6bba7cd5fe5ba379ce245e447bc92`
- Patch apply status: `applied`
- Profile: `vim`
- Effective profile: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p`
- Analysis mode: `normal`
- Mode reason: user requested normal mode; no hard threshold exceeded
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2442 |
| `patch_lines` | 85 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 37 |
| `candidate_context_bytes` | 4288 |
| `candidates_json_bytes` | 14557 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/vim show 27865e206ce6bba7cd5fe5ba379ce245e447bc92:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/insexpand.c` old `6408-6416` new `6408-6417` symbol `ins_compl_check_keys, Typed, keys, that, get, mapped` surface `ex_commands, vimscript, ui_behavior`
- `HUNK-0002` `src/testdir/test_ins_complete.vim` old `6535-6538` new `6535-6566` symbol `Test_call_complete_while_filtering, func, Test_complete_check_mapped_typed_key, SlowComplete, findstart, base` surface `tests, proc_sys_consumers, ex_commands, ui_behavior`
- `HUNK-0003` `src/version.c` old `759-764` new `759-766` symbol `init_longVersion` surface `ex_commands, ui_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/vim/pca-results/0001-p/analysis.json`
