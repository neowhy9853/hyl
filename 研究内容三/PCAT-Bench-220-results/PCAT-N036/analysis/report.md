# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/_worktrees/patched`
- Patch ID: `4c3e1e4e775ed8b70d8d64845f95fb245d348a02`
- Base ref: `2dd6a1a155f4efe35606fe01734a55708b91a3c7`
- Base commit: `2dd6a1a155f4efe35606fe01734a55708b91a3c7`
- Patch apply status: `applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5637 |
| `patch_lines` | 173 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 3 |
| `churn` | 139 |
| `candidate_context_bytes` | 5221 |
| `candidates_json_bytes` | 18357 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show 2dd6a1a155f4efe35606fe01734a55708b91a3c7:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/libnmc-base/tests/meson.build` old `0--1` new `1-26` symbol `SPDX, License, Identifier, LGPL, or, later` surface `user_visible_output, logging, nmcli`
- `HUNK-0002` `src/libnmc-base/tests/test-client-utils.c` old `0--1` new `1-112` symbol `SPDX, License, Identifier, LGPL, or, later, Copyright` surface `nmcli`
- `HUNK-0003` `src/meson.build` old `123-128` new `123-129` symbol `subdir, libnmc, base, tests` surface `nmcli`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/4c3e1e/analysis.json`
