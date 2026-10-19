#!/usr/bin/env python3
"""PCAT-Bench-220 → 批量清单生成器。

读取 bench items 目录下每个用例的 meta.yaml 与 patch.patch，映射为
batch_manifest.yaml（字段映射见设计方案 §5.1.3）：

    local_repo_path → repo（本地路径不存在时回退 repo_url，由 runner 克隆）
    base_commit     → base_commit
    patch.patch     → patch
    package_profile → profile（取文件名 stem，如 kernel_6_6）
    expected.*      → expected（仅用于指标计算）

用法：
    python3 gen_manifest.py --from-bench /data/PCAT-Bench-220/items \
        --output /data/batch_manifest.yaml [--prefer url]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("错误：需要 PyYAML（pip install pyyaml）", file=sys.stderr)
    sys.exit(1)

VALID_PRIORITIES = {"high", "medium", "low"}


def load_meta(case_dir: Path) -> Dict[str, Any]:
    meta_path = case_dir / "meta.yaml"
    if not meta_path.is_file():
        raise SystemExit(f"错误: 缺少 {meta_path}")
    with open(meta_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SystemExit(f"错误: {meta_path} 结构非法")
    return data


def map_profile(package_profile: Any) -> str:
    if not package_profile or not isinstance(package_profile, str):
        return "auto"
    stem = Path(package_profile).stem.strip()
    return stem or "auto"


def map_expected(meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    expected = meta.get("expected")
    if not isinstance(expected, dict):
        return None
    value = expected.get("is_compatibility_change")
    if not isinstance(value, bool):
        return None
    result: Dict[str, Any] = {"is_compatibility_change": value}
    priority = expected.get("test_priority")
    if priority in VALID_PRIORITIES:
        result["test_priority"] = priority
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gen_manifest.py",
        description="PCAT-Bench-220 items → batch_manifest.yaml 生成器")
    parser.add_argument("--from-bench", required=True,
                        help="bench items 目录（含 PCAT-*/meta.yaml）")
    parser.add_argument("--output", required=True, help="输出 manifest 路径")
    parser.add_argument("--prefer", choices=["local", "url"], default="local",
                        help="repo 来源优先级（默认 local：本地路径存在即用，否则回退 URL）")
    parser.add_argument("--output-base", help="覆盖默认 output_base（默认 <bench根>/batch-results）")
    parser.add_argument("--repo-cache", help="覆盖默认 repo_cache（默认 <bench根>/_repos）")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--mode", choices=["analysis", "analysis-test"], default="analysis")
    parser.add_argument("--timeout-sec", type=int, default=3600)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--model", help="全批统一模型（可省略用默认）")
    parser.add_argument("--agent", default="patch-compatibility-utils")
    parser.add_argument("--ids", help="只生成指定用例（逗号分隔）")
    args = parser.parse_args()

    items_dir = Path(args.from_bench).expanduser().absolute()
    if not items_dir.is_dir():
        print(f"错误: items 目录不存在: {items_dir}", file=sys.stderr)
        return 1

    wanted = None
    if args.ids:
        wanted = {item.strip() for item in args.ids.split(",") if item.strip()}

    cases: List[Dict[str, Any]] = []
    repos_local = 0
    repos_url = 0
    label_counts = {"positive": 0, "negative": 0, "unknown": 0}

    for case_dir in sorted(items_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        case_id = case_dir.name
        if wanted is not None and case_id not in wanted:
            continue
        patch_path = case_dir / "patch.patch"
        if not patch_path.is_file():
            print(f"错误: {case_id} 缺少 patch.patch", file=sys.stderr)
            return 1
        meta = load_meta(case_dir)
        meta_id = meta.get("id")
        if meta_id and str(meta_id) != case_id:
            print(f"警告: {case_id} 的 meta.id={meta_id!r} 与目录名不一致，以目录名为准",
                  file=sys.stderr)

        local_repo = meta.get("local_repo_path")
        repo_url = meta.get("repo_url")
        if args.prefer == "url" and repo_url:
            repo: Optional[str] = str(repo_url)
        elif local_repo and Path(str(local_repo)).expanduser().is_dir():
            repo = str(Path(str(local_repo)).expanduser())
        elif repo_url:
            repo = str(repo_url)
        elif local_repo:
            repo = str(local_repo)
        else:
            print(f"错误: {case_id} 既无 local_repo_path 也无 repo_url", file=sys.stderr)
            return 1
        if repo.startswith(("http://", "https://", "git://", "ssh://", "git@")):
            repos_url += 1
        else:
            repos_local += 1

        base_commit = meta.get("base_commit")
        if not base_commit or not str(base_commit).strip():
            print(f"错误: {case_id} 缺少 base_commit", file=sys.stderr)
            return 1

        case_entry: Dict[str, Any] = {
            "id": case_id,
            "repo": repo,
            "base_commit": str(base_commit).strip(),
            "patch": str(patch_path),
            "profile": map_profile(meta.get("package_profile")),
        }
        expected = map_expected(meta)
        if expected:
            case_entry["expected"] = expected
        cases.append(case_entry)

        label = meta.get("label")
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts["unknown"] += 1

    if not cases:
        print("错误: 未生成任何用例（items 目录为空或 --ids 过滤后为空）", file=sys.stderr)
        return 1

    bench_root = items_dir.parent
    output_base = args.output_base or str(bench_root / "batch-results")
    repo_cache = args.repo_cache or str(bench_root / "_repos")

    global_cfg: Dict[str, Any] = {
        "concurrency": args.concurrency,
        "mode": args.mode,
        "timeout_sec": args.timeout_sec,
        "retries": args.retries,
        "agent": args.agent,
        "output_base": output_base,
        "repo_cache": repo_cache,
    }
    if args.model:
        global_cfg["model"] = args.model

    manifest: Dict[str, Any] = {
        "schema_version": "1.0",
        "global": global_cfg,
        "cases": cases,
    }

    output_path = Path(args.output).expanduser().absolute()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True,
                       default_flow_style=False)

    print(f"已生成清单: {output_path}")
    print(f"用例: {len(cases)}（正例 {label_counts['positive']} · "
          f"负例 {label_counts['negative']} · 其他 {label_counts['unknown']}）")
    print(f"repo: 本地 {repos_local} · URL(将克隆) {repos_url}")
    print(f"output_base: {output_base}")
    print(f"repo_cache: {repo_cache}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
