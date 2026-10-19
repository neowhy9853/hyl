# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/_worktrees/patched`
- Patch ID: `7d5fbe7da380135a70ab7b7f3f117cc870207503`
- Base ref: `ded935be3708f7df2c836046bd73b373a1dc40ac`
- Base commit: `ded935be3708f7df2c836046bd73b373a1dc40ac`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 4
- Candidate hunks: 6
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 5799 |
| `patch_lines` | 154 |
| `raw_hunks` | 7 |
| `candidate_hunks` | 6 |
| `changed_files` | 4 |
| `churn` | 52 |
| `candidate_context_bytes` | 12909 |
| `candidates_json_bytes` | 41968 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show ded935be3708f7df2c836046bd73b373a1dc40ac:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `src/arp.c` old `111-132` new `111-136` symbol `mysockaddr, If, the, database, is, less, find_mac` surface `callbacks, plugin_api, daemon_control, persistence_state, dns_protocol`
- `HUNK-0003` `src/arp.c` old `141-146` new `145-154` symbol `mysockaddr, Not, in, cache, child, no, find_mac` surface `callbacks, plugin_api, daemon_control, persistence_state, dns_protocol`
- `HUNK-0004` `src/dnsmasq.c` old `2033-2041` new `2033-2056` symbol `listener, The, code, in, edns0, c, indextoname` surface `cli_options, protocol, network_protocol, daemon_control, persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0005` `src/dnsmasq.h` old `1918-1923` new `1918-1924` symbol `dns_header, edns0_needs_mac, mysockaddr, addr, time_t, now, add_pseudoheader` surface `public_headers, config_keys, protocol, network_protocol, persistence_state, dns_protocol`
- `HUNK-0006` `src/edns0.c` old `265-270` new `265-279` symbol `encoder, This, function, needs, to, call, find_mac` surface `cli_options, protocol, network_protocol, persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0007` `src/edns0.c` old `562-564` new `571-574` symbol `dns_header, add_edns0_config` surface `cli_options, config_keys, protocol, network_protocol, persistence_state, config_cli, dns_protocol, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/output_dir_rerun/PCAT-P056/analysis.json`
