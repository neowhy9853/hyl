---
name: patch-intent-analysis
description: 根据 Git 仓库中指定 commit 的说明和变更内容分析补丁意图，判断补丁类型、问题级别、全量功能和详细分析结论，并以 JSON 返回结构化依据。用于研究内容一的补丁意图分析、单个历史 commit 审查或补丁分析流程接入；调用时必须提供仓库路径和 commit ID。不负责判断目标基线是否受影响、执行补丁合入或分析前置/后置依赖。
---

# 补丁意图分析

根据直接证据分析补丁的主要意图。使用外部 harness 的原生 Git 能力读取补丁；本 Skill 附带的脚本只负责依赖探测和额外静态分析。

## 运行环境

要求 Python 3.10+ 和 Git。附带脚本仅使用 Python 标准库。

环境中没有兼容的系统版本时，在初始化阶段安装一次固定版本的 Universal Ctags：

```bash
python <skill目录>/scripts/install_ctags.py
```

不要在补丁分析过程中运行安装器。安装器只下载当前平台构建，验证 SHA-256 和 JSON 能力，然后保存到用户缓存。

分析前运行：

```bash
python <skill目录>/scripts/check_dependencies.py
```

解析其 JSON 输出。按以下顺序选择静态分析能力：

1. `PATCH_INTENT_CTAGS` 环境变量指定的版本。
2. 用户缓存中安装的固定版本。
3. `PATH` 中的 Universal Ctags。
4. `bin/<操作系统>-<架构>/ctags` 中兼容的可执行文件。
5. 内置 Python AST 和保守的源码模式匹配。

分类过程中不要安装软件包或系统软件。缺少 Ctags 只会降低分析精度，不应阻塞分类。

## 输入

只接受以下两个必填输入：

- `repo`：包含目标 commit 的本地 Git 仓库路径。
- `commit`：目标 commit 的完整 SHA 或可唯一解析的 revision。

使用 harness 提供的结构化 Git 工具或原生 Git 命令，从指定仓库读取 commit message、changed files 和完整 patch。缺少任一输入时停止分析，并要求调用者补充。

## 工作流

1. 解析 `repo` 和 `commit`，读取目标 commit 的 message、changed files 和完整 patch。
2. 总结修改对象、修改内容及其效果。
3. 确定整个 patch 的唯一补丁类型，并应用下面的决策规则。
4. 输出 `full_feature`：用一句话概括这个补丁实际做了什么。
5. 针对全量功能/修改写出 `detailed_analysis`。
6. 根据补丁自身证据判断问题级别。
7. 证据足够时立即停止。只有 patch 缺少必要符号上下文时才运行：

   ```bash
   python <skill目录>/scripts/analyze_commit.py \
     --repo <仓库路径> \
     --commit <commit-id>
   ```

   使用其 JSON 中的 `changed_symbols`、`files` 和 `warnings` 作为辅助证据。

8. 返回符合输出契约的单个 JSON 对象。

以目标补丁为准，不要用更新后的 worktree 推断历史行为。不要只根据关键词或路径分类。

## 补丁类型规则

只返回一个 `patch_type`，取值必须是：

`BugFix`、`CVE`、`Optimize`、`Feature`、`Refactor`、`CleanUp`、`Doc`、`Typo修复`、`TestCode`、`资源泄露&crash补丁`、`其他`。

按以下优先级判断：

1. 修复或缓解 CVE、明确安全漏洞时选择 `CVE`。它优先于普通 BugFix。
2. 主要修复 crash、panic、oops、hang、deadlock、NULL dereference、use-after-free、double free、越界、overflow、memory leak、reference leak、resource leak 时选择 `资源泄露&crash补丁`。如果同时是 CVE，选择 `CVE`。
3. 主要修正拼写、typo、语法、注释措辞或文档措辞时选择 `Typo修复`。
4. 文档、示例、README/RST/Markdown 或文档构建链修改占主导，且产品行为未改变时选择 `Doc`。
5. 修改仅位于测试、fixture、测试脚本、harness、selftests 或 baseline，且产品行为未改变时选择 `TestCode`。
6. 主要改善性能、内存占用、延迟、CPU 开销、IO 行为或避免不必要工作，且不扩展能力时选择 `Optimize`。
7. 新增支持、引入新能力/API/配置/平台行为，或扩展用户、调用者、平台或配置可执行能力时选择 `Feature`。
8. 主要重组实现且保持外部可观察行为不变时选择 `Refactor`。
9. 删除无用代码、简化样式、格式、构建胶水、warning 或维护性代码，且不是具体 bug 修复时选择 `CleanUp`。
10. 修正已有错误行为，但不满足更高优先级的 `CVE` 或 `资源泄露&crash补丁` 时选择 `BugFix`。
11. 以上均不适用时选择 `其他`。

常见边界：

- 恢复预期行为通常是 `BugFix`；扩大能力边界是 `Feature`。
- 修改产品代码并由测试佐证时，按产品代码变化分类，不选 `TestCode`。
- 只修改测试侧是 `TestCode`。
- 仅修正文档错字或措辞是 `Typo修复`；更广泛的文档修改是 `Doc`。
- 不要仅因为标题出现 “fix” 就选择 `BugFix`，必须说明修改前的失败及对应修正。

证据不足时降低置信度。

## 详细分析结论规则

`detailed_analysis` 是针对全量功能/修改的详细分析，不只是重复补丁类型。

必须包含：

- `patch_description`：补丁主要针对什么功能、特性、缺陷、行为或代码路径，具体修改了什么。
- `impact_and_risk`：分析该补丁可能对产品产生的影响和风险。如果没有提供产品基线、版本、配置或使用场景，必须说明无法确认最终产品影响，只能给出潜在影响/风险。
- `trigger_condition`：非必填；当补丁修复 bug/安全/稳定性问题且可以推断触发条件时填写。
- `other_analysis`：非必填；记录不确定性、兼容性关注点、仅测试/文档影响或其他分析备注。

不要编造产品侧暴露面。必须区分“补丁自身问题级别”和“当前产品是否确认受影响”。

## 问题级别规则

只返回一个 `severity`，取值必须是：`致命`、`严重`、`一般`、`提示`。

这里的问题级别是补丁自身的内在问题级别，不是最终产品影响结论；不需要当前产品基线或配置上下文。

按以下规则判断：

1. 远程代码执行、权限提升、认证绕过、不可恢复数据破坏、默认暴露面的高危安全问题、稳定系统/kernel panic、大面积服务不可用，选择 `致命`。
2. 未明确达到 `致命` 的 CVE、use-after-free、越界访问、double free、NULL dereference crash、deadlock/hang、可利用 DoS、信息泄露、可能影响服务的资源/内存泄露、范围有限的数据损坏、重要运行路径中的高概率 crash，选择 `严重`。
3. 普通功能 bug、regression、错误结果、错误处理问题、兼容性问题、性能退化、低概率 crash、平台/驱动特定问题、非关键运行时行为变化，选择 `一般`。
4. 文档、测试、typo、cleanup、格式化、构建/CI 维护、低风险重构、注释或无运行时行为影响的变更，选择 `提示`。

按补丁类型的默认级别：

- `CVE` 默认 `严重`，除非证据支持 `致命`。
- `资源泄露&crash补丁` 默认 `严重`，除非 crash 稳定且系统级可判 `致命`，或明显低风险可判 `一般`。
- `BugFix`、`Optimize`、`Feature`、`其他` 通常为 `一般`。
- `Refactor`、`CleanUp`、`Doc`、`Typo修复`、`TestCode` 通常为 `提示`。

必须输出 `severity_reason` 和 `severity_factors`，使级别判断可审计。如果触发条件不清楚，应降低 confidence。

## 证据策略

- patch 展示的行为变化优先于标题措辞。
- 必须先在指定仓库中解析 commit ID 并检查目标补丁。
- 相似补丁、RAG、调用图和符号分析只能作为直接 patch 的补充。
- 明显补丁默认不超过两次证据收集工具调用。
- 将 `fallback` 静态分析结果视为近似结果，不得据此声称精确调用图或引用关系。
- 只有 harness 已配置语料库和检索工具时才使用 RAG；RAG 不是本 Skill 的运行依赖。

## 输出契约

只返回合法 JSON，不添加 Markdown 围栏或说明文字：

```json
{
  "patch_type": "BugFix | CVE | Optimize | Feature | Refactor | CleanUp | Doc | Typo修复 | TestCode | 资源泄露&crash补丁 | 其他",
  "severity": "致命 | 严重 | 一般 | 提示",
  "full_feature": "一句话概括该补丁实际做了什么",
  "confidence": 0.0,
  "reason": "选择该补丁类型的简短说明",
  "severity_reason": "选择该问题级别的简短说明",
  "severity_factors": {
    "failure_mode": "security | crash | data_corruption | resource_leak | functional_bug | performance | compatibility | docs_test_cleanup | unknown",
    "trigger_condition": "easy | conditional | rare | unknown",
    "runtime_exposure": "runtime | build_time | test_only | docs_only | unknown",
    "blast_radius": "system | service | component | local | none | unknown"
  },
  "detailed_analysis": {
    "patch_description": "补丁主要针对什么功能、特性、缺陷或代码路径做了什么修改",
    "impact_and_risk": "该补丁可能对产品产生的影响和风险；缺少基线/配置上下文时需要说明",
    "trigger_condition": "",
    "other_analysis": ""
  },
  "intent_items": [
    {
      "target": "修改了谁或什么",
      "change": "具体修改内容",
      "effect_or_reason": "产生的效果或修改原因",
      "context_used": [],
      "source_breakdown": {
        "shared_support": [],
        "message_only_details": [],
        "code_only_details": []
      },
      "evidence": [
        "一条直接且关键的证据"
      ]
    }
  ]
}
```

输出限制：

- `patch_type` 必须且只能是一个允许的补丁类型。不要输出 `feat`、`fix`、`docs`、`test`、`refactor` 等旧标签。
- `severity` 必须且只能是一个允许的问题级别。
- `full_feature` 必须是一句简洁描述，说明该补丁的实际修改，不要只重复补丁类型。
- 必须填写 `detailed_analysis.patch_description` 和 `detailed_analysis.impact_and_risk`。
- `trigger_condition` 和 `other_analysis` 不适用时使用空字符串。
- `confidence` 必须位于 `0.0` 到 `1.0`。
- 至少包含一个 `intent_items` 项。
- 默认只使用一个意图项；仅在多个目的同等重要时增加。
- `context_used` 和 `evidence` 各不超过两项。
- `BugFix`、`CVE` 或 `资源泄露&crash补丁` 必须说明修改前哪里失败以及如何修正。
- `Feature`、`Optimize` 或 `Refactor` 必须明确说明用户可见能力是否扩大。
