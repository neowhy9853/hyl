# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/ruby`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/_worktrees/patched`
- Patch ID: `6328380a3a83713ff6f55eec772358aadd2f9014`
- Base ref: `6328380a3a83713ff6f55eec772358aadd2f9014~1`
- Base commit: `8ff8963995e6df14c0ec589a526a268dde4b9cc5`
- Patch apply status: `applied`
- Profile: `ruby`
- Effective profile: `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 2
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1565 |
| `patch_lines` | 49 |
| `raw_hunks` | 2 |
| `candidate_hunks` | 2 |
| `changed_files` | 2 |
| `churn` | 13 |
| `candidate_context_bytes` | 5247 |
| `candidates_json_bytes` | 11881 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/ruby/pca-results/632838/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/ruby show 8ff8963995e6df14c0ec589a526a268dde4b9cc5:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/632838/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/632838/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `lib/time.rb` old `670-676` new `670-676` symbol `rfc3339, new, time, strip` surface `ruby_exceptions, exceptions`
- `HUNK-0002` `test/test_time.rb` old `245-250` new `245-260` symbol `subtest_xmlschema_encode, def, subtest_xmlschema_whitespaces, method, t, Time` surface `tests, ruby_exceptions, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/ruby/pca-results/632838/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/ruby/pca-results/632838/analysis.json`
