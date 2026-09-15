# 验证产物契约

先运行 `scripts/validate_candidate.py` 生成 `output_dir/details/validation-evidence.json`，默认不生成额外 Markdown 摘要。该文件只证明输入一致性、干净重放、diff 结构与命令运行事实，不能替代安全语义判断。本契约写入 `output_dir/details/validation.json`；面向用户的简短报告写入 `output_dir/VALIDATION_REPORT.md`。跨文件引用使用实际绝对路径，不重复附上已有源码或日志。

```json
{
  "schema_version": "1.0",
  "validation_status": "passed | partial | failed | blocked",
  "target_commit": "完整 SHA",
  "artifact_hashes": {},
  "validation_evidence": "validation-evidence.json 绝对路径",
  "structural_integrity": {
    "status": "passed | failed | blocked",
    "findings": []
  },
  "change_unit_coverage": [],
  "security_invariants": [],
  "target_compatibility": {
    "status": "passed | failed | partial",
    "findings": []
  },
  "build_and_tests": [],
  "regression_risk": {
    "level": "low | medium | high | critical",
    "findings": []
  },
  "failed_findings": [],
  "not_run": [],
  "confidence": 0.0,
  "summary": ""
}
```

`validation-evidence.json` 的 `blocked` 表示输入或目标准备条件不足，`structural_checks.status=not_run` 时未进行重放；`structurally_valid` 保留所有命令的执行状态。无法启动的命令记录 `status=not_run`、`exit_code=null`，并在最终 `not_run` 中说明影响。

每个安全不变量至少记录 reference 证据、候选实现证据、正向路径、负向路径和结论。`passed` 不得包含 failed finding、未覆盖 mandatory unit 或阻塞性 `not_run` 项；脚本的 `structurally_valid` 最多支持 `partial`，不能单独支持 `passed`。

路径检查须独立引用精确目标实现，并提供目标位置对应的语义证据。必要证据缺口未解决时为 `blocked`，错误历史路径为 `failed`，不得统一归因于缺少构建环境。

跨仓库输出补充 `port_mode=cross_repo_semantic`、reference_repo 和 target_repo。验证目标侧安全不变量和 API/构建兼容性，而非参考补丁文本一致性。独立复核 semantic_mapping 两侧代码、差异以及多位置覆盖，并明确记录验证依据和未验证项。
