# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/ruby`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/_worktrees/patched`
- Patch ID: `0d7e50a1746bfa3db2a50478d3680cd7c36ea383`
- Base ref: `3760fedbff`
- Base commit: `3760fedbffb87b29d554f3b270b7c92c9a660a50`
- Patch apply status: `already_applied`
- Profile: `ruby`
- Effective profile: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 4
- Candidate hunks: 12
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 8720 |
| `patch_lines` | 250 |
| `raw_hunks` | 12 |
| `candidate_hunks` | 12 |
| `changed_files` | 4 |
| `churn` | 108 |
| `candidate_context_bytes` | 27884 |
| `candidates_json_bytes` | 75051 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/ruby show 3760fedbffb87b29d554f3b270b7c92c9a660a50:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `eval.c` old `147-161` new `147-172` symbol `rb_ec_fiber_scheduler_finalize, ruby_tag_type, state, TAG_NONE, VALUE, trap_errinfo, error_handle, rb_ec_teardown` surface `ruby_c_extension_api, user_visible_output, c_ext_api`
- `HUNK-0002` `eval_error.c` old `276-281` new `276-291` symbol `shown_cause_p, add_shown_cause, VALUE, cause, shown_causes, NIL_OR_UNDEF_P, rb_obj_is_kind_of, rb_hash_aset` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0003` `eval_error.c` old `309-323` new `319-336` symbol `rb_exc_check_circular_cause, rb_error_write0, VALUE, errinfo, emesg, errat, rb_error_write, rb_raise` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0004` `eval_error.c` old `340-358` new `353-377` symbol `rb_error_write, show_cause, errinfo, str, opt, highlight, APPEND` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0005` `eval_error.c` old `378-384` new `397-403` symbol `rb_ec_error_print_detailed, rb_error_write0, errinfo, emesg, errat, str, rb_error_write, EC_PUSH_TAG` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0006` `eval_error.c` old `386-391` new `405-416` symbol `rb_ec_error_print_detailed, rb_execution_context_t, ec, VALUE, errinfo, str, rb_ec_error_print_detailed0, rb_ec_raised_set` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0007` `eval_error.c` old `504-510` new `529-535` symbol `exiting_split, error_handle_with_shown_causes, rb_execution_context_t, ec, VALUE, errinfo, error_handle, rb_bug` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0008` `eval_error.c` old `546-552` new `571-577` symbol `ruby_tag_type, rb_ec_error_print_detailed0, ec, errinfo, Qnil, Qundef, rb_ec_error_print, warn_print` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0009` `eval_error.c` old `555-557` new `580-588` symbol `ruby_tag_type, error_handle, rb_execution_context_t, ec, VALUE, errinfo, error_handle_with_shown_causes, rb_ec_reset_raised` surface `ruby_c_extension_api, ruby_exceptions, user_visible_output, c_ext_api, exceptions`
- `HUNK-0010` `eval_jump.c` old `114-119` new `114-121` symbol `rb_ec_exec_end_proc, Share, only, among, END, at_exit` surface `ruby_c_extension_api, user_visible_output, c_ext_api`
- `HUNK-0011` `eval_jump.c` old `125-132` new `127-136` symbol `rb_ec_exec_end_proc, VALUE, err, ec, errinfo, add_shown_cause, error_handle_with_shown_causes, exec_end_procs_chain` surface `ruby_c_extension_api, user_visible_output, c_ext_api`
- `HUNK-0012` `test/ruby/test_exception.rb` old `826-831` new `826-868` symbol `def, test_multiple_error_handle, errs, END3, RuntimeError, n, test_cause_at_end` surface `tests, ruby_exceptions, user_visible_output, exceptions`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/ruby/pca-results/0d7e50/analysis.json`
