# 评测脚本

统一运行入口为 `run_evaluation.py`。环境配置、完整命令、计分、续跑和故障处理见 [一键运行指南](../ONE_CLICK_GUIDE.md)。以下路径和命令均相对于 `研究内容二/`。

| 文件 | 用途 |
|---|---|
| `run_evaluation.py` | 编排全部 496 条或指定案例的准备、生成、独立评分与汇总 |
| `port_sources.py` | 下载公开源码、还原固定基线、校验 oracle，并导出生成模型可见的独立仓库 |
| `port_runtime.py` | 解析模型配置，管理 Docker/OpenCode 会话、凭据传递和日志脱敏 |
| `port_trace.py` | 保存每例输入、结果和自包含 trace，校验三文件及证据哈希 |
| `verify_run.py` | 核验一键入口新输出的 schema 2 案例、轨迹和统计 |
| `verify_saved_results.py` | 核验仓库随附固定 496 条结果的 schema 1 轨迹和交付统计 |
| `container-entrypoint.sh` | 向独立会话安装镜像中的 Skill 并启动 OpenCode |

两类核验入口处理不同输出格式，分别用于新运行和交付结果，不能互换。

```bash
python3 evaluation/scripts/run_evaluation.py --help
python3 evaluation/scripts/verify_run.py --output /absolute/path/to/new-run
python3 evaluation/scripts/verify_saved_results.py
```

公共模块由统一入口调用，无需逐个运行。
