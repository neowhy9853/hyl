# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux
**基线**: 475b2384bb91576e7881bca8f17548a6bbee8ded
**补丁**: a23d8e124fbd (original: 5c262bd0e39320a6d6c8277cb8349ce21c01b8c1)
**Profile**: kernel_6_6
**补丁来源**: bpf/bonding: reject vlan+srcmac xmit_hash_policy change when XDP is loaded

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 5 |
| 兼容性变更 | 2 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: sysfs/netlink 配置行为变更 — xmit_hash_policy 切换被拒绝

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: bond_option_xmit_hash_policy_set (sysfs `/sys/class/net/<bond>/bonding/xmit_hash_policy` + netlink `IFLA_BOND_XMIT_HASH_POLICY`)
- **旧代码位置**: drivers/net/bonding/bond_options.c:1592-1597
- **新代码位置**: drivers/net/bonding/bond_options.c:1592-1599
- **类型**: CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为

修改 bonding xmit_hash_policy 时，sysfs 或 netlink 接口直接接受新值并应用到 bond->params.xmit_policy，不会检查已加载 XDP 程序的兼容性。即使用户在 802.3ad/balance-xor 模式下已加载 XDP 程序，也能将 xmit_hash_policy 切换为不兼容的 vlan+srcmac。

### 变更后行为

修改 xmit_hash_policy 时，新增 guard 检查：若 bond->xdp_prog 已加载且 __bond_xdp_check(BOND_MODE(bond), newval->value) 返回 false（即 802.3ad/balance-xor 模式 + vlan+srcmac 策略），则返回 -EOPNOTSUPP，拒绝该变更。错误码经 bond_opt_tryset_rtnl 和 __bond_opt_set 向上传播至 sysfs store 操作（返回负错误码给 write 调用）和 netlink 操作（返回 err 给调用方）。

### 兼容性影响

该变更会破坏用户空间工具的兼容性。之前可以通过 `echo 'vlan+srcmac 2' > /sys/class/net/<bond>/bonding/xmit_hash_policy` 或 ip link netlink 消息在已加载 XDP 程序的 802.3ad/balance-xor 模式 bond 上更改哈希策略。现在该操作会失败并返回 EOPNOTSUPP。依赖此行为的自动化脚本、网络配置工具和编排系统会受到影响。

### 证据

```c
// drivers/net/bonding/bond_options.c:1592-1599
static int bond_option_xmit_hash_policy_set(struct bonding *bond,
					    const struct bond_opt_value *newval)
{
	if (bond->xdp_prog && !__bond_xdp_check(BOND_MODE(bond), newval->value))
		return -EOPNOTSUPP;
	netdev_dbg(bond->dev, "Setting xmit hash policy to %s (%llu)\n",
		   newval->string, newval->value);
	WRITE_ONCE(bond->params.xmit_policy, newval->value);
```

```c
// drivers/net/bonding/bond_sysfs.c:222-224
static DEVICE_ATTR(xmit_hash_policy, 0644,
		   bonding_show_xmit_hash, bonding_sysfs_store_option);
```

### 复核建议

无需人工复核，代码变更逻辑清晰，与已有 bond_option_mode_set 的 guard 模式一致。

### 测试建议

创建 802.3ad 或 balance-xor 模式 bonding 设备，加载 XDP 程序，通过 sysfs 写 vlan+srcmac 策略，验证返回 -EOPNOTSUPP；再卸载 XDP 后验证可正常切换。同时通过 ip link set type bond 命令验证 netlink 接口同样拒绝。

---

## PCA-0002: 新增公共 API __bond_xdp_check

- **测试优先级**: LOW
- **置信度**: 0.90
- **影响接口**: include/net/bonding.h: __bond_xdp_check(int mode, int xmit_policy)
- **旧代码位置**: include/net/bonding.h:697-702
- **新代码位置**: include/net/bonding.h:697-703
- **类型**: API_SIGNATURE_CHANGE

### 变更前行为

bonding.h 仅声明 bond_xdp_check(struct bonding *bond, int mode)，该函数同时负责兼容性判断逻辑。

### 变更后行为

bonding.h 新增 __bond_xdp_check(int mode, int xmit_policy) 声明。该函数将原 bond_xdp_check 的兼容性判断逻辑抽取为独立函数，接受 mode 和 xmit_policy 两个 int 参数（不再依赖 struct bonding 指针）。原有 bond_xdp_check 保留为 wrapper，内部调用 __bond_xdp_check(mode, bond->params.xmit_policy)。

### 兼容性影响

这是一个纯加法变更：新增了一个内核内部公共 API 函数。原有 bond_xdp_check 签名和行为完全不变。但该新符号是 bonding.h 中的公开声明（非 static），其他内核模块或驱动可以依赖它。

### 证据

```c
// include/net/bonding.h:700-701
bool __bond_xdp_check(int mode, int xmit_policy);
bool bond_xdp_check(struct bonding *bond, int mode);
```

```c
// drivers/net/bonding/bond_main.c:325-342 (新函数实现)
bool __bond_xdp_check(int mode, int xmit_policy)
{
	switch (mode) {
	case BOND_MODE_ROUNDROBIN:
	case BOND_MODE_ACTIVEBACKUP:
		return true;
	case BOND_MODE_8023AD:
	case BOND_MODE_XOR:
		if (xmit_policy != BOND_XMIT_POLICY_VLAN_SRCMAC)
			return true;
		fallthrough;
	default:
		return false;
	}
}
```

```c
// drivers/net/bonding/bond_main.c:344-347 (wrapper 保持兼容)
bool bond_xdp_check(struct bonding *bond, int mode)
{
	return __bond_xdp_check(mode, bond->params.xmit_policy);
}
```

### 复核建议

建议确认 __bond_xdp_check 是否有意被外部模块使用。双下划线前缀通常暗示内部函数，但在公开头文件中的声明使其成为事实 API。

### 测试建议

验证 bond_xdp_check 的原有调用方（bond_main.c:1874 和 bond_main.c:5705，以及 bond_options.c:913 bond_option_mode_set）行为不变。确保 __bond_xdp_check 对于所有 mode/policy 组合返回正确布尔值。

---

## 分析摘要

该补丁在 bonding 驱动中修复一个兼容性问题：防止用户在已加载 XDP 程序的 802.3ad/balance-xor 模式 bond 上将 xmit_hash_policy 切换为 vlan+srcmac（该组合不兼容 XDP，会导致 bond 销毁时的 WARN_ON）。修复方式是将 bond_xdp_check 的兼容性判断逻辑抽取为 __bond_xdp_check(mode, xmit_policy)，并在 bond_option_xmit_hash_policy_set 中新增 XDP 兼容性 guard。这与已有的 bond_option_mode_set 的 guard 逻辑对称。
