#!/usr/bin/env python3
"""Deterministic orchestration front-end for Patch Compatibility Analyzer.

The key invariant is that candidate extraction and call-graph construction read
from a reproducible analysis worktree, not from whatever branch the user's repo
happens to have checked out.  The worktree is created from base_ref (or HEAD)
and the patch is applied there before any source context is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCRIPT_DIR = Path(__file__).resolve().parent
PROFILE_LOADER = SCRIPT_DIR / "profile_loader.py"
DIFF_PARSER = SCRIPT_DIR / "diff_parser.py"
CALLGRAPH = SCRIPT_DIR / "callgraph.py"
VALIDATOR = SCRIPT_DIR / "validate_analysis.py"
CHECK_DEPENDENCIES = SCRIPT_DIR / "check_dependencies.py"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from profile_loader import _dump_yaml, load_profile

LANG_BY_EXT = {
    ".c": "c",
    ".h": "c",
    ".cc": "c",
    ".cpp": "c",
    ".cxx": "c",
    ".hpp": "c",
    ".py": "python",
    ".go": "go",
    ".rb": "ruby",
}

HEAVY_SOFT_THRESHOLDS = {
    "patch_lines": 600,
    "raw_hunks": 30,
    "changed_files": 12,
    "churn": 250,
    "candidate_hunks": 25,
    "candidate_context_bytes": 100_000,
    "candidates_json_bytes": 100_000,
}

HEAVY_HARD_THRESHOLDS = {
    "patch_lines": 1000,
    "raw_hunks": 45,
    "changed_files": 25,
    "candidate_hunks": 40,
    "candidate_context_bytes": 180_000,
    "candidates_json_bytes": 180_000,
}

SHARD_LIMITS = {
    "max_hunks": 12,
    "max_files": 8,
    "max_context_bytes": 80_000,
    "max_symbols": 20,
}

SURFACE_METADATA_KEYS = (
    "analysis_guidance",
    "compatibility_focus",
    "risk_examples",
)


@dataclass
class AnalysisState:
    source_repo: Path
    analysis_repo: Path
    requested_base_ref: str
    base_commit: str
    patch_apply_status: str
    patch_apply_message: str


def run_result(
    cmd: list[str], cwd: Optional[Path] = None, timeout: int = 120
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def run(cmd: list[str], cwd: Optional[Path] = None, timeout: int = 120) -> str:
    result = run_result(cmd, cwd=cwd, timeout=timeout)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout
        raise RuntimeError(
            "command failed (%s): %s\n%s"
            % (result.returncode, " ".join(cmd), detail)
        )
    return result.stdout.strip()


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "ssh", "git"} or value.startswith("git@")


def repo_name_from_url(url: str) -> str:
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    if tail.endswith(".git"):
        tail = tail[:-4]
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", tail) or "repo"


def commit_hash_from_value(value: str) -> str:
    match = re.search(r"(?i)([0-9a-f]{12,40})(?:\.patch|\.diff)?(?=$|[\s/?#])", value)
    return match.group(1).lower() if match else ""


def normalize_patch_download_url(value: str) -> str:
    """Convert common commit URLs to raw patch URLs."""
    parsed = urlparse(value)
    if not parsed.scheme:
        return value
    path = parsed.path.rstrip("/")
    if path.endswith((".patch", ".diff")):
        return value

    netloc = parsed.netloc.lower()
    base = parsed._replace(path=path, params="", query="", fragment="").geturl()
    if "github.com" in netloc:
        if re.search(r"/(?:commit|pull|compare)/[^/]+$", path):
            return base + ".patch"
    if "gitlab." in netloc:
        if re.search(r"/(?:-/)?(?:commit|merge_requests)/[^/]+$", path):
            return base + ".patch"
    return value


def patch_cache_name(value: str, download_url: str) -> str:
    commit = commit_hash_from_value(value) or commit_hash_from_value(download_url)
    suffix = ".diff" if urlparse(download_url).path.endswith(".diff") else ".patch"
    if commit:
        return commit[:12] + suffix
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:12]
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(urlparse(value).path).stem).strip("-")
    return "%s-%s%s" % (stem or "patch", digest, suffix)


def download_patch_url(value: str, cache_dir: Path) -> tuple[Path, dict]:
    download_url = normalize_patch_download_url(value)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / patch_cache_name(value, download_url)
    request = Request(
        download_url,
        headers={
            "User-Agent": "patch-compatibility-analysis/1.0",
            "Accept": "text/x-patch,text/plain,*/*",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            content = response.read(50 * 1024 * 1024 + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError("failed to download patch URL %s: %s" % (download_url, exc))

    if len(content) > 50 * 1024 * 1024:
        raise RuntimeError("refusing to analyze patch larger than 50 MiB: %s" % download_url)

    text = content.decode("utf-8", errors="replace")
    if "diff --git " not in text and not re.search(r"(?m)^(---|\+\+\+)\s+", text):
        raise RuntimeError(
            "downloaded URL does not look like a unified diff/patch: %s" % download_url
        )
    cache_path.write_text(text, encoding="utf-8")
    return cache_path, {
        "kind": "url",
        "input": value,
        "download_url": download_url,
        "cached_patch": str(cache_path),
        "commit": commit_hash_from_value(value) or commit_hash_from_value(text),
    }


def resolve_patch_input(patch_arg: str, cache_dir: Path) -> tuple[Path, dict]:
    if is_url(patch_arg):
        return download_patch_url(patch_arg, cache_dir)

    patch_path = Path(patch_arg).expanduser().resolve()
    if not patch_path.is_file():
        raise FileNotFoundError("patch file does not exist: %s" % patch_path)
    return patch_path, {
        "kind": "local_file",
        "input": patch_arg,
        "cached_patch": "",
        "commit": "",
    }


def prepare_repo(repo_arg: str, clone_root: Path) -> Path:
    if not is_url(repo_arg):
        repo = Path(repo_arg).resolve()
        if not repo.is_dir():
            raise FileNotFoundError("repo path does not exist: %s" % repo)
        return repo

    clone_root.mkdir(parents=True, exist_ok=True)
    repo = (clone_root / repo_name_from_url(repo_arg)).resolve()
    if repo.exists():
        return repo
    run(["git", "clone", "--depth", "100", repo_arg, str(repo)], timeout=300)
    return repo


def patch_id_from_text(patch_path: Path, patch_text: str) -> str:
    patterns = [
        r"(?m)^From\s+([0-9a-fA-F]{7,40})\b",
        r"(?m)^commit\s+([0-9a-fA-F]{40})\b",
        r"(?m)^commit\s+([0-9a-fA-F]{12,40})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, patch_text)
        if match:
            return match.group(1).lower()

    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", patch_path.stem).strip("-")
    stem_hash = re.search(r"(?i)([0-9a-f]{7,40})", stem)
    if stem_hash:
        return stem_hash.group(1).lower()
    if stem and stem.lower() not in {"patch", "diff"}:
        return stem

    return hashlib.sha256(patch_text.encode("utf-8", errors="replace")).hexdigest()[:12]


def infer_language(file_path: str) -> str:
    return LANG_BY_EXT.get(Path(file_path).suffix.lower(), "c")


def detect_profile(repo: Path, profile: str) -> str:
    if profile != "auto":
        return profile
    detected = run([sys.executable, str(PROFILE_LOADER), "--detect", str(repo)])
    return detected or "c_project"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def flatten_patch_metrics(candidates: dict, candidates_path: Optional[Path] = None) -> dict:
    summary = candidates.get("summary", {})
    metrics = dict(summary.get("patch_metrics") or {})
    metrics.setdefault("changed_files", summary.get("total_changed_files", 0))
    metrics.setdefault("candidate_hunks", summary.get("total_hunks", 0))
    metrics.setdefault("public_candidate_hunks", summary.get("public_api_hunks", 0))
    if candidates_path and candidates_path.exists():
        metrics["candidates_json_bytes"] = candidates_path.stat().st_size
    else:
        metrics.setdefault("candidates_json_bytes", 0)
    return metrics


def threshold_reasons(metrics: dict, thresholds: dict[str, int]) -> list[str]:
    reasons = []
    for key, threshold in thresholds.items():
        value = metrics.get(key, 0)
        if isinstance(value, (int, float)) and value >= threshold:
            reasons.append("%s=%s >= %s" % (key, value, threshold))
    return reasons


def decide_analysis_mode(requested_mode: str, metrics: dict) -> dict:
    hard_reasons = threshold_reasons(metrics, HEAVY_HARD_THRESHOLDS)
    soft_reasons = threshold_reasons(metrics, HEAVY_SOFT_THRESHOLDS)

    if requested_mode == "heavy":
        mode = "heavy"
        reason = ["user requested heavy mode"] + soft_reasons + hard_reasons
    elif hard_reasons:
        mode = "heavy"
        reason = ["hard threshold exceeded"] + hard_reasons
    elif requested_mode == "normal":
        mode = "normal"
        reason = ["user requested normal mode; no hard threshold exceeded"]
    elif soft_reasons:
        mode = "heavy"
        reason = ["soft threshold exceeded"] + soft_reasons
    else:
        mode = "normal"
        reason = ["below heavy thresholds"]

    return {
        "mode": mode,
        "requested_mode": requested_mode,
        "heavy_reason": reason,
        "soft_thresholds": HEAVY_SOFT_THRESHOLDS,
        "hard_thresholds": HEAVY_HARD_THRESHOLDS,
        "metrics": metrics,
    }


def candidate_context_bytes(candidate: dict) -> int:
    snippet = (candidate.get("context") or {}).get("snippet", "")
    return len(snippet.encode("utf-8", errors="replace"))


def candidate_symbols(candidate: dict) -> set[str]:
    return {symbol for symbol in candidate.get("changed_symbols", []) if symbol}


def candidate_surface_key(candidate: dict) -> str:
    api_surface = candidate.get("api_surface") or {}
    surfaces = api_surface.get("matched_surfaces") or []
    if surfaces:
        return surfaces[0].get("name") or "unknown_surface"
    reasons = api_surface.get("surface_reasons") or []
    return reasons[0] if reasons else "internal_or_unknown"


def shard_would_exceed(shard: dict, candidate: dict) -> bool:
    files = set(shard["files"])
    files.add(candidate.get("file", ""))
    symbols = set(shard["symbols"]) | candidate_symbols(candidate)
    context_bytes = shard["metrics"]["context_bytes"] + candidate_context_bytes(candidate)
    hunk_count = shard["metrics"]["hunks"] + 1
    return (
        hunk_count > SHARD_LIMITS["max_hunks"]
        or len(files) > SHARD_LIMITS["max_files"]
        or len(symbols) > SHARD_LIMITS["max_symbols"]
        or context_bytes > SHARD_LIMITS["max_context_bytes"]
    )


def new_shard(index: int, surface: str) -> dict:
    return {
        "id": "SHARD-%04d" % index,
        "surface": surface,
        "candidate_indexes": [],
        "hunk_ids": [],
        "files": [],
        "symbols": [],
        "metrics": {
            "hunks": 0,
            "context_bytes": 0,
        },
        "artifact": "",
        "status": "planned",
    }


def add_candidate_to_shard(shard: dict, candidate_index: int, candidate: dict) -> None:
    shard["candidate_indexes"].append(candidate_index)
    shard["hunk_ids"].append(candidate.get("hunk_id") or "HUNK-%04d" % (candidate_index + 1))
    if candidate.get("file") not in shard["files"]:
        shard["files"].append(candidate.get("file"))
    for symbol in sorted(candidate_symbols(candidate)):
        if symbol not in shard["symbols"]:
            shard["symbols"].append(symbol)
    shard["metrics"]["hunks"] += 1
    shard["metrics"]["context_bytes"] += candidate_context_bytes(candidate)


def plan_shards(candidates: dict) -> list[dict]:
    shards: list[dict] = []
    current: Optional[dict] = None
    current_surface = ""

    ordered = sorted(
        enumerate(candidates.get("candidates", [])),
        key=lambda item: (
            candidate_surface_key(item[1]),
            item[1].get("file", ""),
            ",".join(item[1].get("changed_symbols", []) or []),
            item[1].get("new_start", 0),
        ),
    )

    for candidate_index, candidate in ordered:
        surface = candidate_surface_key(candidate)
        if current is None or surface != current_surface or shard_would_exceed(current, candidate):
            current = new_shard(len(shards) + 1, surface)
            shards.append(current)
            current_surface = surface
        add_candidate_to_shard(current, candidate_index, candidate)

    return shards


def write_shard_artifacts(
    result_dir: Path,
    candidates: dict,
    mode_decision: dict,
) -> dict:
    shards = plan_shards(candidates)
    shard_dir = result_dir / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    candidate_list = candidates.get("candidates", [])

    for shard in shards:
        shard_path = shard_dir / ("%s.json" % shard["id"].lower())
        shard["artifact"] = str(shard_path.relative_to(result_dir)).replace("\\", "/")
        instructions = (
            "Analyze only candidates in this shard. Use the repository paths "
            "from analysis.json. Do not infer compatibility findings from "
            "other shards. Emit confirmed findings only; use manual_review_required "
            "when a cross-shard dependency is needed."
        )
        payload = {
            "shard_id": shard["id"],
            "surface": shard["surface"],
            "analysis_mode": mode_decision["mode"],
            "limits": SHARD_LIMITS,
            "candidate_indexes": shard["candidate_indexes"],
            "hunk_ids": shard["hunk_ids"],
            "files": shard["files"],
            "symbols": shard["symbols"],
            "metrics": shard["metrics"],
            "candidates": [candidate_list[index] for index in shard["candidate_indexes"]],
            "instructions": instructions,
        }
        write_json(shard_path, payload)

    shard_plan = {
        "analysis_mode": mode_decision["mode"],
        "requested_mode": mode_decision["requested_mode"],
        "heavy_reason": mode_decision["heavy_reason"],
        "limits": SHARD_LIMITS,
        "shard_count": len(shards),
        "shards": shards,
        "aggregation": {
            "expected_input": "shard-results/*.json or shard result paths passed to --aggregate-shards",
            "dedupe_key": "affected_api.name + location.file + location.new_lines + compatibility_type",
        },
    }
    write_json(result_dir / "shards.json", shard_plan)
    return shard_plan

def write_effective_profile(
    profile: str,
    repo: Path,
    result_dir: Path,
) -> Path:
    output = result_dir / "effective-profile.yaml"
    profile_data = load_profile(profile, str(repo))
    output.write_text(_dump_yaml(profile_data), encoding="utf-8")
    return output


def analysis_result_dir(analysis_path: Path, analysis: dict) -> Path:
    configured = analysis.get("artifact_dir")
    if configured:
        path = Path(configured).resolve()
        analysis_parent = analysis_path.parent.resolve()
        if path == analysis_parent:
            return path
        if (path / "analysis.json").resolve() == analysis_path.resolve():
            return path
    return analysis_path.parent.resolve()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def ensure_git_repo(repo: Path) -> Path:
    top = Path(run(["git", "rev-parse", "--show-toplevel"], cwd=repo)).resolve()
    return top


def remove_previous_analysis_worktree(
    source_repo: Path, worktree_path: Path, result_dir: Path
) -> None:
    if not is_relative_to(worktree_path, result_dir):
        raise RuntimeError("refusing to remove worktree outside result dir: %s" % worktree_path)

    if worktree_path.exists():
        if os.environ.get("PCA_ALLOW_WORKTREE_DELETE") != "1":
            raise RuntimeError(
                "analysis worktree already exists and deletion is disabled: %s. "
                "Use finalize-patch cleanup or set PCA_ALLOW_WORKTREE_DELETE=1 only for approved cleanup."
                % worktree_path
            )
        removed = run_result(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=source_repo,
            timeout=180,
        )
        if removed.returncode != 0:
            shutil.rmtree(worktree_path)
    run_result(["git", "worktree", "prune"], cwd=source_repo, timeout=60)


def apply_patch_to_worktree(worktree: Path, patch_path: Path) -> tuple[str, str]:
    attempts = []

    forward_check = run_result(
        ["git", "apply", "--check", str(patch_path)],
        cwd=worktree,
        timeout=180,
    )
    if forward_check.returncode == 0:
        run(["git", "apply", "--whitespace=nowarn", str(patch_path)], cwd=worktree, timeout=300)
        return "applied", "patch applied cleanly"
    attempts.append("git apply --check: %s" % (forward_check.stderr.strip() or "failed"))

    reverse_check = run_result(
        ["git", "apply", "--reverse", "--check", str(patch_path)],
        cwd=worktree,
        timeout=180,
    )
    if reverse_check.returncode == 0:
        return "already_applied", "patch content is already present in analysis worktree"
    attempts.append(
        "git apply --reverse --check: %s" % (reverse_check.stderr.strip() or "failed")
    )

    threeway_check = run_result(
        ["git", "apply", "--3way", "--check", str(patch_path)],
        cwd=worktree,
        timeout=180,
    )
    if threeway_check.returncode == 0:
        run(
            ["git", "apply", "--3way", "--whitespace=nowarn", str(patch_path)],
            cwd=worktree,
            timeout=300,
        )
        return "applied_3way", "patch applied with git apply --3way"
    attempts.append("git apply --3way --check: %s" % (threeway_check.stderr.strip() or "failed"))

    raise RuntimeError(
        "patch does not apply to the selected base and is not already applied. "
        "Pass the correct --base-ref or update the repository.\n"
        + "\n".join(attempts)
    )


def prepare_analysis_worktree(
    source_repo: Path,
    result_dir: Path,
    patch_path: Path,
    base_ref: Optional[str],
    requested_base_ref: Optional[str] = None,
) -> AnalysisState:
    git_root = ensure_git_repo(source_repo)
    checkout_ref = base_ref or "HEAD"
    displayed_base_ref = requested_base_ref or checkout_ref
    base_commit = run(["git", "rev-parse", checkout_ref], cwd=git_root)

    worktree_path = result_dir / "_worktrees" / "patched"
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    remove_previous_analysis_worktree(git_root, worktree_path, result_dir)
    run(
        ["git", "worktree", "add", "--detach", str(worktree_path), base_commit],
        cwd=git_root,
        timeout=300,
    )
    status, message = apply_patch_to_worktree(worktree_path, patch_path)

    return AnalysisState(
        source_repo=git_root,
        analysis_repo=worktree_path.resolve(),
        requested_base_ref=displayed_base_ref,
        base_commit=base_commit,
        patch_apply_status=status,
        patch_apply_message=message,
    )


def infer_base_ref_from_patch_source(
    source_repo: Path,
    explicit_base_ref: Optional[str],
    patch_source: dict,
) -> tuple[Optional[str], dict]:
    if explicit_base_ref:
        return explicit_base_ref, patch_source

    commit = patch_source.get("commit") or ""
    if not commit:
        return explicit_base_ref, patch_source

    parent_ref = "%s^" % commit
    result = run_result(["git", "rev-parse", "--verify", parent_ref], cwd=source_repo)
    if result.returncode != 0:
        return explicit_base_ref, patch_source

    updated = dict(patch_source)
    updated["base_ref_inferred"] = parent_ref
    updated["base_ref_inference"] = "target commit parent exists in source repo"
    return parent_ref, updated



def set_analysis_worktree_status(analysis_path: Path, status: str) -> None:
    if not analysis_path.exists():
        return
    analysis = load_json(analysis_path)
    analysis["analysis_worktree_status"] = status
    write_json(analysis_path, analysis)


def update_manifest_worktree_status(manifest_path: Path, status: str) -> None:
    if not manifest_path.exists():
        return
    manifest = load_json(manifest_path)
    manifest["analysis_worktree_status"] = status
    manifest["worktree_recreate_command"] = (
        "%s %s --ensure-worktree %s"
        % (sys.executable, Path(__file__).resolve(), manifest_path.parent / "analysis.json")
    )
    manifest["worktree_cleanup_command"] = (
        "%s %s --cleanup-worktree %s"
        % (sys.executable, Path(__file__).resolve(), manifest_path.parent / "analysis.json")
    )
    write_json(manifest_path, manifest)


def cleanup_analysis_worktree(state: AnalysisState, result_dir: Path) -> None:
    remove_previous_analysis_worktree(state.source_repo, state.analysis_repo, result_dir)
    set_analysis_worktree_status(result_dir / "analysis.json", "cleaned")
    update_manifest_worktree_status(result_dir / "manifest.json", "cleaned")


def ensure_worktree_from_analysis(analysis_path: Path) -> AnalysisState:
    analysis = load_json(analysis_path)
    source_repo = Path(analysis.get("repo", "")).resolve()
    result_dir = analysis_result_dir(analysis_path, analysis)
    patch_path = result_dir / "patch.diff"
    base_commit = analysis.get("base_commit")
    if not source_repo.is_dir():
        raise RuntimeError("source repo does not exist: %s" % source_repo)
    if not patch_path.is_file():
        raise RuntimeError("patch.diff does not exist: %s" % patch_path)
    if not base_commit:
        raise RuntimeError("analysis.json has no base_commit; rerun initial orchestrator")

    state = prepare_analysis_worktree(
        source_repo=source_repo,
        result_dir=result_dir,
        patch_path=patch_path,
        base_ref=base_commit,
        requested_base_ref=analysis.get("base_ref") or base_commit,
    )
    analysis["analysis_repo"] = str(state.analysis_repo)
    analysis["base_commit"] = state.base_commit
    analysis["patch_apply_status"] = state.patch_apply_status
    analysis["patch_apply_message"] = state.patch_apply_message
    analysis["analysis_worktree_status"] = "available"
    write_json(analysis_path, analysis)
    update_manifest_worktree_status(result_dir / "manifest.json", "available")
    return state


def build_callchains(
    analysis_repo: Path,
    result_dir: Path,
    targets: list[tuple[str, str, str]],
    max_depth: int,
    max_chains: int,
) -> list[dict]:
    aggregate: list[dict] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for symbol, file_path, language in targets:
        safe_symbol = re.sub(r"[^A-Za-z0-9_.-]+", "_", symbol)
        out_path = result_dir / ("callchains-%s.json" % safe_symbol)
        try:
            run(
                [
                    sys.executable,
                    str(CALLGRAPH),
                    "--repo",
                    str(analysis_repo),
                    "--target",
                    symbol,
                    "--file",
                    file_path,
                    "--language",
                    language,
                    "--max-depth",
                    str(max_depth),
                    "--max-chains",
                    str(max_chains),
                    "--output",
                    str(out_path),
                ],
                timeout=45,
            )
            chains = load_json(out_path) if out_path.exists() else []
        except Exception:
            chains = []
            write_json(out_path, chains)

        for chain in chains:
            key = (
                chain.get("entry_kind", ""),
                chain.get("entry", ""),
                tuple(chain.get("chain", [])),
            )
            if key not in seen:
                seen.add(key)
                aggregate.append(chain)

    write_json(result_dir / "callchains.json", aggregate)
    return aggregate


def dependency_check_for_callgraph(targets: list[tuple[str, str, str]]) -> None:
    languages = sorted({language for _, _, language in targets})
    if not languages:
        return
    run(
        [
            sys.executable,
            str(CHECK_DEPENDENCIES),
            "--include-callgraph",
            "--languages",
            ",".join(languages),
        ],
        timeout=60,
    )


def finding_targets(analysis: dict) -> list[tuple[str, str, str]]:
    targets: dict[tuple[str, str, str], None] = {}
    for finding in analysis.get("findings", []):
        location = finding.get("location") or {}
        affected_api = finding.get("affected_api") or {}
        symbol = location.get("symbol") or affected_api.get("name")
        file_path = location.get("file", "")
        language = affected_api.get("language") or infer_language(file_path)
        if symbol and file_path:
            targets[(symbol, file_path, language)] = None
    return list(targets.keys())


def analysis_state_from_analysis(analysis: dict, analysis_path: Path) -> AnalysisState:
    analysis_repo = analysis.get("analysis_repo") or analysis.get("patched_worktree")
    if not analysis_repo:
        raise RuntimeError(
            "analysis.json has no analysis_repo/patched_worktree field. "
            "Run orchestrator.py --ensure-worktree analysis.json first."
        )
    source_repo = Path(analysis.get("repo", "")).resolve()
    return AnalysisState(
        source_repo=source_repo,
        analysis_repo=Path(analysis_repo).resolve(),
        requested_base_ref=analysis.get("base_ref") or analysis.get("base_commit") or "HEAD",
        base_commit=analysis.get("base_commit") or "",
        patch_apply_status=analysis.get("patch_apply_status") or "",
        patch_apply_message=analysis.get("patch_apply_message") or "",
    )


def ensure_analysis_worktree_available(analysis_path: Path) -> AnalysisState:
    analysis = load_json(analysis_path)
    state = analysis_state_from_analysis(analysis, analysis_path)
    if state.analysis_repo.is_dir():
        return state
    return ensure_worktree_from_analysis(analysis_path)


def attach_callchains_to_analysis(
    analysis_path: Path,
    max_depth: int,
    max_chains: int,
) -> None:
    analysis = load_json(analysis_path)
    state = ensure_analysis_worktree_available(analysis_path)
    analysis = load_json(analysis_path)
    analysis_repo = state.analysis_repo
    result_dir = analysis_result_dir(analysis_path, analysis)
    targets = finding_targets(analysis)
    dependency_check_for_callgraph(targets)
    callchains = build_callchains(analysis_repo, result_dir, targets, max_depth, max_chains)

    chains_by_tail = {}
    for chain in callchains:
        tail = (chain.get("chain") or [""])[-1]
        chains_by_tail.setdefault(tail, []).append(chain)

    for finding in analysis.get("findings", []):
        location = finding.get("location") or {}
        affected_api = finding.get("affected_api") or {}
        symbol = location.get("symbol") or affected_api.get("name")
        finding["static_call_chains"] = chains_by_tail.get(symbol, [])

    analysis["callgraph_repo"] = str(analysis_repo)
    if "candidate_artifacts" in analysis:
        analysis["candidate_artifacts"]["callchains"] = "callchains.json"
        analysis["candidate_artifacts"]["callchain_count"] = len(callchains)
    write_json(analysis_path, analysis)
    run([sys.executable, str(VALIDATOR), str(analysis_path)], timeout=60)


def finding_dedupe_key(finding: dict) -> tuple:
    location = finding.get("location") or {}
    affected_api = finding.get("affected_api") or {}
    return (
        affected_api.get("name", ""),
        location.get("file", ""),
        tuple(location.get("new_lines", [])),
        finding.get("compatibility_type", ""),
    )


def collect_shard_result_paths(result_dir: Path, explicit_paths: Optional[list[str]]) -> list[Path]:
    if explicit_paths:
        return [Path(path).resolve() for path in explicit_paths]
    candidates = []
    for pattern in ("shard-results/*.json", "shards/*-analysis.json", "shards/*-result.json"):
        candidates.extend(result_dir.glob(pattern))
    return sorted(path.resolve() for path in candidates)


def load_findings_from_shard(path: Path) -> list[dict]:
    data = load_json(path)
    if isinstance(data, dict):
        findings = data.get("findings", [])
        return findings if isinstance(findings, list) else []
    if isinstance(data, list):
        return data
    return []


def aggregate_shards(analysis_path: Path, explicit_paths: Optional[list[str]]) -> None:
    analysis = load_json(analysis_path)
    result_dir = analysis_result_dir(analysis_path, analysis)
    result_paths = collect_shard_result_paths(result_dir, explicit_paths)
    if not result_paths:
        raise RuntimeError(
            "no shard result files found. Expected shard-results/*.json or pass --shard-result"
        )

    merged = []
    seen = set()
    source_map = {}
    for path in result_paths:
        for finding in load_findings_from_shard(path):
            if not isinstance(finding, dict):
                continue
            key = finding_dedupe_key(finding)
            if key in seen:
                source_map.setdefault(str(key), []).append(str(path))
                continue
            seen.add(key)
            finding = dict(finding)
            finding.setdefault("static_call_chains", [])
            finding.setdefault("test_entries", [])
            finding["source_shard_result"] = str(path.relative_to(result_dir)) if is_relative_to(path, result_dir) else str(path)
            merged.append(finding)
            source_map[str(key)] = [str(path)]

    for index, finding in enumerate(merged, start=1):
        finding["id"] = "PCA-%04d" % index

    summary = analysis.setdefault("summary", {})
    summary["compatibility_changes"] = len(merged)
    summary["high_priority"] = sum(1 for item in merged if item.get("test_priority") == "high")
    summary["medium_priority"] = sum(1 for item in merged if item.get("test_priority") == "medium")
    summary["low_priority"] = sum(1 for item in merged if item.get("test_priority") == "low")

    analysis["findings"] = merged
    analysis["analysis_mode"] = analysis.get("analysis_mode", "heavy")
    analysis["shard_aggregation"] = {
        "result_files": [
            str(path.relative_to(result_dir)) if is_relative_to(path, result_dir) else str(path)
            for path in result_paths
        ],
        "input_findings": sum(len(load_findings_from_shard(path)) for path in result_paths),
        "deduped_findings": len(merged),
        "dedupe_key": "affected_api.name + location.file + location.new_lines + compatibility_type",
    }
    write_json(analysis_path, analysis)
    run([sys.executable, str(VALIDATOR), str(analysis_path)], timeout=60)


def write_analysis_scaffold(
    state: AnalysisState,
    result_dir: Path,
    patch_id: str,
    profile: str,
    patch_source: dict,
    candidates: dict,
    callchains: list[dict],
    mode_decision: dict,
    shard_plan: Optional[dict],
    patch_metrics: dict,
) -> dict:
    summary = candidates.get("summary", {})
    analysis = {
        "repo": str(state.source_repo),
        "analysis_repo": str(state.analysis_repo),
        "artifact_dir": str(result_dir),
        "base_ref": state.requested_base_ref,
        "base_commit": state.base_commit,
        "patch_apply_status": state.patch_apply_status,
        "patch_apply_message": state.patch_apply_message,
        "analysis_worktree_status": "available",
        "patch_id": patch_id,
        "patch_source": patch_source,
        "package_profile": profile,
        "effective_profile": "effective-profile.yaml",
        "analysis_mode": mode_decision["mode"],
        "analysis_mode_requested": mode_decision["requested_mode"],
        "heavy_reason": mode_decision["heavy_reason"],
        "heavy_thresholds": {
            "soft": HEAVY_SOFT_THRESHOLDS,
            "hard": HEAVY_HARD_THRESHOLDS,
        },
        "patch_metrics": patch_metrics,
        "shard_artifacts": {
            "plan": "shards.json",
            "workspace": "shards/",
            "shard_count": shard_plan.get("shard_count", 0) if shard_plan else 0,
        } if shard_plan else {},
        "summary": {
            "total_changed_files": summary.get("total_changed_files", 0),
            "total_candidates": summary.get("total_hunks", 0),
            "compatibility_changes": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
        },
        "findings": [],
        "candidate_artifacts": {
            "analysis_context": "analysis-context.json",
            "candidates": "candidates.json",
            "callchains": "callchains.json",
            "callchain_count": len(callchains),
            "effective_profile": "effective-profile.yaml",
            "patch_metrics": "patch-metrics.json",
        },
        "next_step": (
            "Agent must adjudicate candidates and write final compatibility findings. "
            "If analysis_mode is heavy, analyze shard files under shards/ first and "
            "merge shard results with orchestrator.py --aggregate-shards analysis.json. "
            "Final findings should include only confirmed compatibility changes. "
            "Every finding must include location.file, location.old_lines, "
            "location.new_lines, location.symbol, and evidence[].lines. "
            "Read analysis-context.json before candidates.json/report.md; it "
            "contains the bounded hunk, surface, changed-line context, and "
            "source_excerpt needed for normal adjudication. Treat source_excerpt "
            "as the first-pass source window and open candidates.json or source "
            "files only when the compact context is insufficient. If a command is "
            "rejected, do not retry equivalent list/search/read commands. "
            "Post-patch source search/read operations, including rg/grep/sed/git grep, "
            "must use analysis_repo as the root. repo is only the source repository "
            "and artifact location. For pre-patch code, use git show base_commit:path "
            "against repo. If analysis_worktree_status is cleaned or analysis_repo is "
            "missing, run orchestrator.py --ensure-worktree analysis.json before "
            "post-patch source search or callgraph. Do not generate runnable test "
            "entries in the analysis stage. After final validation and reporting, if "
            "the user has not already requested testing, ask whether to continue "
            "with directed dynamic testing via the sibling "
            "patch-compatibility-testing skill."
        ),
    }
    write_json(result_dir / "analysis.json", analysis)
    return analysis


def compact_changed_lines(candidate: dict, key: str, limit: int = 12) -> list[str]:
    lines = [line.rstrip("\n") for line in candidate.get(key, []) if str(line).strip()]
    if len(lines) <= limit:
        return lines
    return lines[:limit] + ["..."]


def compact_surfaces(candidate: dict) -> list[dict]:
    api_surface = candidate.get("api_surface") or {}
    output = []
    for item in api_surface.get("matched_surfaces") or []:
        if not isinstance(item, dict):
            continue
        compact = {
            "name": item.get("name", ""),
            "test_priority": item.get("test_priority", ""),
            "stability": item.get("stability", ""),
            "public": item.get("public", api_surface.get("is_public", False)),
            "semantic_dimensions": item.get("semantic_dimensions", []),
            "description": item.get("description", ""),
        }
        for key in SURFACE_METADATA_KEYS:
            if key in item:
                compact[key] = item.get(key)
        output.append(compact)
    if output:
        return output[:8]
    return [
        {
            "name": reason,
            "test_priority": "",
            "stability": "",
            "public": api_surface.get("is_public", False),
        }
        for reason in (api_surface.get("surface_reasons") or [])[:8]
    ]


def compact_source_excerpt(
    candidate: dict,
    max_lines: int = 80,
    max_chars: int = 12_000,
) -> dict:
    context = candidate.get("context") or {}
    snippet = (context.get("snippet") or "").rstrip("\n")
    snippet_start = context.get("snippet_start_line")
    if not snippet or not isinstance(snippet_start, int):
        return {
            "file": candidate.get("file", ""),
            "start_line": context.get("snippet_start_line"),
            "end_line": context.get("snippet_end_line"),
            "enclosing_function": context.get("enclosing_function", ""),
            "lines": [],
            "truncated": False,
        }

    lines = snippet.splitlines()
    hunk_start = candidate.get("new_start")
    if not isinstance(hunk_start, int):
        hunk_start = snippet_start

    if len(lines) > max_lines:
        preferred_offset = max(0, hunk_start - snippet_start - (max_lines // 3))
        offset = min(preferred_offset, max(0, len(lines) - max_lines))
        selected = lines[offset : offset + max_lines]
    else:
        offset = 0
        selected = lines

    selected_text = "\n".join(selected)
    char_truncated = False
    while len(selected_text.encode("utf-8", errors="replace")) > max_chars and len(selected) > 20:
        selected = selected[:-10]
        selected_text = "\n".join(selected)
        char_truncated = True

    start_line = snippet_start + offset
    return {
        "file": candidate.get("file", ""),
        "start_line": start_line,
        "end_line": start_line + len(selected) - 1 if selected else start_line,
        "enclosing_function": context.get("enclosing_function", ""),
        "lines": [
            {
                "line": start_line + idx,
                "text": line,
            }
            for idx, line in enumerate(selected)
        ],
        "truncated": offset > 0 or len(selected) < len(lines) or char_truncated,
    }


def compact_candidate(
    candidate: dict,
    patch_id: str = "",
) -> dict:
    context = candidate.get("context") or {}
    compact = {
        "hunk_id": candidate.get("hunk_id", ""),
        "file": candidate.get("file", ""),
        "old_lines": [candidate.get("old_start"), candidate.get("old_end")],
        "new_lines": [candidate.get("new_start"), candidate.get("new_end")],
        "context_hint": candidate.get("context_hint", ""),
        "changed_symbols": (candidate.get("changed_symbols") or [])[:20],
        "surfaces": compact_surfaces(candidate),
        "is_public_candidate": bool((candidate.get("api_surface") or {}).get("is_public")),
        "added_lines": compact_changed_lines(candidate, "added_lines"),
        "deleted_lines": compact_changed_lines(candidate, "deleted_lines"),
        "source_excerpt": compact_source_excerpt(candidate),
        "context_window": {
            "file": candidate.get("file", ""),
            "start_line": context.get("snippet_start_line"),
            "end_line": context.get("snippet_end_line"),
            "enclosing_function": context.get("enclosing_function", ""),
        },
    }
    return compact


def write_analysis_context(
    state: AnalysisState,
    result_dir: Path,
    patch_id: str,
    profile: str,
    patch_source: dict,
    candidates: dict,
    mode_decision: dict,
    shard_plan: Optional[dict],
    patch_metrics: dict,
) -> dict:
    summary = candidates.get("summary", {})
    payload = {
        "purpose": (
            "Low-context adjudication input. Read this before candidates.json "
            "or report.md. It embeds bounded source excerpts for each candidate "
            "so agents should not reopen large source files just to locate the "
            "changed function."
        ),
        "repo": str(state.source_repo),
        "analysis_repo": str(state.analysis_repo),
        "artifact_dir": str(result_dir),
        "patch_id": patch_id,
        "patch_source": patch_source,
        "base_ref": state.requested_base_ref,
        "base_commit": state.base_commit,
        "patch_apply_status": state.patch_apply_status,
        "package_profile": profile,
        "effective_profile": "effective-profile.yaml",
        "analysis_mode": mode_decision["mode"],
        "heavy_reason": mode_decision["heavy_reason"],
        "patch_metrics": patch_metrics,
        "summary": {
            "total_changed_files": summary.get("total_changed_files", 0),
            "candidate_hunks": summary.get("total_hunks", 0),
            "public_candidate_hunks": summary.get("public_api_hunks", 0),
        },
        "changed_files": sorted(
            {candidate.get("file", "") for candidate in candidates.get("candidates", []) if candidate.get("file")}
        ),
        "candidate_hunks": [
            compact_candidate(candidate, patch_id)
            for candidate in candidates.get("candidates", [])
        ],
        "heavy_shards": {
            "plan": "shards.json",
            "workspace": "shards/",
            "shard_count": shard_plan.get("shard_count", 0),
        } if shard_plan else {},
        "agent_efficiency_rules": [
            "Do not scan repo roots, patch-list directories, output directories, or profile trees.",
            "Do not list artifact directories with ls/os.listdir; read the named artifact files directly.",
            "Use this file plus patch.diff before opening candidates.json, report.md, or source files.",
            "Treat candidate_hunks[].source_excerpt as the authoritative focused source window for first-pass semantic judgment.",
            "Open candidates.json only when this compact context is insufficient for a specific finding.",
            "Do not inspect unchanged callee implementations merely to restate changed argument/data-flow unless the callee contract itself is disputed.",
            "If an extra source read is necessary, read only a bounded window for the changed file or public declaration named by the candidate.",
            "If any shell command is rejected by the environment or harness policy, stop trying equivalent list/search/read commands.",
            "If validation passes and all required artifacts exist, submit the artifact immediately.",
        ],
        "agent_evidence_budget": {
            "default_extra_source_reads_per_candidate": 0,
            "max_extra_source_reads_per_candidate": 1,
            "prefer_artifacts": [
                "analysis-context.json",
                "analysis.json",
                "patch.diff",
            ],
            "avoid_until_needed": [
                "candidates.json",
                "report.md",
                "effective-profile.yaml",
                "unchanged source files outside candidate_hunks[].file",
            ],
        },
    }
    write_json(result_dir / "analysis-context.json", payload)
    return payload


def write_report(
    state: AnalysisState,
    result_dir: Path,
    patch_id: str,
    profile: str,
    candidates: dict,
    callchains: list[dict],
) -> None:
    summary = candidates.get("summary", {})
    lines = [
        "# Patch Compatibility Analyzer 报告草稿",
        "",
        f"- 源仓库: `{state.source_repo}`",
        f"- 分析 worktree: `{state.analysis_repo}`",
        f"- Patch ID: `{patch_id}`",
        f"- Base ref: `{state.requested_base_ref}`",
        f"- Base commit: `{state.base_commit}`",
        f"- Patch apply status: `{state.patch_apply_status}`",
        f"- Profile: `{profile}`",
        f"- 产物目录: `{result_dir}`",
        f"- 补丁后源码检索根目录: `{state.analysis_repo}`",
        f"- 重建 worktree 命令: `{sys.executable} {Path(__file__).resolve()} --ensure-worktree {result_dir / 'analysis.json'}`",
        f"- 补丁前源码读取命令: `git -C {state.source_repo} show {state.base_commit}:<path>`",
        f"- 变更文件数: {summary.get('total_changed_files', 0)}",
        f"- 候选 hunk 数: {summary.get('total_hunks', 0)}",
        f"- 静态调用链数: {len(callchains)}",
        "",
        "## 代码检索目录（必须遵守）",
        "",
        f"- 补丁后代码：只在 `{state.analysis_repo}` 下检索和读取。",
        "- 默认保留该 worktree；只有用户要求释放空间且不会继续测试入口/fuzzing 时才清理。",
        f"- 可选清理 worktree 命令：`{sys.executable} {Path(__file__).resolve()} --cleanup-worktree {result_dir / 'analysis.json'}`",
        "- 若目录已被清理但仍需复核，先运行上面的重建 worktree 命令。",
        f"- 通用示例：`rg \"<pattern>\" \"{state.analysis_repo}/<relative-subdir>\"`",
        f"- Kernel 调度器示例：`rg \"\\\\.pick_task\\\\s*=\" \"{state.analysis_repo}/kernel/sched\"`",
        f"- 不要在源仓库 `{state.source_repo}` 下执行补丁后源码检索。",
        f"- 补丁前代码：使用 `git -C {state.source_repo} show {state.base_commit}:<path>` 读取。",
        "",
        "## 候选变更及代码行位置",
        "",
    ]
    for candidate in candidates.get("candidates", []):
        symbols = ", ".join(candidate.get("changed_symbols") or ["unknown"])
        lines.append(
            f"- `{candidate.get('file')}` old `{candidate.get('old_start')}-{candidate.get('old_end')}` "
            f"new `{candidate.get('new_start')}-{candidate.get('new_end')}` symbol `{symbols}`"
        )

    lines.extend(["", "## 静态调用链", ""])
    if callchains:
        for chain in callchains[:20]:
            lines.append(
                f"- `{chain.get('entry_kind')}` `{chain.get('entry')}`: "
                + " -> ".join(chain.get("chain", []))
            )
    else:
        lines.append("- 未生成调用链；调用链需在最终 findings 确认后按 finding 目标附加。")

    lines.extend(
        [
            "",
            "## Agent 语义判定要求",
            "",
            "本报告只是确定性证据草稿。最终 agent 必须基于 candidates、patch.diff、"
            "analysis worktree 中的补丁后上下文，以及必要时 base commit 的旧代码上下文，"
            "确认兼容性变更并更新 analysis.json。",
            "所有补丁后源码搜索、文件打开和静态分析命令都必须以本报告列出的"
            "补丁后源码检索根目录为根目录。",
            "",
            "最终 findings 只能包含已经确认的兼容性变更，并且必须能作为后续回归测试、"
            "已有断言复核或 fuzzing 种子目标。每条 finding 必须包含 `location.file`、`location.old_lines`、"
            "`location.new_lines`、`location.symbol` 和至少一条 `evidence[].lines`。",
            "分析阶段不要生成可运行测试入口或修改 findings 写入 test_entries。",
            "完成并校验分析后，如果用户尚未要求测试，询问是否把本次 analysis.json 交给同级"
            " patch-compatibility-testing skill 继续进行定向动态测试。",
            "",
            "写完后运行：",
            "",
            f"`python {VALIDATOR} {result_dir / 'analysis.json'}`",
            "",
        ]
    )
    (result_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(
    state: AnalysisState,
    result_dir: Path,
    patch_id: str,
    profile: str,
    candidates: dict,
    callchains: list[dict],
    mode_decision: dict,
    shard_plan: Optional[dict],
) -> None:
    summary = candidates.get("summary", {})
    patch_metrics = flatten_patch_metrics(candidates, result_dir / "candidates.json")
    lines = [
        "# Patch Compatibility Analyzer Report Draft",
        "",
        f"- Source repo: `{state.source_repo}`",
        f"- Patched analysis worktree: `{state.analysis_repo}`",
        f"- Patch ID: `{patch_id}`",
        f"- Base ref: `{state.requested_base_ref}`",
        f"- Base commit: `{state.base_commit}`",
        f"- Patch apply status: `{state.patch_apply_status}`",
        f"- Profile: `{profile}`",
        f"- Effective profile: `{result_dir / 'effective-profile.yaml'}`",
        f"- Low-context agent input: `{result_dir / 'analysis-context.json'}`",
        f"- Artifact dir: `{result_dir}`",
        f"- Analysis mode: `{mode_decision['mode']}`",
        f"- Mode reason: {'; '.join(mode_decision['heavy_reason'])}",
        f"- Changed files: {summary.get('total_changed_files', 0)}",
        f"- Candidate hunks: {summary.get('total_hunks', 0)}",
        f"- Static call chains: {len(callchains)}",
        "",
        "## Patch Metrics",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for key in (
        "patch_bytes",
        "patch_lines",
        "raw_hunks",
        "candidate_hunks",
        "changed_files",
        "churn",
        "candidate_context_bytes",
        "candidates_json_bytes",
    ):
        lines.append(f"| `{key}` | {patch_metrics.get(key, 0)} |")

    if shard_plan:
        lines.extend(
            [
                "",
                "## Heavy Shards",
                "",
                f"- Shard plan: `{result_dir / 'shards.json'}`",
                f"- Shard workspace: `{result_dir / 'shards'}`",
                f"- Shard count: {shard_plan.get('shard_count', 0)}",
                "",
                "| shard | surface | hunks | files | context bytes | artifact |",
                "|---|---|---:|---:|---:|---|",
            ]
        )
        for shard in shard_plan.get("shards", []):
            lines.append(
                "| `{id}` | `{surface}` | {hunks} | {files} | {context} | `{artifact}` |".format(
                    id=shard.get("id"),
                    surface=shard.get("surface"),
                    hunks=shard.get("metrics", {}).get("hunks", 0),
                    files=len(shard.get("files", [])),
                    context=shard.get("metrics", {}).get("context_bytes", 0),
                    artifact=shard.get("artifact"),
                )
            )

    lines.extend(
        [
            "",
            "## Source-Context Rules",
            "",
            f"- Post-patch source search/read root: `{state.analysis_repo}`.",
            f"- Pre-patch source read command: `git -C {state.source_repo} show {state.base_commit}:<path>`.",
            f"- Rebuild worktree: `{sys.executable} {Path(__file__).resolve()} --ensure-worktree {result_dir / 'analysis.json'}`.",
            f"- Optional cleanup only when no later testing/fuzzing work needs the worktree: `{sys.executable} {Path(__file__).resolve()} --cleanup-worktree {result_dir / 'analysis.json'}`.",
            "",
            "## Candidate Hunks",
            "",
        ]
    )
    for candidate in candidates.get("candidates", []):
        symbols = ", ".join(candidate.get("changed_symbols") or ["unknown"])
        surfaces = ", ".join(
            item.get("name", "")
            for item in (candidate.get("api_surface") or {}).get("matched_surfaces", [])
            if item.get("name")
        ) or ", ".join((candidate.get("api_surface") or {}).get("surface_reasons", []) or ["unknown"])
        lines.append(
            f"- `{candidate.get('hunk_id', '')}` `{candidate.get('file')}` "
            f"old `{candidate.get('old_start')}-{candidate.get('old_end')}` "
            f"new `{candidate.get('new_start')}-{candidate.get('new_end')}` "
            f"symbol `{symbols}` surface `{surfaces}`"
        )

    lines.extend(["", "## Static Call Chains", ""])
    if callchains:
        for chain in callchains[:20]:
            lines.append(
                f"- `{chain.get('entry_kind')}` `{chain.get('entry')}`: "
                + " -> ".join(chain.get("chain", []))
            )
    else:
        lines.append("- Not generated yet. Call chains are attached only after final findings exist.")

    lines.extend(
        [
            "",
            "## Agent Adjudication Requirements",
            "",
            "- This report is deterministic evidence, not the final compatibility decision.",
            "- Start from analysis-context.json. It is the bounded context for agent adjudication and includes focused source excerpts.",
            "- Do not reopen large source files to locate a changed function already present in analysis-context.json.",
            "- Do not scan repo roots, patch-list directories, output directories, or profile trees.",
            "- Final findings must include only confirmed compatibility changes.",
        ]
    )
    lines.extend(
        [
            "- Every finding must include code line locations and at least one evidence snippet.",
            "- In heavy mode, analyze each shard independently, then aggregate shard results with:",
            "",
            f"`python {Path(__file__).resolve()} --aggregate-shards {result_dir / 'analysis.json'}`",
            "",
            "Validate final output with:",
            "",
            f"`python {VALIDATOR} {result_dir / 'analysis.json'}`",
            "",
        ]
    )
    write_text(result_dir / "report.md", "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic Patch Compatibility Analyzer artifact generation"
    )
    parser.add_argument("--repo", help="Repository path or URL")
    parser.add_argument("--patch", help="Patch/diff file path or GitHub/GitLab commit/patch URL")
    parser.add_argument(
        "--base-ref",
        help=(
            "Baseline git ref. The patch is applied to an isolated worktree "
            "created from this ref. Defaults to HEAD."
        ),
    )
    parser.add_argument("--profile", default="auto", help="Package profile or auto")
    parser.add_argument(
        "--output-dir",
        help=(
            "Explicit directory for this analysis run's artifacts. When omitted, "
            "artifacts are written to <repo>/pca-results/<patch_id[:6]>."
        ),
    )
    parser.add_argument(
        "--analysis-mode",
        default="auto",
        choices=["auto", "normal", "heavy"],
        help=(
            "auto selects heavy mode when patch/candidate thresholds are exceeded; "
            "heavy always creates shards; normal skips soft-threshold sharding but "
            "hard thresholds still force heavy mode"
        ),
    )
    parser.add_argument(
        "--include-call-chain",
        action="store_true",
        help=(
            "Deprecated in initial extraction. Call chains are attached after "
            "final findings with --attach-call-chains."
        ),
    )
    parser.add_argument(
        "--attach-call-chains",
        help="Existing analysis.json whose final findings should receive call chains",
    )
    parser.add_argument(
        "--ensure-worktree",
        help="Existing analysis.json whose patched analysis worktree should be recreated",
    )
    parser.add_argument(
        "--cleanup-worktree",
        help="Existing analysis.json whose patched analysis worktree should be removed",
    )
    parser.add_argument(
        "--aggregate-shards",
        help="Existing analysis.json whose shard result files should be merged into final findings",
    )
    parser.add_argument(
        "--shard-result",
        action="append",
        help="Explicit shard result JSON path for --aggregate-shards; may be repeated",
    )
    parser.add_argument(
        "--clone-root",
        default=str(Path.cwd() / "repo"),
        help="Where to clone repo URLs",
    )
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--max-chains", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.ensure_worktree:
        state = ensure_worktree_from_analysis(Path(args.ensure_worktree).resolve())
        print("Analysis worktree available: %s" % state.analysis_repo)
        print("Patch apply status: %s" % state.patch_apply_status)
        return 0

    if args.cleanup_worktree:
        analysis_path = Path(args.cleanup_worktree).resolve()
        analysis = load_json(analysis_path)
        state = analysis_state_from_analysis(analysis, analysis_path)
        result_dir = analysis_result_dir(analysis_path, analysis)
        cleanup_analysis_worktree(state, result_dir)
        print("Analysis worktree cleaned: %s" % state.analysis_repo)
        return 0

    if args.attach_call_chains:
        attach_callchains_to_analysis(
            Path(args.attach_call_chains).resolve(),
            args.max_depth,
            args.max_chains,
        )
        print("Call chains attached to: %s" % Path(args.attach_call_chains).resolve())
        return 0

    if args.aggregate_shards:
        aggregate_shards(
            Path(args.aggregate_shards).resolve(),
            args.shard_result,
        )
        print("Shard results aggregated into: %s" % Path(args.aggregate_shards).resolve())
        return 0

    if not args.repo or not args.patch:
        raise ValueError(
            "--repo and --patch are required unless --attach-call-chains, "
            "--ensure-worktree, --cleanup-worktree, or --aggregate-shards is used"
        )

    run([sys.executable, str(CHECK_DEPENDENCIES)], timeout=60)

    source_repo = prepare_repo(args.repo, Path(args.clone_root).resolve())
    source_repo = ensure_git_repo(source_repo)
    explicit_result_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else None
    patch_cache_dir = (
        explicit_result_dir / "_patch-cache"
        if explicit_result_dir
        else source_repo / "pca-results" / "_patch-cache"
    )
    patch_path, patch_source = resolve_patch_input(args.patch, patch_cache_dir)

    patch_text = patch_path.read_text(encoding="utf-8", errors="replace")
    patch_id = patch_id_from_text(patch_path, patch_text)
    result_dir = explicit_result_dir or source_repo / "pca-results" / patch_id[:6]
    result_dir.mkdir(parents=True, exist_ok=True)
    stored_patch = result_dir / "patch.diff"
    if patch_path.resolve() != stored_patch.resolve():
        shutil.copyfile(patch_path, stored_patch)

    effective_base_ref, patch_source = infer_base_ref_from_patch_source(
        source_repo, args.base_ref, patch_source
    )
    state = prepare_analysis_worktree(source_repo, result_dir, stored_patch, effective_base_ref)
    profile = detect_profile(state.analysis_repo, args.profile)
    effective_profile_path = write_effective_profile(
        profile,
        state.analysis_repo,
        result_dir,
    )

    candidates_path = result_dir / "candidates.json"
    diff_parser_cmd = [
        sys.executable,
        str(DIFF_PARSER),
        "--repo",
        str(state.analysis_repo),
        "--patch",
        str(stored_patch),
        "--profile",
        profile,
        "--output",
        str(candidates_path),
    ]
    run(diff_parser_cmd, timeout=120)
    candidates = load_json(candidates_path)
    patch_metrics = flatten_patch_metrics(candidates, candidates_path)
    write_json(result_dir / "patch-metrics.json", patch_metrics)
    mode_decision = decide_analysis_mode(args.analysis_mode, patch_metrics)
    shard_plan = (
        write_shard_artifacts(
            result_dir,
            candidates,
            mode_decision,
        )
        if mode_decision["mode"] == "heavy"
        else None
    )
    if args.include_call_chain:
        print(
            "Call-chain generation is deferred until final findings exist. "
            "Use: %s %s --attach-call-chains %s"
            % (sys.executable, Path(__file__).resolve(), result_dir / "analysis.json")
        )
    callchains: list[dict] = []
    write_json(result_dir / "callchains.json", callchains)
    write_analysis_context(
        state,
        result_dir,
        patch_id,
        profile,
        patch_source,
        candidates,
        mode_decision,
        shard_plan,
        patch_metrics,
    )
    if args.include_call_chain:
        print(
            "Call-chain generation is deferred until final findings exist. "
            "Use: %s %s --attach-call-chains %s"
            % (sys.executable, Path(__file__).resolve(), result_dir / "analysis.json")
        )
    callchains: list[dict] = []
    write_json(result_dir / "callchains.json", callchains)
    write_analysis_scaffold(
        state,
        result_dir,
        patch_id,
        profile,
        patch_source,
        candidates,
        callchains,
        mode_decision,
        shard_plan,
        patch_metrics,
    )
    write_report(
        state,
        result_dir,
        patch_id,
        profile,
        candidates,
        callchains,
        mode_decision,
        shard_plan,
    )

    manifest = {
        "repo": str(state.source_repo),
        "analysis_repo": str(state.analysis_repo),
        "base_ref": state.requested_base_ref,
        "base_commit": state.base_commit,
        "patch_apply_status": state.patch_apply_status,
        "patch_apply_message": state.patch_apply_message,
        "analysis_worktree_status": "available",
        "worktree_recreate_command": (
            "%s %s --ensure-worktree %s"
            % (sys.executable, Path(__file__).resolve(), result_dir / "analysis.json")
        ),
        "worktree_cleanup_command": (
            "%s %s --cleanup-worktree %s"
            % (sys.executable, Path(__file__).resolve(), result_dir / "analysis.json")
        ),
        "patch_id": patch_id,
        "patch_source": patch_source,
        "artifact_dir": str(result_dir),
        "profile": profile,
        "effective_profile": str(effective_profile_path),
        "analysis_mode": mode_decision["mode"],
        "analysis_mode_requested": mode_decision["requested_mode"],
        "heavy_reason": mode_decision["heavy_reason"],
        "patch_metrics": "patch-metrics.json",
        "shards": "shards.json" if shard_plan else "",
        "artifacts": [
            "patch.diff",
            "analysis-context.json",
            "candidates.json",
            "patch-metrics.json",
            "effective-profile.yaml",
            "callchains.json",
            "analysis.json",
            "report.md",
        ] + (["shards.json", "shards/"] if shard_plan else []),
        "validator": str(VALIDATOR),
        "dependency_checker": str(CHECK_DEPENDENCIES),
    }
    write_json(result_dir / "manifest.json", manifest)
    print("Artifacts written to: %s" % result_dir)
    print("Analysis worktree: %s" % state.analysis_repo)
    print("Patch apply status: %s" % state.patch_apply_status)
    print("Analysis mode: %s" % mode_decision["mode"])
    if shard_plan:
        print("Shard count: %s" % shard_plan.get("shard_count", 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
