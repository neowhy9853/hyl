#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from relation_core import RelationError, cluster_commits, compare_commits, dump_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze issue/CVE and backport relationships between Git commits.")
    parser.add_argument("--repo", required=True, help="Git repository path")
    parser.add_argument("--mode", choices=["pairwise", "cluster"], required=True)
    parser.add_argument("--commit-a", help="First commit for pairwise mode")
    parser.add_argument("--commit-b", help="Second commit for pairwise mode")
    parser.add_argument("--commits", nargs="*", default=[], help="Commit list for cluster mode")
    parser.add_argument("--cluster-threshold", type=float, default=0.75)
    parser.add_argument("--max-commits", type=int, default=50)
    parser.add_argument("--max-issue-group-size", type=int, default=10)
    parser.add_argument("--issue-group-scope", choices=["repo", "input"], default="input")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.mode == "pairwise":
            if not args.commit_a or not args.commit_b:
                raise RelationError("E_INPUT_INVALID", "pairwise mode requires --commit-a and --commit-b")
            result = compare_commits(
                args.repo,
                args.commit_a,
                args.commit_b,
                max_issue_group_size=args.max_issue_group_size,
                issue_group_scope=args.issue_group_scope,
            )
        else:
            result = cluster_commits(
                args.repo,
                args.commits,
                max_commits=args.max_commits,
                cluster_threshold=args.cluster_threshold,
                max_issue_group_size=args.max_issue_group_size,
                issue_group_scope=args.issue_group_scope,
            )
        print(dump_json(result))
        return 0
    except RelationError as error:
        print(dump_json(error.as_dict()), file=sys.stderr)
        return 2
    except Exception as error:
        payload = RelationError("E_INTERNAL", str(error)).as_dict()
        print(dump_json(payload), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
