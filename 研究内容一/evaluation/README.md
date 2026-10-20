# 补丁分类评测目录

本目录包含研究内容一的分类评测数据、执行脚本、配置，以及逐条结果和轨迹。

首次运行及本次修改与验收记录见 [一键测评说明](ONE_CLICK_GUIDE.md)。

```text
evaluation/
├── README.md
├── data/
│   ├── README.md
│   ├── round_1_50x5.jsonl … round_5_50x5.jsonl
│   └── oracle_commits_8117.jsonl
├── scripts/
│   ├── README.md
│   ├── run_evaluation.py
│   ├── benchmark.py
│   ├── prepare_sanitized_repo.py
│   ├── verify_run.py
│   └── container-entrypoint.sh
├── config/
│   ├── README.md
│   ├── repositories.json
│   ├── label_mapping.json
│   └── opencode.example.json
└── results/
    ├── README.md
    └── round_1/ … round_5/
        ├── results.jsonl
        ├── metrics.json
        └── traces/case_NNN/
```

| 路径 | 内容 |
|---|---|
| [data/](data/README.md) | 五轮各 250 条分类评测记录，以及 8,117 条基础数据 |
| [scripts/](scripts/README.md) | 批量评测、仓库准备、执行结果核验和容器入口脚本；包含运行说明 |
| [config/](config/README.md) | 仓库清单、标签映射和模型服务配置示例 |
| [results/](results/README.md) | 按轮次和案例保存的输入、分类结果、工具轨迹及指标 |

新测评输出目录的核验方法见 [脚本说明](scripts/README.md)。
