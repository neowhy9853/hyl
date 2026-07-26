---
name: patch-relation-analysis
description: 分析两个或多个 Git 补丁是否因相同 issue/CVE、backport/cherry-pick/upstream 来源或代码依赖而相关，判断前置依赖和后置依赖，并可对补丁集合进行聚类。用于研究内容一的补丁关联性分析、合入失败后的依赖诊断、重复修复归并和 backport 分析；不负责执行补丁合入或判断目标基线是否受影响。
---

# 补丁关联性分析

分析两个或多个补丁之间是否有关联，以及候选补丁相对于目标补丁是前置依赖、后置依赖还是仅有关联。本 Skill 独立于补丁意图分析：它不判断单个补丁的类型和问题级别，也不执行补丁合入。

## 运行环境

要求 Python 3.10+ 和 Git。附带脚本仅使用 Python 标准库，不要求网络访问。

当输入包含仓库路径和补丁 ID（Git commit ID）时，先运行附带的证据提取脚本：

```bash
python <skill目录>/scripts/analyze_relation.py \
  --repo <仓库路径> \
  --mode pairwise \
  --commit-a <commit-a> \
  --commit-b <commit-b>
```

聚类模式：

```bash
python <skill目录>/scripts/analyze_relation.py \
  --repo <仓库路径> \
  --mode cluster \
  --commits <commit-a> <commit-b> <commit-c>
```

将 stdout 解析为 JSON。非零退出码表示工具失败；stderr 中包含 JSON 错误对象。

## 输入

接受以下输入：

- 仓库路径和两个补丁 ID（Git commit ID），用于 pairwise 分析；
- 仓库路径和一组补丁 ID，用于聚类；
- 调用者直接提供的补丁意图分析 JSON、补丁说明、patch 和关系证据；
- 补丁合入失败日志、缺失符号/API 或冲突信息，作为依赖方向的补充证据。

当仓库和补丁 ID 可用时，优先使用附带脚本获取结构化证据，然后只在必要时使用 Git 做小范围补充检查。

## 工作流

1. 固定分析方向：`commit_a` 是当前目标补丁，`commit_b` 是候选关联补丁。
2. 如果调用者已提供每个补丁的意图分析 JSON，将其作为主要语义输入。
3. 读取目标补丁和候选补丁，收集直接证据。
4. 运行 `scripts/analyze_relation.py` 提取：
   - CVE 标识；
   - `Bugzilla:`、`Closes:`、`Resolves:` 字段和 issue URL；
   - backport、cherry-pick、upstream commit 标记；
   - pairwise 分数和证据；
   - 多补丁输入的连通聚类结果。
5. 比较补丁意图分析 JSON、直接关系证据和合入失败证据。
6. 判断 `commit_b` 相对于 `commit_a` 是否为前置依赖、后置依赖或无依赖。
7. 返回符合输出契约的单个 JSON 对象。

## 使用补丁意图分析 JSON

当输入包含 `patch-intent-analysis` 的结果时，先比较两个补丁的结构化分析，再判断关系。意图分析 JSON 是语义证据，不是 oracle；精确关系标记仍然优先于泛泛语义相似。

优先使用这些字段：

- `patch_type`、`severity`、`full_feature`、`reason`、`severity_reason`、`severity_factors`、`detailed_analysis`、`intent_items`、`evidence`，以及任何显式 `cve`、`bug`、`issue`、`syzbot`、`upstream`、`backport`、`cherry-pick` 或 `fixes` 字段。

判断步骤：

1. 从两个意图分析对象中归一化提取标识：
   - CVE ID；
   - Bugzilla ID；
   - issue URL 或 issue 编号；
   - syzbot/syzkaller 报告 ID；
   - `Fixes:` commit ID；
   - upstream/backport/cherry-pick commit ID。
2. 如果任一分析结果明确说明一个补丁是从另一个补丁 cherry-pick/backport，或二者引用同一个 upstream/source commit，返回 `backport`。
3. 如果二者共享同一个具体 CVE、Bugzilla、syzbot 报告、issue URL 或 issue ID，返回 `same_issue`。
4. 如果 summary/root cause 描述的是同一个具体缺陷，但没有精确标识，返回 `related`；只有证据足够强时才返回 `same_issue`，并说明不确定性。
5. 如果只是 `patch_type` 相同、属于同一大子系统、问题级别相同或漏洞类型相似，不要返回 `same_issue`，应返回 `unrelated` 或 `uncertain`。
6. 如果 Git/脚本证据包含精确 identifier 或 backport marker，用它确认或覆盖基于意图分析 JSON 的推理。

打分建议：

- 直接 A↔B cherry-pick/backport marker：`backport_score = 1.0`；共享 upstream/source commit：`0.85`。
- 共享 CVE：`issue_cve_score = 1.0`；共享具体 issue/Bugzilla/syzkaller：`0.85-0.95`；仅从 summary 推断同一具体缺陷：`0.55-0.75`。
- 共享同一个 `Fixes:` SHA 只作为共同回归来源的弱证据，建议分数 `0.55`；它不足以单独证明 `same_issue` 或前置依赖。
- `overall_score = max(issue_cve_score, backport_score)`。
- 如果关系只来自 `full_feature` 或 `detailed_analysis` 的语义推断，应降低 confidence。

## 判断规则

Pairwise 模式：

- `backport`：一个补丁明确说明从另一个补丁 cherry-pick/backport，或二者引用同一个 upstream source commit。
- `same_issue`：二者引用同一个具体 CVE、bug、issue、Bugzilla、syzkaller 报告或等价 issue URL。
- `related`：存在有意义的共享证据，但弱于 `same_issue` 或 `backport`。
- `unrelated`：没有具体共享 issue/CVE/backport 证据。

依赖方向独立于 `relation_type`，并且固定相对于目标补丁 `commit_a` 判断：

- `commit_b_is_prerequisite`：`commit_a` 需要先合入 `commit_b`，或依赖 `commit_b` 提供的 API/代码/上下文。
- `commit_b_is_subsequent`：`commit_b` 依赖、跟进、补全、回滚或 backport/cherry-pick 了 `commit_a`。
- `mutual_or_series`：两个补丁属于同一补丁系列，但无法确定单一方向。
- `none`：存在关联，但没有证据支持依赖/顺序要求。
- `unknown`：证据不足。

不要只根据提交时间推断依赖。应使用直接标记（`Depends-on`、`Fixes`、`cherry picked from`、`upstream commit`、follow-up、revert 引用）、意图分析、patch/API 证据和合入失败日志。共享 issue 说明二者相关，但不一定说明存在依赖。

合入失败证据的使用规则：

- 当前补丁引用了目标基线不存在、但候选补丁引入的符号/API/结构体字段时，候选补丁可判为 `symbol_or_api` 前置依赖。
- 当前补丁属于明确的 patch series 且候选补丁顺序在前时，可判为 `series` 前置依赖。
- 候选补丁继续修复、补全或回滚当前补丁时，可判为 `follow_up` 或 `revert` 后置依赖。
- 只存在文本冲突或修改同一文件，不足以证明依赖；必须说明缺失能力、顺序要求或后续语义。

高置信证据：

- 完全相同的 CVE ID；
- 完全相同的 Bugzilla/issue/syzkaller URL key；
- `cherry picked from commit <sha>`；
- `upstream commit <sha>`；
- `backport from/of upstream commit <sha>`。

低置信证据：

- 仅属于同一子系统或修改同类文件；
- 标题都包含 “fix”；
- 措辞相似但没有共享标识；
- 指向大量无关 commit 的宽泛 issue 页面。

Cluster 模式中，将 pairwise 分数达到阈值的 commit 连边；无关 commit 保留为 singleton。

## 证据策略

- 补丁 message/body 中的标记优先于标题措辞。
- 精确标识优先于语义相似。
- 没有具体 commit marker 时，不要声称 backport 关系。
- 补丁对象缺失或历史不完整会降低置信度，应报告 warning。
- 除非调用者明确提供检索工具并要求使用，否则不要访问网络。
- 候选集不完整时，只能表述为“未发现依赖”，不能声称“依赖不存在”。

## Pairwise 输出契约

只返回合法 JSON，不添加 Markdown 围栏：

```json
{
  "mode": "pairwise",
  "relation_type": "same_issue | backport | related | unrelated | uncertain",
  "issue_cve_score": 0.0,
  "backport_score": 0.0,
  "overall_score": 0.0,
  "confidence": 0.0,
  "reason": "简短说明",
  "dependency_direction": "commit_b_is_prerequisite | commit_b_is_subsequent | mutual_or_series | none | unknown",
  "dependency_type": "fixes | depends_on | follow_up | backport | cherry_pick | revert | symbol_or_api | series | none | unknown",
  "dependency_reason": "简短说明依赖方向，或说明为什么没有依赖证据",
  "prerequisite_dependencies": [
    {
      "commit": "当 commit_b 是 commit_a 的前置依赖时填写 commit_b",
      "type": "fixes | depends_on | symbol_or_api | series | unknown",
      "summary": "为什么 commit_b 是 commit_a 的前置依赖",
      "evidence": [],
      "confidence": 0.0
    }
  ],
  "subsequent_dependencies": [
    {
      "commit": "当 commit_b 是 commit_a 的后置依赖时填写 commit_b",
      "type": "follow_up | backport | cherry_pick | revert | series | unknown",
      "summary": "为什么 commit_b 是 commit_a 的后置依赖",
      "evidence": [],
      "confidence": 0.0
    }
  ],
  "evidence": [
    "直接证据"
  ],
  "commit_a": "完整 sha 或输入 id",
  "commit_b": "完整 sha 或输入 id"
}
```

## Cluster 输出契约

只返回合法 JSON，不添加 Markdown 围栏：

```json
{
  "mode": "cluster",
  "cluster_threshold": 0.75,
  "clusters": [
    {
      "cluster_id": "cluster_1",
      "commits": ["sha1", "sha2"],
      "relation_summary": "这些 commit 为什么被连接",
      "evidence": []
    }
  ],
  "singletons": ["sha3"],
  "pairwise_edges": []
}
```

`evidence` 保持简短，最多包含五条关键证据。
