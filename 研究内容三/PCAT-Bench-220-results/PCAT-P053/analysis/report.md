# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnf`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/_worktrees/patched`
- Patch ID: `cc7fe62`
- Base ref: `HEAD`
- Base commit: `c9ae937afb79829ac544d20bdd9675a0dd2b1060`
- Patch apply status: `already_applied`
- Profile: `dnf`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 779 |
| `patch_lines` | 16 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 4 |
| `candidate_context_bytes` | 2632 |
| `candidates_json_bytes` | 6847 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnf show c9ae937afb79829ac544d20bdd9675a0dd2b1060:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `dnf/cli/output.py` old `1777-1785` new `1777-1785` symbol `persistence, libdnf, transaction, TransactionPersistence_PERSIST, elif, TransactionPersistence_TRANSIENT, _simple_pkg` surface `python_public_api, python_api, cli`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnf/pca-results/cc7fe6/analysis.json`
