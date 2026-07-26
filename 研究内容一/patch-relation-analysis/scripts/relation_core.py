from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import itertools
import json
from pathlib import Path
import re
import subprocess
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


FIELD_SEP = b"\x1f"
RECORD_SEP = b"\x1e"

CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
ISSUE_FIELD_RE = re.compile(r"^(bugzilla|closes|resolves):\s*(.+)$", re.IGNORECASE | re.MULTILINE)
FIXES_COMMIT_RE = re.compile(r"^fixes:\s*([0-9a-f]{7,40})\b", re.IGNORECASE | re.MULTILINE)
URL_RE = re.compile(r"https?://[^\s<>\"]+")
ISSUE_ID_RE = re.compile(r"^(?:#)?[A-Z][A-Z0-9_-]{2,}$|^\d{2,}$", re.IGNORECASE)
COMMIT_RE = r"([0-9a-f]{7,40})"
BACKPORT_PATTERNS = (
    ("cherry-pick", re.compile(r"\bcherry[ -]picked from commit\s+%s\b" % COMMIT_RE, re.IGNORECASE)),
    ("upstream", re.compile(r"\bupstream commit\s+%s\b" % COMMIT_RE, re.IGNORECASE)),
    ("upstream", re.compile(r"\bcommit\s+%s\s+upstream\b" % COMMIT_RE, re.IGNORECASE)),
    (
        "backport",
        re.compile(r"\bbackport(?:ed)?\s+(?:from|of)\s+(?:upstream\s+)?commit\s+%s\b" % COMMIT_RE, re.IGNORECASE),
    ),
)


class RelationError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, object]:
        return {"ok": False, "error": {"code": self.code, "message": self.message}}


@dataclass(frozen=True, slots=True)
class Identifier:
    kind: str
    key: str
    value: str
    source: str


@dataclass(frozen=True, slots=True)
class BackportRef:
    source_commit: str
    source_commit_resolved: str
    source_in_repo: bool
    marker_type: str
    marker: str

    @property
    def comparable(self) -> str:
        return self.source_commit_resolved or self.source_commit.lower()


@dataclass(frozen=True, slots=True)
class CommitInfo:
    input: str
    commit: str
    found: bool
    subject: str
    body: str
    identifiers: tuple[Identifier, ...]
    backport_refs: tuple[BackportRef, ...]

    def short(self) -> str:
        return self.commit[:12] if self.commit else self.input[:12]


class GitCommitSource:
    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.is_dir():
            raise RelationError("E_REPO_NOT_FOUND", f"repository not found: {self.repo_path}")
        if not (self.repo_path / ".git").exists():
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-parse", "--git-dir"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode != 0:
                raise RelationError("E_REPO_INVALID", f"not a git repository: {self.repo_path}")
        self._resolved: dict[str, str] = {}
        self._commits: dict[tuple[str, bool], CommitInfo] = {}
        self._identifier_groups: dict[str, list[CommitInfo]] = {}

    def read_commit(self, commit: str, *, allow_missing: bool = False) -> CommitInfo:
        raw = commit.strip()
        if not raw:
            raise RelationError("E_INPUT_INVALID", "commit must not be empty")
        cache_key = (raw.lower(), allow_missing)
        if cache_key in self._commits:
            return self._commits[cache_key]
        canonical = self.resolve_commit(raw)
        if not canonical:
            if allow_missing and looks_like_commit(raw):
                info = CommitInfo(raw, raw.lower(), False, "", "", (), ())
                self._commits[cache_key] = info
                return info
            raise RelationError("E_COMMIT_NOT_FOUND", f"commit not found: {raw}")
        meta = self._git(["show", "-s", "--format=%H%x1f%s%x1f%b", "--end-of-options", canonical])
        parts = meta.split("\x1f", 2)
        if len(parts) != 3:
            raise RelationError("E_GIT_PARSE", "failed to parse git commit metadata")
        resolved, subject, body = parts
        body = body.strip()
        info = CommitInfo(
            input=raw,
            commit=resolved.strip(),
            found=True,
            subject=subject.strip(),
            body=body,
            identifiers=tuple(extract_identifiers(subject, body)),
            backport_refs=tuple(self.extract_backport_refs(subject, body)),
        )
        self._commits[cache_key] = info
        self._commits[(info.commit.lower(), allow_missing)] = info
        return info

    def resolve_commit(self, commit: str) -> str:
        key = commit.strip().lower()
        if not key:
            return ""
        if key not in self._resolved:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-parse", "--verify", "-q", f"{commit}^{{commit}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            self._resolved[key] = result.stdout.strip() if result.returncode == 0 else ""
        return self._resolved[key]

    def extract_backport_refs(self, subject: str, body: str) -> list[BackportRef]:
        refs: list[BackportRef] = []
        seen: set[str] = set()
        for line in f"{subject}\n{body}".splitlines():
            marker = line.strip()
            if not marker:
                continue
            for marker_type, pattern in BACKPORT_PATTERNS:
                for match in pattern.finditer(marker):
                    source_commit = match.group(1).lower()
                    if source_commit in seen:
                        continue
                    seen.add(source_commit)
                    resolved = self.resolve_commit(source_commit)
                    refs.append(BackportRef(source_commit, resolved, bool(resolved), marker_type, marker))
        return refs

    def identifier_group(self, identifier: Identifier) -> list[CommitInfo]:
        if identifier.key in self._identifier_groups:
            return self._identifier_groups[identifier.key]
        terms = identifier_grep_terms(identifier)
        if not terms:
            self._identifier_groups[identifier.key] = []
            return []
        group: list[CommitInfo] = []
        for commit, subject, body in self._iter_git_log(terms):
            identifiers = tuple(extract_identifiers(subject, body))
            if identifier.key not in {item.key for item in identifiers}:
                continue
            group.append(CommitInfo(commit, commit, True, subject, body.strip(), identifiers, ()))
        self._identifier_groups[identifier.key] = group
        return group

    def seed_identifier_groups_from_commits(self, commits: Iterable[CommitInfo]) -> None:
        groups: dict[str, list[CommitInfo]] = {}
        for info in commits:
            for identifier in info.identifiers:
                groups.setdefault(identifier.key, []).append(info)
        self._identifier_groups.update(groups)

    def _iter_git_log(self, grep_terms: list[str]) -> Iterable[tuple[str, str, str]]:
        cmd = ["git", "-C", str(self.repo_path), "log", "--all", "--format=%x1e%H%x1f%s%x1f%b"]
        for term in grep_terms:
            cmd.extend(["--regexp-ignore-case", "--fixed-strings", "--grep", term])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdout is not None
        buf = b""
        while True:
            chunk = proc.stdout.read(1024 * 1024)
            if not chunk:
                break
            buf += chunk
            while True:
                try:
                    idx = buf.index(RECORD_SEP)
                except ValueError:
                    break
                record = buf[:idx]
                buf = buf[idx + 1 :]
                parsed = parse_record(record)
                if parsed:
                    yield parsed
        parsed = parse_record(buf)
        if parsed:
            yield parsed
        _, stderr = proc.communicate()
        if proc.returncode:
            raise RelationError("E_GIT_LOG", stderr.decode("utf-8", errors="replace").strip() or "git log failed")

    def _git(self, args: list[str]) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RelationError("E_GIT_FAILED", result.stderr.strip() or result.stdout.strip() or "git command failed")
        return result.stdout


def compare_commits(
    repo_path: str | Path,
    commit_a: str,
    commit_b: str,
    *,
    source: GitCommitSource | None = None,
    max_issue_group_size: int = 10,
    issue_group_scope: str = "repo",
) -> dict[str, object]:
    src = source or GitCommitSource(repo_path)
    a = src.read_commit(commit_a)
    b = src.read_commit(commit_b)
    if issue_group_scope == "input":
        src.seed_identifier_groups_from_commits([a, b])
    issue = issue_cve_score(src, a, b, max_issue_group_size=max_issue_group_size)
    backport = backport_score(src, a, b)
    overall = max(float(issue["score"]), float(backport["score"]))
    relation_type = relation_type_from_scores(float(issue["score"]), float(backport["score"]))
    evidence = compact_evidence(backport.get("evidence", []), issue.get("evidence", []))
    reason = relation_reason(relation_type, issue, backport)
    return {
        "ok": True,
        "mode": "pairwise",
        "relation_type": relation_type,
        "commit_a": commit_payload(a),
        "commit_b": commit_payload(b),
        "issue_cve": issue,
        "backport": backport,
        "issue_cve_score": issue["score"],
        "backport_score": backport["score"],
        "overall_score": overall,
        "confidence": max(float(issue.get("confidence", 0.0)), float(backport.get("confidence", 0.0)), overall),
        "reason": reason,
        "evidence": evidence,
        "matched": overall > 0.0,
    }


def cluster_commits(
    repo_path: str | Path,
    commits: list[str],
    *,
    max_commits: int = 50,
    cluster_threshold: float = 0.75,
    max_issue_group_size: int = 10,
    issue_group_scope: str = "input",
) -> dict[str, object]:
    if len(commits) < 2:
        raise RelationError("E_INPUT_INVALID", "cluster mode requires at least 2 commits")
    if len(commits) > max_commits:
        raise RelationError("E_INPUT_INVALID", f"cluster mode accepts at most {max_commits} commits")
    src = GitCommitSource(repo_path)
    infos = [src.read_commit(item) for item in commits]
    if issue_group_scope == "input":
        src.seed_identifier_groups_from_commits(infos)
    graph: dict[str, set[str]] = {info.commit: set() for info in infos}
    pairwise_edges = []
    for left, right in itertools.combinations(infos, 2):
        result = compare_commits(
            repo_path,
            left.commit,
            right.commit,
            source=src,
            max_issue_group_size=max_issue_group_size,
            issue_group_scope=issue_group_scope,
        )
        score = float(result["overall_score"])
        edge = {
            "commit_a": left.commit,
            "commit_b": right.commit,
            "relation_type": result["relation_type"],
            "overall_score": score,
            "issue_cve_score": result["issue_cve_score"],
            "backport_score": result["backport_score"],
            "linked": score >= cluster_threshold,
            "evidence": result["evidence"],
        }
        pairwise_edges.append(edge)
        if edge["linked"]:
            graph[left.commit].add(right.commit)
            graph[right.commit].add(left.commit)
    components = connected_components(graph)
    payload_by_commit = {info.commit: commit_payload(info) for info in infos}
    clusters = []
    singletons = []
    for idx, component in enumerate(components, start=1):
        if len(component) == 1:
            singletons.append(component[0])
            continue
        evidence = []
        for edge in pairwise_edges:
            if edge["linked"] and edge["commit_a"] in component and edge["commit_b"] in component:
                evidence.extend(edge["evidence"])
        clusters.append(
            {
                "cluster_id": f"cluster_{idx}",
                "commits": component,
                "commit_details": [payload_by_commit[item] for item in component],
                "relation_summary": summarize_cluster_edges(pairwise_edges, component),
                "evidence": list(dict.fromkeys(evidence))[:5],
            }
        )
    return {
        "ok": True,
        "mode": "cluster",
        "cluster_threshold": cluster_threshold,
        "commits": [commit_payload(info) for info in infos],
        "clusters": clusters,
        "singletons": singletons,
        "pairwise_edges": pairwise_edges,
    }


def extract_identifiers(subject: str, body: str) -> list[Identifier]:
    text = f"{subject}\n{body}"
    identifiers: list[Identifier] = []
    seen: set[str] = set()

    def add(identifier: Identifier) -> None:
        if identifier.key not in seen:
            seen.add(identifier.key)
            identifiers.append(identifier)

    for cve in CVE_RE.findall(text):
        norm = cve.upper()
        add(Identifier("cve", f"cve:{norm}", norm, "CVE"))
    for match in ISSUE_FIELD_RE.finditer(text):
        field = match.group(1).lower()
        for value in split_issue_values(match.group(2)):
            identifier = identifier_from_issue_value(value, source=field, force=True)
            if identifier:
                add(identifier)
    for match in FIXES_COMMIT_RE.finditer(text):
        commit = match.group(1).lower()
        add(Identifier("fixes", f"fixes:{commit}", commit, "fixes"))
    for url in URL_RE.findall(text):
        identifier = identifier_from_issue_value(url, source="url", force=False)
        if identifier:
            add(identifier)
    return identifiers


def issue_cve_score(source: GitCommitSource, a: CommitInfo, b: CommitInfo, *, max_issue_group_size: int) -> dict[str, object]:
    shared = shared_identifiers(a, b)
    if not shared:
        return {"score": 0.0, "confidence": 0.0, "matched": False, "identifiers": [], "evidence": [], "reason": "no shared issue/CVE identifier"}
    best: dict[str, object] | None = None
    for identifier in shared:
        if identifier.kind == "cve":
            candidate = {
                "score": 1.0,
                "confidence": 1.0,
                "matched": True,
                "identifiers": [asdict(identifier)],
                "group_size": None,
                "evidence": [commit_evidence(a), commit_evidence(b)],
                "reason": "shared exact CVE identifier",
            }
        elif identifier.kind == "fixes":
            candidate = {
                "score": 0.55,
                "confidence": 0.6,
                "matched": True,
                "identifiers": [asdict(identifier)],
                "group_size": None,
                "evidence": [commit_evidence(a), commit_evidence(b)],
                "reason": "shared Fixes commit is weak common-regression evidence, not proof of the same issue",
            }
        else:
            group = source.identifier_group(identifier)
            group_size = len(group) or 2
            matched = group_size <= max_issue_group_size
            score = 0.85 if matched else 0.0
            candidate = {
                "score": score,
                "confidence": 0.85 if matched else 0.5,
                "matched": matched,
                "identifiers": [asdict(identifier)],
                "group_size": group_size,
                "evidence": [commit_evidence(item) for item in (group or [a, b])[:12]],
                "reason": "shared concrete issue identifier" if matched else f"shared issue identifier group too large: {group_size}",
            }
        if best is None or float(candidate["score"]) > float(best["score"]):
            best = candidate
    assert best is not None
    return best


def backport_score(source: GitCommitSource, a: CommitInfo, b: CommitInfo) -> dict[str, object]:
    direct = direct_backport_match(a, b, direction="a_backports_b")
    if direct:
        return direct
    reverse = direct_backport_match(b, a, direction="b_backports_a")
    if reverse:
        return reverse
    for left in a.backport_refs:
        for right in b.backport_refs:
            if commit_matches(left.comparable, right.comparable):
                return {
                    "score": 0.85,
                    "confidence": 0.9,
                    "matched": True,
                    "direction": "shared_source",
                    "source_commit": left.comparable,
                    "source_in_repo": bool(left.source_in_repo or right.source_in_repo or source.resolve_commit(left.comparable)),
                    "marker": [left.marker, right.marker],
                    "evidence": [commit_evidence(a), commit_evidence(b)],
                    "reason": "both commits cite the same source commit",
                }
    return {
        "score": 0.0,
        "confidence": 0.0,
        "matched": False,
        "direction": None,
        "source_commit": None,
        "source_in_repo": None,
        "marker": None,
        "evidence": [],
        "reason": "no backport/cherry-pick source match",
    }


def direct_backport_match(backport: CommitInfo, source: CommitInfo, *, direction: str) -> dict[str, object] | None:
    for ref in backport.backport_refs:
        if commit_matches(ref.comparable, source.commit):
            return {
                "score": 1.0,
                "confidence": 1.0,
                "matched": True,
                "direction": direction,
                "source_commit": ref.comparable,
                "source_in_repo": ref.source_in_repo,
                "marker": ref.marker,
                "evidence": [commit_evidence(backport), commit_evidence(source)],
                "reason": "direct backport/cherry-pick marker references the other commit",
            }
    return None


def split_issue_values(value: str) -> list[str]:
    urls = URL_RE.findall(value)
    if urls:
        return [url.strip().rstrip(".,;:)]}>") for url in urls]
    values = []
    for item in re.split(r"[\s,]+", value):
        item = item.strip().rstrip(".,;:)]}>")
        if item and item.upper() not in {"NA", "N/A", "NONE"}:
            values.append(item)
    return values


def identifier_from_issue_value(value: str, *, source: str, force: bool) -> Identifier | None:
    raw = value.strip().rstrip(".,;:)]}>")
    if not raw:
        return None
    if CVE_RE.fullmatch(raw):
        norm = raw.upper()
        return Identifier("cve", f"cve:{norm}", norm, source)
    try:
        parts = urlsplit(raw)
    except ValueError:
        parts = None
    if parts and parts.scheme and parts.netloc:
        normalized = normalize_url(raw)
        issue_key = issue_url_key(normalized)
        if issue_key:
            return Identifier("issue", issue_key, normalized, source)
        if force:
            return Identifier("issue", f"issue:url:{normalized}", normalized, source)
        return None
    if force and ISSUE_ID_RE.match(raw):
        norm = raw.strip("#").upper()
        return Identifier("issue", f"issue:id:{norm}", norm, source)
    return None


def normalize_url(value: str) -> str:
    value = value.strip().rstrip(".,;:)]}>")
    try:
        parts = urlsplit(value)
    except ValueError:
        return value
    if not parts.scheme or not parts.netloc:
        return value
    kept_query = []
    for key, val in parse_qsl(parts.query, keep_blank_values=True):
        low_key = key.lower()
        if low_key == "from" or low_key.startswith("utm_"):
            continue
        kept_query.append((key, val))
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(kept_query), ""))


def issue_url_key(url: str) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return ""
    path = parts.path.rstrip("/")
    match = re.search(r"/issues/([^/?#]+)$", path, re.IGNORECASE)
    if match:
        return f"issue:url:{parts.scheme}://{parts.netloc}{path.lower()}"
    if "bugzilla" in parts.netloc.lower():
        params = dict(parse_qsl(parts.query, keep_blank_values=True))
        bug_id = params.get("id") or params.get("bug_id")
        if bug_id:
            return f"issue:bugzilla:{parts.netloc.lower()}:{bug_id}"
    if "syzkaller" in parts.netloc.lower():
        params = dict(parse_qsl(parts.query, keep_blank_values=True))
        extid = params.get("extid")
        if extid:
            return f"issue:syzkaller:{extid}"
    return ""


def identifier_grep_terms(identifier: Identifier) -> list[str]:
    if identifier.kind in {"cve", "fixes"}:
        return [identifier.value]
    value = identifier.value
    terms = []
    try:
        parts = urlsplit(value)
    except ValueError:
        parts = None
    if parts is not None:
        params = dict(parse_qsl(parts.query, keep_blank_values=True))
        for key in ("id", "bug_id", "extid"):
            if params.get(key):
                terms.append(params[key])
        if not terms:
            tail = parts.path.rstrip("/").rsplit("/", 1)[-1]
            if tail:
                terms.append(tail)
    if identifier.key.startswith("issue:id:"):
        terms.append(identifier.key.rsplit(":", 1)[-1])
    elif not terms:
        terms.append(value)
    return list(dict.fromkeys(item for item in terms if item))


def shared_identifiers(a: CommitInfo, b: CommitInfo) -> list[Identifier]:
    by_key = {item.key: item for item in a.identifiers}
    result = [by_key[item.key] for item in b.identifiers if item.key in by_key]
    result.sort(key=lambda item: (item.kind != "cve", item.key))
    return result


def commit_matches(left: str, right: str) -> bool:
    a = (left or "").lower()
    b = (right or "").lower()
    if not looks_like_commit(a) or not looks_like_commit(b):
        return False
    return a == b or (len(a) >= 7 and b.startswith(a)) or (len(b) >= 7 and a.startswith(b))


def looks_like_commit(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", value or ""))


def relation_type_from_scores(issue_score: float, backport_score_value: float) -> str:
    if backport_score_value >= 0.75:
        return "backport"
    if issue_score >= 0.75:
        return "same_issue"
    if max(issue_score, backport_score_value) > 0:
        return "related"
    return "unrelated"


def relation_reason(relation_type: str, issue: dict[str, object], backport: dict[str, object]) -> str:
    if relation_type == "backport":
        return str(backport.get("reason") or "backport relation evidence found")
    if relation_type == "same_issue":
        return str(issue.get("reason") or "shared issue/CVE evidence found")
    if relation_type == "related":
        return "weak relation evidence found"
    return "no concrete shared issue/CVE or backport evidence found"


def connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    seen: set[str] = set()
    components: list[list[str]] = []
    for commit in graph:
        if commit in seen:
            continue
        queue = deque([commit])
        seen.add(commit)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for nxt in sorted(graph[current]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(sorted(component))
    components.sort(key=lambda item: (-len(item), item[0]))
    return components


def summarize_cluster_edges(edges: list[dict[str, object]], component: list[str]) -> str:
    types = [str(edge["relation_type"]) for edge in edges if edge["linked"] and edge["commit_a"] in component and edge["commit_b"] in component]
    if "backport" in types:
        return "connected by backport/cherry-pick/upstream evidence"
    if "same_issue" in types:
        return "connected by shared issue/CVE evidence"
    return "connected by relation evidence"


def compact_evidence(*groups: object) -> list[str]:
    result = []
    for group in groups:
        if not isinstance(group, list):
            continue
        for item in group:
            if isinstance(item, dict):
                subject = str(item.get("subject", "")).strip()
                short = str(item.get("short") or item.get("commit", ""))[:12]
                text = f"{short}: {subject}".strip(": ")
            else:
                text = str(item).strip()
            if text:
                result.append(text[:300])
    return list(dict.fromkeys(result))[:5]


def commit_payload(info: CommitInfo) -> dict[str, object]:
    return {
        "input": info.input,
        "commit": info.commit,
        "found": info.found,
        "subject": info.subject,
        "identifiers": [asdict(item) for item in info.identifiers],
        "backport_refs": [asdict(item) for item in info.backport_refs],
    }


def commit_evidence(info: CommitInfo) -> dict[str, str]:
    return {"commit": info.commit, "short": info.short(), "subject": info.subject}


def parse_record(record: bytes) -> tuple[str, str, str] | None:
    record = record.strip(b"\r\n")
    if not record:
        return None
    parts = record.split(FIELD_SEP, 2)
    if len(parts) != 3:
        return None
    return (
        parts[0].decode("utf-8", errors="replace").strip(),
        parts[1].decode("utf-8", errors="replace").strip(),
        parts[2].decode("utf-8", errors="replace"),
    )


def dump_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
