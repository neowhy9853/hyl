# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/_worktrees/patched`
- Patch ID: `8c84e6802c0e23503bfe655dadcdc4a15de7373a`
- Base ref: `94f057755b7941b321fd11fec1b2e3ca5313a4e0`
- Base commit: `94f057755b7941b321fd11fec1b2e3ca5313a4e0`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/8c84e6`
- Analysis mode: `normal`
- Mode reason: user requested normal mode; no hard threshold exceeded
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3755 |
| `patch_lines` | 92 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 20 |
| `candidate_context_bytes` | 4622 |
| `candidates_json_bytes` | 13301 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show 94f057755b7941b321fd11fec1b2e3ca5313a4e0:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `t/t3070-wildmatch.sh` old `99-104` new `99-111` symbol `match_with_ls_files, prereqs, EXPENSIVE_ON_WINDOWS, pattern, in, BSLASHPSPEC` surface `tests, user_visible_output`
- `HUNK-0002` `t/t3070-wildmatch.sh` old `108-143` new `115-150` symbol `match_with_ls_files, test_expect_success, prereqs, match_function, via, ls` surface `tests, user_visible_output`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/8c84e6/analysis.json`
