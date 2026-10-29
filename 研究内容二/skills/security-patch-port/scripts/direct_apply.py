#!/usr/bin/env python3
"""Apply an unchanged patch to an isolated target; exit 10 if adaptation is needed.

No model, semantic review or project build/test is run by this fast path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def direct_apply(repo, target_ref, patch, output, port_mode="history"):
    start = time.monotonic()
    repo, patch, output = (Path(p).resolve() for p in (repo, patch, output))
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args, cwd=repo, check=True, index=None):
        result = subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-C", str(cwd), *args],
            env={**env, **({"GIT_INDEX_FILE": str(index)} if index else {})},
            capture_output=True, timeout=300)
        if check and result.returncode:
            raise RuntimeError(result.stderr.decode(errors="replace").strip())
        return result

    target = git("rev-parse", "--verify", "--end-of-options", target_ref + "^{commit}").stdout.decode().strip()
    content = patch.read_bytes()
    if not content.strip():
        raise ValueError("reference patch is empty")
    candidate = output / "candidate-worktree"
    for path in (candidate, output / "final.json", output / "generated.patch",
                 output / "details/application.json", output / "details/direct-apply.json"):
        if path.exists() or path.is_symlink():
            raise ValueError(f"fast-path output already exists: {path}")
    output.mkdir(parents=True, exist_ok=True)
    # Probe committed target blobs using a separate index, without checking out an
    # entire Linux tree on the fallback path or touching the caller's index.
    with tempfile.TemporaryDirectory(prefix="patch-direct-index-") as temp:
        index = Path(temp) / "index"
        git("read-tree", target, index=index)
        probe = git("apply", "--cached", "--check", str(patch), index=index, check=False)
    evidence = {"schema_version": "1.0", "repo": str(repo), "target_commit": target,
                "reference_patch_sha256": hashlib.sha256(content).hexdigest(),
                "precheck_exit_code": probe.returncode,
                "precheck_stderr": probe.stderr.decode(errors="replace").strip()}
    if probe.returncode:
        evidence.update(status="not_applicable", elapsed_seconds=time.monotonic() - start)
        save(output / "details/direct-apply.json", evidence)
        return evidence

    git("worktree", "add", "--quiet", "--detach", str(candidate), target)
    check_start = time.monotonic()
    git("apply", "--check", "--index", str(patch), cwd=candidate)
    check_seconds = time.monotonic() - check_start
    apply_start = time.monotonic()
    git("apply", "--index", str(patch), cwd=candidate)
    apply_seconds = time.monotonic() - apply_start
    candidate_tree = git("write-tree", cwd=candidate).stdout.decode().strip()
    baseline_tree = git("rev-parse", target + "^{tree}").stdout.decode().strip()
    if candidate_tree == baseline_tree:
        raise ValueError("patch produced no change")
    # Keep the exact original bytes: this branch never adapts or rewrites a patch.
    (output / "generated.patch").write_bytes(content)
    evidence.update(status="applied", worktree_path=str(candidate),
                    candidate_tree=candidate_tree, baseline_tree=baseline_tree,
                    strict_check_exit_code=0, apply_exit_code=0,
                    check_seconds=check_seconds, apply_seconds=apply_seconds,
                    elapsed_seconds=time.monotonic() - start)
    save(output / "details/direct-apply.json", evidence)
    save(output / "details/application.json", {
        "application_status": "candidate_ready", "strategy": "direct-apply",
        "repo": str(repo), "target_commit": target, "worktree_path": str(candidate),
        "candidate_tree": candidate_tree,
        "generated_patch_sha256": evidence["reference_patch_sha256"],
        "reference_patch_sha256": evidence["reference_patch_sha256"]})
    result = {
        "status": "success", "completion_mode": "direct_apply",
        "repo": str(repo), "verification_scope": "patch_application", "target_commit": target,
        "port_mode": port_mode, "strategy": "direct-apply",
        "output_dir": str(output), "worktree_path": str(candidate),
        "artifacts": {"patch": "generated.patch", "application": "details/application.json",
                      "direct_apply": "details/direct-apply.json"},
        "gates": {"analysis": "not_run", "application": "passed", "validation": "not_run"},
        "semantic_review": "not_run", "build_and_tests": "not_run",
        "summary": "原补丁通过严格应用检查，已直接合入隔离工作树。",
        "warnings": []}
    save(output / "final.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--target-ref", required=True)
    parser.add_argument("--patch", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--port-mode", choices=("history", "cross_repo_semantic"), default="history")
    args = parser.parse_args()
    try:
        result = direct_apply(args.repo, args.target_ref, args.patch, args.output, args.port_mode)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 10 if result["status"] == "not_applicable" else 0


if __name__ == "__main__":
    raise SystemExit(main())
