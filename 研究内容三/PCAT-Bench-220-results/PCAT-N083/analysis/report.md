# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/httpd`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/_worktrees/patched`
- Patch ID: `27ab5180290aee410c9e0424d4a2dee2a9f3450a`
- Base ref: `62147ea0da345e6a3c35b3c34f8f7a88829d6995`
- Base commit: `62147ea0da345e6a3c35b3c34f8f7a88829d6995`
- Patch apply status: `already_applied`
- Profile: `httpd`
- Effective profile: `/home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 890 |
| `patch_lines` | 27 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 3 |
| `candidate_context_bytes` | 1695 |
| `candidates_json_bytes` | 6077 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/httpd show 62147ea0da345e6a3c35b3c34f8f7a88829d6995:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `modules/filters/sed1.c` old `433-439` new `433-439` symbol `sed_eval_buffer, n, eval_errf` surface `cli_options, user_visible_output, cli, plugin_api, module_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/httpd/pca-results/27ab51/analysis.json`
