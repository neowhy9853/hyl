# 分类评测数据

| 文件 | 记录数 | 内容 |
|---|---:|---|
| `round_1_50x5.jsonl` | 250 | 第一轮，五类各 50 条 |
| `round_2_50x5.jsonl` | 250 | 第二轮，五类各 50 条 |
| `round_3_50x5.jsonl` | 250 | 第三轮，五类各 50 条 |
| `round_4_50x5.jsonl` | 250 | 第四轮，五类各 50 条 |
| `round_5_50x5.jsonl` | 250 | 第五轮，五类各 50 条 |
| `oracle_commits_8117.jsonl` | 8,117 | 按 commit message 前缀标注的八类基础数据；包含仓库、commit、标签、message、作者和日期，不包含 patch |

五轮使用 `feat`、`fix`、`refactor`、`docs`、`test` 五个标签，共 1,250 个评测位置、926 个不同 commit。第三轮和第五轮使用相同数据，其他轮次之间也有交集；各评测位置分别保存结果和轨迹。

五轮去重后的 commit 中，528 个包含在基础数据文件中，另有 398 个不在其中。`refactor/docs/test` 主要来自基础数据，`feat/fix` 主要来自内核数据。

这些五分类标签不能直接作为当前 Skill 的 11 类人工金标。当前评测入口通过 [`../config/label_mapping.json`](../config/label_mapping.json) 将 Skill 输出映射到五类，具体计分规则见 [脚本说明](../scripts/README.md)。
