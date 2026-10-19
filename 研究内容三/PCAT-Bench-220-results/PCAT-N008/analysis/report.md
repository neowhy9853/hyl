# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/git`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/_worktrees/patched`
- Patch ID: `96ee7f1650e6096561599f069d18c052412d7506`
- Base ref: `96ee7f1650e6096561599f069d18c052412d7506^`
- Base commit: `c69baaf57ba26cf117c2b6793802877f19738b0d`
- Patch apply status: `applied`
- Profile: `git`
- Effective profile: `/home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/git/pca-results/96ee7f`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1141 |
| `patch_lines` | 36 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 3 |
| `candidate_context_bytes` | 1475 |
| `candidates_json_bytes` | 4527 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/git show c69baaf57ba26cf117c2b6793802877f19738b0d:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `http.c` old `2609-2617` new `2609-2615` symbol `packfile_list, unlink, tmp_idx, fetch_and_setup_pack_index` surface `user_visible_output`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/git/pca-results/96ee7f/analysis.json`
