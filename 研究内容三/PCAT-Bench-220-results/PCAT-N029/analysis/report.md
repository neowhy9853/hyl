# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/ruby`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/ruby/pca-results/812738/_worktrees/patched`
- Patch ID: `812738f94074ae6fffa017933aa5bcdd05a15014`
- Base ref: `HEAD`
- Base commit: `3760fedbffb87b29d554f3b270b7c92c9a660a50`
- Patch apply status: `already_applied`
- Profile: `ruby`
- Effective profile: `/home/soong/pca_benchmark/_repos/ruby/pca-results/812738/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/ruby/pca-results/812738/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/812738`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1446 |
| `patch_lines` | 35 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 4 |
| `candidate_context_bytes` | 1583 |
| `candidates_json_bytes` | 5987 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/ruby/pca-results/812738/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/ruby show 3760fedbffb87b29d554f3b270b7c92c9a660a50:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/812738/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/812738/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `test/rubygems/test_bundled_ca.rb` old `33-39` new `33-40` symbol `assert_https, rescue, Errno, ENOENT, ETIMEDOUT, ECONNRESET` surface `tests, ruby_exceptions, user_visible_output, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/ruby/pca-results/812738/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/ruby/pca-results/812738/analysis.json`
