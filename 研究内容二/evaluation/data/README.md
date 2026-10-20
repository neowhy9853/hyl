# 评测数据

| 文件 | 内容 |
|---|---|
| [linux404.jsonl](linux404.jsonl) | 404 条 Linux 补丁配对记录，包含 385 个不同提交对 |
| [feishu92.jsonl](feishu92.jsonl) | 92 条开源项目补丁配对记录 |
| `patches/<case_id>/` | 上游参考补丁 `reference.patch`、目标修复 `oracle.patch`，以及按需提供的规范重放补丁 `oracle-replay.patch` |
| `baselines/` | 87 条项目案例的增量 Git 基线包，用于恢复固定目标提交和源码树 |

### Linux

每条记录包含：

- `case_id`：样本标识。
- `cve`：漏洞编号。
- `source_commit`：参考修复提交。
- `oracle_commit`：目标版本的已知修复提交。

目标基线为 `oracle_commit` 的父提交，参考基线为 `source_commit` 的父提交。两个修复提交均须具有唯一父提交。

样本按原始记录计分，重复提交对保留各自记录。配对数据可通过提供的 Linux Git 仓库解析为源码和补丁。

### 开源项目

每条记录包含：

- `case_id`、`package`、`version`（如有）：样本及项目版本。
- `source_commit`：参考修复提交。
- `target_ref`、`target_tree`：目标基线的提交和 Git tree 标识。
- `reference_patch`、`oracle_patch`：相对于 `data/` 目录的补丁路径。
- `reference_sha256`、`oracle_sha256`：当前补丁文件原始字节的 SHA-256。
- `oracle_source_sha256`、`oracle_normalization`（如有）：格式规范化前的原始哈希及处理方式；`crlf_to_lf` 表示仅统一换行，补丁内容逐行保持一致。

源码包类案例的目标基线包含发行版前序补丁。`target_ref` 标识准备后的 Git 提交，`target_tree` 用于核对源码内容。统一评测入口结合公开上游历史和本目录的基线补充包，自动恢复并校验这些目标。

`reference.patch` 用作迁移输入，`oracle.patch` 仅用于独立评审，Agent 另行生成 `generated.patch`。案例编号与 `feishu92.jsonl` 的 `case_id` 对应。

[`../scripts/run_evaluation.py`](../scripts/run_evaluation.py) 覆盖两组全部 496 条，依据 [`../config/sources.json`](../config/sources.json) 自动下载源码并还原、校验目标基线。`baselines/` 保存 87 条项目案例的增量 Git 基线包；8 个案例另含 `oracle-replay.patch`，用于重现原 oracle 在准确目标上的相同结果树，原始 `oracle.patch` 保留。详细规则见 [一键运行指南](../ONE_CLICK_GUIDE.md)。
