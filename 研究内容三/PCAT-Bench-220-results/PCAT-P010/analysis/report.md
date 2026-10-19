# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/_worktrees/patched`
- Patch ID: `ca30c82`
- Base ref: `66d9658`
- Base commit: `66d9658f5f557e0e525e5db5449ef94686df50d3`
- Patch apply status: `already_applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2937 |
| `patch_lines` | 66 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 2 |
| `churn` | 19 |
| `candidate_context_bytes` | 8902 |
| `candidates_json_bytes` | 28188 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show 66d9658f5f557e0e525e5db5449ef94686df50d3:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/auth.c` old `591-597` new `591-597` symbol `dns_header, newoffset, ansp, header, offset, log_query` surface `user_visible_output, logging, network_protocol, persistence_state, dns_protocol`
- `HUNK-0002` `src/auth.c` old `631-638` new `631-637` symbol `dns_header, anscount, ns, soa, newoffset, ansp, sprintf` surface `user_visible_output, network_protocol, dns_protocol`
- `HUNK-0003` `src/auth.c` old `650-660` new `649-658` symbol `dns_header, newoffset, ansp, header, add_resource_record` surface `user_visible_output, network_protocol, dns_protocol`
- `HUNK-0004` `src/auth.c` old `669-677` new `667-677` symbol `dns_header, add_resource_record, header, limit, trunc, offset` surface `config_keys, network_protocol, dns_protocol`
- `HUNK-0005` `src/rfc1035.c` old `1427-1432` new `1427-1437` symbol `dns_header, Nameoffset, means, that, the, name, check_bad_address` surface `user_visible_output, logging, network_protocol, persistence_state, dns_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/ca30c8/analysis.json`
