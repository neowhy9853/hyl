# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `36c41e9724c9a7a7cda37f5a4e9d94f25c8031c4` |
| 仓库 | `/data7/wanghy/tmp/linux` |
| 基线 | `d68b621bb5a48051932f1017a6e1bc9b18f854d0` |
| Profile | `kernel_6_6` |
| 执行状态 | `partial` |
| 向后兼容结论 | `inconclusive` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `False` |

**结论依据**：静态代码分析确认补丁引入SIDE_EFFECT_CHANGE: NCM gadget的net_device生命周期改变, sysfs拓扑通过device_move()动态迁移。但动态测试(契约验证、覆盖率)因缺少QEMU VM环境和内核构建基础设施而无法在本次执行中实施。测试入口(ncm_gadget_reproducer.sh)和5个测试输入已生成, 可在配置好QEMU VM后直接执行。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 0 |
| 规划输入 | 5 |
| 执行输入 | 0 |
| 契约通过 | 0 |
| 契约违约 | 0 |
| 契约跳过 | 1 |
| 补丁可执行行 | 54 |
| 已覆盖行 | 0 |
| 未覆盖行 | 54 |
| 补丁行覆盖率 | 0.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `not_available` |
| 基线构建 | `not_run` |
| 补丁后构建 | `not_run` |
| 编译器 | `gcc (未配置/未运行)` |
| 优化级别 | `N/A` |
| 覆盖率工具 | `gcov (未运行 — 需要内核构建环境和QEMU VM)` |
- 内核补丁兼容性测试需要完整的QEMU VM环境和内核构建基础设施
- USB gadget子系统测试需要dummy_hcd模块模拟USB硬件
- 当前执行环境无QEMU VM和内核构建工具链配置
- 已在静态层面完成代码分析和测试入口生成

## Finding 测试结果

### PCA-0001: SIDE_EFFECT_CHANGE

- **优先级**: `medium`
- **状态**: `partial`
- **目标**: `drivers/usb/gadget/function/u_ether.c:896-923 (gether_attach_gadget)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | static_valid_not_run | `test-entry-work/PCA-0001/ncm_gadget_reproducer.sh` | `bash test-entry-work/PCA-0001/ncm_gadget_reproducer.sh {BEFORE_DIR} {AFTER_DIR}` | net_device在bind/unbind间持久存在; sysfs路径在/sys/devices/virtual/net/<iface>与gadget设备间动态迁移; udevadm monitor显示KOBJ_MOVE事件而非KOBJ_ADD/KOBJ_REMOVE | dmesg或ftrace确认device_move()被调用; udevadm monitor捕获KOBJ_MOVE事件 |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| ncm_sysfs_side_effect | skipped | 契约验证需要两个分别运行baseline和patched内核的QEMU VM。当前环境无可用的内核构建基础设施和QEMU VM。静态代码分析已确认device_move()行为变更将导致sysfs拓扑迁移和uevent事件类型变化(KOBJ_MOVE替代KOBJ_ADD/KOBJ_REMOVE)。 |

- **覆盖率**: 0/54 (0.00%)
- **未覆盖行**: drivers/usb/gadget/function/u_ether.c:899, drivers/usb/gadget/function/u_ether.c:900, drivers/usb/gadget/function/u_ether.c:901, drivers/usb/gadget/function/u_ether.c:902, drivers/usb/gadget/function/u_ether.c:903, drivers/usb/gadget/function/u_ether.c:904, drivers/usb/gadget/function/u_ether.c:905, drivers/usb/gadget/function/u_ether.c:906, drivers/usb/gadget/function/u_ether.c:907, drivers/usb/gadget/function/u_ether.c:908, drivers/usb/gadget/function/u_ether.c:909, drivers/usb/gadget/function/u_ether.c:910, drivers/usb/gadget/function/u_ether.c:912, drivers/usb/gadget/function/u_ether.c:913, drivers/usb/gadget/function/u_ether.c:914, drivers/usb/gadget/function/u_ether.c:915, drivers/usb/gadget/function/u_ether.c:916, drivers/usb/gadget/function/u_ether.c:917, drivers/usb/gadget/function/u_ether.c:918, drivers/usb/gadget/function/u_ether.c:919, drivers/usb/gadget/function/f_ncm.c:1428, drivers/usb/gadget/function/f_ncm.c:1442, drivers/usb/gadget/function/f_ncm.c:1443, drivers/usb/gadget/function/f_ncm.c:1444, drivers/usb/gadget/function/f_ncm.c:1445, drivers/usb/gadget/function/f_ncm.c:1446, drivers/usb/gadget/function/f_ncm.c:1447, drivers/usb/gadget/function/f_ncm.c:1448, drivers/usb/gadget/function/f_ncm.c:1449, drivers/usb/gadget/function/f_ncm.c:1450, drivers/usb/gadget/function/f_ncm.c:1451, drivers/usb/gadget/function/f_ncm.c:1452, drivers/usb/gadget/function/f_ncm.c:1453, drivers/usb/gadget/function/f_ncm.c:1550, drivers/usb/gadget/function/f_ncm.c:1551, drivers/usb/gadget/function/f_ncm.c:1552, drivers/usb/gadget/function/f_ncm.c:1553, drivers/usb/gadget/function/f_ncm.c:1599, drivers/usb/gadget/function/f_ncm.c:1600, drivers/usb/gadget/function/f_ncm.c:1601, drivers/usb/gadget/function/f_ncm.c:1602, drivers/usb/gadget/function/f_ncm.c:1603, drivers/usb/gadget/function/f_ncm.c:1604, drivers/usb/gadget/function/f_ncm.c:1605, drivers/usb/gadget/function/f_ncm.c:1664, drivers/usb/gadget/function/f_ncm.c:1665, drivers/usb/gadget/function/f_ncm.c:1666, drivers/usb/gadget/function/f_ncm.c:1667, drivers/usb/gadget/function/f_ncm.c:1668, drivers/usb/gadget/function/f_ncm.c:1669, drivers/usb/gadget/function/f_ncm.c:1688, drivers/usb/gadget/function/f_ncm.c:1689, drivers/usb/gadget/function/f_ncm.c:1690, drivers/usb/gadget/function/f_ncm.c:1691
- 测试入口PCA-TE-0001已生成完整的shell录制脚本, 覆盖bind/unbind循环、sysfs监控和uevent验证
- 5个测试输入(I1-I5)覆盖正常路径、错误路径、首次绑定、重新绑定和fault injection场景
- 静态代码分析已充分表征兼容性变更: device_move()引入sysfs拓扑迁移, KOBJ_MOVE替代KOBJ_ADD/KOBJ_REMOVE
- 契约验证(core contract verification)需要KVM/QEMU环境和两个内核构建, 当前环境不支持
- 覆盖率测试需要启用GCOV的内核构建和VM启动, 超出当前环境能力

## 阻塞与未执行项

| Scope | ID | Reason | Required action |
|---|---|---|---|
| environment | BLOCKER-0001 | 内核补丁测试需要QEMU VM环境, 包含: (1)两个内核构建(baseline commit d68b621bb5 + patched commit 36c41e9724c9a); (2)CONFIG_USB_GADGET=y, CONFIG_USB_CONFIGFS=y, CONFIG_USB_CONFIGFS_NCM=y, CONFIG_GCOV_KERNEL=y; (3)dummy_hcd USB gadget硬件模拟; (4)configfs挂载和root权限。当前执行环境缺少上述基础设施。 | 搭建QEMU VM测试环境: 安装qemu-system-x86_64, 使用kernel build script构建两个内核, 创建包含configfs和dummy_hcd的rootfs, 启动VM并执行ncm_gadget_reproducer.sh进行before/after对比测试。 |
| build | BLOCKER-0002 | 内核构建工具链未在当前环境配置。需要gcc, make, 内核源码和.config。对GCOV覆盖率测试还需GCOV_PROFILE_u_ether.o和GCOV_PROFILE_f_ncm.o的Makefile配置。 | 在构建环境中运行make olddefconfig && make -j$(nproc)编译全量内核或make M=drivers/usb/gadget/function/编译目标模块。启用GCOV需要修改drivers/usb/gadget/function/Makefile添加GCOV_PROFILE_配置。 |
| coverage | BLOCKER-0003 | GCOV覆盖率数据收集需要在内核运行时执行测试并提取gcov数据。步骤: VM中执行bind/unbind循环测试 -> echo 0 > /sys/kernel/debug/gcov/reset -> 再次执行测试 -> 从/debugfs/gcov/提取.gcda文件 -> 运行gcov分析覆盖率。 | 在QEMU VM环境中: 挂载debugfs, 加载目标模块, 执行bind/unbind测试, 提取gcov数据, 运行'gcov -o <obj_dir> u_ether.c'分析补丁行覆盖率。 |

## 产物

| Artifact | Path |
|---|---|
| analysis_json | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/analysis.json` |
| contract_summary | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase3_contracts/contract_summary.json` |
| coverage_data | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase4_execution/coverage_data.json` |
| execution_results | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase4_execution/results.json` |
| impact_map | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase1_impact/impact_map.json` |
| patch_diff | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/patch.diff` |
| phase1_impact | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase1_impact/impact_map.json` |
| report | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/COVERAGE_REPORT.md` |
| reproducer_script | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-work/PCA-0001/ncm_gadget_reproducer.sh` |
| test_entries | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_plan | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-plan.md` |
| test_entry_tasks | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-tasks.json` |
| test_entry_verification | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-work/test-entry-verification.json` |
| test_entry_verification_md | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/test-entry-work/test-entry-verification.md` |
| test_inputs | `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P044/compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 搭建QEMU VM环境并构建baseline和patched两个内核版本
- 执行ncm_gadget_reproducer.sh进行before/after sysfs和uevent对比
- 启用GCOV覆盖率收集, 验证补丁行是否被测试覆盖
- 使用configfs反复bind/unbind NCM function验证net_device持久性
- 监控udev事件类型变化(KOBJ_MOVE vs KOBJ_ADD/KOBJ_REMOVE)
- 验证DHCP客户端在gadget重连后能否保留租约
