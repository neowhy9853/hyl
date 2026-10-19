# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/grub2
**分析仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P061/_worktrees/patched
**基线**: d84e4091ed0c581ac647a0019c1ee82227d77949^ (cb5cfe9cc6bd6ad1aaed2fc1cb3ad2975401edf4)
**补丁**: d84e4091ed0c581ac647a0019c1ee82227d77949
**Profile**: grub2
**产物目录**: /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P061

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: SIDE_EFFECT_CHANGE（副作用变更）

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: systemd-integration.sh grubenv menu_show_once
- **旧代码位置**: util/systemd/systemd-integration.sh.in:4-6
- **新代码位置**: util/systemd/systemd-integration.sh.in:4-11
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
仅设置 `menu_show_once_timeout=$TIMEOUT` 到 grubenv。使用旧版 grub.cfg（仅检查 `menu_show_once` 而非 `menu_show_once_timeout`）的用户可能看不到启动菜单或菜单行为不正确。

### 变更后行为
同时设置 `menu_show_once_timeout=$TIMEOUT` 和 `menu_show_once=1`。对于新版 grub.cfg，`menu_show_once_timeout` 会覆盖 `menu_show_once` 的固定 60 秒超时，行为不变。对于旧版 grub.cfg，`menu_show_once=1` 确保启动菜单能正确显示。

### 兼容性影响
该脚本新增了对 grubenv 的写入操作（设置 `menu_show_once=1`），这是一个新增的副作用。grubenv 在重启后持久化并被 grub 在启动时读取，因此对于使用旧版 grub.cfg 的用户，启动菜单行为将发生可观察变化（从不显示/异常变为正确显示）。虽然该变更是向下兼容的附加变更，但它确实改变了外部可观察的启动行为。

### 证据
```sh
@grub_editenv@ - set menu_show_once=1
```

### 静态调用链
未生成（未启用调用链分析）。

### 复核建议
确认下游场景中旧版 grub.cfg 确实只检查 `menu_show_once` 而非 `menu_show_once_timeout`，且 `menu_show_once_timeout` 的覆盖行为在同时设置两者时按预期工作。

### 测试建议
1. 验证同时设置 `menu_show_once_timeout` 和 `menu_show_once` 时，新版 grub.cfg 优先使用 `menu_show_once_timeout` 而非固定的 60 秒超时
2. 验证仅设置 `menu_show_once=1`（不设置 `menu_show_once_timeout`）时，旧版 grub.cfg 能正确显示启动菜单并使用 60 秒默认超时
