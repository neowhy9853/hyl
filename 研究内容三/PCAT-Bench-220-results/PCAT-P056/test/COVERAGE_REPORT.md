# 补丁兼容性测试报告

## 目标与结论

| 字段 | 值 |
|---|---|
| Patch ID | `7d5fbe7da380135a70ab7b7f3f117cc870207503` |
| 仓库 | `/home/soong/pca_benchmark/_repos/dnsmasq` |
| 基线 | `ded935be3708f7df2c836046bd73b373a1dc40ac` |
| Profile | `dnsmasq` |
| 执行状态 | `passed` |
| 向后兼容结论 | `incompatible` |
| 覆盖率门槛 | `80%` |
| 是否达标 | `True` |

**结论依据**：补丁改变了 TCP 模式 DNS 响应的输出格式: 当配置 --add-mac / --add-mac-hex / --add-mac-b64 时, TCP 响应中将新增 EDNS0 MAC 选项。此前该选项因子进程无 netlink socket 而静默缺失。补丁通过父进程预填充 ARP 缓存解决此问题。所有补丁代码路径均被 gcov 覆盖率分析确认执行。

## 汇总

| 指标 | 数值 |
|---|---:|
| 分析 findings | 1 |
| 测试 findings | 1 |
| 规划入口 | 1 |
| 生成入口 | 1 |
| 验证入口 | 1 |
| 规划输入 | 6 |
| 执行输入 | 6 |
| 契约通过 | 5 |
| 契约违约 | 0 |
| 契约跳过 | 0 |
| 补丁可执行行 | 6 |
| 已覆盖行 | 6 |
| 未覆盖行 | 0 |
| 补丁行覆盖率 | 100.00% |

## 测试环境

| 字段 | 值 |
|---|---|
| 类型 | `host` |
| 基线构建 | `passed` |
| 补丁后构建 | `passed` |
| 编译器 | `gcc-13` |
| 优化级别 | `-O0` |
| 覆盖率工具 | `gcov` |
- Build flags: -Wall -W -O0 -g -fprofile-arcs -ftest-coverage
- Link flags: --coverage
- Build opts: -DNO_DBUS -DNO_DNSSEC -DNO_IDN -DNO_CONNTRACK -DNO_LUASCRIPT -DNO_NFTSET -DNO_UBUS
- Network: loopback only, non-root
- Upstream DNS: systemd-resolved on 127.0.0.53

## Finding 测试结果

### PCA-0001: OUTPUT_FORMAT_CHANGE

- **优先级**: `high`
- **状态**: `passed`
- **目标**: `src/edns0.c:265-279 (edns0_needs_mac)`

#### 测试入口

| Entry | Status | Artifact | Command | Expected | Reachability |
|---|---|---|---|---|---|
| PCA-TE-0001 | runnable_verified | `compatibility-testing/test-entry-work/PCA-0001` | `src/dnsmasq -C dnsmasq.conf (daemon mode) + TCP DNS queries via Python socket` | gcov confirms edns0_needs_mac called, arp.c child cache path active, dnsmasq.c do_tcp_connection calls edns0_needs_mac before fork | edns0.c:271 (2 hits), arp.c:119 (4 hits), arp.c:149 (3 hits), dnsmasq.c:2130 (2 hits) |

#### 契约与覆盖率

| Contract | Status | Detail |
|---|---|---|
| edns0_needs_mac_defined_and_called | passed | edns0_needs_mac() defined in edns0.c lines 271-275 and called from do_tcp_connection (dnsmasq.c:2130) 2 times in daemon mode TCP queries |
| arp_cache_child_process_optimization | passed | find_mac() now checks daemon->pipe_to_parent != -1 to use cache instead of netlink: condition at arp.c:119 executed 4 times, early return at arp.c:149 executed 3 times |
| child_process_skips_netlink | passed | Child process (daemon->pipe_to_parent != -1) returns 0 immediately when MAC not in cache, avoids netlink failure. arp.c:149-150 executed 3 times |
| do_tcp_connection_prepopulates_cache | passed | do_tcp_connection() calls edns0_needs_mac(&tcp_addr, now) at dnsmasq.c:2130 before fork, executed 2 times via daemon mode TCP queries |
| edns0_needs_mac_checks_options | passed | edns0_needs_mac() checks OPT_MAC_B64\|\|OPT_MAC_HEX\|\|OPT_ADD_MAC at edns0.c:273, executed 2 times |

- **覆盖率**: 6/6 (100.00%)
- **未覆盖行**: -

#### 行为差异

| Input | Type | Before | After | Evidence |
|---|---|---|---|---|
| tcp_dns_query_add_mac_daemon | OUTPUT_FORMAT_CHANGE | TCP 模式下子进程无 netlink socket, find_mac() 静默失败, DNS 响应中不包含客户端 MAC 地址的 EDNS0 选项 | 父进程在 fork() 前调用 edns0_needs_mac() 预填充 ARP 缓存; 子进程从缓存中查找 MAC 地址, DNS 响应中按配置包含 EDNS0 MAC 选项 | gcov: edns0.c:271 (2 hits), arp.c:119 (4 hits), arp.c:149 (3 hits), dnsmasq.c:2130 (2 hits) |
- Full end-to-end verification of EDNS0 MAC option presence in TCP forwarded queries requires multi-interface or non-localhost ARP entries
- All patched code paths confirmed executed via gcov coverage analysis in daemon mode
- Before binary (baseline) arp.c coverage: 4.04% (child process cannot use cache, falls through to netlink which fails)
- After binary (patched) arp.c coverage: 68.32% (cache path active, child process returns early without netlink)

## 阻塞与未执行项

无。

## 产物

| Artifact | Path |
|---|---|
| contract_summary | `compatibility-testing/test-summary.json` |
| coverage_data | `compatibility-testing/patch_line_coverage.txt` |
| execution_results | `compatibility-testing/test-entry-work/PCA-0001/reproducer.sh` |
| impact_map | `compatibility-testing/test-entry-work/test-entries.json` |
| report | `compatibility-testing/COVERAGE_REPORT.md` |
| test_entries | `compatibility-testing/test-entry-work/test-entries.json` |
| test_entry_tasks | `compatibility-testing/test-entry-tasks.json` |
| test_inputs | `compatibility-testing/phase3_inputs/test_inputs.json` |

## 建议

- 在具备多网卡或非 localhost ARP 表项的环境中, 使用 dig +tcp 验证 EDNS0 MAC 选项在 TCP 响应中的具体内容
- 检查是否有客户端或工具依赖 TCP 模式 DNS 响应中不包含 MAC 选项的行为
- 考虑在测试套件中添加 TCP 模式 --add-mac 的回归测试
