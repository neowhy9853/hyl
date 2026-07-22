# PCA 测试范围与测试入口生成改进计划

## 1. 首批待测 Repo

首批目标选择标准：环境配置成本低、项目自带测试或可本地构造入口、patch 中容易出现 commit-message reproducer / fuzz / crash 线索、与兼容性分析目标有明确外部接口边界。

| 优先级 | Repo | Profile | 为什么先测 | 重点 patch 类型 | 测试入口策略 |
|---:|---|---|---|---|---|
| 1 | `libxml2` | `libxml2` | C 库规模适中，解析器输入天然适合 fuzz seed，漏洞修复 commit 常带 reproducer 或新增回归样本 | OSS-Fuzz/ClusterFuzz、CVE、crash、parser/tree/xinclude/encoding 行为变更 | 优先保留 commit 中的 `xmllint`/fuzzer 命令；其次使用新增 XML/HTML 样本作为 seed |
| 2 | `git` | `git` | 已有本地样本，测试框架成熟，CLI/config/protocol/output 兼容性 surface 清晰 | CLI option、config key、stderr/stdout、protocol negotiation | 优先 `t/*.sh` 原生测试；commit message 命令直接进入 test-entry plan |
| 3 | `dnsmasq` | `dnsmasq` | 已有本地样本，小型 C daemon，CLI/config/DNS 协议入口可用高端口本地构造 | DNSSEC、DHCP option、config parser、daemon output、crash/fuzz | config seed + DNS/DHCP payload；使用本地 upstream stub 或 `dig` 命令 |
| 4 | `vim` | `vim` | testdir 成熟，很多修复由最小输入文件触发，适合作为 parser/script fuzz seed | crash/assert、regexp、script、file parser、testdir 新增样本 | 优先新增 testdir case；其次 headless `vim` 命令或最小输入文件 |
| 5 | `haproxy` | `haproxy` | 构建直接，config/protocol surface 明确；完整 reg-test 需要 vtest，但最小 config + HTTP payload 可先做 | config parser、HTTP/TCP protocol、reg-test、crash reproducer | `haproxy.cfg` seed + `curl`/`vtest`；没有 vtest 时输出 manual_required 或最小命令 |

第二批：`cpython`、`httpd`、`glib2`、`libsoup`、`ruby`。这些项目测试价值高，但构建或依赖成本高于首批。

暂缓作为主测试入口质量改进样本：`kernel_6_6`、`golang`、`grub2`、`networkmanager`、`dnf`、`rsyslog`、`lvm2`、`openldap`。这些项目仍在兼容性分析范围内，但环境、权限、硬件或测试耗时使其不适合作为第一轮“入口生成质量”闭环验证对象。

## 2. Patch 优先级筛选

对每个 repo 先生成最近 N 个非 merge commit patch：

```bash
git -C <repo> format-patch --no-merges -100 HEAD -o <patch-dir>
```

然后运行筛选脚本：

```bash
python scripts/patch_test_target_selector.py \
  --repo <repo> \
  --package <profile> \
  --patch-dir <patch-dir> \
  --output-json <out>/patch-test-targets.json \
  --markdown <out>/patch-test-targets.md
```

筛选分级：

| 分级 | 含义 | 下一步 |
|---|---|---|
| `P0_commit_reproducer` | commit message 中直接出现测试命令、PoC、reproducer、触发 crash 的命令 | 优先做 full PCA；确认 finding 后测试入口生成必须保留原始命令并构造成回归/seed |
| `P1_fuzz_or_crash_seed` | commit message 含 fuzz/crash/CVE/ASAN/UBSAN/OSS-Fuzz 等线索，或 patch 新增/修改 seed-like 文件 | 优先做 full PCA；测试入口生成以新增样本或 commit 语义作为 seed provenance |
| `P2_surface_regression` | 没有显式 reproducer，但 commit message 或 patch 触及 API/ABI/CLI/config/protocol/output 等兼容性 surface | 进入常规 PCA 队列；入口生成优先找项目原生测试 |
| `P3_low_signal` | 暂无测试入口或兼容性 surface 信号 | 低优先级，不作为入口生成质量改进样本 |

## 3. 测试入口生成的新规则

测试入口不是简单给一个“可能能跑”的命令。它要服务后续回归测试和 fuzz seed 生成，因此必须包含：

- 原始来源：commit-message command、项目原生测试、新增 testdata/corpus、文档示例、静态调用链或 synthetic harness
- 目标：`location.file`、`location.new_lines`、`location.symbol`
- 可达证明：coverage、breakpoint、tracepoint、sanitizer、确定性输出、返回值或断言
- 输入策略：如何触发 old/new contract 差异
- seed 元数据：seed 文件或生成命令、provenance、expected signal、mutation axes、是否已最小化
- 限制条件：root、设备、网络端口、依赖、内核配置、硬件、非确定性等

入口来源优先级：

1. commit message 中已有 reproducer / crash command / sanitizer command / PoC
2. 项目已有测试或 patch 新增测试样本
3. 现有 fuzzer target / corpus / seed
4. 文档、man page、example config
5. 静态调用链推导出的 public entry
6. synthetic harness

如果前五类证据都没有，不要硬造看似可运行但无法证明可达的测试；输出 `manual_required` 并说明缺口。

## 4. 首轮执行建议

第一轮闭环不建议追求覆盖 21 个 profile。建议：

1. 用 `libxml2` 验证 commit-message reproducer 和 fuzz seed 生成。
2. 用本地 `git` 验证 CLI/config/output 类入口生成。
3. 用本地 `dnsmasq` 验证 daemon/config/protocol 类入口生成。
4. 视时间加入 `vim` 或 `haproxy`，分别覆盖 parser/script seed 和 daemon protocol/config seed。

每个 repo 先取 `P0 + P1` patch；如果数量不足，再补 `P2` 中触及 public API/CLI/config/protocol 的 patch。
