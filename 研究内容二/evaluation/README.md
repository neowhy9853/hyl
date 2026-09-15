# 补丁迁移评测

提供 Linux 跨版本修复配对数据、重点开源项目补丁配对数据，以及 Linux 评测脚本。

## 数据集

| 文件 | 内容 |
|---|---|
| [linux404.jsonl](linux404.jsonl) | 404 条 Linux 补丁配对记录，包含 385 个不同提交对 |
| [feishu92.jsonl](feishu92.jsonl) | 92 条开源项目补丁配对记录 |
| `patches/<case_id>/` | 开源项目案例的上游参考补丁 `reference.patch` 和供独立评审使用的目标版本标准修复补丁 `oracle.patch` |

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
- `reference_patch`、`oracle_patch`：相对于本目录的补丁路径。
- `reference_sha256`、`oracle_sha256`：当前补丁文件原始字节的 SHA-256。
- `oracle_source_sha256`、`oracle_normalization`（如有）：格式规范化前的原始哈希及处理方式；`crlf_to_lf` 表示仅统一换行，补丁内容逐行保持一致。

源码包类案例的目标基线包含发行版前序补丁。`target_ref` 标识准备后的 Git 提交，`target_tree` 用于核对源码内容。运行这些案例时需提供与目标基线匹配的源码环境；本目录包含配对元数据和补丁文件。

`reference.patch` 用作迁移输入，`oracle.patch` 仅用于独立评审，Agent 另行生成 `generated.patch`。案例编号与 `feishu92.jsonl` 的 `case_id` 对应。

`evaluate_linux.py` 仅接受 Linux 记录格式。开源项目配对数据需自行准备匹配 `target_tree` 的源码环境，再调用迁移 Skill；当前评测器未提供这些案例的批量执行入口。

## 环境

- 完整的本地 Linux Git 仓库，包含所选案例的参考和目标提交。
- Linux 环境、Python 3.10 或更新版本、Git；评测器使用 `fcntl` 文件锁。
- 支持 `run --pure --auto` 的 OpenCode 运行时。
- OpenCode JSON 模型配置和访问凭据。

评测器从 `PATH` 查找 `opencode`，也可通过 `--opencode` 指定可执行文件。通过 `--model` 和 `--judge-model` 指定生成与评审模型。

输出目录应与源码仓库和 Skill 目录分离。每例使用独立源码副本；并发数应结合磁盘、内存和服务容量设置。Git 对象隔离由评测器检查，文件系统和网络隔离由宿主环境提供，可使用受限容器或沙箱部署。

## 流程

1. **准备环境**：导出参考修复和目标基线可达的完整源码及祖先历史，核验提交、文件树和 oracle 对象隔离。
2. **生成补丁**：安装 Skill，由 Agent 分析参考修复、适配目标代码并输出候选补丁及阶段证据。
3. **独立评审**：在准确目标基线上重放候选，结合 oracle 和目标源码核对修复完整性及语义等价性。
4. **汇总结果**：保存逐例结果、执行日志和 `summary.json`。

生成任务只接收参考修复与授权历史；oracle 用于独立评审。评测指标为静态语义正确率，构建和运行测试的结果另行记录。评审响应超时为 240 秒，最多尝试三次。

## 使用

以下命令在项目根目录执行。

准备检查：

```bash
python3 evaluation/evaluate_linux.py \
  --repo /path/to/linux \
  --output /path/to/prepare-check \
  --case-ids 17 \
  --prepare-only
```

执行测评，使用独立输出目录：

```bash
python3 evaluation/evaluate_linux.py \
  --repo /path/to/linux \
  --output /path/to/evaluation-results \
  --config /path/to/opencode.json \
  --workers 4 \
  --allow-model-service
```

`--case-ids 17,19` 选择指定记录；省略时运行全部记录。`--prepare-only` 执行仓库准备和隔离检查。`--allow-model-service` 授权将生成和评审所需代码发送给配置的模型服务。

模型配置支持 `apiKey` 的文件引用和环境变量引用，例如 `{env:MODEL_API_KEY}`。凭据由运行环境提供。正式评测前会检查 OpenCode 的必要命令行参数，检查通过后才准备仓库副本；`--prepare-only` 不要求安装 OpenCode。

## 结果与续跑

- `correct`：候选可应用，独立评审确认修复要求满足。
- `incorrect`：无有效候选、应用失败或修复要求未满足。
- `uncertain`：现有上下文不足以判断语义。
- `*_error`：准备、生成或评审过程发生基础设施错误。

正确率为 `correct / 所选记录总数`。重复执行相同命令可跳过已有结果；`--retry-errors` 为基础设施错误创建新尝试。调整数据、脚本、Skill、运行时或配置后使用新输出目录。续跑协议记录 OpenCode 路径、文件哈希和版本。同一输出目录由文件锁保护。
