# Commit 分类评测数据

本目录保存研究内容一历史五轮 `50 × 5` commit 分类数据、8,117 条基础数据，以及评测时用于隔离目标 commit message 的仓库准备脚本。

## 数据文件

`data/` 下包含：

| 文件 | 记录数 | 标签构成 | 说明 |
|---|---:|---|---|
| `round_1_50x5.jsonl` | 250 | 五类各 50 | 由历史 Run 1 的 150 条数据补齐得到 |
| `round_2_50x5.jsonl` | 250 | 五类各 50 | 由历史 Run 2 的 150 条数据补齐得到 |
| `round_3_50x5.jsonl` | 250 | 五类各 50 | 历史 `eval_50_each_v3` 数据 |
| `round_4_50x5.jsonl` | 250 | 五类各 50 | 历史 `eval_50_each_v2` 数据 |
| `round_5_50x5.jsonl` | 250 | 五类各 50 | 历史 Run 5，和 Run 3 使用同一数据文件 |
| `oracle_commits_8117.jsonl` | 8,117 | 八类旧标签 | 严格 commit-message 前缀数据；保留仓库、commit、标签、message、作者和日期，不包含 patch |

五个评测文件共有 1,250 个评测位置，去重后为 926 个 commit。Run 3 和 Run 5 内容完全相同，其他轮次之间也存在交集。

历史评测的五个标签是：

```text
feat, fix, refactor, docs, test
```

其中 `refactor/docs/test` 主要来自 8,117 条基础数据，`feat/fix` 主要来自历史内核数据。因此五轮去重后的 926 个 commit 中，528 个位于 `oracle_commits_8117.jsonl`，另外 398 个不在其中。

这些是旧五分类数据，不是当前 11 类补丁类型的正式金标。Run 1、Run 2 的历史指标来自原始 150 条运行结果，不能直接视为对补齐后 250 条数据的完整评测。

## 仓库复制与 commit message 替换

[`prepare_sanitized_repo.py`](prepare_sanitized_repo.py) 实现以下流程：

1. 从源 Git 仓库创建一个新的 clone，不修改源仓库。
2. 解析目标 commit 的完整 SHA 和原始 commit object。
3. 默认只移除 message 第一行开头的旧分类标签，例如 `feat:`、`fix(scope):`、`docs!:`。
4. 保留 commit object 的原始 headers，因此 tree、parents、author、committer 等信息不变。
5. 写入新的 commit object，并在 clone 中执行 `git replace <原始 commit> <新 commit>`。
6. 校验普通 Git 视图与原始对象的 tree、parents 完全一致。
7. detached checkout 到目标 commit，供 OpenCode 或其他评测程序分析。

创建快速共享 clone：

```bash
python3 prepare_sanitized_repo.py \
  --source-repo /path/to/source/repo \
  --commit <commit-id> \
  --output-repo /tmp/evaluation-repo \
  --clone-mode shared
```

创建不依赖源仓库对象目录的完整 clone：

```bash
python3 prepare_sanitized_repo.py \
  --source-repo /path/to/source/repo \
  --commit <commit-id> \
  --output-repo /tmp/evaluation-repo \
  --clone-mode full
```

使用自定义 message：

```bash
python3 prepare_sanitized_repo.py \
  --source-repo /path/to/source/repo \
  --commit <commit-id> \
  --output-repo /tmp/evaluation-repo \
  --message-file /path/to/replacement-message.txt
```

输出目录必须尚不存在。`shared` 模式速度快，但 clone 依赖源仓库的对象目录；`full` 模式复制 Git 对象，适合需要独立保留的评测仓库。

普通 Git 命令会读取替换后的 message：

```bash
git -C /tmp/evaluation-repo show -s --format=%B <commit-id>
```

`git replace` 是评测视图隔离，不是安全边界。`--no-replace-objects`、`GIT_NO_REPLACE_OBJECTS` 或直接读取原始 object 都能绕过替换。运行评测 Agent 时必须禁止这些绕过方式，也不能把原始标签作为 prompt、文件名或其他元数据暴露给模型。

## 测试

脚本仅依赖 Python 标准库和 Git。运行：

```bash
python3 -m unittest discover -s tests -v
```

测试会创建临时 Git 仓库，验证：

- 源仓库未被修改；
- clone 中普通 Git 视图看到脱敏 message；
- tree 和 parents 未改变；
- checkout 后源码内容保持一致。
