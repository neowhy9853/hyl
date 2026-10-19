# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/glib`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/_worktrees/patched`
- Patch ID: `c9da977c`
- Base ref: `HEAD`
- Base commit: `6a7a743f75aaaa08227a06f7bd0b569e6a871371`
- Patch apply status: `already_applied`
- Profile: `glib2`
- Effective profile: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2770 |
| `patch_lines` | 64 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 2 |
| `churn` | 35 |
| `candidate_context_bytes` | 8384 |
| `candidates_json_bytes` | 20301 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/glib show 6a7a743f75aaaa08227a06f7bd0b569e6a871371:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `gio/gdbusintrospection.c` old `1266-1272` new `1266-1272` symbol `parser_start_element, stack, next, NULL, strcmp, data` surface `user_visible_output, daemon_control, gio_behavior`
- `HUNK-0002` `gio/tests/gdbus-introspection.c` old `300-305` new `300-337` symbol `test_extra_data, test_invalid, xml, GMarkupError, expected_error_code, vectors, g_dbus_node_info_unref` surface `user_visible_output, daemon_control, gio_behavior`
- `HUNK-0003` `gio/tests/gdbus-introspection.c` old `317-322` new `349-355` symbol `main, g_test_add_func, gdbus, introspection, invalid, test_invalid` surface `user_visible_output, daemon_control, gio_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/glib/pca-results/c9da97/analysis.json`
