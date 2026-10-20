# 补丁迁移评测目录

本目录包含 Linux 404 条和重点开源项目 92 条评测数据、执行脚本、配置，以及逐条结果与轨迹。首次配置、运行、续跑和核验见 [一键运行指南](ONE_CLICK_GUIDE.md)。

```text
evaluation/
├── README.md
├── ONE_CLICK_GUIDE.md
├── data/
│   ├── README.md
│   ├── linux404.jsonl
│   ├── feishu92.jsonl
│   ├── patches/<case_id>/
│   └── baselines/
├── scripts/
│   ├── README.md
│   ├── run_evaluation.py
│   ├── port_sources.py
│   ├── port_runtime.py
│   ├── port_trace.py
│   ├── verify_run.py
│   ├── verify_saved_results.py
│   └── container-entrypoint.sh
├── config/
│   ├── README.md
│   ├── sources.json
│   └── opencode.example.json
└── results/
    ├── README.md
    ├── linux/
    └── projects/
        # 每组包含 results.jsonl、metrics.json 和 cases/<case_id>/
```

| 路径 | 内容 |
|---|---|
| [ONE_CLICK_GUIDE.md](ONE_CLICK_GUIDE.md) | 环境和模型配置、全量与小样本运行、计分、输出、续跑及故障处理 |
| [data/](data/README.md) | 补丁配对数据、参考与 oracle 补丁，以及恢复准确目标版本所需的基线补充包 |
| [scripts/](scripts/README.md) | 一键执行、源码准备、容器运行、轨迹打包和两类结果核验脚本 |
| [config/](config/README.md) | 公开源码清单与模型服务配置模板 |
| [results/](results/README.md) | 按数据集和案例保存的输入、候选补丁、判定、工具轨迹和指标 |

每个案例目录仅含 `input.json`、`result.json`、`trace.jsonl`。新运行写入调用者指定的项目外目录。评测执行与结果核验脚本统一位于项目的 [`scripts/`](scripts/)，当前交付版本不包含独立的回归测试目录。
