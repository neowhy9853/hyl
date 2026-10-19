# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/glib`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/_worktrees/patched`
- Patch ID: `pca_glib_patch`
- Base ref: `HEAD`
- Base commit: `6a7a743f75aaaa08227a06f7bd0b569e6a871371`
- Patch apply status: `already_applied`
- Profile: `glib2`
- Effective profile: `/home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1244 |
| `patch_lines` | 31 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 1 |
| `churn` | 6 |
| `candidate_context_bytes` | 5961 |
| `candidates_json_bytes` | 14981 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/glib show 6a7a743f75aaaa08227a06f7bd0b569e6a871371:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `gio/tests/iptosmessage.c` old `26-32` new `26-32` symbol `defined, G_OS_WIN32, __APPLE__, __GNU__, _AIX, __sun__` surface `user_visible_output, daemon_control, gio_behavior`
- `HUNK-0002` `gio/tests/iptosmessage.c` old `118-123` new `118-125` symbol `test_ip_tos, elif, defined, __sun__, g_test_skip, IP_RECVTOS` surface `user_visible_output, daemon_control, gio_behavior`
- `HUNK-0003` `gio/tests/iptosmessage.c` old `144-149` new `146-153` symbol `test_ipv6_tclass, elif, defined, __sun__, g_test_skip, IPV6_RECVTCLASS` surface `gio_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/glib/pca-results/pca_gl/analysis.json`
