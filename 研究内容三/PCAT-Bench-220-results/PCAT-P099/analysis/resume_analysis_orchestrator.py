#!/usr/bin/env python3
"""Resume PCA artifact generation from the prepared sparse worktree."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


SKILL_SCRIPTS = Path(
    "/home/soong/.agents/skills/patch-compatibility-utils/"
    "patch-compatibility-analysis/scripts"
)
RESULT_DIR = Path(
    "/home/soong/pca_benchmark/PCAT-Bench-220-results/PCAT-P099/analysis"
)
SOURCE_REPO = Path("/home/soong/pca_benchmark/_repos/linux")
ANALYSIS_REPO = RESULT_DIR / "_worktrees/patched"
INPUT_PATCH = Path(
    "/home/soong/pca_benchmark/PCAT-Bench-220/items/PCAT-P099/patch.patch"
)
STORED_PATCH = RESULT_DIR / "patch.diff"
BASE_COMMIT = "09b8a7aa5a341bb345dc492aac139525efa13515"


def load_orchestrator():
    sys.path.insert(0, str(SKILL_SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "pca_analysis_orchestrator", SKILL_SCRIPTS / "orchestrator.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    orch = load_orchestrator()
    state = orch.AnalysisState(
        source_repo=SOURCE_REPO,
        analysis_repo=ANALYSIS_REPO,
        requested_base_ref=BASE_COMMIT,
        base_commit=BASE_COMMIT,
        patch_apply_status="applied",
        patch_apply_message=(
            "patch applied cleanly after worktree-local sparse expansion of "
            "drivers/infiniband and include/rdma"
        ),
    )

    patch_text = STORED_PATCH.read_text(encoding="utf-8", errors="replace")
    patch_id = orch.patch_id_from_text(STORED_PATCH, patch_text)
    profile = orch.detect_profile(ANALYSIS_REPO, "kernel_6_6")
    effective_profile = orch.write_effective_profile(
        profile, ANALYSIS_REPO, RESULT_DIR
    )

    candidates_path = RESULT_DIR / "candidates.json"
    subprocess.run(
        [
            sys.executable,
            str(orch.DIFF_PARSER),
            "--repo",
            str(ANALYSIS_REPO),
            "--patch",
            str(STORED_PATCH),
            "--profile",
            profile,
            "--output",
            str(candidates_path),
        ],
        check=True,
    )
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    metrics = orch.flatten_patch_metrics(candidates, candidates_path)
    orch.write_json(RESULT_DIR / "patch-metrics.json", metrics)
    mode = orch.decide_analysis_mode("auto", metrics)
    shards = (
        orch.write_shard_artifacts(RESULT_DIR, candidates, mode)
        if mode["mode"] == "heavy"
        else None
    )
    callchains = []
    orch.write_json(RESULT_DIR / "callchains.json", callchains)
    patch_source = {
        "kind": "local_file",
        "input": str(INPUT_PATCH),
        "resolved_patch": str(STORED_PATCH),
    }
    orch.write_analysis_context(
        state,
        RESULT_DIR,
        patch_id,
        profile,
        patch_source,
        candidates,
        mode,
        shards,
        metrics,
    )
    orch.write_analysis_scaffold(
        state,
        RESULT_DIR,
        patch_id,
        profile,
        patch_source,
        candidates,
        callchains,
        mode,
        shards,
        metrics,
    )
    orch.write_report(
        state,
        RESULT_DIR,
        patch_id,
        profile,
        candidates,
        callchains,
        mode,
        shards,
    )
    manifest = {
        "repo": str(SOURCE_REPO),
        "analysis_repo": str(ANALYSIS_REPO),
        "base_ref": BASE_COMMIT,
        "base_commit": BASE_COMMIT,
        "patch_apply_status": "applied",
        "patch_apply_message": state.patch_apply_message,
        "analysis_worktree_status": "available",
        "patch_id": patch_id,
        "patch_source": patch_source,
        "artifact_dir": str(RESULT_DIR),
        "profile": profile,
        "effective_profile": str(effective_profile),
        "analysis_mode": mode["mode"],
        "analysis_mode_requested": mode["requested_mode"],
        "heavy_reason": mode["heavy_reason"],
        "patch_metrics": "patch-metrics.json",
        "shards": "shards.json" if shards else "",
        "artifacts": [
            "patch.diff",
            "analysis-context.json",
            "candidates.json",
            "patch-metrics.json",
            "effective-profile.yaml",
            "callchains.json",
            "analysis.json",
            "report.md",
        ],
        "resume_script": str(Path(__file__).resolve()),
        "validator": str(orch.VALIDATOR),
        "dependency_checker": str(orch.CHECK_DEPENDENCIES),
    }
    orch.write_json(RESULT_DIR / "manifest.json", manifest)
    print(f"Artifacts written to: {RESULT_DIR}")
    print(f"Analysis worktree: {ANALYSIS_REPO}")
    print(f"Patch id: {patch_id}")
    print(f"Analysis mode: {mode['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
