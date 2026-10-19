# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/vim`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/_worktrees/patched`
- Patch ID: `5fdb44c438747d419a403110f3c2dd792f539497`
- Base ref: `9ed2c957fee9508c158bbc92b1404e93a2854197`
- Base commit: `9ed2c957fee9508c158bbc92b1404e93a2854197`
- Patch apply status: `applied`
- Profile: `vim`
- Effective profile: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 4711 |
| `patch_lines` | 135 |
| `raw_hunks` | 8 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 32 |
| `candidate_context_bytes` | 5182 |
| `candidates_json_bytes` | 16192 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/vim show 9ed2c957fee9508c158bbc92b1404e93a2854197:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis.json`.

## Candidate Hunks

- `HUNK-0006` `src/job.c` old `386-392` new `386-393` symbol `get_job_options, STRCMP, val, open, close, noclose, semsg` surface `callbacks, plugin_api, ex_commands, options, vimscript, ui_behavior`
- `HUNK-0007` `src/testdir/test_terminal.vim` old `774-779` new `774-795` symbol `Test_terminal_finish_open_close, Test, noclose, term_start, let, cmd` surface `tests, proc_sys_consumers, ex_commands, ui_behavior`
- `HUNK-0008` `src/version.c` old `759-764` new `759-766` symbol `init_longVersion` surface `ex_commands, ui_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/vim/pca-results/5fdb44/analysis.json`
