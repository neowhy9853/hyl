# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnf`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/_worktrees/patched`
- Patch ID: `1f000c191f10d6ae7f114cf583f771789134b7d1`
- Base ref: `1f000c191f10d6ae7f114cf583f771789134b7d1~1`
- Base commit: `5a94d90fc1595b7ce0faeab190117e0778d392a5`
- Patch apply status: `applied`
- Profile: `dnf`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3281 |
| `patch_lines` | 65 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 23 |
| `candidate_context_bytes` | 5562 |
| `candidates_json_bytes` | 15832 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnf show 5a94d90fc1595b7ce0faeab190117e0778d392a5:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tests/test_cli.py` old `225-241` new `225-242` symbol `ConfigureTest, self, cli, configure, installroot, _installroot, test_conf_exists_in_installroot` surface `tests, python_cli, cli_options, config_keys, user_visible_output`
- `HUNK-0002` `tests/test_cli.py` old `248-254` new `249-256` symbol `ConfigureTest, conf_path, os, path, join, self, test_installroot_configurable` surface `tests, cli_options, config_keys, user_visible_output`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnf/pca-results/1f000c/analysis.json`
