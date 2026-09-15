# 实施产物契约

本契约写入 output_dir/details/application.json；脚本证据写入 output_dir/details/application-evidence.json，工作树元数据写入 output_dir/details/worktree.json。generated.patch 和 candidate-worktree/ 仍在 output_dir 根目录。所有文件引用使用实际绝对路径，补丁、分析和证据哈希绑定写定后的文件。

```json
{
  "schema_version": "1.0",
  "application_status": "candidate_ready | blocked | failed",
  "port_mode": "history | cross_repo_semantic",
  "strategy": "direct-apply | history-trace | semantic-adaptation | none",
  "target_commit": "完整 SHA",
  "analysis_path": "port-analysis.json 绝对路径",
  "application_evidence": "application-evidence.json 绝对路径",
  "application_evidence_sha256": "",
  "worktree_path": "隔离工作树绝对路径",
  "generated_patch": "generated.patch 绝对路径",
  "generated_patch_sha256": "",
  "changed_files": [],
  "unit_ledger": [
    {
      "unit_id": "CU-001",
      "coupled_group": "CG-001",
      "status": "implemented | not_applicable | blocked",
      "target_location": "path:symbol",
      "implementation_summary": "",
      "diff_evidence": []
    }
  ],
  "coupled_group_coverage": [],
  "self_checks": [],
  "replay_check": {
    "status": "passed | failed | not_run",
    "detail": ""
  },
  "warnings": []
}
```

规则：

- `candidate_ready` 要求所有 mandatory unit 已实施或有分析阶段认可的 `not_applicable` 证明。
- coupled group 不能部分成功。
- 有未解决 `missing_context` 时必须 `blocked`。目标不存在的路径只有经分析明确批准的功能性新增才可创建；重建缺失历史实现不属于功能性新增。
- `generated_patch` 必须以 `target_commit` 为基线。
- 跨仓库时记录 `target_repo`，候选 worktree 必须属于该目标仓库，参考仓库保持只读。每个已实施 unit 引用 semantic_mapping 的证据；参考路径不作为目标修改路径。
- `generated_patch_sha256` 必须与实际候选 patch 一致，供独立验证阶段拒绝产物替换。
- 自检失败、重放失败或存在未解决 unit 时不得输出 `candidate_ready`。
- `scripts/candidate_workspace.py finalize` 只生成结构化 `application-evidence.json`；Agent 必须独立补齐 unit ledger 和 coupled-group 覆盖后才能生成本契约。
