---
name: patch-compatibility-utils
description: "统一编排补丁静态兼容性分析和分析驱动的动态测试。处理源码补丁、diff、commit 或 PCA 分析结果；当请求包含兼容性变更、补丁兼容性、影响分析、兼容性测试、定向测试、测试入口、回归验证、契约验证、覆盖率、复现、patch compatibility、impact analysis、directed testing、reproducer、contract verification 或 patch coverage 等词时使用。仅要求判断或分析时路由到 patch-compatibility-analysis，明确要求测试、验证、复现或覆盖率时路由到 patch-compatibility-testing，同时要求分析和测试时先分析再测试。"
---

# Patch Compatibility Utils

将补丁兼容性工作拆成两个可独立运行、通过稳定产物协议衔接的子 skill：

- `patch-compatibility-analysis/SKILL.md`：只做静态兼容性分析，生成 `analysis.json`、`report.md` 和证据产物，不运行动态测试。
- `patch-compatibility-testing/SKILL.md`：读取已完成的 `analysis.json`，生成测试入口和定向输入，执行 before/after 契约验证与补丁行覆盖率测试，并从固定 JSON 自动渲染报告。

测试子 skill 对分析 schema 中的 13 个 `compatibility_type` 使用同一注册表
逐类规划入口、输入和契约；遇到未知类型必须失败，不能降级为通用测试。

将包含本文件的目录视为 `UTILS_SKILL_DIR`。完成路由后，直接读取
`${UTILS_SKILL_DIR}/patch-compatibility-analysis/SKILL.md` 或
`${UTILS_SKILL_DIR}/patch-compatibility-testing/SKILL.md`；不要求两个子 skill
另行注册为顶层 Skill。只有用户需要按子 Skill 名称直接调用时，才为它们创建额外发现入口。

## 路由

1. 用户只要求分析、评审、识别影响或分类兼容性变化时，读取并执行 `patch-compatibility-analysis/SKILL.md`。
2. 用户提供 `analysis.json` 或分析产物目录并要求测试、验证、覆盖率或复现时，读取并执行 `patch-compatibility-testing/SKILL.md`。
3. 用户只提供 repo 与 patch，但直接要求测试时，先执行分析子 skill 生成有效 `analysis.json`，随后直接执行测试子 skill；用户已经明确要求测试，不重复询问。
4. 用户要求先分析、未明确要求测试时，分析完成并汇报结果后必须询问：`补丁兼容性分析已完成，是否继续基于该分析结果进行定向测试？` 在得到肯定答复前不启动动态测试。
5. 用户同时明确要求分析和测试时，顺序执行两个子 skill，不在中间重复询问。

## 触发词与路由优先级

按语义匹配，不要求逐字一致。出现多组词时按以下优先级路由：

1. 同时包含分析和测试动作，例如“分析这个补丁并验证兼容性”，依次运行分析和测试。
2. 包含明确执行动作，例如“测试、验证、复现、跑一下、覆盖率、测试入口、before/after、contract”，选择测试；如果没有 `analysis.json`，测试子 skill 先调用分析。
3. 只包含“兼容性变更、兼容性影响、接口变化、行为变化、API/ABI 变化、影响分析、review”等判断性词汇，选择分析。
4. 只有“兼容性变更”而没有动作词时，默认选择分析。

| 用户意图/关键词示例 | Skill |
|---|---|
| `兼容性变更`、`兼容性影响`、`补丁分析`、`API/ABI 变更`、`行为变化`、`impact analysis`、`compatibility review` | `patch-compatibility-analysis` |
| `兼容性测试`、`验证兼容性变更`、`定向测试`、`测试入口`、`回归验证`、`契约验证`、`覆盖率`、`复现`、`directed testing`、`reproducer`、`patch coverage` | `patch-compatibility-testing` |
| `先分析再测试`、`分析并验证`、`analyze and test` | 先 analysis，后 testing |

## 子 skill 交接协议

分析阶段是测试阶段的前置依赖，但两个子 skill 可分别触发。交给测试阶段的最小输入为：

- `<ANALYSIS_RESULT_DIR>/analysis.json`
- `<ANALYSIS_RESULT_DIR>/patch.diff`
- `analysis.json.repo`、`analysis_repo`、`base_commit`、`artifact_dir`、`findings[]`

先用分析子 skill 的 `scripts/validate_analysis.py` 校验 `analysis.json`。如果 `analysis_repo` 已清理，先用其 `scripts/orchestrator.py --ensure-worktree` 重建。测试产物默认写入 `<ANALYSIS_RESULT_DIR>/compatibility-testing/`，除非用户指定其他目录。

分析子 skill 不生成新的 `test-entry-work/`。测试子 skill 负责在自己的结果目录中规划、生成和验证入口；旧 `analysis.json` 若仍引用历史入口，只将其作为 provenance，并把可用内容迁入测试结果目录后再执行。

## 完成条件

- 分析完成：`analysis.json` 校验通过，分析摘要和实际产物目录已报告，并按路由规则询问是否继续测试。
- 测试完成：`test-summary.json` 通过 `finalize_test_report.py` 校验并自动生成 `COVERAGE_REPORT.md`，明确区分 passed、failed、partial、blocked 和未执行项，且所有覆盖率结论均有实际工具输出支撑。
