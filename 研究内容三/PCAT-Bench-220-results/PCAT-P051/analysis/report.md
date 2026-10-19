# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnf`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/_worktrees/patched`
- Patch ID: `017bbab0a253d84978f645cd358cdeb63e9ecb18`
- Base ref: `017bbab0a253d84978f645cd358cdeb63e9ecb18`
- Base commit: `017bbab0a253d84978f645cd358cdeb63e9ecb18`
- Patch apply status: `already_applied`
- Profile: `c_project`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 4
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5623 |
| `patch_lines` | 122 |
| `raw_hunks` | 6 |
| `candidate_hunks` | 4 |
| `changed_files` | 2 |
| `churn` | 46 |
| `candidate_context_bytes` | 13788 |
| `candidates_json_bytes` | 31349 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnf show 017bbab0a253d84978f645cd358cdeb63e9ecb18:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `dnf/cli/cli.py` old `844-850` new `844-850` symbol `Cli, self, _read_conf_file, opts, releasever, releasever_major, configure` surface `cli_options, config_keys, user_visible_output, cli, plugin_api`
- `HUNK-0002` `dnf/cli/cli.py` old `953-959` new `953-959` symbol `Cli, def, _read_conf_file, self, releasever, None, configure` surface `cli_options, config_keys, user_visible_output, cli, plugin_api`
- `HUNK-0003` `dnf/cli/cli.py` old `981-998` new `981-1003` symbol `Cli, det_major, None, det_minor, releasever, dnf, or_else, _read_conf_file` surface `cli_options, config_keys, user_visible_output, cli`
- `HUNK-0004` `dnf/cli/option_parser.py` old `199-204` new `199-210` symbol `OptionParser, general_grp, add_argument, releasever, major, default, _add_general_options` surface `cli_options, config_keys, cli, plugin_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnf/pca-results/017bba/analysis.json`
