# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/libsoup`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/_worktrees/patched`
- Patch ID: `04d0a30ca93c`
- Base ref: `HEAD`
- Base commit: `00858a9740fd67cbf3b6ee4ba6def1b681e3c9da`
- Patch apply status: `already_applied`
- Profile: `libsoup`
- Effective profile: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1085 |
| `patch_lines` | 29 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 7 |
| `candidate_context_bytes` | 4622 |
| `candidates_json_bytes` | 11949 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/libsoup show 00858a9740fd67cbf3b6ee4ba6def1b681e3c9da:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `libsoup/soup-message-headers.c` old `9-14` new `9-15` symbol `include, errno, h, Copyright` surface `config_keys, network_protocol, http_semantics`
- `HUNK-0002` `libsoup/soup-message-headers.c` old `296-307` new `297-310` symbol `soup_message_headers_append_common, errno, end, ERANGE, g_warning` surface `user_visible_output, network_protocol, http_semantics`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/libsoup/pca-results/04d0a3/analysis.json`
