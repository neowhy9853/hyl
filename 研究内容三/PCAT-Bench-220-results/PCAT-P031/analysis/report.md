# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/_worktrees/patched`
- Patch ID: `pca-git-sideband-patch`
- Base ref: `31e8fcabd8a75b2c27cd4c98ea694c6836c29ad2^`
- Base commit: `9a2fb147f2c61d0cab52c883e7e26f5b7948e3ed`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1924 |
| `patch_lines` | 66 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 1 |
| `churn` | 22 |
| `candidate_context_bytes` | 8662 |
| `candidates_json_bytes` | 22750 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 9a2fb147f2c61d0cab52c883e7e26f5b7948e3ed:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `sideband.c` old `120-126` new `120-126` symbol `strbuf, define, ANSI_PREFIX, K, ANSI_SUFFIX, strbuf_add` surface `user_visible_output`
- `HUNK-0002` `sideband.c` old `129-143` new `129-146` symbol `demultiplex_sideband, prefix, suffix, isatty, is_terminal_dumb, ANSI_PREFIX` surface `user_visible_output, wire_protocol`
- `HUNK-0003` `sideband.c` old `171-178` new `174-180` symbol `demultiplex_sideband, strbuf_addf, scratch, s, len, n` surface `user_visible_output, wire_protocol`
- `HUNK-0004` `sideband.c` old `203-209` new `205-211` symbol `demultiplex_sideband, strbuf_addstr, scratch, prefix, DISPLAY_PREFIX, write` surface `user_visible_output`
- `HUNK-0005` `sideband.c` old `229-236` new `231-238` symbol `demultiplex_sideband, scratch, len, strbuf_addstr, prefix, DISPLAY_PREFIX, strbuf_reset` surface `user_visible_output, wire_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/pca-gi/analysis.json`
