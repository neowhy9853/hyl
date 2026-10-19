# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/_worktrees/patched`
- Patch ID: `742a78609d0171d7e54c7b2ca0aa7eeaa9743ce0`
- Base ref: `742a78609d0171d7e54c7b2ca0aa7eeaa9743ce0~1`
- Base commit: `6d5f1f9ba0613e6d2170fde7dcfe75dce6930eac`
- Patch apply status: `applied`
- Profile: `rsyslog`
- Effective profile: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2538 |
| `patch_lines` | 67 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 1 |
| `churn` | 15 |
| `candidate_context_bytes` | 5626 |
| `candidates_json_bytes` | 19389 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/rsyslog show 6d5f1f9ba0613e6d2170fde7dcfe75dce6930eac:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tests/segmented-da-idle-dematerialize.sh` old `4-9` new `4-12` symbol `The, reset, probe, uses, a, second` surface `tests, user_visible_output, plugin_api, logging, persistence_state, daemon_interfaces`
- `HUNK-0002` `tests/segmented-da-idle-dematerialize.sh` old `52-58` new `55-61` symbol `template, queue, diskQueueIdleTimeout` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`
- `HUNK-0003` `tests/segmented-da-idle-dematerialize.sh` old `67-76` new `70-79` symbol `msleep` surface `tests, user_visible_output, plugin_api, logging, persistence_state, output_format, daemon_interfaces`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/rsyslog/pca-results/742a78/analysis.json`
