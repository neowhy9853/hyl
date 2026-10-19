# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/ruby`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/_worktrees/patched`
- Patch ID: `23c056c83cebad03f716c7af490c8bec9753ec90`
- Base ref: `0b2b21767b`
- Base commit: `0b2b21767beb73cd8497ac6b18248e7b87dc433e`
- Patch apply status: `applied`
- Profile: `ruby`
- Effective profile: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 6
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 6554 |
| `patch_lines` | 215 |
| `raw_hunks` | 7 |
| `candidate_hunks` | 7 |
| `changed_files` | 6 |
| `churn` | 130 |
| `candidate_context_bytes` | 17991 |
| `candidates_json_bytes` | 44647 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/ruby show 0b2b21767beb73cd8497ac6b18248e7b87dc433e:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `bignum.c` old `7029-7034` new `7029-7051` symbol `rb_big_bit_length, VALUE, rb_big_bit_count, big, BIGNUM_NEGATIVE_P, rb_raise, rb_integer_unpack` surface `ruby_c_extension_api, ruby_exceptions, c_ext_api, exceptions`
- `HUNK-0002` `internal/bignum.h` old `123-128` new `123-129` symbol `rb_big_aref2, VALUE, rb_big_bit_count, big, rb_big_abs` surface `ruby_c_extension_api, ruby_exceptions, c_ext_api, exceptions`
- `HUNK-0003` `internal/numeric.h` old `126-131` new `126-132` symbol `rb_int_even_p, VALUE, rb_int_bit_count, num, rb_int_odd_p` surface `ruby_c_extension_api, c_ext_api`
- `HUNK-0004` `numeric.c` old `5732-5737` new `5732-5780` symbol `rb_int_bit_length, VALUE, rb_fix_bit_count, fix, v, FIX2LONG, rb_raise, rb_big_bit_length` surface `ruby_c_extension_api, ruby_exceptions, c_ext_api, exceptions`
- `HUNK-0005` `numeric.c` old `6610-6615` new `6653-6659` symbol `Init_Numeric, rb_define_method, rb_cInteger, bit_count, rb_int_bit_count` surface `ruby_c_extension_api, c_ext_api`
- `HUNK-0006` `spec/ruby/core/integer/bit_count_spec.rb` old `0--1` new `1-31` symbol `require_relative, spec_helper, ruby_version_is, describe, Integer, bit_count` surface `tests, ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0007` `test/ruby/test_integer.rb` old `632-637` new `632-672` symbol `def, test_bit_count, assert_equal, bit_count, Fixnum, boundaries, test_bit_count_for_negative_numbers, test_bit_length` surface `tests, ruby_exceptions, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/ruby/pca-results/23c056/analysis.json`
