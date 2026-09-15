# 查询证据契约

`output_dir/details/analysis-evidence.json` 由模型随实际工具调用维护。记录可复查的观察结果和来源，不记录私有推理过程；它本身不证明语义判断正确。原始输出优先保存在 `output_dir/details/observations/`，避免终端截断后只剩不可复核的摘要。output_file 为绝对路径或相对于本证据 JSON 所在的 details/ 目录；例如 observations/E-001.txt。同一输出保存一次，多个结论引用同一证据 ID。

结构示意（占位符须替换为实际值）：

```json
{
  "schema_version": "1.0",
  "artifact_type": "patch-port-analysis-evidence",
  "producer": "model-led-tool-observations",
  "inputs": {
    "reference_parent": "完整 SHA",
    "target_commit": "完整 SHA",
    "reference_patch_sha256": "实际补丁哈希"
  },
  "observations": [
    {
      "id": "E-001",
      "purpose": "检查当前父子边是否移动目标实现",
      "tool": "bash",
      "input": {"command": "实际执行的只读命令"},
      "revisions": ["完整 parent SHA", "完整 child SHA"],
      "paths": ["旧路径", "候选新路径"],
      "exit_code": 0,
      "output_file": "observations/E-001.txt",
      "output_sha256": "原始输出文件的实际 SHA256"
    }
  ]
}
```

也可用接收方能访问的 `tool_call_id`/日志定位替代输出文件；没有退出码的工具记录真实状态，不虚构 exit_code。失败或截断的查询如实记录，并补读必要范围。

`port-analysis.json` 的映射项引用 `evidence_ids`，另写简洁的对应关系说明，如“函数抽取到 helper，原调用者仍执行同一边界检查”。查询输出是事实，映射说明是模型判断；不得将模型判断标为脚本验证通过。

每次确认映射后更新当前 commit/path/symbol/range；新读取的声明、调用者和目标检查也使用独立证据 ID。退出分析前核对引用、文件哈希和目标版本一致性。验证阶段重新读取关键证据及源码，不仅检查 JSON 字段。

跨仓库模式：inputs 增加 reference_repo、target_repo；每条 observation 必须增加 `repo_role: reference | target` 和实际 `repo` 绝对路径，revisions 在该仓库内解析。对两侧代码的比较分别引用两条 observation，不把同名路径或 SHA 当作仓库身份。`search_rounds` 引用这些证据并记录返回是否截断；总读取预算包含两侧源码。
