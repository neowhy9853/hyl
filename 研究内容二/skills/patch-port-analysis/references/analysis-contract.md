# 分析产物契约

分析写入 output_dir/port-analysis.json；证据写入 output_dir/details/analysis-evidence.json。inputs.analysis_evidence 使用证据文件的实际绝对路径。保留必要 map_chain、差异和证据引用，不在每个 unit 中重复整段查询输出。

模型在调查过程中维护 `analysis-evidence.json`，记录实际查询的版本、命令或工具输入、结果引用和退出状态；模型的映射判断写入 `port-analysis.json` 并引用对应证据。证据结构见 [查询证据契约](analysis-evidence.md)。

`port-analysis.json` 必须包含：

```json
{
  "schema_version": "2.0",
  "analysis_mode": "model-led",
  "port_mode": "history | cross_repo_semantic",
  "analysis_status": "ready | direct_apply_ready | not_affected | blocked | failed",
  "repository_scope": {},
  "missing_context": [],
  "approved_new_paths": [],
  "inputs": {
    "repo": "绝对路径",
    "reference_patch": "绝对路径",
    "reference_fix": "完整 SHA 或空字符串",
    "reference_parent": "完整 SHA 或空字符串",
    "target_commit": "完整 SHA",
    "analysis_evidence": "analysis-evidence.json 绝对路径",
    "analysis_evidence_sha256": "实际文件 SHA256"
  },
  "reference_semantics": {
    "vulnerable_behavior": "",
    "trigger_condition": "",
    "security_invariants": [],
    "sensitive_operations": []
  },
  "direct_apply_probe": {
    "strategies": [],
    "recommended": "strict | recount | whitespace | three-way | three-way-whitespace | none",
    "semantic_fit": false,
    "reason": ""
  },
  "change_units": [],
  "coupled_groups": [],
  "target_exposure": {
    "status": "affected | not_affected | uncertain",
    "evidence": []
  },
  "implementation_plan": [],
  "validation_plan": [],
  "risk_assessment": {
    "level": "low | medium | high | critical",
    "factors": []
  },
  "confidence": 0.0,
  "warnings": []
}
```

每个 `change_units` 项至少包含：

```json
{
  "id": "CU-001",
  "coupled_group": "CG-001",
  "mandatory": true,
  "intent": "该修改建立的局部安全语义",
  "reference_location": {
    "path": "",
    "symbol": "",
    "line_range": "",
    "anchors": []
  },
  "dependencies": [],
  "map_status": "direct | mapped | not_applicable | unresolved",
  "map_chain": [],
  "target_location": {
    "path": "",
    "symbol": "",
    "line_range": ""
  },
  "location_evidence": [],
  "target_behavior": "",
  "required_context": [],
  "adaptation": ""
}
```

规则：

- `ready` 不得包含 `unresolved` mandatory unit。
- `missing_context` 记录证据缺口。每项包含 `unit_id`、`status`（`pending | resolved`）、`reason`、`searched_scope` 和 `evidence_ids`；跨仓库时另标明仓库身份及 revision。无缺口时为空；解决缺口须引用实际查询证据。`ready/direct_apply_ready` 不得包含未解决的必要缺口。
- `not_affected` 必须引用实际目标实现或完整相关范围的证据；路径过滤下的搜索无结果不足以支持该结论。
- `approved_new_paths` 默认空；仅允许有功能性新增理由及目标构建接入证据的新文件，不能批准重建已过滤或迁移的历史实现来绕过定位。
- `location_evidence` 至少两项，除非 `map_status=direct` 且 path/symbol/blob 均未演化。
- 同一 coupled group 的 mandatory units 必须具有一致的实施决策。
- `confidence` 必须位于 0 到 1。
- `analysis_evidence_sha256` 必须与实际证据文件一致，证据 ID 必须存在并指向实际工具查询。
- `map_chain` 每条记录含 before/after 状态、direction、明确的 parent/child 或有证据的跳过区间、映射结论及 `evidence_ids`。前后状态须衔接；多个后继实现用独立分支标识记录，不能只保留最相似的一处。
- 遇到断点时保存已确认状态和候选；证据充分才能更新该边，之后继续调查直至 target。最终 ready 的依据不能只是将 unresolved 改成 mapped。

## cross_repo_semantic 扩展

此模式以语义对应替代跨仓库 map_chain 条件；`map_chain=[]`，`map_status=mapped` 表示语义映射已确认，不表示有共同历史。

- `inputs.reference_repo`、`inputs.target_repo` 为不同仓库的绝对路径，`inputs.repo=inputs.target_repo`；reference_parent/fix 属于参考仓库，target_commit 属于目标仓库。
- `repository_scope` 分别记录 `reference` 和 `target` 的可见范围、revision 与元数据，不假设任一仓库完整。
- 顶层 `reference_signature` 保存有代码证据的检索线索；`search_budget` 保存限制及累计用量；`search_rounds` 保存查询 evidence_ids、目录、候选 ID、保留/排除原因及停止原因。
- 每个 unit 增加如下 `semantic_mapping`。target_location 仍为主要实施落点；多个必须修改位置拆成耦合 units，防止路径收尾遗漏。

```json
{
  "semantic_mapping": {
    "status": "confirmed | unresolved | not_applicable",
    "reference": {"repo_role": "reference", "commit": "SHA", "path": "", "symbol": ""},
    "targets": [{"repo_role": "target", "commit": "SHA", "path": "", "symbol": ""}],
    "behavior_correspondence": "输入、危险操作、guard 与错误路径的对应",
    "differences": [],
    "evidence_ids": ["E-001", "E-002"]
  }
}
```

ready 要求 mandatory units 的映射 confirmed，相关目标位置可读且依赖闭合。找不到候选或预算耗尽时仍是证据不足，不得输出 no_change。semantic_mapping 的声明和两侧证据须由验证阶段独立复核，字段齐全不证明语义正确。
