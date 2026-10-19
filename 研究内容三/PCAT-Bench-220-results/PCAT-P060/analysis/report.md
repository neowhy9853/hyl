# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnsmasq`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/_worktrees/patched`
- Patch ID: `pca_84415a`
- Base ref: `84415a8^`
- Base commit: `1537645e8f4606101b9a593393552438bc23415c`
- Patch apply status: `applied`
- Profile: `dnsmasq`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 460 |
| `patch_lines` | 13 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 2 |
| `candidate_context_bytes` | 2028 |
| `candidates_json_bytes` | 6339 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnsmasq show 1537645e8f4606101b9a593393552438bc23415c:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/dhcp.c` old `399-405` new `399-405` symbol `dhcp_packet, is_relay_use_source, mess, giaddr, s_addr, is_relay_reply, lease_update_dns` surface `protocol, network_protocol, persistence_state, dhcp_protocol`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnsmasq/pca-results/pca_84/analysis.json`
