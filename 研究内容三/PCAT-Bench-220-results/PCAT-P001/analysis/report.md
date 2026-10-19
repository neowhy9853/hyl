# PCA 兼容性变更分析报告

**仓库**: `/home/soong/pca_benchmark/_repos/linux`  
**基线**: `ffc253263a1375a65fa6c9f62a893e9767fbebfa`  
**补丁**: `632ca5e16e3e3141e559b9b4a4e588d252d0df2a`  
**Profile**: `kernel_6_6`

## 概要

| 指标 | 数量 |
|---|---:|
| 变更文件 | 1 |
| 候选变更 | 1 |
| 兼容性变更 | 1 |
| 高优先级测试 | 1 |

## PCA-0001：UAPI 结构体 ABI 变化

- **测试优先级**: HIGH
- **置信度**: 0.99
- **影响接口**: `struct input_event`
- **旧代码位置**: `include/uapi/linux/input.h:44-49`
- **新代码位置**: `include/uapi/linux/input.h:44-50`
- **类型**: `ABI_CHANGE`

### 变更前行为

`struct input_event` 在 `__s32 value` 后结束，用户态按旧头文件计算的记录大小不包含额外的 32 位尾部字段。

### 变更后行为

结构体新增 `__u32 compat_reserved`，改变结构体大小、尾部布局和连续记录数组步长。

### 兼容性影响

evdev 消费者用该稳定 UAPI 结构体解释 `read(2)` 返回的记录。新旧头文件编译出的消费者可能使用不同的记录长度解释相同字节流，因此属于 ABI 兼容性变化。

### 证据

```c
struct input_event {
        /* time fields */
        __u16 type;
        __u16 code;
        __s32 value;
        __u32 compat_reserved;
};
```

### 测试建议

分别针对基线与补丁后的 UAPI 头文件编译同一 C harness，比较 `sizeof(struct input_event)`、`offsetof(compat_reserved)` 与数组步长；真实 evdev 运行时验证需要装载补丁内核和输入设备环境。
