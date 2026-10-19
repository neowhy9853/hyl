# 测试入口验证

`PCA-TE-0001` 状态：`runnable_verified`。

- 命令：`timeout 120 bash test-entry-work/PCA-0001/reproducer.sh`
- 退出码：`0`
- 观察信号：`sizeof(struct input_event)` 与数组步长均从 24 变为 32，`compat_reserved` 偏移为 24。
- 限制：此入口只验证编译期 UAPI 布局；运行时证据由 `PCA-TE-0002` 补充。

`PCA-TE-0002` 状态：`runnable_verified`。

- 命令：`timeout 600 bash test-entry-work/PCA-0001/runtime_evdev.sh`
- 退出码：`0`
- 观察信号：基线 24 字节 write/read 成功；补丁内核相同调用返回 `EINVAL`；两侧 native-size write/read 均成功。
- 环境：无特权 QEMU TCG、内嵌静态 initramfs、guest 内 uinput 虚拟键盘。
