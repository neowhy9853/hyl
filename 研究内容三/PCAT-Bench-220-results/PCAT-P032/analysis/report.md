# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/44d04e/_worktrees/patched`
- Patch ID: `44d04e442683b53ed618b74861f056f93fcbd783`
- Base ref: `67ad42147a7acc2af6074753ebd03d904476118f`
- Base commit: `67ad42147a7acc2af6074753ebd03d904476118f`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/44d04e/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/44d04e/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/44d04e`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2606 |
| `patch_lines` | 65 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 2 |
| `churn` | 14 |
| `candidate_context_bytes` | 4027 |
| `candidates_json_bytes` | 12146 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/44d04e/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 67ad42147a7acc2af6074753ebd03d904476118f:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/44d04e/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/44d04e/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `builtin/receive-pack.c` old `1427-1434` new `1427-1434` symbol `push_to_checkout, strvec_pushf, opt, env, GIT_WORK_TREE, s, child_process_init` surface `cli_options, cli, config, plugin_api, commands`
- `HUNK-0002` `t/t5516-fetch-push.sh` old `1791-1796` new `1791-1807` symbol `test_expect_success, denyCurrentBranch, and, core, worktree, test_when_finished` surface `tests, config_keys, plugin_api`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/44d04e/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/44d04e/analysis.json`
