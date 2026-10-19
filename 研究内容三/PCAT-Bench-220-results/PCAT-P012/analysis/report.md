# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/_worktrees/patched`
- Patch ID: `8839fe2a8962`
- Base ref: `c8168e8`
- Base commit: `c8168e888eb42870e10e6d9d96609d4c3cf2e06d`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2676 |
| `patch_lines` | 74 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 1 |
| `churn` | 30 |
| `candidate_context_bytes` | 12147 |
| `candidates_json_bytes` | 33840 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show c8168e888eb42870e10e6d9d96609d4c3cf2e06d:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/rfc3315.c` old `40-45` new `40-46` symbol `log6_opts, opt6_first, uint8_t, opt, end, log6_packet` surface `config_keys, network_protocol, persistence_state, config_cli, dhcp_protocol`
- `HUNK-0002` `src/rfc3315.c` old `112-122` new `113-130` symbol `state, msg_type, must, have, at, least, dhcp6_maybe_relay` surface `network_protocol, persistence_state, dns_protocol, dhcp_protocol`
- `HUNK-0003` `src/rfc3315.c` old `233-243` new `241-248` symbol `state, opt, opt6_first, opts, end, opt6_next, memcpy` surface `config_keys, network_protocol, persistence_state, config_cli, dhcp_protocol`
- `HUNK-0004` `src/rfc3315.c` old `290-296` new `295-301` symbol `state, dhcp6_no_relay` surface `cli_options, config_keys, user_visible_output, logging, network_protocol, persistence_state, config_cli, dhcp_protocol`
- `HUNK-0005` `src/rfc3315.c` old `2113-2118` new `2118-2136` symbol `opt6_find, opt6_first, uint8_t, opt, end, make, GETSHORT` surface `user_visible_output, logging, persistence_state, config_cli, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8839fe/analysis.json`
