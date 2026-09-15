# 输出契约

output_dir 是整次任务的产物根目录；以下两个 JSON 写入 output_dir/details/，查询输出写入 output_dir/details/dependency-observations/。evidence_artifact、输出文件和关系产物引用使用实际绝对路径。未调用本阶段时不生成占位文件。

## dependency-evidence.json

包含 `schema_version=1`、`queries` 数组。每条 query 记录 id、purpose、repository、revision、command、exit_code、输出文件或可访问工具记录引用、scope、truncated。保存真实执行结果；事实与模型解释分开。

所有用于确认依赖的证据 ID 必须指向实际查询。错误、未执行、空结果和截断分别记录，不能都写成“无”。

## dependency-discovery.json

返回单个 JSON。以下字段为必需；空集合用 []，未知 SHA 或未提供值用 null：

- `schema_version`：1。
- `status`：complete / partial / blocked，描述调查完整性；补丁合入结论由迁移验证阶段确定。必要问题仍未解决时用 partial；因输入或权限无法继续时用 blocked。
- `inputs`：reference_repo、reference_fix、reference_parent、reference_patch_sha256、target_repo、target_commit、target_state。原始目标 target_state 可为 null；叠加补丁基线需含 ordered_patch_hashes 和 cumulative_diff_sha256。
- `scope`：reference_history、target_tree_complete、limitations；未知完整性用 null。
- `capabilities`：能力条目数组，每项含 id、required_capability、source_use（含 evidence_ids）、target_presence、target_evidence_ids、target_exposure（affected / not_affected / unknown）、candidates。
- 每个 candidate：repository、commit、provides_evidence_ids、relation（relation_type、dependency_direction、verification_method、artifact）、reference_dependency（confirmed / rejected / unknown）、target_port_requirement（migrate_candidate / adapt_in_target / already_satisfied / feature_expansion / unknown）、necessity_reason、alternative、evidence_ids。
- `dependency_graph`：nodes（id、repository、commit）、edges（from、to、capability_id、evidence_ids）、unresolved。边 from→to 表示 from 必须先于 to；同一 commit 跨仓库仍是不同节点。
- `recommended_action`：return_to_port_analysis / request_scope_approval / collect_more_evidence / repair_environment。
- `implementation_authorized`：表示已知用户授权范围是否覆盖建议；未知时 false。实施还需满足迁移分析门禁。
- `summary`、`warnings`、`evidence_artifact`。

reference_dependency=confirmed 需要 A 使用和 B 提供的直接代码证据；target_port_requirement=migrate_candidate 还需要目标缺少等价能力、目标暴露面为 affected 以及为什么就地适配不合适的说明。无法证明时选择 unknown 或 feature_expansion，不强行提升为必需。

relation.verification_method 为 relation_skill 或 model_code_review；relation_skill 必须有最终关系产物引用，不能只引用标记提取脚本。代码关联可为 related，同时标记分数为 0，两者不矛盾。

不要输出 success、自动可合入或最小依赖集保证。发现阶段可以 complete 且建议 request_scope_approval；complete 只表示本轮问题有证据结论。零候选时说明已查范围，不宣称不存在其他依赖。
