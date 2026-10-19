# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/_worktrees/patched`
- Patch ID: `8fa68a6`
- Base ref: `1269f074f86bb959863012063060a3a082d37dc4`
- Base commit: `1269f074f86bb959863012063060a3a082d37dc4`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 4
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2576 |
| `patch_lines` | 70 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 4 |
| `changed_files` | 3 |
| `churn` | 19 |
| `candidate_context_bytes` | 9464 |
| `candidates_json_bytes` | 29491 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show 1269f074f86bb959863012063060a3a082d37dc4:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/analysis.json`.

## Candidate Hunks

- `HUNK-0002` `src/cache.c` old `2254-2259` new `2254-2268` symbol `edestr, error_occured, flags, F_RCODE, F_NEG, sprintf` surface `cli_options, user_visible_output, logging, network_protocol, persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0003` `src/cache.c` old `2266-2271` new `2275-2283` symbol `all_addr, option_bool, OPT_LOG_ONLY_FAILED, error_occured, flags, log_query` surface `cli_options, user_visible_output, logging, network_protocol, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0004` `src/dnsmasq.h` old `289-295` new `289-296` symbol `event_desc, define, OPT_LOG_ONLY_FAILED, OPT_LAST, capget` surface `public_headers, cli_options, user_visible_output, protocol, logging, network_protocol, persistence_state, config_cli, dns_protocol, dhcp_protocol`
- `HUNK-0005` `src/option.c` old `3463-3468` new `3463-3470` symbol `one_opt, strcmp, arg, only_failed, set_option_bool, OPT_LOG_ONLY_FAILED` surface `cli_options, logging, network_protocol, config_cli, dns_protocol, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/8fa68a/analysis.json`
