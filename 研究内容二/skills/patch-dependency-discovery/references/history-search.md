# 按问题查询历史

以下命令用于按需查询 Git 历史。revision 先解析为完整 SHA，路径和符号从 A 的代码取得；每次输出由模型阅读后选择下一步。查询只读，限定授权仓库及可见历史，不 fetch。

## 固定身份

```bash
git -C "$REFERENCE_REPO" rev-parse --verify "$REFERENCE_FIX^{commit}"
git -C "$REFERENCE_REPO" show -s --format='%H %P' "$REFERENCE_FIX"
git -C "$TARGET_REPO" rev-parse --verify "$TARGET_REF^{commit}"
git -C "$REFERENCE_REPO" rev-parse --is-shallow-repository
```

merge commit 必须确认分析哪个 parent。没有修复 commit 而有 patch 时，先核实 reference_parent 与 patch 的对应关系；无法核实就记录缺口。

## 检查目标和参考使用点

```bash
git -C "$REFERENCE_REPO" show "$REFERENCE_PARENT:$SOURCE_PATH"
git -C "$TARGET_REPO" ls-tree -r --name-only "$TARGET_SHA" -- "$TARGET_AREA"
git -C "$TARGET_REPO" grep -n -F -e "$SYMBOL" "$TARGET_SHA" -- "$TARGET_AREA"
```

git grep 返回 1 表示无匹配；其他非零返回需记录错误。目标目录只是初始提示，必要时扩大授权源码搜索范围。

## 查引入、修改和移动

文件疑似尚未引入：

```bash
git -C "$REFERENCE_REPO" log --diff-filter=A --format='%H %s' "$REFERENCE_PARENT" -- "$SOURCE_PATH"
```

函数、宏、字段或关键表达式：

```bash
git -C "$REFERENCE_REPO" log --format='%H %s' -S "$SYMBOL" "$REFERENCE_PARENT" -- "$SOURCE_PATH"
git -C "$REFERENCE_REPO" blame -L "$START_LINE,$END_LINE" "$REFERENCE_PARENT" -- "$SOURCE_PATH"
git -C "$REFERENCE_REPO" log --follow --format='%H %s' "$REFERENCE_PARENT" -- "$SOURCE_PATH"
```

-S 查字符串出现次数变化，可能漏掉次数不变的语义修改。此时使用带转义的 -G 表达式、函数周边历史 diff 或逐条父子查询。blame 的最后修改者也不一定是能力引入者。--follow 一次只查一条路径，rename/copy 的启发式结果需要两侧代码确认。

候选命中后：

```bash
git -C "$REFERENCE_REPO" show -s --format='%H %P%n%B' "$CANDIDATE"
git -C "$REFERENCE_REPO" diff "$CANDIDATE_PARENT" "$CANDIDATE" -- "$SOURCE_PATH"
git -C "$REFERENCE_REPO" show "$CANDIDATE_PARENT:$SOURCE_PATH"
git -C "$REFERENCE_REPO" show "$CANDIDATE:$SOURCE_PATH"
```

文件尚未存在导致 show 失败时，用父提交 ls-tree 验证不存在，区分对象缺失和文件未引入。对不同仓库不要在 target_repo 查询 reference 的 SHA。

## 缩小必要集合

比较候选的提供点、调用点、初始化/清理和构建连接。检查 A 自身新增的 helper，避免把“目标没有但 A 会创建”的代码误当成 B。对于 B 伴随的重构，先考虑目标 API 等价适配；记录采取哪种方案的依据，不靠候选大小猜测必需性。
