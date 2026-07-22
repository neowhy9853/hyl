#!/usr/bin/env python3
"""
Collect gcov coverage data for specific lines in changed source files.
Generates a structured coverage report.

Usage:
    python3 collect_coverage.py <project_dir> <report_file.md> \\
        --file builtin/fetch.c --lines 1561,1602,2662 \\
        --file fetch-pack.c --lines 496,511,1363

Output: Markdown report with per-line coverage status, summary statistics,
and actionable recommendations for uncovered lines.
"""
import argparse
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

def run_gcov(project_dir, source_file):
    """Run gcov and return the .gcov file path."""
    base = os.path.basename(source_file)
    gcov_file = os.path.join(project_dir, base + ".gcov")

    result = subprocess.run(
        ["gcov", "-o", os.path.dirname(source_file) or ".", source_file],
        cwd=project_dir,
        capture_output=True, text=True
    )

    if os.path.exists(gcov_file):
        return gcov_file
    # Try alternative location
    alt_file = os.path.join(project_dir, base.replace("/", "-") + ".gcov")
    if os.path.exists(alt_file):
        return alt_file
    return None

def extract_coverage(gcov_file, target_lines):
    """Extract coverage status for specific lines from a gcov file."""
    results = {}
    with open(gcov_file, errors='replace') as f:
        for line in f:
            line = line.rstrip()
            # gcov format: "EXEC_COUNT:SOURCE_LINE:CODE"
            # Match pattern: leading whitespace/#####, colon, line_number, colon, code
            parts = line.split(":", 2)
            if len(parts) < 2:
                continue
            try:
                exec_str = parts[0].strip()
                src_line = int(parts[1].strip())
                code = parts[2].strip() if len(parts) > 2 else ""
            except ValueError:
                continue

            if src_line not in target_lines:
                continue

            if exec_str == "#####":
                results[src_line] = ("NOT COVERED", 0, code)
            elif exec_str == "=====":
                results[src_line] = ("UNREACHABLE", 0, code)
            elif exec_str == "-":
                results[src_line] = ("NON-CODE", -1, code)
            else:
                results[src_line] = ("COVERED", int(exec_str), code)

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Collect gcov coverage for specific lines"
    )
    parser.add_argument("project_dir", help="Project directory with .gcda files")
    parser.add_argument("report_file", help="Output markdown report")
    parser.add_argument("--file", nargs="+", action="append", dest="file_groups",
                        default=[], help="Source file path")
    parser.add_argument("--lines", nargs="+", type=int, action="append",
                        dest="line_groups", default=[],
                        help="Line numbers (matched to preceding --file)")
    args = parser.parse_args()

    report = []
    report.append("# GCOV Patch Coverage Report")
    report.append("")
    report.append(f"**Project directory**: `{args.project_dir}`")
    report.append("")

    total_covered = 0
    total_executable = 0
    all_file_stats = []

    # Process each file group
    for i, fg in enumerate(args.file_groups):
        source_file = fg[0] if isinstance(fg, list) else fg
        target_lines = set(args.line_groups[i]) if i < len(args.line_groups) else set()

        report.append(f"## {source_file}")
        report.append("")

        gcov_file = run_gcov(args.project_dir, source_file)
        if not gcov_file:
            report.append(f"⚠️ gcov file not found — not compiled with coverage flags?")
            report.append("")
            continue

        coverage = extract_coverage(gcov_file, target_lines)

        report.append("| Line | Status | Count | Code |")
        report.append("|------|--------|-------|------|")

        covered = 0
        executable = 0

        for line in sorted(target_lines):
            if line in coverage:
                status, count, code = coverage[line]
                short = code[:55] + "..." if len(code) > 55 else code
                status_icon = {"COVERED": "✅", "NOT COVERED": "❌",
                               "UNREACHABLE": "⬜", "NON-CODE": "—"}
                icon = status_icon.get(status, "?")
                report.append(
                    f"| {line} | {icon} {status} | {count} | `{short}` |"
                )
                if status == "COVERED":
                    covered += 1
                    executable += 1
                elif status in ("NOT COVERED", "UNREACHABLE"):
                    executable += 1
            else:
                report.append(
                    f"| {line} | ❓ NOT FOUND | — | (line not in gcov output) |"
                )

        report.append("")
        rate = (covered / executable * 100) if executable > 0 else 0
        report.append(f"**{source_file}**: {covered}/{executable} ({rate:.1f}%)")
        report.append("")
        total_covered += covered
        total_executable += executable
        all_file_stats.append((source_file, covered, executable, rate))

    # Summary table
    report.append("## Summary")
    report.append("")
    report.append("| File | Exec Lines | Covered | Rate |")
    report.append("|------|-----------|---------|------|")
    for fn, cov, exe, rate in all_file_stats:
        report.append(f"| {fn} | {exe} | {cov} | {rate:.1f}% |")
    total_rate = (total_covered / total_executable * 100) if total_executable > 0 else 0
    report.append(f"| **Total** | **{total_executable}** | **{total_covered}** | **{total_rate:.1f}%** |")
    report.append("")
    report.append(f"**Patch impact coverage**: {total_covered}/{total_executable} ({total_rate:.1f}%)")

    with open(args.report_file, "w") as f:
        f.write("\n".join(report))

    print(f"Report: {args.report_file}")
    print(f"Coverage: {total_covered}/{total_executable} ({total_rate:.1f}%)")

if __name__ == "__main__":
    main()
