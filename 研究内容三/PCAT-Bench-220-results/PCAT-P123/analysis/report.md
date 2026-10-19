# PCA 兼容性变更分析报告

**仓库**: https://github.com/rhboot/grub2
**基线**: fe274638bb01
**补丁**: 8811797b13b31605fd02155e44c7299bfee2ab4a
**Profile**: grub2
**补丁来源**: https://github.com/rhboot/grub2/commit/8811797b13b31605fd02155e44c7299bfee2ab4a

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 4 |
| 候选变更 | 5 |
| 兼容性变更 | 2 |
| 高优先级测试 | 1 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 输入契约变更 (INPUT_CONTRACT_CHANGE)

- **测试优先级**: HIGH
- **置信度**: 0.95
- **影响接口**: grub_script_function_create
- **位置**: grub-core/script/function.c:60-79, grub-core/script/parser.y:289-294
- **类型**: INPUT_CONTRACT_CHANGE

### 变更前行为

当通过 grub.cfg 中的 function 语句重定义一个已存在且正在执行的函数时，旧函数体会被释放并替换为新函数体。这导致在执行过程中释放正在使用的 grub_script 内存，引发 use-after-free，可能导致任意代码执行、崩溃或意外行为。

### 变更后行为

当重定义一个正在执行的函数（executing > 0）时，grub_script_function_create 拒绝操作，设置 grub_errno 为 GRUB_ERR_BAD_ARGUMENT 并返回 NULL。当前执行继续使用旧函数定义不变。调用方 parser.y 正确处理 NULL 返回值，通过 grub_script_free 释放未使用的脚本内存。

### 兼容性影响

grub_script_function_create 的返回契约发生了变化：之前该函数在重定义场景下从不失败（总是返回有效指针），现在当一个正在执行的函数被重定义时会返回 NULL。下游调用方（如 parser.y 中的 function 语法规则）必须检查 NULL 返回值，否则将引用空指针。不过，旧行为（use-after-free）本身就是损坏的，任何依赖旧行为的 grub.cfg 配置本身就存在内存安全问题，因此此变更是向后兼容的缺陷修复。

### 证据

```c
/* grub-core/script/function.c:64-70 */
      q = *p;
      grub_free (func);
      if (q->executing > 0)
        {
          grub_error (GRUB_ERR_BAD_ARGUMENT,
                      N_("attempt to redefine a function being executed"));
          func = NULL;
        }
```

```c
/* grub-core/script/parser.y:289-294 */
            if (! script)
              grub_script_mem_free (state->func_mem);
            else {
              script->children = state->scripts;
              if (!grub_script_function_create ($2, script))
                grub_script_free (script);
```

```c
/* grub-core/script/execute.c:894-897 */
  func->executing++;
  ret = grub_script_execute (func->func);
  func->executing--;
```

### 复核建议

建议人工确认：1) parser.y 中新增的 NULL 检查是否覆盖了所有 grub_script_function_create 调用点；2) grub_error 设置的错误码是否会被正确传播和展示给用户；3) 是否有其他模块（非 parser.y）直接调用 grub_script_function_create 且未处理 NULL 返回值。

### 测试建议

建议编写定向测试：1) 在 grub.cfg 中定义一个自引用函数（如递归调用自身的函数），执行时触发重定义，验证 grub_error 被正确设置且函数定义被正确拒绝；2) 验证函数执行计数器在嵌套调用、递归和异常退出场景下正确增减；3) 测试正常重定义（非执行中）行为不受影响。

---

## PCA-0002: ABI / 结构体布局变更 (ABI_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.85
- **影响接口**: struct grub_script_function
- **位置**: include/grub/script_sh.h:361-368
- **类型**: ABI_CHANGE

### 变更前行为

struct grub_script_function 包含三个字段：char *name（函数名）、struct grub_script *func（脚本体）、struct grub_script_function *next（链表指针）。结构体大小为 3 个指针大小。

### 变更后行为

struct grub_script_function 末尾新增 unsigned executing 字段，增加了结构体总大小（增加 sizeof(unsigned) 字节，在大多数平台上为 4 字节）。

### 兼容性影响

该结构体定义在公开头文件 include/grub/script_sh.h 中，布局和大小发生了变化。任何直接使用 sizeof(struct grub_script_function) 或在栈上分配该结构体的外部代码都会受到影响。不过，实际使用中所有代码均通过 grub_script_function_t 指针类型访问，且所有内存分配由库内部 grub_script_function_create 管理，外部模块不会直接分配或嵌入该结构体。因此实际 ABI 影响极小。

### 证据

```c
/* include/grub/script_sh.h:355-368 */
struct grub_script_function
{
  /* The name.  */
  char *name;

  /* The script function.  */
  struct grub_script *func;

  /* The next element.  */
  struct grub_script_function *next;

  unsigned executing;
};
typedef struct grub_script_function *grub_script_function_t;
```

### 复核建议

无需人工复核。该变更实际影响极小，因为所有分配和访问都通过库内部函数管理。

### 测试建议

建议进行基本的模块加载兼容性测试：加载使用 FOR_SCRIPT_FUNCTIONS 宏的外部 GRUB 模块，验证模块仍能正常加载和遍历函数列表。

---

## 分析产物位置

产物已写入 `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P063/`
