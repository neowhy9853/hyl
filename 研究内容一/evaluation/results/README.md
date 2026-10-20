# 补丁分类评测结果目录

本目录包含五轮补丁分类评测数据，每轮 250 个案例，共 1250 个案例。

## 目录结构

```text
results/
├── README.md
└── round_1/ … round_5/
    ├── results.jsonl
    ├── metrics.json
    └── traces/
        └── case_001/ … case_250/
            ├── input.json
            ├── result.json
            ├── events.jsonl
            ├── metadata.json
            └── runtime.jsonl       # 部分案例包含
```

## 文件说明

| 文件或目录 | 内容 |
|---|---|
| `round_N/` | 第 N 轮评测的结果、指标和案例轨迹 |
| `round_N/results.jsonl` | 本轮全部案例的结果，每行一个 JSON 对象 |
| `round_N/metrics.json` | 本轮准确率、分类别 Precision、Recall、F1、混淆矩阵及轨迹统计 |
| `round_N/traces/case_NNN/` | 本轮第 NNN 个案例的输入、结果和运行记录 |
| `input.json` | 仓库、目标提交、任务提示词和来源信息；`task_input` 为任务输入，`evaluation_reference` 为评分用 oracle 标签 |
| `result.json` | 单条分类结果，包含预测标签、oracle 标签、是否正确、运行状态，以及 `parsed_candidate` 中的置信度和分类依据；与本轮 `results.jsonl` 中的对应记录一致 |
| `events.jsonl` | 运行事件、工具调用参数与输出、可见模型文本和最终答案，每行一条事件 |
| `metadata.json` | 案例与会话标识、事件数量、工具调用统计及文件索引 |
| `runtime.jsonl` | 运行器发出的事件记录，仅部分案例包含 |
