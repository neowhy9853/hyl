# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/libsoup`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/_worktrees/patched`
- Patch ID: `b68a14fc`
- Base ref: `b68a14fcf0ef15b6018d3aa849638ce606c9cc96^`
- Base commit: `f3eb7f5ffd6dd6001354ed9006fc4615dcae084d`
- Patch apply status: `applied`
- Profile: `libsoup`
- Effective profile: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 772 |
| `patch_lines` | 12 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 1 |
| `candidate_context_bytes` | 4205 |
| `candidates_json_bytes` | 10623 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/libsoup show f3eb7f5ffd6dd6001354ed9006fc4615dcae084d:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `libsoup/soup-connection.h` old `50-56` new `50-55` symbol `soup_connection_disconnect, GUri, soup_connection_get_remote_uri, SoupConnection, conn` surface `public_headers, callbacks, user_visible_output, plugin_api, network_protocol, daemon_control, persistence_state, http_semantics`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/libsoup/pca-results/b68a14/analysis.json`
