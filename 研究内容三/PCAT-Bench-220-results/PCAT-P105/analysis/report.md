# PCA 兼容性变更分析报告

**仓库**: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/linux-stable`
**基线**: `234681c54581756c28cd928b0dac75ab4576e59d`
**补丁**: `8a3cd890fd2a7d016a821a1c9dfd8a84d45ad320` — ksmbd: add support for supplementary groups
**Profile**: `kernel_6_6`
**分析模式**: heavy (6 shards)

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 7 |
| 候选变更 | 20 |
| 兼容性变更 | 2 |
| 高优先级测试 | 1 |
| 中优先级测试 | 1 |
| 低优先级测试 | 0 |

---

## PCA-0001: 文件访问凭证覆盖的辅助组副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.85
- **影响接口**: `__ksmbd_override_fsids` — SMB 客户端文件操作时的进程凭证设置函数
- **旧代码位置**: `fs/smb/server/smb_common.c:759-766`
- **新代码位置**: `fs/smb/server/smb_common.c:761-778`
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为

在执行 SMB 文件操作（创建文件、目录、读写等）时，`__ksmbd_override_fsids()` 通过 `groups_alloc(0)` 设置空的辅助组列表，仅使用用户的主组（primary group）进行文件访问权限检查。这意味着即使用户属于某个辅助组且有文件访问权限，通过 SMB 访问仍会返回 `NT_STATUS_ACCESS_DENIED`。

### 变更后行为

`groups_alloc(user->ngroups)` 被调用，并通过 `user->sgid` 数组填充用户的辅助组 ID 到凭证中。当用户属于辅助组时，该组对文件的权限将被正确应用于 SMB 文件访问。辅助组列表通过 `groups_sort()` 排序后设置到进程凭证。

### 兼容性影响

此变更改变了 SMB 客户端可观察的文件访问行为：补丁前，用户即使通过辅助组有文件访问权限，通过 SMB 操作文件时也会被拒绝访问（NT_STATUS_ACCESS_DENIED）；补丁后，辅助组权限被正常识别，用户可以通过 SMB 访问原来无法访问的文件。这改变了文件服务器对外部客户端的安全行为语义。该行为变更对所有使用辅助组进行文件权限管理的部署具有广泛影响。

### 证据

```c
// smb_common.c: __ksmbd_override_fsids() — 补丁前
gi = groups_alloc(0);

// smb_common.c: __ksmbd_override_fsids() — 补丁后
gi = groups_alloc(user->ngroups);
if (!gi) {
    abort_creds(cred);
    return -ENOMEM;
}
for (i = 0; i < user->ngroups; i++)
    gi->gid[i] = make_kgid(&init_user_ns, user->sgid[i]);
if (user->ngroups)
    groups_sort(gi);
set_groups(cred, gi);
```

### 复核建议
无需额外人工复核。该变更的兼容性语义清晰：补丁前使用空辅助组列表，补丁后支持辅助组。

### 测试建议
1. 设置一个文件，其组权限仅授予某辅助组，验证通过 SMB 访问该文件时补丁前后行为差异
2. 验证旧 ksmbd-tools 与新内核的兼容性（KSMBD_USER_FLAG_EXTENSION 未设置时行为不变）
3. 验证 `ngroups > NGROUPS_MAX` 时的错误处理
4. 验证 `groups_alloc()` 分配失败时的错误路径

---

## PCA-0002: ksmbd 通用 netlink 协议扩展 (IOCTL_NETLINK_ABI_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.80
- **影响接口**: `KSMBD_EVENT_LOGIN_REQUEST_EXT` / `KSMBD_EVENT_LOGIN_RESPONSE_EXT` — ksmbd SMBD_GENL netlink 协议
- **旧代码位置**: `fs/smb/server/ksmbd_netlink.h:308-313`
- **新代码位置**: `fs/smb/server/ksmbd_netlink.h:321-329`
- **类型**: IOCTL_NETLINK_ABI_CHANGE

### 变更前行为
ksmbd 通用 netlink 协议 (SMBD_GENL) 定义了 15 个事件类型（`KSMBD_EVENT_UNSPEC` 到 `KSMBD_EVENT_SPNEGO_AUTHEN_RESPONSE = 15`）。`resv_start_op` 设置为 `KSMBD_EVENT_SPNEGO_AUTHEN_RESPONSE + 1 = 16`。`nla_policy` 数组定义了对应 16 个类型的属性验证策略。

### 变更后行为
协议扩展为 17 个事件类型，新增 `KSMBD_EVENT_LOGIN_REQUEST_EXT` (=16) 和 `KSMBD_EVENT_LOGIN_RESPONSE_EXT` (=17)。新增结构体 `ksmbd_login_response_ext` 作为扩展登录响应（包含 `handle`、`ngroups`、`reserved[128]`、`____payload[]` 字段）。新增 `KSMBD_USER_FLAG_EXTENSION BIT(6)` 标志。`resv_start_op` 更新为 `KSMBD_EVENT_LOGIN_RESPONSE_EXT + 1 = 18`。新增 `nla_policy` 条目和 `genl_ops` 条目处理新事件。

### 兼容性影响
该变更扩展了 ksmbd 内核模块与 ksmbd-tools 用户态守护进程之间的 netlink 协议。枚举值增加改变了后续事件类型的隐式编号，`resv_start_op` 的更新向 genl 子系统声明了新的命令范围。旧版本 ksmbd-tools 不会发送新的扩展事件，因此向后兼容；但新版本 ksmbd-tools 需要了解这些新事件和结构体才能使用辅助组功能。

### 证据

```c
// ksmbd_netlink.h — 新结构体
struct ksmbd_login_response_ext {
    __u32 handle;
    __s32 ngroups;          /* supplementary group count */
    __s8  reserved[128];    /* Reserved room */
    __s8  ____payload[];
};

// ksmbd_netlink.h — 新枚举值
KSMBD_EVENT_LOGIN_REQUEST_EXT,
KSMBD_EVENT_LOGIN_RESPONSE_EXT,

// ksmbd_netlink.h — 新标志
#define KSMBD_USER_FLAG_EXTENSION BIT(6)

// transport_ipc.c — resv_start_op 变更
// 旧: .resv_start_op = KSMBD_EVENT_SPNEGO_AUTHEN_RESPONSE + 1,  (=16)
// 新: .resv_start_op = KSMBD_EVENT_LOGIN_RESPONSE_EXT + 1,    (=18)
```

### 复核建议
建议确认 ksmbd-tools 是否直接 `#include` 该头文件，以及旧版本 ksmbd-tools 在接收未知 netlink 命令号时的行为。

### 测试建议
1. 使用旧版本 ksmbd-tools 连接新内核，验证基本功能不受影响
2. 使用新版本 ksmbd-tools 设置辅助组，验证请求和响应的正确性
3. 验证 `ipc_validate_msg` 正确计算扩展响应的消息大小
4. 验证 `nla_policy` 中的新属性长度约束

---

产物已写入 `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_151130/PCIA-P045/`
