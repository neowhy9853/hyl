#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

RUNNER = Path(__file__).resolve().parent.parent / "scripts" / "batch_runner.py"

MOCK_CHECK_DEPS = """#!/usr/bin/env python3
import json, sys
print(json.dumps({"ok": True}))
sys.exit(0)
"""

MOCK_VALIDATE = """#!/usr/bin/env python3
import argparse, json, sys

parser = argparse.ArgumentParser()
parser.add_argument("analysis")
parser.add_argument("--require-affected-scope", action="store_true")
parser.add_argument("--allow-legacy-ids", action="store_true")
args = parser.parse_args()
try:
    data = json.load(open(args.analysis, encoding="utf-8"))
except (OSError, ValueError) as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    sys.exit(1)
if args.require_affected_scope:
    for index, finding in enumerate(data.get("findings", [])):
        scope = finding.get("affected_scope")
        if (not isinstance(scope, dict) or not scope.get("status")
                or not str(scope.get("summary", "")).strip()):
            print(f"ERROR: finding[{index}].affected_scope missing", file=sys.stderr)
            sys.exit(1)
sys.exit(0)
"""

MOCK_ORCHESTRATOR = """#!/usr/bin/env python3
import argparse, json, os, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--attach-impact-scope")
parser.add_argument("--ensure-worktree")
parser.add_argument("--cleanup-worktree")
args = parser.parse_args()
if args.cleanup_worktree:
    target = Path(args.cleanup_worktree).resolve()
    (target.parent / ".mock-cleanup-called").write_text("1", encoding="utf-8")
    sys.exit(0)
if args.attach_impact_scope:
    if os.environ.get("MOCK_REPAIR_FAIL") == "1":
        print("mock repair failure", file=sys.stderr)
        sys.exit(1)
    target = Path(args.attach_impact_scope).resolve()
    (target.parent / "affected-scope.json").write_text(
        json.dumps({"schema_version": "1.0", "findings": {}, "repaired": True}),
        encoding="utf-8")
    print(f"Affected scope written to: {target.parent / 'affected-scope.json'}")
sys.exit(0)
"""

MOCK_FINALIZE = """#!/usr/bin/env python3
import argparse, json, sys

parser = argparse.ArgumentParser()
parser.add_argument("summary_json")
parser.add_argument("--output")
parser.add_argument("--coverage-output")
parser.add_argument("--validate-only", action="store_true")
args = parser.parse_args()
try:
    data = json.load(open(args.summary_json, encoding="utf-8"))
except (OSError, ValueError) as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    sys.exit(1)
if data.get("mock_valid") is not True:
    print("ERROR: mock test-summary invalid", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
"""

MOCK_OPENCODE = '''#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path

args = sys.argv[1:]
if not args or args[0] == "models":
    print("test/mock-model")
    sys.exit(0)
if args[0] != "run":
    sys.exit(0)

prompt = args[-1]
case_id = re.search(r"case_id:\\s*(\\S+)", prompt).group(1)
out_dir = Path(re.search(r"output_dir:\\s*(\\S+)", prompt).group(1)).resolve()
out_dir.mkdir(parents=True, exist_ok=True)
scenario = os.environ.get("MOCK_SCENARIO", "complete")

if scenario == "bad_analysis":
    analysis = {"schema_version": "1.0", "patch_id": case_id,
                "findings": [{"id": "PCA-0001", "test_priority": "high"}]}
else:
    analysis = {"schema_version": "1.0", "patch_id": case_id,
                "findings": [{"id": "PCA-0001", "test_priority": "high",
                              "compatibility_type": "INPUT_CONTRACT_CHANGE",
                              "location": {"file": "a.c", "new_lines": [1, 2], "symbol": "f"},
                              "affected_scope": {"status": "computed", "summary": "mock scope"}}]}
(out_dir / "analysis.json").write_text(json.dumps(analysis), encoding="utf-8")

if scenario != "no_scope":
    (out_dir / "affected-scope.json").write_text(
        json.dumps({"schema_version": "1.0", "findings": {}}), encoding="utf-8")

if scenario in ("test_ok", "no_coverage_report", "bad_summary", "test_failed_null_coverage"):
    test_dir = out_dir / "compatibility-testing"
    test_dir.mkdir(exist_ok=True)
    if scenario == "test_failed_null_coverage":
        summary = {"status": "failed", "patch_line_coverage_rate": 0.0,
                   "conclusion": {"backward_compatibility": "inconclusive",
                                  "coverage_gate_met": False},
                   "coverage_report": None,
                   "mock_valid": True}
    else:
        summary = {"status": "passed", "patch_line_coverage_rate": 100.0,
                   "conclusion": {"backward_compatibility": "compatible",
                                  "coverage_gate_met": True},
                   "coverage_report": {"gate": {"threshold": 80, "rate": 100.0, "met": True}},
                   "mock_valid": scenario != "bad_summary"}
    (test_dir / "test-summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (test_dir / "TEST_REPORT.md").write_text("# test report", encoding="utf-8")
    if scenario not in ("no_coverage_report", "test_failed_null_coverage"):
        (test_dir / "COVERAGE_REPORT.md").write_text("# coverage report", encoding="utf-8")

print("mock done")
sys.exit(0)
'''


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_script(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def build_fixture(root: Path) -> dict:
    mock_skill = root / "mock-skill"
    analysis_scripts = mock_skill / "patch-compatibility-analysis" / "scripts"
    testing_scripts = mock_skill / "patch-compatibility-testing" / "scripts"
    write_script(analysis_scripts / "check_dependencies.py", MOCK_CHECK_DEPS)
    write_script(analysis_scripts / "validate_analysis.py", MOCK_VALIDATE)
    write_script(analysis_scripts / "orchestrator.py", MOCK_ORCHESTRATOR)
    write_script(testing_scripts / "finalize_test_report.py", MOCK_FINALIZE)

    opencode_bin = root / "bin" / "opencode"
    write_script(opencode_bin, MOCK_OPENCODE)

    repo = root / "repo"
    repo.mkdir(parents=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    (repo / "a.c").write_text("int f(void) { return 1; }\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, env=env)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "base"],
                   cwd=repo, check=True, env=env)
    base_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True,
                                 capture_output=True, text=True).stdout.strip()

    patch = root / "case.patch"
    patch.write_text("--- a/a.c\n+++ b/a.c\n", encoding="utf-8")
    return {"skill_dir": mock_skill, "opencode_bin": opencode_bin,
            "repo": repo, "base_commit": base_commit, "patch": patch}


def make_manifest(ws: Path, fixture: dict, mode: str = "analysis",
                  env_authorized: bool = False) -> Path:
    ws.mkdir(parents=True, exist_ok=True)
    manifest = ws / "batch_manifest.yaml"
    manifest.write_text(textwrap.dedent(f"""\
        schema_version: '1.0'
        global:
          concurrency: 1
          mode: {mode}
          timeout_sec: 60
          retries: 0
          agent: patch-compatibility-utils
          output_base: {ws / 'results'}
          repo_cache: {ws / '_repos'}
          skill_dir: {fixture['skill_dir']}
          progress_interval_sec: 0
          disk_check_interval_sec: 10
          disk_low_watermark_gb: 0
          per_case_disk_estimate_gb: 0
          consecutive_fail_limit: 5
          env_authorized: {str(env_authorized).lower()}
        cases:
          - id: T-CASE
            repo: {fixture['repo']}
            base_commit: {fixture['base_commit']}
            patch: {fixture['patch']}
            profile: auto
        """), encoding="utf-8")
    return manifest


def run_runner(manifest: Path, args=None, env_extra=None,
               opencode_bin: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(RUNNER), "--manifest", str(manifest)]
    if opencode_bin is not None:
        cmd += ["--opencode-bin", str(opencode_bin)]
    if args:
        cmd += list(args)
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)


def load_state(manifest: Path) -> dict:
    return json.loads((manifest.parent / "batch_state.json").read_text(encoding="utf-8"))


def load_events(manifest: Path) -> list:
    path = manifest.parent / "progress.jsonl"
    if not path.is_file():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


def case_state(manifest: Path) -> dict:
    return load_state(manifest)["cases"]["T-CASE"]


def fail_context(result: subprocess.CompletedProcess) -> str:
    return (f"rc={result.returncode}\n"
            f"stdout tail:\n{result.stdout[-1500:]}\n"
            f"stderr tail:\n{result.stderr[-1500:]}")


def scenario_analysis_complete(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t1", fixture)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "complete"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 0, fail_context(result))
    expect(state["status"] == "done", f"status={state['status']} error={state['error']}")
    expect("mock done" in (manifest.parent / "results" / "T-CASE" / "run.log").read_text(
        encoding="utf-8", errors="replace"), "mock opencode was not used")


def scenario_analysis_missing_scope(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t2", fixture)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "no_scope"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 2, fail_context(result))
    expect(state["status"] == "failed", f"status={state['status']}")
    expect("affected-scope.json" in (state["error"] or ""),
           f"error={state['error']}")


def scenario_resume_self_heal(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t3", fixture)
    first = run_runner(manifest, env_extra={"MOCK_SCENARIO": "no_scope"},
                       opencode_bin=fixture["opencode_bin"])
    expect(first.returncode == 2, fail_context(first))
    second = run_runner(manifest, ["--resume", "--retry-failed"],
                        env_extra={"MOCK_SCENARIO": "no_scope"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(second.returncode == 0, fail_context(second))
    expect(state["status"] == "already_done", f"status={state['status']}")
    expect((manifest.parent / "results" / "T-CASE" / "affected-scope.json").is_file(),
           "affected-scope.json not repaired")
    expect((manifest.parent / "results" / "T-CASE" / ".mock-cleanup-called").is_file(),
           "cleanup-worktree was not called after repair")
    expect(any(e.get("event") == "case_repaired" for e in load_events(manifest)),
           "case_repaired event missing")


def scenario_repair_failure_falls_back(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t6", fixture)
    first = run_runner(manifest, env_extra={"MOCK_SCENARIO": "no_scope"},
                       opencode_bin=fixture["opencode_bin"])
    expect(first.returncode == 2, fail_context(first))
    second = run_runner(manifest, ["--resume", "--retry-failed"],
                        env_extra={"MOCK_SCENARIO": "complete", "MOCK_REPAIR_FAIL": "1"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(second.returncode == 0, fail_context(second))
    expect(state["status"] == "done", f"status={state['status']} error={state['error']}")
    expect(any(e.get("event") == "repair_failed" for e in load_events(manifest)),
           "repair_failed event missing")


def scenario_bad_analysis_rejected(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t7", fixture)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "bad_analysis"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 2, fail_context(result))
    expect(state["status"] == "failed", f"status={state['status']}")
    expect("require-affected-scope" in (state["error"] or ""),
           f"error={state['error']}")


def scenario_analysis_test_complete(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t4", fixture, mode="analysis-test", env_authorized=True)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "test_ok"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 0, fail_context(result))
    expect(state["status"] == "done", f"status={state['status']} error={state['error']}")
    expect((state.get("test") or {}).get("status") == "passed",
           f"test info missing: {state.get('test')}")
    report = (manifest.parent / "batch_report.md").read_text(encoding="utf-8")
    expect("测试与覆盖率" in report, "batch_report.md missing test section")


def scenario_analysis_test_missing_coverage_report(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t5", fixture, mode="analysis-test", env_authorized=True)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "no_coverage_report"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 2, fail_context(result))
    expect(state["status"] == "failed", f"status={state['status']}")
    expect("COVERAGE_REPORT.md" in (state["error"] or ""), f"error={state['error']}")


def scenario_analysis_test_failed_null_coverage(root: Path, fixture: dict) -> None:
    manifest = make_manifest(root / "t8", fixture, mode="analysis-test", env_authorized=True)
    result = run_runner(manifest, env_extra={"MOCK_SCENARIO": "test_failed_null_coverage"},
                        opencode_bin=fixture["opencode_bin"])
    state = case_state(manifest)
    expect(result.returncode == 0, fail_context(result))
    expect(state["status"] == "done", f"status={state['status']} error={state['error']}")
    expect((state.get("test") or {}).get("status") == "failed",
           f"test info missing: {state.get('test')}")


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="pca-batch-runner-tests-"))
    scenarios = [
        scenario_analysis_complete,
        scenario_analysis_missing_scope,
        scenario_resume_self_heal,
        scenario_repair_failure_falls_back,
        scenario_bad_analysis_rejected,
        scenario_analysis_test_complete,
        scenario_analysis_test_missing_coverage_report,
        scenario_analysis_test_failed_null_coverage,
    ]
    failures = []
    print(f"fixture: {root}")
    try:
        fixture = build_fixture(root)
        for scenario in scenarios:
            try:
                scenario(root, fixture)
                print(f"PASS {scenario.__name__}")
            except AssertionError as exc:
                failures.append(scenario.__name__)
                print(f"FAIL {scenario.__name__}: {exc}")
    finally:
        if failures:
            print(f"fixture kept for debugging: {root}")
        else:
            shutil.rmtree(root, ignore_errors=True)
    if failures:
        print(f"\n{len(failures)}/{len(scenarios)} failed: {', '.join(failures)}")
        return 1
    print(f"\nall {len(scenarios)} scenarios passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
