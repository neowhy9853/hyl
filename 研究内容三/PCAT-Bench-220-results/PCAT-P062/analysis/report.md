# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/_worktrees/patched`
- Patch ID: `96b08e959ca1b44f5b7e0917a4b53e73858fd29d`
- Base ref: `HEAD`
- Base commit: `0748799ad18db4eeb72b33b30c5e0c420a8216ea`
- Patch apply status: `already_applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 5
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3323 |
| `patch_lines` | 98 |
| `raw_hunks` | 5 |
| `candidate_hunks` | 5 |
| `changed_files` | 2 |
| `churn` | 32 |
| `candidate_context_bytes` | 11161 |
| `candidates_json_bytes` | 27914 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show 0748799ad18db4eeb72b33b30c5e0c420a8216ea:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `include/haproxy/ssl_sock-t.h` old `255-260` new `255-261` symbol `ssl_keylog, define, SSL_SOCK_F_KTLS_ULP, TLS, ULP, is, void` surface `public_headers, config_keys, user_visible_output, struct_layout, logging, daemon_control, persistence_state, protocol_behavior`
- `HUNK-0002` `src/ssl_sock.c` old `439-444` new `439-460` symbol `ha_ssl_read, ktls_enable_ulp, ssl_sock_ctx, ctx, ret, flags, setsockopt, BIO_set_retry_read` surface `protocol_behavior`
- `HUNK-0003` `src/ssl_sock.c` old `485-490` new `501-509` symbol `ha_ssl_ctrl, ktls_enable_ulp, ctx` surface `user_visible_output, protocol_behavior`
- `HUNK-0004` `src/ssl_sock.c` old `5670-5683` new `5689-5694` symbol `connection, ifdef, HA_USE_KTLS, Make, the, socket, ssl_sock_start` surface `daemon_control, protocol_behavior`
- `HUNK-0005` `src/ssl_sock.c` old `6617-6622` new `6628-6636` symbol `ssl_sock_ctx, ktls_enable_ulp, ctx, ssl_sock_setup_ktls` surface `protocol_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/96b08e/analysis.json`
