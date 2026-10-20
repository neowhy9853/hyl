# 补丁迁移评测结果

本目录按 Linux（404 条）和重点开源项目（92 条）组织，共 496 个案例。

```text
results/
├── README.md
├── linux/
│   ├── results.jsonl
│   ├── metrics.json
│   └── cases/<case_id>/
│       ├── input.json
│       ├── result.json
│       └── trace.jsonl
└── projects/
    ├── results.jsonl
    ├── metrics.json
    └── cases/<case_id>/
        ├── input.json
        ├── result.json
        └── trace.jsonl
```

## 案例文件

| 文件 | 内容 |
|---|---|
| `input.json` | 任务提示词、仓库与目标版本、参考提交及补丁全文、对应数据集记录；`task_input` 是生成输入，`evaluation_reference` 是独立评分参考，包含 oracle 补丁 |
| `result.json` | 实际输出和评测结果；`candidate_patch.text` 保存完整候选补丁，另含判定、计分依据、补丁哈希、结果树标识和 `trace_file` |
| `trace.jsonl` | 生成事件、用于最终判定的评审及其各次尝试、代码查询与测试证据、阶段产物和运行记录 |

无有效候选时，`candidate_patch.text` 为空，原因由结果和轨迹记录。`decision_basis` 的 `result_tree_identical` 表示候选与 oracle 在同一目标基线上得到相同完整结果树，`agent_semantic_review` 表示采用独立功能修复语义评审，`no_candidate` 表示没有有效候选。是否执行编译、测试及其具体结果以案例轨迹为准。

## Trace 格式

`trace.jsonl` 每行是一个 JSON 对象，使用 `record_type` 区分：

| 类型 | 内容 |
|---|---|
| `manifest` | 第一行，记录案例标识、会话与事件统计、证据路径索引、事件校验值及嵌入文件的位置 |
| `generation_event` | `event` 保存一条生成事件，`index` 保留原始事件顺序；包含工具调用、工具输出及模型可见文本 |
| `artifact` | `path` 标识证据或评审记录的逻辑路径，`content` 保存原内容；附编码、字节数和 SHA-256 |

`artifact` 的 `encoding` 为 `utf-8` 或 `base64`；相同内容只存一份，其他记录通过 `content_ref` 引用前面已出现的逻辑路径。这些路径是 trace 内部索引，不是独立的磁盘文件。

生成事件按原顺序排列，证据记录按逻辑路径组织；不能将整个 JSONL 的排列顺序理解为跨生成和评审的统一时间线。

常用证据路径包括：

- `review/result.json`：支撑最终评分的评审结论。
- `review/attempts/<attempt>/agent-review/`：评审任务、逐轮请求响应、对话和查询证据；部分案例包含。
- `comparison.json`、`tree-evidence/`：补丁应用与结果树核验记录。
- `generation/artifacts/`：分析、实施、验证阶段的产物、代码片段及日志。

`input.json` 内的 `selected_review_task` 以及 trace 中元数据涉及的证据路径，通过 `artifact.path` 查找。`candidate.patch`、`oracle.patch`、`generation/prompt.txt` 分别对应结果中的候选补丁、输入中的 oracle 和任务提示词，其位置见首行的 `embedded_files`。

## 分组文件与校验

每组的 `results.jsonl` 每行保存完整的案例结果，与相应 `result.json` 一致；`metrics.json` 保存该组的数量、判定分布和准确率。数据集位于 [`../data/`](../data/README.md)。

[`../scripts/verify_saved_results.py`](../scripts/verify_saved_results.py) 核验样本覆盖、输入与输出、trace 事件和证据哈希、逐例判定及分组指标，并输出总体统计。从 `evaluation/` 目录运行：

```bash
python3 scripts/verify_saved_results.py
```
