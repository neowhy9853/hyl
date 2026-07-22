#!/usr/bin/env python3
"""Create test-entry generation tasks from finalized PCA findings.

The script does not invent runnable tests. It turns validated compatibility
findings into a deterministic worklist that an agent can use to write one
command or code artifact per target path. All generated planning artifacts
belong to the testing result directory; the input analysis.json is immutable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from compatibility_types import get_type_support


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def default_test_result_dir(analysis_path: Path) -> Path:
    return analysis_path.parent.resolve() / "compatibility-testing"


def surface_strategy_for(kind: str, profile: str) -> Dict[str, object]:
    kind = kind or ""
    profile = profile or ""

    if kind == "ioctl":
        return {
            "entry_kind": "ioctl_reproducer",
            "preferred_artifact": "minimal C reproducer or kselftest shell wrapper",
            "trigger_surface": "open the documented device node, prepare the UAPI struct, call ioctl(), and assert the changed errno/side effect",
            "seed_sources": ["patch.diff", "affected header/UAPI struct", "existing kselftests or syzkaller reproducers"],
        }
    if kind in {"procfs_entry", "sysfs_attribute", "sysctl_entry"}:
        return {
            "entry_kind": "fs_interface_command",
            "preferred_artifact": "shell command sequence or kselftest shell script",
            "trigger_surface": "read/write the procfs/sysfs/sysctl node and assert output, errno, permission, or state transition",
            "seed_sources": ["Documentation/ABI", "existing tools/tests", "finding evidence"],
        }
    if kind in {"syscall"}:
        return {
            "entry_kind": "syscall_reproducer",
            "preferred_artifact": "C reproducer, kselftest, or syzkaller program",
            "trigger_surface": "invoke the syscall with boundary inputs that cross the changed contract",
            "seed_sources": ["include/uapi", "tools/testing/selftests", "syzkaller descriptions"],
        }
    if kind in {"netlink_family"}:
        return {
            "entry_kind": "netlink_command",
            "preferred_artifact": "iproute2/pyroute2 command, C netlink reproducer, or kselftest",
            "trigger_surface": "send the netlink operation/attributes that reach the changed policy or handler",
            "seed_sources": ["nla_policy", "existing selftests", "iproute2 command syntax"],
        }
    if kind in {"cli_command", "cli_option"}:
        return {
            "entry_kind": "cli_command",
            "preferred_artifact": "single command line or regression test in the project's CLI test framework",
            "trigger_surface": "run the command/option combination that exercises the changed behavior",
            "seed_sources": ["existing CLI tests", "manual pages", "finding evidence"],
        }
    if kind in {"config_key", "env_variable"}:
        return {
            "entry_kind": "config_reproducer",
            "preferred_artifact": "temporary config file plus command invocation",
            "trigger_surface": "load a minimal config/env setting that reaches the changed parser or behavior",
            "seed_sources": ["sample configs", "existing parser tests", "documentation"],
        }
    if kind in {"exported_function", "public_function", "public_method", "public_class", "shared_library_symbol"}:
        return {
            "entry_kind": "api_harness",
            "preferred_artifact": "unit test, small linked program, or language-level test case",
            "trigger_surface": "call the public API with old/new contract boundary inputs and assert behavior",
            "seed_sources": ["existing unit tests", "public headers", "examples"],
        }
    if profile.startswith("kernel") or profile == "openeuler_24_03":
        return {
            "entry_kind": "kernel_reachability_reproducer",
            "preferred_artifact": "kselftest, syzkaller program, shell command, or minimal module only when no user-space path exists",
            "trigger_surface": "drive the externally reachable subsystem path that reaches the changed line",
            "seed_sources": ["tools/testing/selftests", "static_call_chains", "subsystem docs"],
        }
    return {
        "entry_kind": "project_test_harness",
        "preferred_artifact": "project-native regression test or minimal command",
        "trigger_surface": "use the nearest public entry point or existing test fixture that reaches the changed symbol",
        "seed_sources": ["existing tests", "static_call_chains", "finding evidence"],
    }


def strategy_for(kind: str, compatibility_type: str, profile: str) -> Dict[str, object]:
    """Combine surface-specific reachability with type-specific contract needs."""

    surface = surface_strategy_for(kind, profile)
    type_support = get_type_support(compatibility_type)
    surface["surface_entry_kind"] = surface["entry_kind"]
    surface.update(
        {
            "entry_kind": type_support["entry_kind"],
            "contract_id": type_support["contract_id"],
            "comparison": type_support["comparison"],
            "required_observation": type_support["observation"],
            "input_axes": type_support["input_axes"],
            "requires_explicit_probe": type_support["requires_explicit_probe"],
        }
    )
    return surface


def include_priority(priority: str, min_priority: str) -> bool:
    if min_priority == "all":
        return True
    return PRIORITY_ORDER.get(priority, 99) <= PRIORITY_ORDER[min_priority]


def build_task(analysis: dict, finding: dict, index: int) -> dict:
    affected_api = finding.get("affected_api") or {}
    location = finding.get("location") or {}
    profile = finding.get("package_profile") or analysis.get("package_profile", "")
    strategy = strategy_for(
        affected_api.get("kind", ""),
        finding.get("compatibility_type", ""),
        profile,
    )
    entry_id = "PCA-TE-%04d" % (index + 1)
    return {
        "id": entry_id,
        "finding_id": finding.get("id", "PCA-%04d" % (index + 1)),
        "test_priority": finding.get("test_priority", "low"),
        "compatibility_type": finding.get("compatibility_type", ""),
        "affected_api": affected_api,
        "target_location": location,
        "old_behavior": finding.get("old_behavior", ""),
        "new_behavior": finding.get("new_behavior", ""),
        "compatibility_reason": finding.get("compatibility_reason", ""),
        "test_recommendation": finding.get("test_recommendation", ""),
        "static_call_chains": finding.get("static_call_chains", []),
        "strategy": strategy,
        "required_output": {
            "goal": "produce one command or code artifact that reaches target_location.new_lines",
            "must_include": [
                "setup/build prerequisites",
                "exact command(s) or generated code path",
                "expected reachability signal such as return code, log, output, coverage, breakpoint, or tracepoint",
                "input values that exercise old/new compatibility behavior",
                "contract_probe with before/after commands and the registered comparison oracle",
                "limitations and any manual steps",
            ],
            "do_not_execute": "Generate artifacts and commands; do not run destructive or privileged tests unless the user explicitly asks.",
        },
    }


def render_markdown(plan: dict) -> str:
    lines = [
        "# PCA 测试入口挖掘任务",
        "",
        f"- Analysis: `{plan['analysis_json']}`",
        f"- Repo: `{plan['repo']}`",
        f"- Analysis repo: `{plan['analysis_repo']}`",
        f"- Test result dir: `{plan.get('test_result_dir', '')}`",
        f"- Patch ID: `{plan['patch_id']}`",
        f"- Task count: {len(plan['tasks'])}",
        "",
        "所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。",
        "",
    ]
    for task in plan["tasks"]:
        loc = task.get("target_location") or {}
        api = task.get("affected_api") or {}
        strategy = task.get("strategy") or {}
        new_lines = loc.get("new_lines")
        if not isinstance(new_lines, list) or len(new_lines) != 2:
            new_lines = ["", ""]
        lines.extend(
            [
                f"## {task['id']} / {task['finding_id']}",
                "",
                f"- Priority: `{task.get('test_priority')}`",
                f"- Type: `{task.get('compatibility_type')}`",
                f"- API: `{api.get('kind', '')}` `{api.get('name', '')}`",
                f"- Target: `{loc.get('file', '')}:{new_lines[0]}-{new_lines[1]}` `{loc.get('symbol', '')}`",
                f"- Entry kind: `{strategy.get('entry_kind', '')}`",
                f"- Preferred artifact: {strategy.get('preferred_artifact', '')}",
                f"- Trigger surface: {strategy.get('trigger_surface', '')}",
                f"- Contract: `{strategy.get('contract_id', '')}` / `{strategy.get('comparison', '')}`",
                f"- Observation: {strategy.get('required_observation', '')}",
                f"- Input axes: {', '.join(strategy.get('input_axes', []))}",
                "",
                "Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.",
                "",
            ]
        )
    return "\n".join(lines)


def create_plan(analysis_path: Path, min_priority: str) -> dict:
    analysis = load_json(analysis_path)
    tasks = [
        build_task(analysis, finding, index)
        for index, finding in enumerate(analysis.get("findings", []))
        if include_priority(finding.get("test_priority", "low"), min_priority)
    ]
    tasks.sort(key=lambda item: (PRIORITY_ORDER.get(item["test_priority"], 99), item["id"]))
    return {
        "analysis_json": str(analysis_path.resolve()),
        "repo": analysis.get("repo", ""),
        "analysis_repo": analysis.get("analysis_repo", ""),
        "artifact_dir": analysis.get("artifact_dir", str(analysis_path.parent)),
        "patch_id": analysis.get("patch_id", ""),
        "min_priority": min_priority,
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create PCA test-entry generation tasks")
    parser.add_argument("--analysis", required=True, help="Path to final analysis.json")
    parser.add_argument(
        "--min-priority",
        default="high",
        choices=["high", "medium", "low", "all"],
        help="Include findings at this priority or higher; all includes every finding",
    )
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--markdown", help="Output Markdown path")
    parser.add_argument(
        "--result-dir",
        help="Testing result directory; defaults to <analysis-dir>/compatibility-testing",
    )
    args = parser.parse_args()

    analysis_path = Path(args.analysis).resolve()
    plan = create_plan(analysis_path, args.min_priority)
    result_dir = (
        Path(args.result_dir).resolve()
        if args.result_dir
        else default_test_result_dir(analysis_path)
    )
    plan["test_result_dir"] = str(result_dir)
    output = Path(args.output).resolve() if args.output else result_dir / "test-entry-tasks.json"
    markdown = Path(args.markdown).resolve() if args.markdown else result_dir / "test-entry-plan.md"

    write_json(output, plan)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(render_markdown(plan) + "\n", encoding="utf-8")
    print("Test-entry tasks written to: %s" % output)
    print("Test-entry plan written to: %s" % markdown)
    print("Task count: %d" % len(plan["tasks"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
