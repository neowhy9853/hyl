# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/ruby`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/_worktrees/patched`
- Patch ID: `183c9f8f5c7367a65ff6b0574ba966ad158c1ad8`
- Base ref: `3760fedbff`
- Base commit: `3760fedbffb87b29d554f3b270b7c92c9a660a50`
- Patch apply status: `already_applied`
- Profile: `ruby`
- Effective profile: `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3019 |
| `patch_lines` | 70 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 2 |
| `churn` | 16 |
| `candidate_context_bytes` | 9347 |
| `candidates_json_bytes` | 19158 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/ruby show 3760fedbffb87b29d554f3b270b7c92c9a660a50:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `lib/time.rb` old `369-374` new `369-377` symbol `make_time, A, zone, argument, can, be` surface `ruby_exceptions, exceptions`
- `HUNK-0002` `lib/time.rb` old `382-393` new `385-396` symbol `make_time, def, parse, date, now, self` surface `ruby_exceptions, exceptions`
- `HUNK-0003` `test/test_time.rb` old `370-375` new `370-384` symbol `def, test_parse_custom_offset, t, Time, at, utc, test_parse_now_nil` surface `tests, ruby_exceptions, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/ruby/pca-results/183c9f/analysis.json`
