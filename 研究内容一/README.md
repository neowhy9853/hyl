# 华为胡杨林——研究内容一：补丁意图分析交付说明

## 项目背景

研究内容一面向来源补丁的语义理解。该阶段只分析补丁自身的说明和代码变化，识别补丁的主要意图、问题级别、完整功能及潜在影响，为后续补丁合入和补丁关联性分析提供结构化输入。

本目录交付一个可独立安装到 OpenCode 等 Agent Harness 的 Skill：`patch-intent-analysis`。目录中不包含 runner、测评代码、测评数据或历史运行结果。

## Skill 概览

| Skill | 用途 | 主要输出 |
|---|---|---|
| `patch-intent-analysis` | 分析单个来源补丁的主要意图 | 补丁类型、问题级别、全量功能、详细分析结论及证据 |

该 Skill 不负责判断目标软件基线是否受影响，不执行补丁合入，也不分析前置依赖和后置依赖。

## 安装

将整个 Skill 目录复制到 OpenCode 的 Skill 目录：

```bash
cp -r patch-intent-analysis ~/.opencode/skills/
```

运行环境要求：

| 依赖 | 要求 | 用途 |
|---|---|---|
| Python | 3.10+ | 运行依赖检查和静态分析脚本 |
| Git | 可用版本 | 读取仓库中的目标补丁 |
| Universal Ctags | 可选 | 提升多语言符号定位精度 |

如果环境中没有兼容的 Universal Ctags，可在安装阶段执行一次：

```bash
python patch-intent-analysis/scripts/install_ctags.py
```

缺少 Ctags 不会阻塞分析，Skill 会回退到 Python AST 和保守的源码模式匹配。

## 使用

在提示词中提供仓库路径和补丁 ID，例如：

```text
使用 $patch-intent-analysis 分析 /data/project 仓库中的补丁 <patch-id>，
返回补丁类型、问题级别、全量功能和详细分析结论。
```

也可以直接提供补丁说明、变更文件列表和 patch 内容。

Skill 返回单个合法 JSON 对象，核心字段包括：

| 字段 | 说明 |
|---|---|
| `patch_type` | 唯一补丁类型 |
| `severity` | 补丁自身的问题级别 |
| `full_feature` | 一句话说明补丁实际做了什么 |
| `detailed_analysis` | 补丁描述、影响及风险、触发条件和其他分析 |
| `intent_items` | 修改对象、修改内容、效果及直接证据 |
| `confidence` | 当前结论的置信度 |

允许的补丁类型为：`BugFix`、`CVE`、`Optimize`、`Feature`、`Refactor`、`CleanUp`、`Doc`、`Typo修复`、`TestCode`、`资源泄露&crash补丁`、`其他`。

问题级别为：`致命`、`严重`、`一般`、`提示`。
