# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/glib`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/_worktrees/patched`
- Patch ID: `12cf5c3ad1474ec61ff068b2faae68beb3196405`
- Base ref: `754dfebf844e7d9570404631a8a3d41a744b9909`
- Base commit: `754dfebf844e7d9570404631a8a3d41a744b9909`
- Patch apply status: `applied`
- Profile: `glib2`
- Effective profile: `/home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1206 |
| `patch_lines` | 33 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 3 |
| `candidate_context_bytes` | 1964 |
| `candidates_json_bytes` | 5730 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/glib show 754dfebf844e7d9570404631a8a3d41a744b9909:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `glib/gquark.h` old `46-52` new `46-52` symbol `g_quark_from_static_string, gchar, g_quark_to_string, GQuark, quark, G_GNUC_PURE, g_quark_from_string` surface `public_headers, user_visible_output`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/glib/pca-results/12cf5c/analysis.json`
