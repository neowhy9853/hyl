# 测试入口验证

- `PCA-TE-0001`: `runnable_verified`
- 最终退出码：0
- 基线宏值：5
- 补丁后宏值：6
- 旧值静态断言：基线编译成功，补丁后编译失败
- 可达证明：GCC 强制包含两个源码树各自的 `include/uapi/linux/uinput.h`，真实展开第 46 行的 `UINPUT_VERSION`。

首轮直接使用稀疏源码树 UAPI include path 时缺少导出头生成所依赖的内部头；细化后改为强制包含目标头，并仅从主机导出 UAPI 头解析其类型依赖，最终验证通过。
