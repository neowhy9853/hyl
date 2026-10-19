# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/_worktrees/patched`
- Patch ID: `5bbd22ff78daf010c5bd19c466a0c45ac78503d4`
- Base ref: `c19862e5f8415b4f24b189d065ed739517c548ba`
- Base commit: `c19862e5f8415b4f24b189d065ed739517c548ba`
- Patch apply status: `applied`
- Profile: `golang`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5551 |
| `patch_lines` | 178 |
| `raw_hunks` | 7 |
| `candidate_hunks` | 7 |
| `changed_files` | 2 |
| `churn` | 83 |
| `candidate_context_bytes` | 12197 |
| `candidates_json_bytes` | 40553 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/go show c19862e5f8415b4f24b189d065ed739517c548ba:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/net/http/serve_test.go` old `18-24` new `18-23` symbol `import, internal, synctest` surface `tests, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0002` `src/net/http/serve_test.go` old `44-49` new `43-49` symbol `import, testing, synctest` surface `tests, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0003` `src/net/http/serve_test.go` old `815-820` new `815-877` symbol `testServerTimeoutsWithTimeout, func, TestServerUnencryptedHTTP2HeaderTimeout, t, testing, T, TestServerTimeouts` surface `tests, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0004` `src/net/http/server.go` old `978-995` new `978-988` symbol `func, var, wholeReqDeadline, time, Time, or, Close` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0005` `src/net/http/server.go` old `1045-1054` new `1038-1044` symbol `func, c, rwc, SetReadDeadline, wholeReqDeadline, Adjust, Close` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0006` `src/net/http/server.go` old `1981-1986` new `1971-1980` symbol `func, d, c, server, readHeaderTimeout, rwc, SetReadDeadline, Error` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0007` `src/net/http/server.go` old `2110-2116` new `2104-2114` symbol `func, d, c, server, readHeaderTimeout, rwc, SetReadDeadline, Error` surface `go_exported_api, stdlib`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis.json`
