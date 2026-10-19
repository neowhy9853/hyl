# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/dnf`
- Patched analysis worktree: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/_worktrees/patched`
- Patch ID: `de9c5c5b597bf97aa03145de129fb579b5a0e953`
- Base ref: `HEAD`
- Base commit: `c9ae937afb79829ac544d20bdd9675a0dd2b1060`
- Patch apply status: `already_applied`
- Profile: `dnf`
- Effective profile: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 2
- Candidate hunks: 3
- Static call chains: 0

## Summary

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 3 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

## PCA-0001: 输入契约变更 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.85
- **影响接口**: rpm2py_format (Python public API)
- **旧代码位置**: dnf/cli/commands/repoquery.py:68-73
- **新代码位置**: dnf/cli/commands/repoquery.py:68-74
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为
fmt_repl 内部函数直接使用正则匹配到的标签键名查询 ALLOWED_QUERY_TAGS（全小写）。
未匹配的大写标签（如 %{NAME}）被原样保留。只有小写标签被识别并替换为包属性值。

### 变更后行为
fmt_repl 调用 key.lower() 将所有标签转为小写后再查询 ALLOWED_QUERY_TAGS。
大写标签现在也被识别并替换为对应包属性值。小写标签行为不变。

### 兼容性影响
该补丁恢复了 v4.15.0（commit e50488b6）中意外丢失的大写查询标签支持。
这是向后兼容的输入契约放宽：现有小写输入不受影响。

### 证据
```python
key = key.lower()  # we allow both uppercase and lowercase variants
```

### 复核建议
验证大写标签的测试用例输出正确。确认现有小写 queryformat 测试不受影响。

### 测试建议
运行 tests.test_repoquery::OutputTest::test_output 验证大写标签行为。
确认其他小写标签测试仍通过。

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 2511 |
| `patch_lines` | 60 |
| `raw_hunks` | 3 |
| `candidate_hunks` | 3 |
| `changed_files` | 2 |
| `churn` | 6 |
| `candidate_context_bytes` | 7450 |
| `candidates_json_bytes` | 18396 |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/dnf show c9ae937afb79829ac544d20bdd9675a0dd2b1060:<path>`.
- Rebuild worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/BatchAgent/.venv/bin/python3 /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `dnf/cli/commands/repoquery.py` old `68-73` new `68-74` symbol `rpm2py_format, key, lower, we, allow, both, fmt_repl` surface `python_public_api, cli_options, python_api, cli`
- `HUNK-0002` `dnf/cli/commands/repoquery.py` old `76-82` new `77-83` symbol `rpm2py_format, key, fill, lower, fmt_repl` surface `python_public_api, cli_options, python_api, cli`
- `HUNK-0003` `tests/test_repoquery.py` old `125-131` new `125-131` symbol `OutputTest, NAME, version, RELEASE, arch, REPONAME, test_output` surface `tests, cli_options, config_keys`

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

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis.json`

Validate final output with:

`python /home/soong/.agents/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/_repos/dnf/pca-results/de9c5c/analysis.json`
