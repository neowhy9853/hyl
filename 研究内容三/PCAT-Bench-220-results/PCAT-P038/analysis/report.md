# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/ruby
**基线**: 2c574ca7e2 (Symbol#to_s now returns a frozen string)
**补丁**: aa7b013a0f (Add `rb_nogvl` flag for pending interrupts. #17553)
**Profile**: ruby
**模式**: normal
**分析 worktree**: 已清理

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 15 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 兼容性分析结论

**无兼容性变更**。该补丁为 Ruby C API 添加了 `RB_NOGVL_PENDING_INTR_FAIL (0x8)` 新 flag（Feature #22138），属于纯新增特性。15 个候选变更经语义判定后均确认为非兼容性变更：

### 新增公共 flag（include/ruby/thread.h）
- **新增** `#define RB_NOGVL_PENDING_INTR_FAIL (0x8)`
- 纯新增宏，值 0x8 不与现有 flag（0x1/0x2/0x4）重叠
- 累加修改，既有调用方不受影响

### 内部函数重构（thread.c）
- `unblock_function_set()`: 参数 `fail_if_interrupted` → `flags`；新增 `RB_NOGVL_PENDING_INTR_FAIL` 检查分支
- `blocking_region_begin()`: 参数 `fail_if_interrupted` → `flags`
- `BLOCKING_REGION` 宏: 参数 `fail_if_interrupted` → `flags`；条件改为 `(flags) & RB_NOGVL_FAIL_FLAGS`
- 均为 `thread.c` 内部 static 函数/宏，对既有调用方语义等价

### rb_nogvl() 实现变更
- 公开签名不变
- 新增提前返回路径：仅在新 flag 传入且线程有 pending interrupts 时触发，返回 0 且 errno=0
- `ec`、`th` 变量提升至 scheduler 检查之前，无副作用
- 既有调用方行为完全不变

### 测试/spec 变更
- `spec/ruby/optional/capi/ext/thread_spec.c`: 受 `#ifdef RUBY_VERSION_IS_4_1` 保护
- `spec/ruby/optional/capi/thread_spec.rb`: 受 `ruby_version_is "4.1"` 保护
- 仅 Ruby 4.1+，非当前版本兼容性关注范围

## 产物位置

- 分析 JSON: `pca-results/aa7b01/analysis.json`
- 候选 JSON: `pca-results/aa7b01/candidates.json`
- 补丁文件: `pca-results/aa7b01/patch.diff`
- Profile: `pca-results/aa7b01/effective-profile.yaml`
- 全部产物: `/home/soong/pca_benchmark/_repos/ruby/pca-results/aa7b01/`
