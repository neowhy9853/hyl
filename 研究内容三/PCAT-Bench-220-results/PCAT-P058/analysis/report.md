# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/_worktrees/patched`
- Patch ID: `c090f1d17b280c98630914334d341a2fa3318117`
- Base ref: `c090f1d17b280c98630914334d341a2fa3318117^`
- Base commit: `fa48bdb939c34213cac8b92db0f070ceeb69e51e`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 4
- Candidate hunks: 10
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 7106 |
| `patch_lines` | 181 |
| `raw_hunks` | 10 |
| `candidate_hunks` | 10 |
| `changed_files` | 4 |
| `churn` | 76 |
| `candidate_context_bytes` | 25790 |
| `candidates_json_bytes` | 75174 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show fa48bdb939c34213cac8b92db0f070ceeb69e51e:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/cache.c` old `855-861` new `855-861` symbol `cache_end_insert, Sneak, out, possibly, updated, crypto, read_write` surface `daemon_control, persistence_state, dns_protocol, daemon_interfaces`
- `HUNK-0002` `src/cache.c` old `1000-1005` new `1000-1006` symbol `cache_recv_insert, PIPE_OP_KILLED, blockdata_free` surface `network_protocol, daemon_control, persistence_state, dns_protocol, daemon_interfaces`
- `HUNK-0003` `src/cache.c` old `1013-1023` new `1014-1027` symbol `cache_recv_insert, read_write, fd, uid, RW_READ, op, blockdata_free` surface `network_protocol, daemon_control, persistence_state, dns_protocol, daemon_interfaces`
- `HUNK-0004` `src/cache.c` old `1025-1033` new `1029-1040` symbol `cache_recv_insert, op, PIPE_OP_RESULT, repatriate, the, work, blockdata_free` surface `network_protocol, daemon_control, persistence_state, dns_protocol, daemon_interfaces`
- `HUNK-0005` `src/dnsmasq.c` old `1335-1345` new `1335-1376` symbol `sig_handler, daemon, pipe_to_parent, ifdef, HAVE_DNSSEC, forward_to_tcp, _exit` surface `cli_options, user_visible_output, protocol, logging, network_protocol, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0006` `src/dnsmasq.c` old `2231-2238` new `2262-2273` symbol `frec, alarm, CHILD_LIFETIME, daemon, pipe_to_parent, pipefd, close` surface `cli_options, user_visible_output, protocol, logging, network_protocol, daemon_control, persistence_state, config_cli, dns_protocol, dhcp_protocol, daemon_interfaces`
- `HUNK-0007` `src/dnsmasq.h` old `549-554` new `549-555` symbol `crec, define, PIPE_OP_KILLED, child, killed, by, capget` surface `public_headers, callbacks, cli_options, user_visible_output, cli, plugin_api, protocol, network_protocol, dns_protocol`
- `HUNK-0008` `src/dnsmasq.h` old `1271-1276` new `1272-1280` symbol `daemon, frec, forward_to_tcp, dns_header, header_to_tcp, ssize_t, capget` surface `public_headers, config_keys, user_visible_output, protocol, logging, network_protocol, daemon_control, persistence_state, dns_protocol, dhcp_protocol, daemon_interfaces`
- `HUNK-0009` `src/forward.c` old `2223-2229` new `2223-2229` symbol `dns_header, still, too, big, strip, optional, rrfilter` surface `user_visible_output, logging, network_protocol, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0010` `src/forward.c` old `2237-2242` new `2237-2246` symbol `dns_header, we, have, succeeded, and, are, rrfilter` surface `user_visible_output, logging, network_protocol, config_cli, dns_protocol, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/c090f1/analysis.json`
