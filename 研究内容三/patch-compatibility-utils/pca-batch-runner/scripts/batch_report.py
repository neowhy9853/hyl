#!/usr/bin/env python3
"""批量扫描报告独立重生成入口（等价于 batch_runner.py --report-only）。

由 batch_state.json（+ 可选 manifest 提供的 expected）确定性重渲染
batch_summary.json 与 batch_report.md：

    python3 batch_report.py --state /data/pca/batch_state.json \
        --manifest /data/pca/batch_manifest.yaml \
        --output /data/pca/batch_report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from batch_runner import (  # noqa: E402
    BatchCfg,
    BatchError,
    SUMMARY_FILENAME,
    REPORT_FILENAME,
    aggregate,
    compute_counts,
    load_manifest,
    load_state_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="batch_report.py",
        description="由 batch_state.json 重新生成批量汇总与报告")
    parser.add_argument("--state", required=True, help="batch_state.json 路径")
    parser.add_argument("--manifest", help="清单路径（提供后启用 expected 指标；"
                                           "默认取状态文件中记录的 manifest）")
    parser.add_argument("--output", help="batch_report.md 输出路径"
                                         f"（默认与 state 同目录的 {REPORT_FILENAME}）")
    parser.add_argument("--summary-output", help=f"batch_summary.json 输出路径"
                                                 f"（默认与 state 同目录的 {SUMMARY_FILENAME}）")
    parser.add_argument("--no-summary", action="store_true",
                        help="只生成报告，不写 batch_summary.json")
    args = parser.parse_args()

    state_path = Path(args.state).expanduser().absolute()
    try:
        state = load_state_file(state_path)
    except BatchError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    cfg: Optional[BatchCfg] = None
    manifest = args.manifest or state.get("manifest")
    if manifest and Path(manifest).is_file():
        try:
            cfg = load_manifest(Path(manifest))
        except BatchError as exc:
            print(f"警告: 无法加载清单（指标将不可用）: {exc}", file=sys.stderr)
    else:
        print("警告: 未找到清单文件，跳过 expected 指标", file=sys.stderr)

    report_path = (Path(args.output).expanduser().absolute() if args.output
                   else state_path.parent / REPORT_FILENAME)
    if args.no_summary:
        summary_path = report_path.with_name("__unused__")
    else:
        summary_path = (Path(args.summary_output).expanduser().absolute()
                        if args.summary_output
                        else state_path.parent / SUMMARY_FILENAME)

    aggregate(state, cfg, summary_path, report_path)
    if args.no_summary:
        try:
            summary_path.unlink()
        except OSError:
            pass

    counts = compute_counts(state)
    print(f"batch_id: {state.get('batch_id')} · done {counts['done']} · "
          f"failed {counts['failed']} · skipped {counts['skipped']} · "
          f"pending {counts['pending']}")
    print(f"报告: {report_path}")
    if not args.no_summary:
        print(f"汇总: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
