# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnf`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/_worktrees/patched`
- Patch ID: `eabf33aeeb486ec671f3e3fd2120bccc396d2326`
- Base ref: `HEAD`
- Base commit: `c9ae937afb79829ac544d20bdd9675a0dd2b1060`
- Patch apply status: `already_applied`
- Profile: `dnf`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2758 |
| `patch_lines` | 71 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 3 |
| `churn` | 14 |
| `candidate_context_bytes` | 14237 |
| `candidates_json_bytes` | 35034 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnf show c9ae937afb79829ac544d20bdd9675a0dd2b1060:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `dnf/base.py` old `2640-2646` new `2640-2646` symbol `Base, raise, dnf, exceptions, InvalidInstalledGPGKeyError, _prov_key_data` surface `python_public_api, python_exceptions, config_keys, python_api, exceptions`
- `HUNK-0002` `dnf/cli/cli.py` old `284-289` new `284-290` symbol `BaseCli, print_plugin_recommendation, False, do_transaction` surface `python_public_api, python_exceptions, config_keys, user_visible_output, python_api, cli, exceptions`
- `HUNK-0003` `dnf/cli/cli.py` old `304-309` new `305-312` symbol `BaseCli, isinstance, e, dnf, exceptions, InvalidInstalledGPGKeyError, do_transaction` surface `python_public_api, python_exceptions, user_visible_output, python_api, cli, exceptions`
- `HUNK-0004` `dnf/cli/cli.py` old `312-317` new `315-325` symbol `BaseCli, print_plugin_recommendation, msg, n, _, Try, do_transaction` surface `python_public_api, python_exceptions, user_visible_output, python_api, cli, exceptions`
- `HUNK-0005` `dnf/exceptions.py` old `86-91` new `86-95` symbol `DownloadError, class, InvalidInstalledGPGKeyError, Error, pass` surface `python_public_api, user_visible_output, python_api, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnf/pca-results/eabf33/analysis.json`
