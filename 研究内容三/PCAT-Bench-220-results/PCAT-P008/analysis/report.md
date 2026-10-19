# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/_worktrees/patched`
- Patch ID: `pca_patch_e61190`
- Base ref: `e61190e2faf7ee677424c622881899a10e41612c^`
- Base commit: `3fbef193c7e49e8edb5a4421c465df67de944da6`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 9
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2289 |
| `patch_lines` | 98 |
| `raw_hunks` | 9 |
| `candidate_hunks` | 9 |
| `changed_files` | 1 |
| `churn` | 25 |
| `candidate_context_bytes` | 13941 |
| `candidates_json_bytes` | 38843 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 3fbef193c7e49e8edb5a4421c465df67de944da6:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `git-gui.sh` old `1024-1029` new `1024-1031` symbol `enable_option, picker, gitdir_discovery` surface `cli_options, config_keys, cli, config`
- `HUNK-0002` `git-gui.sh` old `1035-1040` new `1037-1045` symbol `subcommand, eq, gui, disable_option, picker` surface `cli_options, config_keys, cli, config`
- `HUNK-0003` `git-gui.sh` old `1050-1055` new `1055-1061` symbol `disable_option, picker` surface `cli_options, cli`
- `HUNK-0004` `git-gui.sh` old `1058-1063` new `1064-1070` symbol `disable_option, picker` surface `cli_options, cli`
- `HUNK-0005` `git-gui.sh` old `1080-1085` new `1087-1095` symbol `pick, disable_option, gitdir_discovery` surface `unknown`
- `HUNK-0006` `git-gui.sh` old `1168-1174` new `1178-1184` symbol `is_enabled, gitdir_discovery, _gitdir, eq` surface `config_keys, user_visible_output`
- `HUNK-0007` `git-gui.sh` old `1180-1186` new `1190-1196` symbol `_gitdir, eq, is_enabled, picker` surface `config_keys, user_visible_output`
- `HUNK-0008` `git-gui.sh` old `1195-1200` new `1205-1216` symbol `_gitdir, eq, catch, wm, withdraw, error_popup` surface `config_keys, user_visible_output`
- `HUNK-0009` `git-gui.sh` old `3103-3116` new `3119-3133` symbol `gui, pick, set, err, mc, usage` surface `cli_options, user_visible_output, cli`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/pca_pa/analysis.json`
