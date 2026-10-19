---
name: pca-batch-runner
description: "PCAT 批量扫描编排：无人值守批量执行补丁兼容性分析（如 PCAT-Bench-220 全量评测）。当用户要求批量扫描、批量分析、跑一批补丁、跑评测集、跑基准、复现 220 例指标、batch scan、batch manifest、PCAT-Bench 评测时使用。负责清单生成、预检、后台启动调度器、进度汇报、断点恢复与结果聚合；不负责单个补丁的分析流程本身（由每用例独立子 Agent 会话内的 patch-compatibility-analysis 完成）。"
---

# PCAT 批量扫描编排（pca-batch-runner）

无人值守地对一批补丁（`id + repo + base_commit + patch`）自动执行完整兼容性分析。
设计原则：**确定性调度 + LLM 分析分离**——并发计数、分派、重试、续跑由脚本
（`scripts/batch_runner.py`）决定；LLM 只在每用例的独立子 Agent 会话内做补丁语义判定。

本 Skill 不修改 `patch-compatibility-analysis` / `patch-compatibility-testing` 的任何
脚本，按原样复用；既可作为 `patch-compatibility-utils` 的子目录使用，也可独立复制到
`~/.opencode/skills/pca-batch-runner/` 安装。

## 组件

| 路径 | 用途 |
|---|---|
| `scripts/batch_runner.py` | 调度器：两阶段预检、状态机、并发槽、超时/重试、熔断、磁盘水位、进程组治理、进度事件流、聚合 |
| `scripts/progress_watcher.py` | 里程碑监视（模式 C）：阻塞至下一个里程碑即退出并打印快照 |
| `scripts/gen_manifest.py` | PCAT-Bench-220 items → `batch_manifest.yaml` 生成器 |
| `scripts/batch_report.py` | 由 `batch_state.json` 重新生成汇总与报告 |
| `templates/prompt.txt.j2` | 子 Agent prompt 模板（`{{var}}` 占位符） |
| `schemas/manifest_schema.json` · `schemas/batch_state_schema.json` | 清单与状态的结构定义 |
| `examples/batch_manifest.example.yaml` | 清单示例 |
| `tests/test_batch_runner_completion.py` | mock 端到端回归：完成口径 / 断点自愈 / analysis-test 产物校验（无需 LLM） |

## 文件契约（三层解耦）

```text
batch_manifest.yaml（人/脚本维护，输入）
  → batch_runner.py 调度
    → batch_state.json（状态事实源，原子写；幂等续跑的依据）
    → progress.jsonl（append-only 事件流 + 心跳，只读消费）
    → <output_base>/<case_id>/analysis.json（子 Agent 产物，完成判定的唯一依据）
  → batch_summary.json + batch_report.md（聚合，含可选评测指标）
```

批次目录（默认 = manifest 所在目录）内：`batch_state.json`、`progress.jsonl`、
`batch_summary.json`、`batch_report.md`；用例产物在 `<output_base>/<case_id>/`
（含 `analysis.json`、`report.md`、`run.log`，worktree 分析完默认清理）。

## Agent 启动协议（收到"跑批量扫描"后的固定动作）

1. **准备清单**：bench 数据集用 `gen_manifest.py` 生成；任意补丁集手写 manifest
   （模板见 `examples/batch_manifest.example.yaml`）。
2. **预检**：`batch_runner.py --manifest <manifest> --dry-run`，向用户展示计划
   （用例数 / 仓库准备 / 磁盘预估 / 首例命令）。
3. **后台启动**（`run_in_background` 或 nohup），记录 batch_id、批次目录、runner pid：

   ```bash
   python3 <RUNNER>/scripts/batch_runner.py --manifest <manifest> \
     [--concurrency 4 --resume]
   ```

   若自身宿主是活的 OpenCode server（TUI/IDE/web），追加模式 E 参数实现真回调：
   `--report-server http://localhost:4096 --report-session <自身会话id> --report-milestone 10`。
4. **回报用户**：batch_id、产物根目录（output_base）、汇报方式（"问我进度"= 模式 A；
   "到点汇报"= 模式 E 首选，不可用时模式 C）。
5. **写入会话上下文**：`batch_state.json` / `progress.jsonl` 的绝对路径——后续任何
   回合零成本读取。
6. **批次结束被唤醒**（E 注入 / C 监视任务完成 / D 通知已直达 / 用户询问）→ 读取
   `batch_summary.json` → 向用户呈现汇总（重点：counts、失败清单、指标）。

## 进度汇报模式

| 模式 | 触发 | 做法 |
|---|---|---|
| **A 拉取式（默认）** | 用户问"进度？" | 执行 `batch_runner.py --progress --manifest <manifest>`（只读、秒级），**原样转述渲染结果**，不自行解读原始 JSON |
| **B 跟随式** | 用户说"盯着" | 后台跑 `--progress --follow`，用户回来时转述增量 |
| **C 里程碑唤醒** | 用户要"每 10%/每小时汇报" | 后台启动 `progress_watcher.py --state <state> --milestone 10%`（或 `--every 1h`）；任务完成即唤醒本会话 → 转述快照 → 再启动下一个监视任务 |
| **D 外部推送** | manifest 配 `notify` | runner 在 `batch_done/circuit_break/disk_low` 时执行 `notify.command`（如 lark-cli），消息直达用户 |
| **E 会话注入回调（宿主 server 在线时首选）** | 启动时传 `--report-server/--report-session` | runner 按里程碑直接 `POST /session/:id/prompt_async` 注入快照触发本会话回合；失败仅记 `report_failed` 事件，不影响批次 |

汇报内容只读 `--progress` 渲染快照（`渲染格式固定：进度条/计数/吞吐/ETA/最近失败/磁盘/心跳`）；
追问细节（如"哪个用例最慢"）再查 `batch_state.json`。**确定性数据 + LLM 表达**，
LLM 不参与进度的事实计算。

## 中断与恢复

- 正确终止：`kill -TERM <runner_pid>`（runner 会 killpg 全部子进程、running 转
  pending、聚合后退出）。**勿对 runner 用 kill -9**。
- runner 被 kill -9/断电后：`--resume` 启动时自动执行孤儿回收（pid 探测 + 进程组
  kill，含 pid 复用防护），随后只补未完成用例；已有有效 `analysis.json`（含
  `affected-scope.json`）的用例自动跳过（`already_done`，汇总计入 skipped）。
- 断点自愈：`--resume` 时若 `analysis.json` 校验有效但缺 `affected-scope.json`
  （会话中断留下的半成品），自动运行 `orchestrator.py --attach-impact-scope` 补全，
  并按分析模式约定清理重建的 worktree；补全失败则保留 pending 重新分派整例。
  事件：`case_repaired` / `repair_failed`。
- 熔断（连续同签名失败 ≥ `consecutive_fail_limit`，默认 5）与磁盘低水位暂停
  （< `disk_low_watermark_gb`，默认 20）都会保留已完成结果，排障/清理后
  `--resume` 续跑；两者均不消耗用例的重试次数。
- 失败子集重跑：`--retry-failed`；指定用例复跑：`--ids A,B`；全部重跑：`--force`。

## 完成判定与评测口径

- **成功判据**：`<output_base>/<id>/analysis.json` 存在、通过
  `validate_analysis.py --require-affected-scope` 校验，且
  `<output_base>/<id>/affected-scope.json` 存在。不信任子进程退出码
  （LLM 会话可能"成功退出但没干活"）。
- **analysis-test 附加判据**：`<output_base>/<id>/compatibility-testing/test-summary.json`
  存在且通过 `finalize_test_report.py --validate-only` 校验，且 `TEST_REPORT.md` /
  `COVERAGE_REPORT.md` 存在；否则用例记 failed（测试产物缺失不再静默通过）。
- **predicted 一律从 `analysis.json` 派生**（findings 非空）；子 Agent 结尾输出的
  `SUMMARY json` 行仅供 run.log 速览，与产物矛盾时在报告标注 `summary_mismatch`。
- 指标（Accuracy/Precision/Recall/Specificity/F1 + TP/TN/FP/FN）仅对清单提供
  `expected` 的 done 用例计算。

## 两种模式

| mode | 行为 | 注意 |
|---|---|---|
| `analysis`（默认） | 仅静态分析至 analysis.json 校验通过；worktree 分析完默认清理 | 无人值守首选 |
| `analysis-test` | 分析后串接定向测试；超时 ×3；隐含保留 worktree | 需逐用例（或全局）`env_authorized: true`，未授权用例记 skipped |

推荐：先跑 analysis 全批，再对高优先级用例用 `--ids` 单独跑 analysis-test 子批。

## 事件流（progress.jsonl）

核心事件：`batch_start / dispatch / case_done / case_failed / retry / heartbeat /
circuit_break / paused / report_failed / batch_done`；扩展事件：`stopping /
case_interrupted / case_skipped / resumed / notify_failed / case_repaired /
repair_failed`。心跳按
`progress_interval_sec`（默认 300，0 关闭）定时发出——"安静"与"卡死"靠心跳判别。

## 常用命令速查

```bash
# 生成清单（bench → manifest）
python3 scripts/gen_manifest.py --from-bench <PCAT-Bench-220/items> --output <manifest.yaml>

# 预检 + 计划
python3 scripts/batch_runner.py --manifest <manifest.yaml> --dry-run

# 无人值守后台运行
nohup python3 scripts/batch_runner.py --manifest <manifest.yaml> > batch-run.out 2>&1 &

# 进度 / 跟随
python3 scripts/batch_runner.py --progress --manifest <manifest.yaml>
python3 scripts/batch_runner.py --progress --follow --manifest <manifest.yaml>

# 里程碑监视（模式 C）
python3 scripts/progress_watcher.py --state <批次目录>/batch_state.json --milestone 10%

# 恢复 / 失败重试 / 子集复跑 / 全部重跑
python3 scripts/batch_runner.py --manifest <manifest.yaml> --resume
python3 scripts/batch_runner.py --manifest <manifest.yaml> --resume --retry-failed
python3 scripts/batch_runner.py --manifest <manifest.yaml> --ids PCAT-P001,PCAT-P005
python3 scripts/batch_runner.py --manifest <manifest.yaml> --force

# 仅重生成报告 / 批次清理
python3 scripts/batch_runner.py --report-only --manifest <manifest.yaml>
python3 scripts/batch_report.py --state <批次目录>/batch_state.json
python3 scripts/batch_runner.py --cleanup <batch_id> --manifest <manifest.yaml>

# mock 端到端回归（完成口径 / 断点自愈 / analysis-test 产物校验，无需 LLM）
python3 tests/test_batch_runner_completion.py
```

退出码：`0` 正常（含子集运行）· `1` 用法/预检错误或锁冲突 · `2` 存在失败用例 ·
`3` 熔断中止 · `4` 磁盘低水位暂停 · `130` 被信号终止。

## 测试钩子

`--opencode-bin` 可替换子 Agent 可执行文件（默认 `opencode`）：用 mock 脚本即可
在没有 LLM 的情况下端到端验证调度行为（分派/重试/熔断/超时/恢复/聚合）。
`tests/test_batch_runner_completion.py` 内置 7 个场景（analysis 完成口径、缺
`affected-scope.json` 拒绝、断点自愈、自愈失败回退、findings 无 `affected_scope`
拒绝、analysis-test 产物齐全通过、缺 `COVERAGE_REPORT.md` 拒绝），mock skill +
mock opencode 运行，无需 LLM；运行：`python3 tests/test_batch_runner_completion.py`。
Skill 目录解析顺序：manifest `global.skill_dir` → 环境变量 `PCAT_SKILL_DIR` →
`~/.opencode/skills/patch-compatibility-utils` → `~/.agents/skills/patch-compatibility-utils`
→ 本目录的上级（嵌套布局）。

## 安全提示

子 Agent 以 `--auto` 运行（自动批准命令执行）。推荐在 Docker 隔离环境
（`hyl/研究内容三/Dockerfile` 构建的 `pcat-opencode:1.0`）中运行批量；宿主机直跑
需自担 `--auto` 权限风险，且测试模式（analysis-test）必须逐用例确认环境授权。
