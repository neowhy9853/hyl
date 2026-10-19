# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/_worktrees/patched`
- Patch ID: `adf6a28f2cbb`
- Base ref: `d1845782d65d90482adc3af130418967965fd640^`
- Base commit: `edb5f85fd10c15ea8f5e0b03fb75371d260aed9e`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 6
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3564 |
| `patch_lines` | 74 |
| `raw_hunks` | 6 |
| `candidate_hunks` | 6 |
| `changed_files` | 1 |
| `churn` | 22 |
| `candidate_context_bytes` | 17000 |
| `candidates_json_bytes` | 40832 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show edb5f85fd10c15ea8f5e0b03fb75371d260aed9e:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `dnsmasq.conf.example` old `27-34` new `27-34` symbol `check, that, an, reply, is, OK` surface `cli_options, cli, network_protocol, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0002` `dnsmasq.conf.example` old `193-203` new `193-203` symbol `dhcp, range, ra, only, add, names` surface `config_keys, persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0003` `dnsmasq.conf.example` old `220-228` new `220-228` symbol `Unless, overridden, by, ra, stateless, names` surface `config_keys, persistence_state, dns_protocol, dhcp_protocol`
- `HUNK-0004` `dnsmasq.conf.example` old `295-305` new `295-305` symbol `Give, a, fixed, IPv6, address, and` surface `persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0005` `dnsmasq.conf.example` old `355-361` new `355-361` symbol `Send, DHCPv6, option, namservers, as, the` surface `persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0006` `dnsmasq.conf.example` old `560-566` new `560-566` symbol `and, configuration, information, This, must, only` surface `config_keys, network_protocol, persistence_state, config_cli, dns_protocol, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/adf6a2/analysis.json`
