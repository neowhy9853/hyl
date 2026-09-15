# 模型主导的历史与语义映射

模型负责每次查询、对应关系判断和状态更新。调查从参考补丁及修复前代码开始；工具查询事实，模型解释变化并选择下一步。随过程维护 `analysis-evidence.json`，不先运行整段追踪器。

## 追踪状态

为每个 change unit 维护 `{commit, path, symbol, range, primary_anchor, context_anchors, semantics}`。change/delete 使用修复前待替换代码；纯新增使用插入点两侧代码或 enclosing symbol，不能把修复前不存在的新增行当锚点。

每一步必须记录：

```text
before commit/path/range
-> transition commit 和 parent edge
-> after commit/path/range
-> 变化类型、对应说明和实际查询的 evidence_ids
```

只记录 commit hash 而不比较两侧代码，不算完成映射。

模型确认当前边的对应关系后，更新状态并继续调用 Git/读取工具查下一条变化。`git log`、`git blame` 用于发现候选提交，不直接证明语义对应。

## 分支关系

```bash
git merge-base <reference-parent> <target>
git merge-base --is-ancestor <target> <reference-parent>
git merge-base --is-ancestor <reference-parent> <target>
```

- target 为 reference-parent 祖先：参考侧逐次反向映射。
- reference-parent 为 target 祖先：同分支逐 commit 正向映射。
- 分属不同分支：参考侧回溯到 merge-base，目标侧从 merge-base 正向重放。

参考 fix 为 merge 时先确认 patch 对应哪个 parent。多个 merge-base、缺少共同祖先或浅历史需记录歧义及证据缺口。

## 反向映射

1. 按需对当前 anchor 执行 `git blame -L` 或 `git log`，寻找最近相关修改。
2. 用 `git show -s --format=%P <map>` 核实父提交，再读取该 parent 与 map 的 diff 和两侧源码，判断新增、删除、改写、移动或行号变化。
3. 把 after 状态映射到选定 parent 的 before 状态。
4. 记录查询证据和新状态，由模型决定继续 blame、读下一条 diff 或查调用者。
5. 重复直到 target 或 merge-base。略过无关区间时记录区间范围、路径演化及无相关修改的查询证据；不能仅凭端点相同忽略中间的移出/移回。

## 正向映射

```bash
git rev-list --reverse --ancestry-path <start>..<target>
```

用 name-status、历史 path、symbol 和语义 anchor 筛出相关 commit。对每个相关 commit：

```bash
git diff --find-renames <parent> <commit> -- <path>
git show <parent>:<old-path>
git show <commit>:<new-path>
```

完成 before 到 after 的状态更新后才能继续下一个 commit。merge commit 必须明确 parent edge，并检查是否吸收其他 parent 的相关修改。

`rev-list` 的结果是候选集合，不一定是一条相邻父子链；核实实际 parent 后才能记录 transition。不能默认 first-parent 已覆盖其他分支带入的行为。

## 路径和语义变化

路径失效时组合使用 `git log --follow --name-status`、`git diff --find-renames`、`git ls-tree` 和精确 symbol 搜索。不得假定同名文件属于同一演化链，也不得用 `git checkout <旧提交> -- <path>` 把旧文件写入目标。

路径消失时，先检查目标树和相关提交的路径变化，并在授权仓库内检索后继实现。若仓库不完整、必要对象缺失或权限不足，保存 `blocked_edge`、最后确认状态、已查范围和缺失证据，返回 `blocked`。不得把找到的第一个历史路径当作最终 target 位置。

anchor 被删除或重写时，从 transition diff 中寻找替代实现，再用 enclosing symbol、数据结构、调用者和危险操作建立新 anchor。至少需要两类独立证据。

模型在当前边扩大上下文并解决对应关系后，再查后续变化；不能从断点直接跳到目标宣布完成。拆分时一个状态可对应多个后继位置，为每个位置记录分支标识和承担的安全行为，分别继续追踪；合并时记录所有来源及行为保留情况。存在相似候选时记录排除其他位置的依据，无法消歧则保持 unresolved。

上下文随当前问题选择，可先读局部 diff，再读完整函数、声明、helper、调用者和配置；不必等最终定位成功才扩展上下文。所有搜索绑定具体 revision，避免混入其他版本代码。

## 完成条件

每个 mandatory unit 的相关分支必须到达精确目标 SHA。重新读取目标实现、入口和必要依赖，形成连续 map chain、最终目标位置、至少两类证据及目标漏洞行为解释。任何一项缺失都标记 `unresolved`。
