# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/libxml2`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/_worktrees/patched`
- Patch ID: `226b5608`
- Base ref: `226b560837b90dea9b14431eca6e6fda8fb01ab4^`
- Base commit: `310564cc6b2c5766bbf053bc29353df6e6a655b6`
- Patch apply status: `applied`
- Profile: `libxml2`
- Effective profile: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1499 |
| `patch_lines` | 32 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 1 |
| `churn` | 10 |
| `candidate_context_bytes` | 4679 |
| `candidates_json_bytes` | 10613 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/libxml2 show 310564cc6b2c5766bbf053bc29353df6e6a655b6:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `parser.c` old `7261-7270` new `7261-7270` symbol `xmlParseReference, ctxt, sax, characters, userData, cur, xmlCtxtParseEntity` surface `parser_behavior`
- `HUNK-0002` `parser.c` old `7284-7293` new `7284-7295` symbol `xmlParseReference, ctxt, sax, characters, userData, cur, xmlCtxtParseEntity` surface `parser_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/libxml2/pca-results/226b56/analysis.json`
