#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


STRATEGIES = {
    "strict": [],
    "recount": ["--recount"],
    "whitespace": ["--ignore-space-change", "--ignore-whitespace"],
    "three-way": ["--3way"],
    "three-way-whitespace": ["--3way", "--ignore-space-change", "--ignore-whitespace"],
}


class CandidateError(RuntimeError):
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
        raise CandidateError(f"git {' '.join(args)}: {detail}")
    return result



def check_cross_repo(repo: Path, analysis: dict) -> None:
    """Check repository identity and mapping declarations, not semantic truth."""
    if analysis.get('port_mode', 'history') != 'cross_repo_semantic':
        return
    inputs = analysis.get('inputs', {})
    if not all(inputs.get(k) and Path(inputs[k]).is_absolute()
               for k in ('reference_repo', 'target_repo', 'repo')):
        raise CandidateError('cross-repo mode requires absolute reference_repo, target_repo and repo')
    target = Path(inputs['target_repo']).resolve()
    reference = Path(inputs['reference_repo']).resolve()
    def identity(path):
        value = Path(git(path, ['rev-parse', '--git-common-dir']).stdout.strip())
        return (value if value.is_absolute() else path/value).resolve()
    if Path(inputs['repo']).resolve() != target or identity(repo) != identity(target):
        raise CandidateError('operation must use the declared target repository')
    if identity(reference) == identity(target):
        raise CandidateError('cross-repo mode requires distinct repositories')
    if repo == reference or repo.is_relative_to(reference):
        raise CandidateError('candidate/output must be outside the reference repository')
    for unit in analysis.get('change_units', []):
        if not unit.get('mandatory', True):
            continue
        mapping = unit.get('semantic_mapping', {})
        if mapping.get('status') != 'confirmed' or not mapping.get('evidence_ids'):
            raise CandidateError('mandatory semantic mapping is unresolved or lacks evidence')
        destinations = mapping.get('targets', [])
        if not destinations or any(t.get('repo_role') != 'target' or
                t.get('commit') != inputs.get('target_commit') for t in destinations):
            raise CandidateError('semantic mapping target identity is inconsistent')
        if unit.get('target_location', {}).get('path') not in [t.get('path') for t in destinations]:
            raise CandidateError('planned location is absent from semantic mapping')


def check_analysis_gate(analysis: dict) -> None:
    if analysis.get("analysis_status") not in ("ready", "direct_apply_ready"):
        raise CandidateError("analysis gate is not ready")
    if any(item.get("status") != "resolved" for item in analysis.get("missing_context", [])):
        raise CandidateError("unresolved required context; return to analysis")
    if any(unit.get("mandatory", True) and
           unit.get("map_status") not in ("direct", "mapped", "not_applicable")
           for unit in analysis.get("change_units", [])):
        raise CandidateError("mandatory change-unit mapping is unresolved")


def prepare(repo: Path, target_ref: str, worktree: Path, metadata_output: Path | None,
            analysis_path: Path | None = None) -> dict[str, object]:
    repo = repo.resolve()
    worktree = worktree.resolve()
    if analysis_path is None:
        raise CandidateError("prepare requires --analysis")
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    check_analysis_gate(analysis)
    check_cross_repo(repo, analysis)
    target_commit = git(repo, ["rev-parse", "--verify", f"{target_ref}^{{commit}}"]).stdout.strip()
    if target_commit != analysis.get("inputs", {}).get("target_commit"):
        raise CandidateError("target revision does not match the analyzed target")
    if analysis.get("port_mode") == "cross_repo_semantic":
        reference = Path(analysis["inputs"]["reference_repo"]).resolve()
        if worktree.is_relative_to(reference) or (metadata_output and metadata_output.resolve().is_relative_to(reference)):
            raise CandidateError("outputs must be outside the reference repository")
    if worktree.exists():
        raise CandidateError(f"worktree path already exists: {worktree}")
    worktree.parent.mkdir(parents=True, exist_ok=True)
    git(repo, ["worktree", "add", "--detach", str(worktree), target_commit])
    result = {
        "schema_version": "1.0",
        "status": "prepared",
        "repo": str(repo),
        "target_commit": target_commit,
        "worktree_path": str(worktree),
        "head": git(worktree, ["rev-parse", "HEAD"]).stdout.strip(),
        "baseline_status": git(worktree, ["status", "--short"]).stdout.splitlines(),
    }
    if metadata_output:
        write_json(metadata_output, result)
    return result


def apply_direct(worktree: Path, patch: Path, strategy: str) -> dict[str, object]:
    worktree = worktree.resolve()
    patch = patch.resolve()
    if strategy not in STRATEGIES:
        raise CandidateError(f"unsupported strategy: {strategy}")
    if git(worktree, ["status", "--porcelain"]).stdout.strip():
        raise CandidateError("candidate worktree is not clean before direct apply")
    patch_text = patch.read_text(encoding="utf-8", errors="replace")
    options = STRATEGIES[strategy]
    checked = git(worktree, ["apply", "--check", *options, "-"], check=False, input_text=patch_text)
    if checked.returncode != 0:
        raise CandidateError(checked.stderr.strip() or "direct apply check failed")
    applied = git(worktree, ["apply", *options, "-"], check=False, input_text=patch_text)
    if applied.returncode != 0:
        raise CandidateError(applied.stderr.strip() or "direct apply failed after successful check")
    return {
        "status": "applied",
        "strategy": strategy,
        "patch": str(patch),
        "changed_paths": git(worktree, ["diff", "--name-only", "HEAD"]).stdout.splitlines(),
    }


def finalize(
    worktree: Path,
    analysis_path: Path,
    patch_output: Path,
    evidence_output: Path,
) -> dict[str, object]:
    worktree = worktree.resolve()
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    check_cross_repo(worktree, analysis)
    if analysis.get('port_mode') == 'cross_repo_semantic':
        reference = Path(analysis['inputs']['reference_repo']).resolve()
        if any(p.resolve().is_relative_to(reference) for p in (patch_output, evidence_output)):
            raise CandidateError('outputs must be outside the reference repository')
    check_analysis_gate(analysis)
    target_commit = str(analysis.get("inputs", {}).get("target_commit", ""))
    if not target_commit:
        raise CandidateError("analysis input does not contain inputs.target_commit")
    head = git(worktree, ["rev-parse", "HEAD"]).stdout.strip()
    if head != target_commit:
        raise CandidateError(f"worktree HEAD {head} does not match analyzed target {target_commit}")

    git(worktree, ["add", "-N", "--", "."])
    diff_check = git(worktree, ["diff", "HEAD", "--check"], check=False)
    patch_text = git(worktree, ["diff", "--binary", "HEAD"]).stdout
    changed_paths = git(worktree, ["diff", "--name-only", "HEAD"]).stdout.splitlines()
    status_lines = git(worktree, ["status", "--short"]).stdout.splitlines()
    expected_paths = _expected_paths(analysis)
    allowed_new = set(analysis.get('approved_new_paths', []))
    absent = [p for p in expected_paths if p not in allowed_new and
              git(worktree, ['cat-file', '-e', f'{target_commit}:{p}'], check=False).returncode != 0]
    if absent:
        raise CandidateError(f'target implementation absent; historical reconstruction forbidden: {absent}')
    missing_expected = sorted(set(expected_paths) - set(changed_paths))
    conflict_markers = _conflict_markers(worktree, changed_paths)
    replay = _check_replay(worktree, target_commit, patch_text) if patch_text else {
        "passed": False,
        "reason": "generated patch is empty",
    }
    candidate_ready = (bool(patch_text.strip()) and diff_check.returncode == 0 and replay["passed"]
                       and not conflict_markers and not missing_expected
                       and not (set(changed_paths) - set(expected_paths)))

    patch_output.parent.mkdir(parents=True, exist_ok=True)
    patch_output.write_text(patch_text, encoding="utf-8")
    result = {
        "schema_version": "1.0",
        "artifact_type": "patch-port-application-evidence",
        "evidence_status": "structurally_ready" if candidate_ready else "blocked",
        "target_commit": target_commit,
        "analysis_path": str(analysis_path.resolve()),
        "worktree_path": str(worktree),
        "generated_patch": str(patch_output.resolve()),
        "generated_patch_sha256": hashlib.sha256(patch_text.encode()).hexdigest(),
        "changed_paths": changed_paths,
        "expected_paths": expected_paths,
        "missing_expected_paths": missing_expected,
        "git_status": status_lines,
        "checks": {
            "non_empty_diff": bool(patch_text.strip()),
            "diff_check": {
                "passed": diff_check.returncode == 0,
                "exit_code": diff_check.returncode,
                "stderr": diff_check.stderr.strip(),
            },
            "conflict_markers": conflict_markers,
            "clean_target_replay": replay,
        },
        "agent_review_required": [
            "mandatory change-unit implementation ledger",
            "coupled-group coverage",
            "target API and control-flow adaptation",
            "absence of unrelated changes",
        ],
        "warnings": (["planned target paths are not all changed"] if missing_expected else []),
    }
    write_json(evidence_output, result)
    return result


def _expected_paths(analysis: dict[str, object]) -> list[str]:
    expected: list[str] = []
    for unit in analysis.get("change_units", []):
        if not isinstance(unit, dict) or not unit.get("mandatory", True):
            continue
        target = unit.get("target_location", {})
        if isinstance(target, dict) and target.get("path"):
            expected.append(str(target["path"]))
    return sorted(set(expected))


def _conflict_markers(worktree: Path, paths: list[str]) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for relative in paths:
        path = worktree / relative
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                found.append({"path": relative, "line": number, "text": line[:120]})
    return found


def _check_replay(source: Path, target_commit: str, patch_text: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="patch-port-replay-") as temporary:
        checkout = Path(temporary) / "repo"
        clone = subprocess.run(
            ["git", "clone", "--quiet", "--shared", "--no-checkout", str(source), str(checkout)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if clone.returncode != 0:
            return {"passed": False, "reason": clone.stderr.strip() or "clone failed"}
        git(checkout, ["checkout", "--quiet", "--detach", target_commit])
        result = git(checkout, ["apply", "--check", "-"], check=False, input_text=patch_text)
        return {
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "stderr": result.stderr.strip(),
        }


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and finalize an isolated patch-port candidate worktree.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--repo", required=True, type=Path)
    prepare_parser.add_argument("--target-ref", required=True)
    prepare_parser.add_argument("--worktree", required=True, type=Path)
    prepare_parser.add_argument("--metadata-output", type=Path)
    prepare_parser.add_argument("--analysis", required=True, type=Path)

    apply_parser = subparsers.add_parser("apply-direct")
    apply_parser.add_argument("--worktree", required=True, type=Path)
    apply_parser.add_argument("--patch", required=True, type=Path)
    apply_parser.add_argument("--strategy", required=True, choices=sorted(STRATEGIES))

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--worktree", required=True, type=Path)
    finalize_parser.add_argument("--analysis", required=True, type=Path)
    finalize_parser.add_argument("--patch-output", required=True, type=Path)
    finalize_parser.add_argument("--evidence-output", required=True, type=Path)

    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.repo, args.target_ref, args.worktree, args.metadata_output, args.analysis)
        elif args.command == "apply-direct":
            result = apply_direct(args.worktree, args.patch, args.strategy)
        else:
            result = finalize(args.worktree, args.analysis, args.patch_output, args.evidence_output)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("evidence_status", "structurally_ready") != "blocked" else 2
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
