---
name: security-patch-port
description: 编排安全补丁跨版本或无共同历史的跨仓库迁移，先尝试严格直接应用，成功即返回；失败再调用 patch-port-analysis、patch-port-apply 和 patch-port-validation。用于补丁合入、backport、跨分支及跨仓库语义适配。
---

# 安全补丁迁移总控

先检查原补丁能否严格应用到目标版本，能应用则直接合入并返回；需要适配时再执行分析、实施和独立验证。

## 输入

必须提供：

- `repo`：包含目标 revision 和必要历史的本地 Git 仓库。
- `reference_patch`：unified diff 格式的参考修复。
- `target_ref`：需要合入修复的目标漏洞版本。

尽量提供：

- `reference_fix` 和 `reference_parent`；
- `output_dir`，默认使用 `<repo父目录>/patch-port-results/<target短SHA>/`；
- 项目适用的构建、测试和静态检查命令。

`port_mode` 默认为 `history`。无共同历史的跨仓库任务使用 `cross_repo_semantic`，另提供只读 `reference_repo`、`reference_parent`（或可确定父提交的 `reference_fix`）及 `target_repo`；`repo` 统一作为 `target_repo` 的兼容别名。参考 revision 只在参考仓库解析，target_ref 只在目标仓库解析。可提供 `target_hints`（目录、子系统或接口提示）和 `search_budget`。两仓库须已获授权可读；权限不足时报告，不能自行扩大访问范围。

## 子 Skill

严格直接应用失败后，按顺序使用：

1. `$patch-port-analysis`：只读分析，输出 `port-analysis.json`。
2. `$patch-port-apply`：消费分析结果，输出 `generated.patch` 和 `application.json`。
3. `$patch-port-validation`：独立验证候选补丁，输出 `validation.json` 和 `VALIDATION_REPORT.md`。

适配分支中，如果 Harness 不能自动调用其他 Skill，停止并报告缺少相应能力，不要在总控中临时重写三个阶段。

## 产物布局与精简

所有阶段传递同一个 `output_dir`，不要把 `details/` 当成新的 output_dir。直接按以下位置写文件，不在结束时搬动文件或工作树：

```text
<output_dir>/
├── generated.patch
├── final.json
├── port-analysis.json
├── VALIDATION_REPORT.md
├── details/
│   ├── analysis-evidence.json
│   ├── observations/
│   ├── application.json
│   ├── application-evidence.json
│   ├── worktree.json
│   ├── validation.json
│   ├── validation-evidence.json
│   └── validation-observations/
└── candidate-worktree/
```

依赖发现被调用时，其结果、证据及查询日志也写入 details/；未执行的阶段不创建空文件或目录。最终索引仅列出实际存在的产物，缺项和原因写入 summary/warnings。

- `final.json.summary` 不超过 200 字；验证报告以 500 字以内概述修改、已验证项、未验证项和风险，完整检查记录写入 details/。重要失败不得因篇幅限制省略。
- 分析中保留必要历史链、映射与证据 ID，不重复粘贴整段源码或日志；同一查询输出保存一份，由各阶段引用。
- 默认不生成重复的 `VALIDATION_EVIDENCE.md`。精简展示不减少必要定位或验证，也不改变成功判定。
- JSON 中的输入、工作树和跨文件引用使用实际绝对路径；final.json.artifacts 中的相对路径以 output_dir 为基准。analysis-evidence 中的 output_file 以证据 JSON 所在目录为基准。写定文件后计算哈希，后续修改必须更新引用方哈希。
- 保留候选工作树供后续编译和复核，不自动清理。用户要求清理时先确认补丁可重放及无额外未保存修改，再使用 Git 工作树清理流程。

## 状态机

```text
INPUT_READY
  -> STRICT_APPLY_CHECK
     -> 通过：直接应用原补丁 -> SUCCESS (direct_apply)
     -> 不通过：ANALYZED
  -> ANALYSIS_GATE_PASSED
  -> APPLIED
  -> APPLICATION_GATE_PASSED
  -> VALIDATED
  -> SUCCESS
```

分析证实目标 `not_affected` 时进入 `NO_CHANGE`；任何阶段缺少必要条件时进入 `BLOCKED`，确认修复错误时进入 `FAILED`。实施或验证阶段发现目标可能已修复时，返回分析确认目标行为后再决定 `NO_CHANGE`。

## Phase 0：输入和隔离

1. 解析模式及仓库绝对路径，在所属仓库解析各 revision 的完整 SHA。跨仓库模式不要求 merge-base，不 fetch/合并两侧对象来制造共同历史。
2. 确认参考补丁可读、目标对象存在；检查仓库历史完整性并记录浅历史限制。
3. 创建 `output_dir`，把输入摘要写入阶段上下文；不得把产物写入候选补丁的工作树 diff。
4. 禁止提交、推送、改写历史或修改调用者现有 checkout。
5. 跨仓库时参考仓库只读，输出和候选工作树均放在参考仓库之外；实施和验证脚本的 `--repo` 均指向目标仓库。

## 严格直接应用：优先分支

完成输入检查后，先调用本 Skill 的 [scripts/direct_apply.py](scripts/direct_apply.py)：

```bash
python3 <本Skill目录>/scripts/direct_apply.py \
  --repo <目标仓库> \
  --target-ref <目标SHA> \
  --patch <参考补丁绝对路径> --output <output_dir> \
  --port-mode <history或cross_repo_semantic>
```

脚本先用独立索引检查目标提交，再在隔离工作树中执行严格 `git apply --check --index` 和 `git apply --index`，不会修改调用者 checkout。仅严格应用属于此快速分支；忽略空白、recount、3-way 等处理仍属于适配分支。

- 退出码 `0`：直接返回脚本生成的 `final.json`，结束内容二。不再调用分析、依赖发现、独立验证，也不执行构建或测试，不补写语义报告。`generated.patch` 保持原补丁的完整字节。
- 退出码 `10`：原补丁不能严格应用，进入下面 Phase 1–3。预检记录保存在 `details/direct-apply.json`，不将预检失败当作最终迁移失败。
- 其他退出码：执行异常，保留日志并报告失败，不能把异常当作可适配信号。

如果入口已完成本次预检，且 `details/direct-apply.json` 的 `target_commit` 与参考补丁 SHA-256 均匹配当前输入、`status=not_applicable`，直接进入 Phase 1，不重复调用脚本。不要覆盖已有候选或旧运行结果。

直接合入的最终状态是 `success`，`completion_mode=direct_apply`、`verification_scope=patch_application`；门禁记录为 analysis=`not_run`、application=`passed`、validation=`not_run`。这表示原补丁已应用，不表示独立语义评审或项目测试通过。只保存实际生成的产物，不创建 `port-analysis.json`、验证产物或空报告。

## Phase 1：迁移分析（需要适配时）

向 `$patch-port-analysis` 传递全部输入，由模型从参考语义开始逐步查询历史、判断映射并选择上下文。随调查记录 `<output_dir>/details/analysis-evidence.json`，完成后写出顶层 `port-analysis.json`。

定位困难时，由模型继续在授权仓库内检索路径、符号、历史和依赖。确实缺少关键历史对象、源码或访问权限时，记录已查范围、缺失证据及其影响，返回 `blocked`；不凭猜测开始实施。

#### 缺失能力的条件分支

分析或失败诊断发现目标可能缺少参考修复所需的函数、API 或行为时，调用 `$patch-dependency-discovery`，传递参考补丁、两侧仓库与 SHA、能力缺口、失败日志和现有授权范围。读取 `<output_dir>/details/dependency-discovery.json`，将其索引放入最终 artifacts 的 `dependency_discovery` 字段（未调用时省略）。

- 候选发现后返回迁移分析核对目标暴露面、必要修改和完整实施计划；不得把发现状态 complete 当作 Analysis Gate 通过。
- 建议引入新功能但尚未获授权时返回 blocked，并在 summary 中请求明确范围；有目标等价实现时优先评估就地适配。
- 实施或验证失败后触发发现时，先保存失败候选及日志，停止当前实施；不得在旧计划上直接追加未经分析的依赖。
- 若批准并实施依赖，以原目标 SHA、有序补丁哈希和累计 diff 哈希绑定新基线，重新分析原修复，再对组合补丁执行独立验证。未解决依赖、循环或验证缺项不能输出 success。

发现 Skill 无法调用时记录缺失能力及未解决问题。

### Analysis Gate

只有同时满足以下条件才能实施：

- `analysis_status` 是 `ready` 或 `direct_apply_ready`；
- 无未解决的必要证据缺口，目标落点已在精确目标版本确认；
- 已提取漏洞行为和安全不变量；
- 每个 change unit 都属于一个 coupled group，并有明确的目标处置；
- `history` 模式需要连续 map chain 和至少两类定位证据，断点之后及拆分分支均已检查；
- `cross_repo_semantic` 模式按分析 Skill 的跨仓库协议完成分层检索及候选核对，mandatory unit 的 `semantic_mapping` 已确认、目标位置明确、依赖与安全条件有两侧代码证据；不得伪造跨仓库 map chain；
- 已判断目标版本为 `affected`，或者 direct apply 后仍证明安全不变量适配；
- 没有未解决的 `critical` 风险或目标路径歧义。

`not_affected` 有实际目标行为证据才进入 `NO_CHANGE`；过滤范围中的搜索无结果不予放行。其他不满足项进入 `BLOCKED`，不得调用实施 Skill。

## Phase 2：补丁实施

调用 `$patch-port-apply`，要求严格消费 `port-analysis.json`，通过其 `scripts/candidate_workspace.py` 管理独立 worktree、direct apply 和候选补丁收尾，并写出：

- `generated.patch`；
- `details/application.json`；
- `details/application-evidence.json`；
- 保留未提交修改的 `worktree_path`。

### Application Gate

只有同时满足以下条件才能验证：

- `application_status` 是 `candidate_ready`；
- 所有 mandatory change unit 均为 `implemented` 或有经分析允许的 `not_applicable` 证明；
- coupled group 没有部分实施；
- diff 中没有 conflict marker、`.rej`、错误路径新增或无关整文件替换；
- `git diff --check` 通过；
- `generated.patch` 能从干净 `target_ref` 重放。

门禁失败时保持证据，但不得宣称候选补丁成功。

## Phase 3：独立验证

调用 `$patch-port-validation`。要求先运行其 `scripts/validate_candidate.py` 得到干净重放、hash、结构和测试证据，再重新读取 reference patch、分析产物和实际 diff 进行语义审核，不能照抄实施阶段的结论。

### Validation Gate

最终 `SUCCESS` 要求：

- 结构完整性通过；
- 每个安全不变量和 coupled group 均有覆盖证据；
- 目标版本 API、宏、include、锁、错误路径和资源生命周期检查通过；
- 所有已运行的构建和测试通过；
- 未运行的重要验证被明确记录，且不会使总体状态虚假升级为 `passed`；
- `validation_status` 为 `passed`。

`validation_status=partial` 或 `blocked` 时，最终 `status=blocked`；`validation_status=failed` 时，最终 `status=failed`。保留阶段原始状态、证据和未运行原因。门禁的 `failed` 表示未满足放行条件；失败原因由阶段状态和 summary 说明。

## 最终输出

将最终结果保存为 `<output_dir>/final.json`，返回同一合法 JSON 对象（不要在终端重复所有阶段内容）：

```json
{
  "status": "success | no_change | blocked | failed",
  "target_commit": "完整目标 SHA",
  "port_mode": "history | cross_repo_semantic",
  "strategy": "direct-apply | history-trace | semantic-adaptation | none",
  "output_dir": "阶段产物目录",
  "worktree_path": "候选修改所在隔离工作树或空字符串",
  "artifacts": {
    "analysis": "port-analysis.json",
    "analysis_evidence": "details/analysis-evidence.json",
    "patch": "generated.patch",
    "application": "details/application.json",
    "application_evidence": "details/application-evidence.json",
    "validation": "details/validation.json",
    "validation_evidence": "details/validation-evidence.json",
    "report": "VALIDATION_REPORT.md"
  },
  "gates": {
    "analysis": "passed | failed | not_run",
    "application": "passed | failed | not_run",
    "validation": "passed | failed | not_run"
  },
  "summary": "最终结果或具体阻塞原因",
  "warnings": []
}
```

适配分支只有三个门禁全部通过时才能返回 `success`。严格直接应用分支使用前述脚本生成的精简结果契约，不伪造未执行阶段的 passed 状态。
