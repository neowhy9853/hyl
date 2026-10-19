# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/_worktrees/patched`
- Patch ID: `7f9c7c8731821149ff42971fad18e2a9abbb4c10`
- Base ref: `7f9c7c8731821149ff42971fad18e2a9abbb4c10^`
- Base commit: `11811349f8a10ce419d980c01a518c774fe8a5e5`
- Patch apply status: `applied`
- Profile: `c_project`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 5
- Candidate hunks: 7
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 8892 |
| `patch_lines` | 215 |
| `raw_hunks` | 8 |
| `candidate_hunks` | 7 |
| `changed_files` | 5 |
| `churn` | 103 |
| `candidate_context_bytes` | 20851 |
| `candidates_json_bytes` | 47650 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup show 11811349f8a10ce419d980c01a518c774fe8a5e5:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `libsoup/libsoup-2.4.sym` old `416-421` new `416-422` symbol `soup_status_get_type` surface `exported_symbols, user_visible_output`
- `HUNK-0003` `libsoup/soup-message.c` old `52-58` new `52-58` symbol `status_code, will, normally, be, a, SoupStatus, soup_request_http_get_message` surface `unknown`
- `HUNK-0004` `libsoup/soup-proxy-uri-resolver.c` old `34-40` new `34-40` symbol `soup_proxy_uri_resolver_default_init, status, a, SoupStatus, SoupKnownStatusCode` surface `callbacks, config_keys, plugin_api`
- `HUNK-0005` `libsoup/soup-status.c` old `68-74` new `68-74` symbol `SoupStatus, SoupKnownStatusCode, Copyright` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink`
- `HUNK-0006` `libsoup/soup-status.c` old `150-163` new `150-170` symbol `Note, that, no, libsoup, functions, take, Supported` surface `ioctl_netlink_consumers, user_visible_output, ioctl_netlink`
- `HUNK-0007` `libsoup/soup-status.h` old `91-97` new `91-97` symbol `SoupStatus, SoupKnownStatusCode, Copyright` surface `public_headers, ioctl_netlink_consumers, user_visible_output, ioctl_netlink`
- `HUNK-0008` `libsoup/soup-status.h` old `100-105` new `100-183` symbol `soup_status_proxify, ifndef, SOUP_DISABLE_DEPRECATED, For, introspection, purposes` surface `public_headers, ioctl_netlink_consumers, user_visible_output, ioctl_netlink`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P048/analysis.json`
