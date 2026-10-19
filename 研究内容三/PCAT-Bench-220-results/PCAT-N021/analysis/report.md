# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/vim`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/vim/pca-results/979602/_worktrees/patched`
- Patch ID: `0c5790c5bb15`
- Base ref: `a65741c8b38aa5d57f9e5e7f1a960a63a466efb5`
- Base commit: `a65741c8b38aa5d57f9e5e7f1a960a63a466efb5`
- Patch apply status: `applied`
- Profile: `vim`
- Effective profile: `/home/soong/pca_benchmark/_repos/vim/pca-results/979602/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/vim/pca-results/979602/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/vim/pca-results/979602`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 9
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5140 |
| `patch_lines` | 133 |
| `raw_hunks` | 9 |
| `candidate_hunks` | 9 |
| `changed_files` | 2 |
| `churn` | 62 |
| `candidate_context_bytes` | 12418 |
| `candidates_json_bytes` | 41297 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/vim/pca-results/979602/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/vim show a65741c8b38aa5d57f9e5e7f1a960a63a466efb5:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/979602/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/vim/pca-results/979602/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/optionstr.c` old `1131-1136` new `1131-1146` symbol `did_set_ambiwidth, completing_value_for_subopt, optexpand_T, args, name_suffix, char_u, check_chars_options` surface `ex_commands, options, ui_behavior`
- `HUNK-0002` `src/optionstr.c` old `2204-2213` new `2214-2220` symbol `expand_set_diffopt, completing_value_for_subopt, args, algorithm, Within, we` surface `cli_options, ex_commands, options, ui_behavior`
- `HUNK-0003` `src/optionstr.c` old `2216-2225` new `2223-2229` symbol `expand_set_diffopt, completing_value_for_subopt, args, inline, Within, we, expand_set_opt_string` surface `cli_options, ex_commands, options, ui_behavior`
- `HUNK-0004` `src/optionstr.c` old `3508-3527` new `3512-3520` symbol `expand_set_popupoption, completing_value_for_subopt, args, close, resize, shadow` surface `ex_commands, options, ui_behavior`
- `HUNK-0005` `src/optionstr.c` old `3530-3536` new `3523-3529` symbol `expand_set_popupoption, completing_value_for_subopt, args, border, is_border, expand_set_opt_string` surface `ex_commands, options, ui_behavior`
- `HUNK-0006` `src/optionstr.c` old `3541-3549` new `3534-3540` symbol `expand_set_popupoption, completing_value_for_subopt, args, align, align_len, STRLEN, expand_set_opt_string` surface `ex_commands, options, ui_behavior`
- `HUNK-0007` `src/optionstr.c` old `3552-3567` new `3543-3550` symbol `expand_set_popupoption, completing_value_for_subopt, args, highlight, borderhighlight, highlight_len, expand_set_opt_string` surface `ex_commands, options, ui_behavior`
- `HUNK-0008` `src/optionstr.c` old `4042-4051` new `4025-4031` symbol `expand_set_tabpanelopt, completing_value_for_subopt, args, align, Within, we` surface `ex_commands, options, ui_behavior`
- `HUNK-0009` `src/version.c` old `759-764` new `759-766` symbol `init_longVersion` surface `ex_commands, ui_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/vim/pca-results/979602/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/vim/pca-results/979602/analysis.json`
