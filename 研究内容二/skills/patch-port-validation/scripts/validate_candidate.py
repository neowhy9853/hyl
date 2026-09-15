#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


def git(repo: Path, args: list[str], *, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ValidationError(f"git {' '.join(args)}: {detail}")
    return result



def check_cross_repo(repo: Path, analysis: dict) -> None:
    """Check repository identity and mapping declarations, not semantic truth."""
    if analysis.get('port_mode', 'history') != 'cross_repo_semantic':
        return
    inputs = analysis.get('inputs', {})
    if not all(inputs.get(k) and Path(inputs[k]).is_absolute()
               for k in ('reference_repo', 'target_repo', 'repo')):
        raise ValidationError('cross-repo mode requires absolute reference_repo, target_repo and repo')
    target = Path(inputs['target_repo']).resolve()
    reference = Path(inputs['reference_repo']).resolve()
    def identity(path):
        value = Path(git(path, ['rev-parse', '--git-common-dir']).stdout.strip())
        return (value if value.is_absolute() else path/value).resolve()
    if Path(inputs['repo']).resolve() != target or identity(repo) != identity(target):
        raise ValidationError('operation must use the declared target repository')
    if identity(reference) == identity(target):
        raise ValidationError('cross-repo mode requires distinct repositories')
    if repo == reference or repo.is_relative_to(reference):
        raise ValidationError('candidate/output must be outside the reference repository')
    for unit in analysis.get('change_units', []):
        if not unit.get('mandatory', True):
            continue
        mapping = unit.get('semantic_mapping', {})
        if mapping.get('status') != 'confirmed' or not mapping.get('evidence_ids'):
            raise ValidationError('mandatory semantic mapping is unresolved or lacks evidence')
        destinations = mapping.get('targets', [])
        if not destinations or any(t.get('repo_role') != 'target' or
                t.get('commit') != inputs.get('target_commit') for t in destinations):
            raise ValidationError('semantic mapping target identity is inconsistent')
        if unit.get('target_location', {}).get('path') not in [t.get('path') for t in destinations]:
            raise ValidationError('planned location is absent from semantic mapping')


def same_path(recorded: str | None, actual: Path) -> bool:
    return bool(recorded) and Path(recorded).is_absolute() and Path(recorded).resolve() == actual.resolve()


def file_hash_matches(recorded: str | None, expected: str | None) -> bool:
    if not recorded or not expected or not Path(recorded).is_absolute():
        return False
    try:
        return hashlib.sha256(Path(recorded).read_bytes()).hexdigest() == expected
    except OSError:
        return False


def blocked_evidence(inputs: dict, checks: dict, reason: str) -> dict:
    return {
        "schema_version": "1.0",
        "artifact_type": "patch-port-validation-evidence",
        "evidence_status": "blocked", "recommended_validation_status": "blocked",
        "inputs": inputs, "input_checks": checks,
        "structural_checks": {"status": "not_run", "reason": reason},
        "commands": [], "semantic_review_required": [],
        "limitations": [reason],
    }


def validate(
    *,
    repo: Path,
    target_ref: str,
    patch_path: Path,
    analysis_path: Path,
    application_path: Path,
    commands: list[str],
    timeout: int,
) -> dict[str, object]:
    repo = repo.resolve()
    patch_path = patch_path.resolve()
    patch_bytes = patch_path.read_bytes()
    patch_text = patch_bytes.decode("utf-8", errors="replace")
    patch_hash = hashlib.sha256(patch_bytes).hexdigest()
    analysis_bytes = analysis_path.read_bytes()
    application_bytes = application_path.read_bytes()
    analysis = json.loads(analysis_bytes)
    application = json.loads(application_bytes)
    check_cross_repo(repo, analysis)
    target_commit = git(repo, ["rev-parse", "--verify", f"{target_ref}^{{commit}}"]).stdout.strip()
    inputs = {
        "repo": str(repo), "target_commit": target_commit,
        "patch": str(patch_path), "patch_sha256": patch_hash,
        "analysis": str(analysis_path.resolve()),
        "analysis_sha256": hashlib.sha256(analysis_bytes).hexdigest(),
        "application": str(application_path.resolve()),
        "application_sha256": hashlib.sha256(application_bytes).hexdigest(),
    }
    input_checks = {
        "required_context_resolved": all(item.get("status") == "resolved"
                                         for item in analysis.get("missing_context", [])),
        "analysis_gate_ready": analysis.get("analysis_status") in ("ready", "direct_apply_ready"),
        "application_gate_ready": application.get("application_status") == "candidate_ready",
        "target_matches_analysis": target_commit == analysis.get("inputs", {}).get("target_commit"),
        "target_matches_application": target_commit == application.get("target_commit"),
        "patch_hash_matches_application": patch_hash == application.get("generated_patch_sha256"),
        "analysis_path_matches_application": same_path(application.get("analysis_path"), analysis_path),
        "patch_path_matches_application": same_path(application.get("generated_patch"), patch_path),
        "analysis_evidence_hash_matches": file_hash_matches(
            analysis.get("inputs", {}).get("analysis_evidence"),
            analysis.get("inputs", {}).get("analysis_evidence_sha256")),
        "application_evidence_hash_matches": file_hash_matches(
            application.get("application_evidence"), application.get("application_evidence_sha256")),
    }
    if not all(input_checks.values()):
        failed = ", ".join(name for name, passed in input_checks.items() if not passed)
        return blocked_evidence(inputs, input_checks, "Input checks failed: " + failed)
    command_results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="patch-port-validation-") as temporary:
        checkout = Path(temporary) / "repo"
        clone = subprocess.run(
            ["git", "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(checkout)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if clone.returncode != 0:
            return blocked_evidence(inputs, input_checks, clone.stderr.strip() or "temporary clone failed")
        try:
            git(checkout, ["checkout", "--quiet", "--detach", target_commit])
        except ValidationError as exc:
            return blocked_evidence(inputs, input_checks, str(exc))
        apply_check = git(checkout, ["apply", "--check", "-"], check=False, input_text=patch_text)
        applied = False
        apply_result = apply_check
        if apply_check.returncode == 0:
            apply_result = git(checkout, ["apply", "-"], check=False, input_text=patch_text)
            applied = apply_result.returncode == 0

        if applied:
            git(checkout, ["add", "-N", "--", "."])
            diff_check = git(checkout, ["diff", "HEAD", "--check"], check=False)
            changed_paths = git(checkout, ["diff", "--name-only", "HEAD"]).stdout.splitlines()
            conflict_markers = find_conflict_markers(checkout, changed_paths)
            for command in commands:
                command_results.append(run_command(checkout, command, timeout))
        else:
            diff_check = subprocess.CompletedProcess([], 1, "", "patch was not applied")
            changed_paths = []
            conflict_markers = []

    planned_paths = expected_paths(analysis)
    absent_target_paths = [p for p in changed_paths if p not in analysis.get('approved_new_paths', [])
                           and git(repo, ['cat-file', '-e', f'{target_commit}:{p}'], check=False).returncode != 0]
    changed_path_check = {
        "planned": planned_paths,
        "actual": changed_paths,
        "missing": sorted(set(planned_paths) - set(changed_paths)),
        "unexpected": sorted(set(changed_paths) - set(planned_paths)) if planned_paths else [],
    }
    structural_passed = (
        all(input_checks.values())
        and apply_check.returncode == 0
        and applied
        and diff_check.returncode == 0
        and not conflict_markers
        and not changed_path_check["missing"]
        and not changed_path_check["unexpected"]
        and not absent_target_paths
    )
    no_command_failures = all(item["status"] != "failed" for item in command_results)
    evidence_status = "structurally_valid" if structural_passed and no_command_failures else "failed"
    return {
        "schema_version": "1.0",
        "artifact_type": "patch-port-validation-evidence",
        "evidence_status": evidence_status,
        "recommended_validation_status": "partial" if evidence_status == "structurally_valid" else "failed",
        "inputs": inputs,
        "input_checks": input_checks,
        "structural_checks": {
            "unapproved_absent_target_paths": absent_target_paths,
            "apply_check": process_fact(apply_check),
            "apply": process_fact(apply_result),
            "diff_check": process_fact(diff_check),
            "conflict_markers": conflict_markers,
            "changed_paths": changed_path_check,
        },
        "commands": command_results,
        "semantic_review_required": [
            "mandatory change-unit and coupled-group coverage",
            "security invariant and vulnerable-path closure",
            "target API, macro, lock, cleanup, and error semantics",
            "positive and vulnerability-triggering negative path",
            "oracle isolation and unrelated-change review",
        ],
        "limitations": [
            "This script produces deterministic evidence, not a final semantic pass decision.",
            "The Agent must create validation.json and may only report passed after all semantic gates pass.",
            *["Verification not run: " + item["command"] + " (" + item["stderr"] + ")"
              for item in command_results if item["status"] == "not_run"],
        ],
    }


def run_command(checkout: Path, command: str, timeout: int) -> dict[str, object]:
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return {"command": command, "status": "not_run", "exit_code": None,
                "stdout": "", "stderr": "invalid command: " + str(exc)}
    if not argv:
        return {"command": command, "status": "not_run", "exit_code": None,
                "stdout": "", "stderr": "empty command"}
    try:
        result = subprocess.run(
            argv,
            cwd=checkout,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "command": command,
            "argv": argv,
            "status": "passed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": limit(result.stdout, 12000),
            "stderr": limit(result.stderr, 12000),
        }
    except OSError as exc:
        return {
            "command": command, "argv": argv, "status": "not_run", "exit_code": None,
            "stdout": "", "stderr": str(exc),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "argv": argv,
            "status": "failed",
            "exit_code": 124,
            "stdout": limit(_text(exc.stdout), 12000),
            "stderr": "command timed out",
        }


def expected_paths(analysis: dict[str, object]) -> list[str]:
    paths: list[str] = []
    for unit in analysis.get("change_units", []):
        if not isinstance(unit, dict) or not unit.get("mandatory", True):
            continue
        location = unit.get("target_location", {})
        if isinstance(location, dict) and location.get("path"):
            paths.append(str(location["path"]))
    return sorted(set(paths))


def find_conflict_markers(checkout: Path, paths: list[str]) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for relative in paths:
        path = checkout / relative
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                found.append({"path": relative, "line": number, "text": line[:120]})
    return found


def process_fact(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return {
        "passed": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": limit(_text(result.stdout), 4000),
        "stderr": limit(_text(result.stderr), 4000),
    }


def limit(text: str, maximum: int) -> str:
    return text if len(text) <= maximum else text[:maximum] + "...[truncated]"


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def write_report(path: Path, evidence: dict[str, object]) -> None:
    structural = evidence["structural_checks"]
    commands = evidence["commands"]
    lines = [
        "# Patch Port Validation Evidence",
        "",
        f"- Evidence status: `{evidence['evidence_status']}`",
        f"- Recommended final status before semantic review: `{evidence['recommended_validation_status']}`",
        f"- Target: `{evidence['inputs']['target_commit']}`",
        f"- Patch SHA-256: `{evidence['inputs']['patch_sha256']}`",
        "",
        "## Structural checks",
        "",
    ]
    if structural.get("status") == "not_run":
        lines.append("- Not run: " + structural["reason"])
    else:
        lines.extend([
            f"- Apply check: {structural['apply_check']['passed']}",
            f"- Apply: {structural['apply']['passed']}",
            f"- Diff check: {structural['diff_check']['passed']}",
            f"- Missing planned paths: {structural['changed_paths']['missing']}",
            f"- Conflict markers: {len(structural['conflict_markers'])}",
        ])
    lines.extend(["", "## Commands", ""])
    if commands:
        for item in commands:
            lines.append(f"- {item['command']}: {item['status']}, exit {item['exit_code']}")
    elif evidence["evidence_status"] == "blocked":
        lines.append("- Commands were not run because validation is blocked.")
    else:
        lines.append("- No build or test command was supplied.")
    lines.extend(
        [
            "",
            "## Required semantic review",
            "",
            *[f"- {item}" for item in evidence["semantic_review_required"]],
            "",
            "This evidence report is not a final validation pass decision.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a generated patch in a clean target checkout.")
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--target-ref", required=True)
    parser.add_argument("--patch", required=True, type=Path)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--application", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path, help="Optional Markdown evidence summary; omitted by default.")
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    try:
        evidence = validate(
            repo=args.repo,
            target_ref=args.target_ref,
            patch_path=args.patch,
            analysis_path=args.analysis,
            application_path=args.application,
            commands=args.command,
            timeout=args.timeout,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.report is not None:
            write_report(args.report, evidence)
        print(json.dumps({"status": evidence["evidence_status"], "output": str(args.output.resolve())}))
        return 0 if evidence["evidence_status"] == "structurally_valid" else 2
    except (ValidationError, OSError, ValueError) as exc:
        evidence = blocked_evidence(
            {"repo": str(args.repo.resolve()), "target_commit": None,
             "target_ref": args.target_ref, "patch": str(args.patch.resolve()),
             "patch_sha256": None, "analysis": str(args.analysis.resolve()),
             "application": str(args.application.resolve())},
            {"inputs_available": False}, str(exc))
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if args.report is not None:
                write_report(args.report, evidence)
        except OSError as output_error:
            print(json.dumps({"status": "blocked", "error": str(exc),
                              "output_error": str(output_error)}, ensure_ascii=False), file=sys.stderr)
            return 2
        print(json.dumps({"status": "blocked", "output": str(args.output.resolve())}))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
