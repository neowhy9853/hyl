# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/glib`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/_worktrees/patched`
- Patch ID: `5f3b17`
- Base ref: `HEAD`
- Base commit: `6a7a743f75aaaa08227a06f7bd0b569e6a871371`
- Patch apply status: `already_applied`
- Profile: `glib2`
- Effective profile: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 5
- Candidate hunks: 6
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2900 |
| `patch_lines` | 83 |
| `raw_hunks` | 6 |
| `candidate_hunks` | 6 |
| `changed_files` | 5 |
| `churn` | 23 |
| `candidate_context_bytes` | 11417 |
| `candidates_json_bytes` | 25452 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/glib show 6a7a743f75aaaa08227a06f7bd0b569e6a871371:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `gio/glocalfileinfo.c` old `1840-1845` new `1840-1849` symbol `get_icon_name, g_strcmp0, path, g_get_user_special_dir, G_USER_DIRECTORY_PROJECTS, name` surface `gio_behavior`
- `HUNK-0002` `glib/gosxutils.m` old `43-49` new `43-49` symbol `find_folder, load_user_special_dirs_macos, gchar, table` surface `config_keys`
- `HUNK-0003` `glib/gosxutils.m` old `53-56` new `53-57` symbol `load_user_special_dirs_macos, table, G_USER_DIRECTORY_PROJECTS, find_folder, NSDocumentDirectory` surface `unknown`
- `HUNK-0004` `glib/gutils.c` old `2243-2248` new `2243-2250` symbol `load_user_special_dirs_unlocked, g_user_special_dirs, G_USER_DIRECTORY_PROJECTS, get_special_folder, FOLDERID_Documents` surface `unknown`
- `HUNK-0005` `glib/gutils.h` old `248-253` new `248-262` symbol `G_USER_DIRECTORY_PROJECTS, The, user, s, Projects, directory, g_get_user_runtime_dir` surface `public_headers, user_visible_output`
- `HUNK-0006` `glib/gutilsprivate.c` old `89-94` new `89-99` symbol `load_user_special_dirs_from_string, strncmp, p, XDG_PROJECTS_DIR, strlen, directory` surface `unknown`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/glib/pca-results/5f3b17/analysis.json`
