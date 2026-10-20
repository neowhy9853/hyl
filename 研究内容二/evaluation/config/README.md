# 评测配置

| 文件 | 用途 |
|---|---|
| `sources.json` | Linux 与 92 条项目案例的公开源码来源、固定提交与文件树、基线补充包和 oracle 重放哈希 |
| `opencode.example.json` | 支持工具调用的 OpenAI-compatible 模型服务配置模板；服务地址与凭据通过环境变量或外部文件提供 |

首次配置、模型选择和运行参数见 [一键运行指南](../ONE_CLICK_GUIDE.md)。源码清单与数据中的固定提交和文件树相互核对，不能替换为近似版本。基线补充包位于 `data/baselines/`，不包含模型生成候选或评分答案。
