# 评测配置

| 文件 | 用途 |
|---|---|
| `repositories.json` | 数据中仓库名称到 Git URL 的映射，用于下载和核验源码对象 |
| `label_mapping.json` | 当前 Skill 的 11 类输出到五分类评测标签的映射及计分约定 |
| `opencode.example.json` | OpenAI-compatible 模型服务配置示例 |

评测器默认读取本目录的仓库清单和标签映射，可通过 `--repositories`、`--mapping` 覆盖。模型服务配置由 `--config` 指定；实际凭据由运行环境提供，不写入示例文件。运行方式见 [脚本说明](../scripts/README.md)。

一键运行示例默认读取本目录的 `opencode.example.json`。使用前设置并导出 `MODEL_BASE_URL`、`MODEL_API_KEY`，并确认模型 ID 与服务一致；需要修改模板时可复制到项目外的个人配置目录。通过 `EVAL_CONFIG` 变量指定该文件（文档命令将其传给 `--config`），通过 `EVAL_OUTPUT` 指定项目外的输出目录（传给 `--output`）。这两个变量是文档中的 shell 约定，不是执行器自动读取的环境变量。完整步骤见 [一键测评说明](../ONE_CLICK_GUIDE.md)。
