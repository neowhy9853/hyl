# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/haproxy`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/_worktrees/patched`
- Patch ID: `9bc372`
- Base ref: `HEAD`
- Base commit: `0748799ad18db4eeb72b33b30c5e0c420a8216ea`
- Patch apply status: `already_applied`
- Profile: `haproxy`
- Effective profile: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 1
- Candidate hunks: 1
- Static call chains: 0

## Final Analysis Result

**结论**: 该补丁不包含兼容性变更。

补丁修改了 `reg-tests/checks/healthcheck-section.vtc` 中的一行正则表达式：将
`srv[0-9]` 修正为 `srv[0-9]+`，以正确匹配多位数字的健康检查服务器编号。

**原因**:
- 补丁仅涉及测试文件（`reg-tests/**`），该路径已在 effective profile 的 `ignore_patterns` 中明确排除。
- 未修改任何生产代码、公共头文件、导出符号、CLI 选项、配置解析、协议行为或运行时 API。
- 这是一个测试脚本中的正则 bug fix，对 HAProxy 本身的 API、ABI、行为、输出格式或配置语义无任何外部可观察影响。

**无需进行定向动态测试**，因为不存在兼容性变更。

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 662 |
| `patch_lines` | 13 |
| `raw_hunks` | 1 |
| `candidate_hunks` | 1 |
| `changed_files` | 1 |
| `churn` | 2 |
| `candidate_context_bytes` | 2030 |
| `candidates_json_bytes` | 6334 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/haproxy show 0748799ad18db4eeb72b33b30c5e0c420a8216ea:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `reg-tests/checks/healthcheck-section.vtc` old `144-150` new `144-150` symbol `expect, h1_pid, Health, check, server, be2` surface `user_visible_output, config, logging, protocol_behavior`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/haproxy/pca-results/9bc372/analysis.json`
