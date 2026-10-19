# PCA 兼容性变更分析报告

**仓库**: https://github.com/golang/go
**基线**: c25263921018fe83cad7916a3bebef020ce9875a^
**补丁**: c25263921018fe83cad7916a3bebef020ce9875a
**Profile**: golang

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 0 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

## 补丁概述

此补丁将回归测试 `issue28698` 从 `src/cmd/compile/testdata/script/issue28698.txt` 迁移至 `test/fixedbugs/issue28698.go`，并增强了软浮点（softfloat）平台的处理逻辑。

### 变更前
- 测试位于 `src/cmd/compile/testdata/script/`，以 txt 脚本形式运行
- 测试无条件运行，在软浮点构建器上会失败

### 变更后
- 测试位于 `test/fixedbugs/`，为标准 Go 独立测试程序
- 增加了 `//go:build !js && !wasip1` 构建约束
- 增加了软浮点平台检测（GO386/GOMIPS/GOMIPS64/GOARM），检测到软浮点则跳过测试
- 强化了测试：不仅验证非软浮点模式下不产生 autotmp，还验证强制软浮点模式下会产生 autotmp

## 兼容性结论

**未检测到兼容性变更。**

此补丁仅修改测试文件（删除 `src/cmd/compile/testdata/script/issue28698.txt`，新建 `test/fixedbugs/issue28698.go`），不涉及任何公共 API、导出符号、CLI 接口、配置文件或运行时行为的变更。

- 变更文件路径均位于 `/test/` 或 `/testdata/` 测试目录下
- 无任何导出符号、结构体、接口或常量发生变化
- 无用户可观察的行为变化

**产物目录**: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-N032/`
