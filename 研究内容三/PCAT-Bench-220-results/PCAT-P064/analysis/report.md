# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/_worktrees/patched`
- Patch ID: `fb38e40`
- Base ref: `9bc37232f40b3c672d660e3f5f684621b2ed0e12`
- Base commit: `9bc37232f40b3c672d660e3f5f684621b2ed0e12`
- Patch apply status: `applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 3
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 1087 |
| `patch_lines` | 30 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 1 |
| `churn` | 4 |
| `candidate_context_bytes` | 7604 |
| `candidates_json_bytes` | 16595 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show 9bc37232f40b3c672d660e3f5f684621b2ed0e12:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `src/quic_tx.c` old `2029-2036` new `2029-2036` symbol `qc_do_build_pkt, qc_build_cc_frm` surface `network_protocol, protocol_behavior`
- `HUNK-0002` `src/quic_tx.c` old `2038-2043` new `2038-2044` symbol `qc_do_build_pkt, len, len_sz_diff, qc_build_cc_frm` surface `network_protocol, protocol_behavior`
- `HUNK-0003` `src/quic_tx.c` old `2074-2079` new `2075-2081` symbol `qc_do_build_pkt, Encode, length, field, of, PN, TRACE_PRINTF` surface `network_protocol, protocol_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/fb38e4/analysis.json`
