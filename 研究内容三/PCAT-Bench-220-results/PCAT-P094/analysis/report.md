# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/_worktrees/patched`
- Patch ID: `06bb174f89c5db340f0913337e2f5c6f8744b191`
- Base ref: `06bb174f89c5db340f0913337e2f5c6f8744b191^`
- Base commit: `9a9246555f6cf7710141541200c31b83890019fb`
- Patch apply status: `applied`
- Profile: `golang`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 9
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 6769 |
| `patch_lines` | 185 |
| `raw_hunks` | 9 |
| `candidate_hunks` | 9 |
| `changed_files` | 2 |
| `churn` | 85 |
| `candidate_context_bytes` | 25445 |
| `candidates_json_bytes` | 64090 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/go show 9a9246555f6cf7710141541200c31b83890019fb:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/net/http/serve_test.go` old `7555-7560` new `7555-7590` symbol `testServerReadAfterHandlerAbort100Continue, Issue, func, TestServerExpect100ContinueUnreadBody, t, testing, TestServerReadAfterHandlerAbort100Continue` surface `tests, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0002` `src/net/http/server.go` old `570-580` new `570-599` symbol `func, disableWriteContinue, stops, Request, Body, Read, EnableFullDuplex` surface `go_exported_api, go_errors, go_commands, user_visible_output, stdlib, errors`
- `HUNK-0003` `src/net/http/server.go` old `983-989` new `1002-1013` symbol `func, ecr, resp, canWriteContinue, Load, disableWriteContinue, Read` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0004` `src/net/http/server.go` old `1185-1194` new `1209-1220` symbol `func, Sending, a, Continue, or, any, WriteHeader` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0005` `src/net/http/server.go` old `1663-1669` new `1689-1695` symbol `func, w, disableWriteContinue, true, WriteString` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0006` `src/net/http/server.go` old `1701-1706` new `1727-1736` symbol `func, w, canWriteContinue, Load, disableWriteContinue, true, WriteString` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0007` `src/net/http/server.go` old `1931-1937` new `1961-1967` symbol `func, inFlightResponse, disableWriteContinue, true, Error` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0008` `src/net/http/server.go` old `2094-2099` new `2124-2130` symbol `func, w, reqBody, req, Body, Error` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`
- `HUNK-0009` `src/net/http/server.go` old `2257-2263` new `2288-2294` symbol `func, w, disableWriteContinue, false, Hijack` surface `go_exported_api, go_errors, user_visible_output, stdlib, errors`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P034/analysis.json`
