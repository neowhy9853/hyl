# PCA 兼容性变更分析报告

**仓库**: /data2/wanghy/hyl_part3/PCIA-evaluate/repo/grub2
**基线**: HEAD (fe274638bb01104f56fce0caebe0a238ac5fc6a4)
**补丁**: 531750f7bfc475332b2046dd516bab582ba7decf
**Profile**: grub2

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

## PCA-0001: 副作用变更 (SIDE_EFFECT_CHANGE)

- **测试优先级**: MEDIUM
- **置信度**: 0.85
- **影响接口**: grub_get_tsc
- **旧代码位置**: include/grub/i386/tsc.h:47-52
- **新代码位置**: include/grub/i386/tsc.h:47-57
- **类型**: SIDE_EFFECT_CHANGE

### 变更前行为
grub_get_tsc()调用 cpuid 作为 rdtsc 前的串行化屏障，然后执行 rdtsc 读取 TSC 值，之后直接返回。由于 rdtsc 指令不是串行化指令，后续指令（包括调用者中的下一条指令）可能在 rdtsc 完成之前就开始执行，导致 TSC 读取的时间点不可靠，在某些多核/多 socket 服务器上可能导致 TSC 校准失败和 GRUB 菜单卡死。

### 变更后行为
grub_get_tsc()在 rdtsc 指令之后新增了 cpuid 串行化屏障，确保 rdtsc 在任何后续指令之前完成执行。返回值不变，但函数的副作用（串行化保证）发生了变化。

### 兼容性影响
该函数位于公共头文件 include/grub/i386/tsc.h 中，作为 static __inline 函数被多个 GRUB 内核模块使用（tsc.c、tsc_pmtimer.c、tsc_pit.c、efi/tsc.c）。新增的 cpuid 指令作为串行化屏障改变了函数的执行顺序保证（副作用变化），同时增加了每次调用的延迟（cpuid 是一个耗时较长的串行化指令）。虽然这是一个正确性修复，但副作用的变化可能影响依赖该函数时序特性的代码。

### 证据
```c
// include/grub/i386/tsc.h:49-54
  asm volatile ("rdtsc":"=a" (lo), "=d" (hi));
  /*
   * Run cpuid after rdtsc instruction to ensure rdtsc is executed before
   * subsequent instruction.
   */
  grub_cpuid (0, a, b, c, d);
```

```c
// grub-core/kern/i386/tsc_pmtimer.c:50-58 (调用者示例)
  start_tsc = grub_get_tsc ();
  while (1)
    {
      ...
      end_tsc = grub_get_tsc();
```

### 静态调用链
未生成。

### 复核建议
检查所有调用 grub_get_tsc 的代码路径，确认新增的 cpuid 串行化不会导致紧密循环或时序敏感代码中的负面影响。重点关注 tsc_pmtimer.c 中的校准循环。

### 测试建议
在 i386 平台上运行 GRUB，验证 TSC 校准成功（grub_tsc_rate > 0），且菜单超时计时正常工作，不会出现卡死。在多次重复启动测试中确认问题已修复。

---

产物已写入 /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P064/
