# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/haproxy
**基线**: 5c0733db9a13516cd664926bd4273844db0ec98d
**补丁**: 784f972a6f085c9ba61256673330cc824fc3c9c1
**补丁说明**: MINOR: acme/lua: implement ACME.challenge_ready() Lua function
**Profile**: haproxy

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 2 |
| 候选变更 | 2 |
| 兼容性变更 | **0** |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 0 |

---

## 分析结论

**未发现兼容性变更。**

该提交是纯粹的新功能增加，在 `src/acme.c` 中添加了由 `#ifdef USE_LUA` 保护的 Lua API 函数 `ACME.challenge_ready(crt, dns)`，并更新了文档 `doc/lua-api/index.rst`。

### 变更内容

1. **`src/acme.c`: Lua 头文件引入**
   - 在 `#ifdef USE_LUA` 下新增 `lua.h`、`lauxlib.h`、`haproxy/hlua.h`、`haproxy/hlua_fcn.h` 的 include
   - 纯新增，不影响非 Lua 构建

2. **`src/acme.c`: `hlua_acme_challenge_ready()` 函数**
   - 新的 static 函数，封装 `acme_challenge_ready()` 的调用
   - 严格检查参数个数（需要 2 个参数），使用 `luaL_checkstring` 获取字符串
   - 处理返回值：-2 表示证书未找到，-1 表示域名未找到，均触发 Lua error
   - 正常返回值通过 `lua_pushinteger` 返回 Lua 层

3. **`src/acme.c`: `acme_hlua_init_state()` 注册函数**
   - 新的 static 函数，通过 `REGISTER_HLUA_STATE_INIT` 注册
   - 创建全局 Lua table `ACME`，注册 `challenge_ready` 方法

4. **`doc/lua-api/index.rst`: API 文档更新**
   - 新增 ACME class 文档，说明 `challenge_ready` 的使用方法

### 为何没有兼容性变更

- **纯新增**：没有修改或删除任何现有代码（只移除了一行尾随空行）
- **条件编译**：所有新代码被 `#ifdef USE_LUA` 保护，不影响非 Lua 构建
- **不修改现有 API**：`__acme_init()` 函数本体未变，ACME CLI 命令未变
- **Lua API 标准模式**：使用 HAProxy 标准的 `REGISTER_HLUA_STATE_INIT`、`hlua_class_function`、`lua_setglobal` 模式
- **不修改配置/CLI/协议/输出/错误行为**
- **提交标记为 MINOR**：次要功能增加

### 产物位置

分析产物已写入 `/home/soong/pca_benchmark/_repos/haproxy/pca-results/784f97/`
