# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/rsyslog`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/_worktrees/patched`
- Patch ID: `8ea0d9751`
- Base ref: `f673f66868131aa9d5a37d7544256644c12171f5`
- Base commit: `f673f66868131aa9d5a37d7544256644c12171f5`
- Patch apply status: `applied`
- Profile: `rsyslog`
- Effective profile: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 747 |
| `patch_lines` | 14 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 3 |
| `candidate_context_bytes` | 1302 |
| `candidates_json_bytes` | 7022 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/rsyslog show f673f66868131aa9d5a37d7544256644c12171f5:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `tests/imtcp-stream-always-zlib-fragmented-ratio.sh` old `35-41` new `35-42` symbol `join, Solaris, older, Python, accepts, the` surface `tests, cli_options, cli, plugin_api, logging, daemon_control, output_format, daemon_interfaces`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/rsyslog/pca-results/pca-pa/analysis.json`
