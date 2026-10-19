# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/NetworkManager`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/_worktrees/patched`
- Patch ID: `58c0fe9d84892621de19adf4234894f34221f92a`
- Base ref: `HEAD`
- Base commit: `4b63ae29a5c030c9a5cd199b546da3d7a1331827`
- Patch apply status: `already_applied`
- Profile: `networkmanager`
- Effective profile: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2688 |
| `patch_lines` | 71 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 38 |
| `candidate_context_bytes` | 5565 |
| `candidates_json_bytes` | 15019 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/NetworkManager show 4b63ae29a5c030c9a5cd199b546da3d7a1331827:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/core/tests/test-systemd.c` old `83-88` new `83-124` symbol `test_sd_event, test_http_url_is_valid_https, CVE, connection, mud, url, g_assert_cmpint` surface `callbacks, config_keys, config, dbus_api`
- `HUNK-0002` `src/core/tests/test-systemd.c` old `91-96` new `127-133` symbol `main, g_test_add_func, systemd, http, url, is, test_http_url_is_valid_https, nmtst_init` surface `callbacks, config_keys, config, dbus_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/NetworkManager/pca-results/58c0fe/analysis.json`
