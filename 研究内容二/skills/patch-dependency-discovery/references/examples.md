# 案例与验收场景

## Linux F2FS 压缩写入

输入只给 A=8e8542437bb4070423c9754d5ba270ffdbae8c8d，target=005f9cdab70c915702254c5eb67a8efced80e821，以及允许读取的 Linux 仓库。不要把答案 B 写进检索输入。

1. 从 A 的 diff 提取 compress.c / f2fs_write_compressed_pages 锁协议。
2. 查看 target 文件、符号和相关非压缩写入路径，区分缺少压缩功能与目标是否受影响。
3. 从 A 的 parent 查文件创建历史，读取候选父子 diff。
4. 找到 4c8ff7095bef64fc47e996a938f7d57f9e077da3 提供压缩实现，确认 A 修复的函数由它引入。
5. 关系为 related / commit_b_is_prerequisite / symbol_or_api；reference_dependency=confirmed。
6. 目标没有压缩功能不自动推出必须迁移整个 B。未授权新增功能时，target_port_requirement=feature_expansion，recommended_action=request_scope_approval；目标暴露面仍由迁移分析根据实际代码判断。

检索输入使用参考补丁与目标版本；依赖结论以实际使用点、能力提供方和目标等价实现的代码证据为依据。

## 反例检查

| 输入情形 | 应作出的判断 |
|---|---|
| B 和 A 改同一文件，但 B 只改注释 | 排除 B，不因路径重叠确认依赖 |
| B 创建 foo，目标已有改名后的等价实现 bar | 优先 adapt_in_target 或 already_satisfied，不要求重引 foo |
| A 自己新增 helper，生成候选时漏了它 | 实施遗漏，返回迁移分析修正原候选 |
| 构建日志只有 make/bc/libelf 缺失 | repair_environment，不搜索成 Git 前置提交 |
| API 名字存在但错误返回或锁语义不同 | present_incompatible，追踪相关行为变化而非只查声明 |
| reference 历史浅克隆或关键父对象缺失 | 保留 unknown 与查询错误，不能断言引入提交 |
| 只有功能缺失，没有目标暴露面证据 | feature_expansion/unknown，不自动 no_change 或 migrate_candidate |
| 两仓库无共同历史 | 在参考仓库追踪来源，在目标仓库判断等价能力；不伪造 ancestry |
| 递归发现 B 需要 C，C 又指回 B | 保留循环 unresolved，不产生可执行拓扑顺序 |

