#!/usr/bin/env python3
"""
Collect gcov coverage data for specific lines in changed source files.

Generates a human-readable Markdown report and, with --json-output, a
structured JSON dataset that downstream coverage-report rendering can consume.

Usage:
    python3 collect_coverage.py <project_dir> <report_file.md> \\
        --file builtin/fetch.c --lines 1561,1602,2662 \\
        --file fetch-pack.c --lines 496,511,1363 \\
        [--json-output coverage_data.json]

Output: Markdown report with per-line coverage status and summary statistics,
plus optional structured JSON with per-line hit counts.
"""
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone


STATUS_LABELS = {
    "covered": "COVERED",
    "not_covered": "NOT COVERED",
    "unreachable": "UNREACHABLE",
    "non_code": "NON-CODE",
    "not_found": "NOT FOUND",
}

STATUS_ICONS = {
    "covered": "✅",
    "not_covered": "❌",
    "unreachable": "⬜",
    "non_code": "—",
    "not_found": "❓",
}


def run_gcov(project_dir, source_file):
    """Run gcov and return the .gcov file path."""
    base = os.path.basename(source_file)
    gcov_file = os.path.join(project_dir, base + ".gcov")

    subprocess.run(
        ["gcov", "-o", os.path.dirname(source_file) or ".", source_file],
        cwd=project_dir,
        capture_output=True,
        text=True,
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
    with open(gcov_file, errors="replace") as f:
        for line in f:
            line = line.rstrip()
            # gcov format: "EXEC_COUNT:SOURCE_LINE:CODE"
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


def summarize_coverage(source_file, coverage, target_lines, gcov_file=None):
    """Summarize extracted coverage for one source file.

    executable = covered + not_covered + unreachable; non_code and not_found
    lines are reported but excluded from the coverage denominator.
    """
    lines = []
    covered_lines = 0
    executable_lines = 0
    uncovered_lines = []

    for line in sorted(target_lines):
        status, count, code = coverage.get(line, ("NOT FOUND", -1, ""))
        if status == "COVERED":
            status_key = "covered"
            covered_lines += 1
            executable_lines += 1
        elif status == "NOT COVERED":
            status_key = "not_covered"
            executable_lines += 1
            uncovered_lines.append("%s:%d" % (source_file, line))
        elif status == "UNREACHABLE":
            status_key = "unreachable"
            executable_lines += 1
            uncovered_lines.append("%s:%d" % (source_file, line))
        elif status == "NON-CODE":
            status_key = "non_code"
        else:
            status_key = "not_found"

        lines.append(
            {
                "line": line,
                "status": status_key,
                "hits": count if count >= 0 else 0,
                "code": code,
            }
        )

    rate = (covered_lines / executable_lines * 100) if executable_lines > 0 else 0.0
    return {
        "file": source_file,
        "gcov_file": gcov_file,
        "executable_lines": executable_lines,
        "covered_lines": covered_lines,
        "uncovered_lines": uncovered_lines,
        "rate": rate,
        "lines": lines,
    }


def build_coverage_json(project_dir, files_and_lines):
    """Build the structured coverage dataset for all requested files."""
    files = []
    total_executable = 0
    total_covered = 0
    total_uncovered = []

    for source_file, target_lines in files_and_lines:
        gcov_file = run_gcov(project_dir, source_file)
        coverage = extract_coverage(gcov_file, target_lines) if gcov_file else {}
        summary = summarize_coverage(source_file, coverage, target_lines, gcov_file)
        files.append(summary)
        total_executable += summary["executable_lines"]
        total_covered += summary["covered_lines"]
        total_uncovered.extend(summary["uncovered_lines"])

    total_rate = (total_covered / total_executable * 100) if total_executable > 0 else 0.0
    return {
        "tool": "gcov",
        "project_dir": str(project_dir),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": files,
        "totals": {
            "executable_lines": total_executable,
            "covered_lines": total_covered,
            "uncovered_lines_count": len(total_uncovered),
            "uncovered_lines": total_uncovered,
            "rate": total_rate,
        },
    }


def render_markdown(project_dir, file_summaries):
    report = []
    report.append("# GCOV Patch Coverage Report")
    report.append("")
    report.append(f"**Project directory**: `{project_dir}`")
    report.append("")

    total_covered = 0
    total_executable = 0
    all_file_stats = []

    for summary in file_summaries:
        source_file = summary["file"]
        report.append(f"## {source_file}")
        report.append("")

        if not summary["gcov_file"]:
            report.append("⚠️ gcov file not found — not compiled with coverage flags?")
            report.append("")

        report.append("| Line | Status | Count | Code |")
        report.append("|------|--------|-------|------|")

        for item in summary["lines"]:
            status_key = item["status"]
            short = item["code"]
            short = short[:55] + "..." if len(short) > 55 else short
            icon = STATUS_ICONS.get(status_key, "?")
            report.append(
                f"| {item['line']} | {icon} {STATUS_LABELS[status_key]} | "
                f"{item['hits']} | `{short}` |"
            )

        report.append("")
        covered = summary["covered_lines"]
        executable = summary["executable_lines"]
        rate = summary["rate"]
        report.append(f"**{source_file}**: {covered}/{executable} ({rate:.1f}%)")
        report.append("")
        total_covered += covered
        total_executable += executable
        all_file_stats.append((source_file, covered, executable, rate))

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
    return "\n".join(report)


def parse_files_and_lines(args):
    pairs = []
    for index, group in enumerate(args.file_groups):
        source_file = group[0] if isinstance(group, list) else group
        target_lines = set(args.line_groups[index]) if index < len(args.line_groups) else set()
        pairs.append((source_file, target_lines))
    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Collect gcov coverage for specific lines"
    )
    parser.add_argument("project_dir", help="Project directory with .gcda files")
    parser.add_argument("report_file", help="Output markdown report")
    parser.add_argument(
        "--file",
        nargs="+",
        action="append",
        dest="file_groups",
        default=[],
        help="Source file path",
    )
    parser.add_argument(
        "--lines",
        nargs="+",
        type=int,
        action="append",
        dest="line_groups",
        default=[],
        help="Line numbers (matched to preceding --file)",
    )
    parser.add_argument(
        "--json-output",
        help="Optional path for structured coverage JSON (per-line hit counts)",
    )
    args = parser.parse_args()

    files_and_lines = parse_files_and_lines(args)
    payload = build_coverage_json(args.project_dir, files_and_lines)
    file_summaries = payload["files"]

    with open(args.report_file, "w") as f:
        f.write(render_markdown(args.project_dir, file_summaries))

    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.write("\n")

    totals = payload["totals"]
    total_covered = totals["covered_lines"]
    total_executable = totals["executable_lines"]
    total_rate = totals["rate"]

    print(f"Report: {args.report_file}")
    if args.json_output:
        print(f"Coverage JSON: {args.json_output}")
    print(f"Coverage: {total_covered}/{total_executable} ({total_rate:.1f}%)")


if __name__ == "__main__":
    main()
