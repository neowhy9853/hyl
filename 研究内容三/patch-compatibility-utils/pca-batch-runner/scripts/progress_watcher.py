#!/usr/bin/env python3
"""里程碑监视器（模式 C）：阻塞至下一个进度里程碑或批次结束，打印快照后退出。

用法（Agent 以后台任务启动，任务完成即唤醒 Agent 会话）：

    python3 progress_watcher.py --state <批次目录>/batch_state.json --milestone 10%
    python3 progress_watcher.py --state <批次目录>/batch_state.json --every 1h

退出码：0 到达里程碑/批次结束 · 1 错误 · 3 超时。
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from batch_runner import (  # noqa: E402
    BatchError,
    compute_counts,
    load_state_file,
    parse_duration,
    render_progress_snapshot,
    STATE_FILENAME,
)

WAIT_FOR_STATE_SEC = 60


def progress_percent(state: dict) -> float:
    counts = compute_counts(state)
    if counts["total"] == 0:
        return 0.0
    completed = counts["done"] + counts["failed"]
    return completed * 100.0 / counts["total"]


def batch_terminal(state: dict) -> bool:
    return bool(state.get("finished_at")) or bool(state.get("abort_reason")) \
        or bool(state.get("paused_reason"))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="progress_watcher.py",
        description="PCAT 批量扫描里程碑监视（模式 C：到达即退出并打印快照）")
    parser.add_argument("--state", required=True,
                        help=f"batch_state.json 路径（progress.jsonl 需在同目录）")
    parser.add_argument("--milestone",
                        help="里程碑步长（百分比，如 10 或 10%%）：下一个 N%% 到达即退出")
    parser.add_argument("--every", help="时间制：每隔该时长退出一次（如 30m、1h）")
    parser.add_argument("--timeout", type=int, default=86400,
                        help="最长等待秒数（默认 86400，超时退出码 3）")
    parser.add_argument("--interval", type=float, default=10,
                        help="轮询间隔秒（默认 10）")
    args = parser.parse_args()

    if not args.milestone and not args.every:
        parser.error("需要 --milestone N%% 或 --every DURATION 之一")

    step: Optional[int] = None
    if args.milestone:
        try:
            step = int(str(args.milestone).rstrip("%"))
        except ValueError:
            parser.error(f"--milestone 非法: {args.milestone!r}（示例：10 或 10%）")
        if not 1 <= step <= 100:
            parser.error("--milestone 取值范围 [1, 100]")
    every_sec: Optional[int] = None
    if args.every:
        every_sec = parse_duration(args.every)

    state_path = Path(args.state).expanduser().absolute()
    deadline = time.time() + WAIT_FOR_STATE_SEC
    while not state_path.exists():
        if time.time() >= deadline:
            print(f"错误: 等待 {WAIT_FOR_STATE_SEC}s 仍未出现状态文件 {state_path}",
                  file=sys.stderr)
            return 1
        time.sleep(2)

    try:
        state = load_state_file(state_path)
    except BatchError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    start_pct = progress_percent(state)
    target: Optional[float] = None
    if step is not None:
        target = min(100.0, (int(start_pct // step) + 1) * step)
        if target <= start_pct and start_pct >= 100:
            target = 100.0
    started = time.time()

    while True:
        try:
            state = load_state_file(state_path)
        except BatchError:
            time.sleep(args.interval)
            continue

        pct = progress_percent(state)
        terminal = batch_terminal(state)
        reason: Optional[str] = None
        if step is not None and target is not None and pct >= target:
            reason = f"里程碑 {target:.0f}% 已到达（当前 {pct:.1f}%）"
        elif step is not None and terminal:
            reason = "批次已结束"
        elif every_sec is not None and (time.time() - started) >= every_sec:
            reason = "到达定时汇报间隔"
        elif every_sec is not None and terminal:
            reason = "批次已结束"

        if reason is not None:
            print(f"[progress_watcher] {reason}")
            print(render_progress_snapshot(state, state_path))
            return 0
        if time.time() - started > args.timeout:
            print(f"[progress_watcher] 等待超时（{args.timeout}s）")
            print(render_progress_snapshot(state, state_path))
            return 3
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
