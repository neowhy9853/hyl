#!/usr/bin/env python3
"""PCAT 自动批量扫描调度器（batch_runner.py）。

按《批量扫描模式设计方案》实现无人值守批量补丁兼容性分析：

- 确定性调度 + LLM 分析分离：并发/分派/重试/续跑由本脚本决定，
  每个用例启动一个独立 ``opencode run`` 子进程（子 Agent）完成分析；
- 文件契约解耦：manifest（输入清单）/ batch_state.json（状态事实源，原子写）/
  progress.jsonl（append-only 事件流）/ analysis.json（单例产物）；
- 断点续跑（--resume）、失败重试（retries）、连续同签名失败熔断、
  运行中磁盘水位暂停、进程组治理与孤儿回收；
- 进度可见性：--progress 一屏快照；模式 D（notify 命令）与模式 E
  （OpenCode server 会话注入回调）。

退出码：0 正常结束（含 --limit/--ids 子集运行）；1 用法/预检错误或锁冲突；
2 批次结束但存在失败用例；3 熔断中止；4 磁盘低水位暂停；130 被信号终止。
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a hard requirement
    print("错误：需要 PyYAML（pip install pyyaml）", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
RUNNER_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = RUNNER_ROOT / "templates" / "prompt.txt.j2"

POLL_SEC = 2.0
FOLLOW_REFRESH_SEC = 5.0
CLONE_TIMEOUT_SEC = 14400
FETCH_TIMEOUT_SEC = 3600
GIT_CHECK_TIMEOUT_SEC = 30
VALIDATE_TIMEOUT_SEC = 120
DEP_CHECK_TIMEOUT_SEC = 300
MODELS_CHECK_TIMEOUT_SEC = 60
NOTIFY_TIMEOUT_SEC = 60
INJECT_TIMEOUT_SEC = 5
KILL_GRACE_SEC = 10
HARD_CONCURRENCY_CAP = 16
BAR_WIDTH = 30
TEST_TIMEOUT_MULTIPLIER = 3
REPAIR_TIMEOUT_SEC = 1200  # orchestrator --attach-impact-scope 内部 900s + 余量
CLEANUP_TIMEOUT_SEC = 300
TEST_RESULT_SUBDIR = "compatibility-testing"
AFFECTED_SCOPE_FILENAME = "affected-scope.json"

CASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
URL_RE = re.compile(r"^(https?://|git://|ssh://|git@)", re.IGNORECASE)
SUMMARY_LINE_RE = re.compile(r"SUMMARY\s+json:\s*(\{.*\})")
TEMPLATE_VAR_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07")

PRIORITY_ORDER: Dict[str, int] = {"high": 3, "medium": 2, "low": 1}

STATE_FILENAME = "batch_state.json"
PROGRESS_FILENAME = "progress.jsonl"
SUMMARY_FILENAME = "batch_summary.json"
REPORT_FILENAME = "batch_report.md"

DEFAULT_GLOBALS: Dict[str, Any] = {
    "concurrency": 4,
    "mode": "analysis",
    "timeout_sec": 3600,
    "retries": 1,
    "model": None,
    "agent": "patch-compatibility-utils",
    "progress_interval_sec": 300,
    "disk_check_interval_sec": 600,
    "disk_low_watermark_gb": 20,
    "per_case_disk_estimate_gb": 5,
    "consecutive_fail_limit": 5,
    "env_authorized": False,
}

ANALYSIS_MODE_INSTRUCTIONS = (
    "3. 不要提出测试询问（本批次只做分析）；按 cleanup_worktree 指令处理 _worktrees（默认清理）。"
)

ANALYSIS_TEST_MODE_INSTRUCTIONS = (
    "3. 分析校验通过后，基于上述 output_dir 下的 analysis.json 继续执行\n"
    "   patch-compatibility-testing 完整流程（本用例环境已获授权 env_authorized=true），\n"
    "   测试产物写入 output_dir/compatibility-testing/。\n"
    "4. 全程不要提出任何确认询问；确实无法自动准备的环境项记为 blocked 并说明原因。"
)


class BatchError(Exception):
    """用法/预检级错误（退出码 1）。"""


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def iso_elapsed(start: Optional[str], end: Optional[str]) -> Optional[float]:
    a, b = parse_iso(start), parse_iso(end)
    if a is None or b is None:
        return None
    return max(0.0, (b - a).total_seconds())


def parse_duration(text: str) -> int:
    """解析 "30s" / "10m" / "1h" / "2d" / "90"（默认秒）。"""
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([smhd]?)\s*", text)
    if not m:
        raise BatchError(f"无法解析时间间隔: {text!r}（示例：30s、10m、1h）")
    value = float(m.group(1))
    unit = m.group(2) or "s"
    return int(value * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit])


def human_duration(sec: Optional[float]) -> str:
    if sec is None:
        return "-"
    sec = int(round(sec))
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec // 3600}h{(sec % 3600) // 60:02d}m"


def human_bytes(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024 or unit == "TB":
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def atomic_write_json(path: Path, obj: Any) -> None:
    # 原子性 = tmp 写入 + rename；文件级 fsync 保内容落盘。
    # 不做目录 fsync：掉电最多丢最后一次状态写，等价于该用例重跑（可接受，
    # 且 rename 本身在 ext4 data=ordered 下已保证原子可见）。
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def tail_text(path: Path, max_bytes: int = 8192) -> str:
    try:
        size = path.stat().st_size
        with open(path, "rb") as fh:
            fh.seek(max(0, size - max_bytes))
            return fh.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def last_nonempty_line(text: str) -> str:
    for line in reversed(strip_ansi(text).splitlines()):
        if line.strip():
            return line.strip()
    return ""


def dir_size_bytes(path: Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path, onerror=lambda _e: None):
        for name in files:
            try:
                total += os.stat(os.path.join(root, name)).st_size
            except OSError:
                pass
    return total


def render_template(text: str, variables: Dict[str, Any]) -> str:
    def substitute(match: "re.Match[str]") -> str:
        name = match.group(1)
        if name not in variables:
            raise BatchError(f"prompt 模板引用未知变量 {name}")
        return str(variables[name])

    rendered = TEMPLATE_VAR_RE.sub(substitute, text)
    if "{{" in rendered or "}}" in rendered:
        raise BatchError("prompt 模板渲染后仍残留 {{ }} 占位符")
    return rendered


# ---------------------------------------------------------------------------
# 清单（batch_manifest.yaml）：数据模型 + 阶段一结构校验
# ---------------------------------------------------------------------------

@dataclass
class CaseCfg:
    id: str
    repo: str
    base_commit: str
    patch: str
    profile: str = "auto"
    expected: Optional[Dict[str, Any]] = None
    env_authorized: Optional[bool] = None
    repo_is_url: bool = False
    result_dir: str = ""


@dataclass
class GlobalCfg:
    concurrency: int = 4
    mode: str = "analysis"
    timeout_sec: int = 3600
    retries: int = 1
    model: Optional[str] = None
    agent: str = "patch-compatibility-utils"
    output_base: str = ""
    repo_cache: str = ""
    skill_dir: Optional[str] = None
    prompt_template: Optional[str] = None
    progress_interval_sec: int = 300
    disk_check_interval_sec: int = 600
    disk_low_watermark_gb: float = 20
    per_case_disk_estimate_gb: float = 5
    consecutive_fail_limit: int = 5
    env_authorized: bool = False
    notify: Optional[Dict[str, Any]] = None
    report_to: Optional[Dict[str, Any]] = None


@dataclass
class BatchCfg:
    path: Path
    schema_version: str
    global_cfg: GlobalCfg
    cases: List[CaseCfg] = field(default_factory=list)

    def expected_map(self) -> Dict[str, Dict[str, Any]]:
        return {c.id: c.expected for c in self.cases if c.expected}


def _resolve_from(base: Path, value: str) -> str:
    expanded = Path(value).expanduser()
    if not expanded.is_absolute():
        return str((base / expanded).resolve())
    return str(expanded)


def _as_int(value: Any, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
        raise BatchError(f"{name}: 必须是整数，得到 {value!r}")
    ivalue = int(value)
    if ivalue < minimum or ivalue > maximum:
        raise BatchError(f"{name}: 取值范围 [{minimum}, {maximum}]，得到 {ivalue}")
    return ivalue


def _as_float(value: Any, name: str, minimum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BatchError(f"{name}: 必须是数字，得到 {value!r}")
    if value < minimum:
        raise BatchError(f"{name}: 不能小于 {minimum}")
    return float(value)


def repo_url_name(url: str) -> str:
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    name = tail[:-4] if tail.endswith(".git") else tail
    if not name or not CASE_ID_RE.fullmatch(name):
        raise BatchError(f"无法从 URL 推导仓库名: {url}")
    return name


def load_manifest(manifest_path: Path) -> BatchCfg:
    """加载清单并执行阶段一结构校验（不触碰仓库、不联网、不执行 clone）。"""
    manifest_path = manifest_path.expanduser().resolve()
    if not manifest_path.is_file():
        raise BatchError(f"清单文件不存在: {manifest_path}")
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BatchError(f"清单 YAML 解析失败: {exc}") from exc
    if not isinstance(raw, dict):
        raise BatchError("清单必须是 YAML mapping")

    schema_version = raw.get("schema_version")
    if schema_version is None:
        raise BatchError("清单缺少 schema_version 字段")
    if str(schema_version) != "1.0":
        raise BatchError(f"不支持的 schema_version: {schema_version!r}（本版本仅支持 '1.0'）")

    base_dir = manifest_path.parent
    g_raw = raw.get("global") or {}
    if not isinstance(g_raw, dict):
        raise BatchError("global 必须是 mapping")

    merged: Dict[str, Any] = dict(DEFAULT_GLOBALS)
    for key in ("concurrency", "mode", "timeout_sec", "retries", "model", "agent",
                "progress_interval_sec", "disk_check_interval_sec",
                "disk_low_watermark_gb", "per_case_disk_estimate_gb",
                "consecutive_fail_limit", "env_authorized"):
        if key in g_raw and g_raw[key] is not None:
            merged[key] = g_raw[key]

    g = GlobalCfg()
    g.concurrency = _as_int(merged["concurrency"], "global.concurrency", 1, HARD_CONCURRENCY_CAP)
    mode = str(merged["mode"])
    if mode == "test":
        mode = "analysis-test"
    if mode not in ("analysis", "analysis-test"):
        raise BatchError(f"global.mode 非法: {mode!r}（analysis | analysis-test）")
    g.mode = mode
    g.timeout_sec = _as_int(merged["timeout_sec"], "global.timeout_sec", 60, 86400 * 7)
    g.retries = _as_int(merged["retries"], "global.retries", 0, 10)
    g.model = str(merged["model"]) if merged["model"] else None
    if not isinstance(merged["agent"], str) or not merged["agent"]:
        raise BatchError("global.agent 必须是非空字符串")
    g.agent = merged["agent"]
    g.progress_interval_sec = _as_int(merged["progress_interval_sec"],
                                      "global.progress_interval_sec", 0, 86400)
    g.disk_check_interval_sec = _as_int(merged["disk_check_interval_sec"],
                                        "global.disk_check_interval_sec", 10, 86400)
    g.disk_low_watermark_gb = _as_float(merged["disk_low_watermark_gb"],
                                        "global.disk_low_watermark_gb", 0)
    g.per_case_disk_estimate_gb = _as_float(merged["per_case_disk_estimate_gb"],
                                            "global.per_case_disk_estimate_gb", 0)
    g.consecutive_fail_limit = _as_int(merged["consecutive_fail_limit"],
                                       "global.consecutive_fail_limit", 2, 1000)
    g.env_authorized = bool(merged["env_authorized"])

    g.output_base = (_resolve_from(base_dir, str(g_raw["output_base"]))
                     if g_raw.get("output_base")
                     else str((base_dir / "batch-results").resolve()))
    g.repo_cache = (_resolve_from(base_dir, str(g_raw["repo_cache"]))
                    if g_raw.get("repo_cache")
                    else str((base_dir / "_repos").resolve()))
    if g_raw.get("skill_dir"):
        g.skill_dir = _resolve_from(base_dir, str(g_raw["skill_dir"]))
    if g_raw.get("prompt_template"):
        g.prompt_template = _resolve_from(base_dir, str(g_raw["prompt_template"]))

    if g_raw.get("notify") is not None:
        notify = g_raw["notify"]
        if not isinstance(notify, dict) or not str(notify.get("command", "")).strip():
            raise BatchError("global.notify 必须包含非空 command 字符串")
        events = notify.get("on") or ["batch_done", "circuit_break", "disk_low"]
        bad = [e for e in events if e not in ("batch_done", "circuit_break", "disk_low")]
        if bad:
            raise BatchError(f"global.notify.on 含未知事件: {bad}")
        g.notify = {"on": list(events), "command": str(notify["command"])}

    if g_raw.get("report_to") is not None:
        rt = g_raw["report_to"]
        if not isinstance(rt, dict):
            raise BatchError("global.report_to 必须是 mapping")
        g.report_to = dict(rt)

    cases_raw = raw.get("cases")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise BatchError("cases 必须是非空数组")

    cases: List[CaseCfg] = []
    seen_ids: set = set()
    url_names: Dict[str, str] = {}
    for index, item in enumerate(cases_raw):
        where = f"cases[{index}]"
        if not isinstance(item, dict):
            raise BatchError(f"{where}: 必须是 mapping")
        for key in ("id", "repo", "base_commit", "patch"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                raise BatchError(f"{where}: 必填字段 {key} 缺失或为空")
        case_id = item["id"].strip()
        if not CASE_ID_RE.fullmatch(case_id):
            raise BatchError(f"{where}.id: {case_id!r} 含非法字符（仅允许 [A-Za-z0-9._-]）")
        if case_id in seen_ids:
            raise BatchError(f"用例 id 重复: {case_id}")
        seen_ids.add(case_id)

        repo_raw = item["repo"].strip()
        is_url = bool(URL_RE.match(repo_raw))
        if is_url:
            name = repo_url_name(repo_raw)
            if name in url_names and url_names[name] != repo_raw:
                raise BatchError(f"{where}.repo: 不同 URL 映射到同一缓存名 {name!r}")
            url_names[name] = repo_raw
            repo_value = repo_raw
        else:
            repo_value = _resolve_from(base_dir, repo_raw)

        patch_value = _resolve_from(base_dir, item["patch"].strip())
        patch_path = Path(patch_value)
        if not patch_path.is_file():
            raise BatchError(f"{where}.patch: 补丁文件不存在: {patch_value}")
        if not os.access(patch_path, os.R_OK):
            raise BatchError(f"{where}.patch: 补丁文件不可读: {patch_value}")

        profile = item.get("profile") or "auto"
        if not isinstance(profile, str) or not profile.strip():
            raise BatchError(f"{where}.profile: 必须是字符串")
        profile = profile.strip()

        expected: Optional[Dict[str, Any]] = None
        if item.get("expected") is not None:
            exp = item["expected"]
            if not isinstance(exp, dict):
                raise BatchError(f"{where}.expected: 必须是 mapping")
            if not isinstance(exp.get("is_compatibility_change"), bool):
                raise BatchError(f"{where}.expected.is_compatibility_change: 必须是布尔值")
            expected = {"is_compatibility_change": exp["is_compatibility_change"]}
            if exp.get("test_priority") is not None:
                if exp["test_priority"] not in ("high", "medium", "low"):
                    raise BatchError(f"{where}.expected.test_priority: 非法值 {exp['test_priority']!r}")
                expected["test_priority"] = exp["test_priority"]

        env_auth = item.get("env_authorized")
        if env_auth is not None and not isinstance(env_auth, bool):
            raise BatchError(f"{where}.env_authorized: 必须是布尔值")

        cases.append(CaseCfg(
            id=case_id,
            repo=repo_value,
            base_commit=item["base_commit"].strip(),
            patch=patch_value,
            profile=profile,
            expected=expected,
            env_authorized=env_auth,
            repo_is_url=is_url,
            result_dir=str((Path(g.output_base) / case_id).resolve()),
        ))

    return BatchCfg(path=manifest_path, schema_version=str(schema_version),
                    global_cfg=g, cases=cases)

# ---------------------------------------------------------------------------
# Skill 目录解析与单例产物校验
# ---------------------------------------------------------------------------

def resolve_skill_dir(manifest_skill_dir: Optional[str]) -> Path:
    candidates: List[Path] = []
    if manifest_skill_dir:
        candidates.append(Path(manifest_skill_dir).expanduser())
    env_dir = os.environ.get("PCAT_SKILL_DIR")
    if env_dir:
        candidates.append(Path(env_dir).expanduser())
    home = Path.home()
    candidates.append(home / ".opencode" / "skills" / "patch-compatibility-utils")
    candidates.append(home / ".agents" / "skills" / "patch-compatibility-utils")
    candidates.append(RUNNER_ROOT.parent)  # 嵌套布局：pca-batch-runner 位于 utils 内
    for candidate in candidates:
        if (candidate / "patch-compatibility-analysis" / "scripts" / "validate_analysis.py").is_file():
            return candidate.resolve()
    tried = "\n  ".join(str(c) for c in candidates)
    raise BatchError(
        "找不到 patch-compatibility-utils Skill 目录（需要 "
        "patch-compatibility-analysis/scripts/validate_analysis.py）。\n"
        f"已尝试:\n  {tried}\n"
        "请在 manifest global.skill_dir 或环境变量 PCAT_SKILL_DIR 中指定。"
    )


def validate_analysis_file(script: Path, analysis_path: Path, *,
                           require_affected_scope: bool = False) -> Tuple[bool, str]:
    """运行 validate_analysis.py，返回 (是否通过, 首条错误)。

    require_affected_scope=True 时附加 --require-affected-scope，与 Skill 的
    Phase 7.1 完成口径一致（每条 finding 必须有 affected_scope.status + summary）。
    """
    cmd = [sys.executable, str(script), str(analysis_path)]
    if require_affected_scope:
        cmd.append("--require-affected-scope")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=VALIDATE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return False, "validate_analysis.py 超时"
    except OSError as exc:
        return False, f"无法执行 validate_analysis.py: {exc}"
    if proc.returncode == 0:
        return True, ""
    lines = (proc.stdout or "").strip().splitlines() or (proc.stderr or "").strip().splitlines()
    return False, lines[0] if lines else f"exit {proc.returncode}"


def validate_test_summary(script: Path, summary_path: Path) -> Tuple[bool, str]:
    """运行 finalize_test_report.py --validate-only，返回 (是否通过, 首条错误)。"""
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(summary_path), "--validate-only"],
            capture_output=True, text=True, timeout=VALIDATE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return False, "finalize_test_report.py 超时"
    except OSError as exc:
        return False, f"无法执行 finalize_test_report.py: {exc}"
    if proc.returncode == 0:
        return True, ""
    lines = (proc.stdout or "").strip().splitlines() or (proc.stderr or "").strip().splitlines()
    return False, lines[0] if lines else f"exit {proc.returncode}"


def try_repair_affected_scope(orchestrator_script: Path, analysis_path: Path, *,
                              cleanup_after: bool = False) -> Tuple[bool, str]:
    """analysis.json 有效但缺 affected-scope.json 时，用 Skill 命令补全（断点自愈）。

    orchestrator.py --attach-impact-scope 会在需要时重建 worktree、计算反向调用图，
    写出 affected-scope.json 并回写 findings[].affected_scope，最后复核校验。
    cleanup_after=True 时在补全后按分析模式约定清理重建的 worktree（尽力而为）。
    """
    if not orchestrator_script.is_file():
        return False, f"orchestrator.py 不存在: {orchestrator_script}"
    try:
        proc = subprocess.run(
            [sys.executable, str(orchestrator_script),
             "--attach-impact-scope", str(analysis_path)],
            capture_output=True, text=True, timeout=REPAIR_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return False, f"attach-impact-scope 超时（{REPAIR_TIMEOUT_SEC}s）"
    except OSError as exc:
        return False, f"无法执行 orchestrator.py: {exc}"
    if proc.returncode != 0:
        lines = (proc.stdout or "").strip().splitlines() or (proc.stderr or "").strip().splitlines()
        return False, lines[0] if lines else f"exit {proc.returncode}"
    if not cleanup_after:
        return True, ""
    try:
        cleanup = subprocess.run(
            [sys.executable, str(orchestrator_script),
             "--cleanup-worktree", str(analysis_path)],
            capture_output=True, text=True, timeout=CLEANUP_TIMEOUT_SEC,
            env=dict(os.environ, PCA_ALLOW_WORKTREE_DELETE="1"),
        )
    except subprocess.TimeoutExpired:
        return True, f"worktree 清理超时（{CLEANUP_TIMEOUT_SEC}s）"
    except OSError as exc:
        return True, f"worktree 清理失败: {exc}"
    if cleanup.returncode != 0:
        lines = ((cleanup.stdout or "").strip().splitlines()
                 or (cleanup.stderr or "").strip().splitlines())
        return True, f"worktree 清理失败: {lines[0] if lines else f'exit {cleanup.returncode}'}"
    try:
        (analysis_path.parent / "_worktrees").rmdir()
    except OSError:
        pass
    return True, ""


def extract_analysis_info(analysis_path: Path) -> Dict[str, Any]:
    """从 analysis.json 提取聚合信息（predicted 一律从 findings 派生，不解析 SUMMARY 文本）。"""
    with open(analysis_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    findings = data.get("findings") or []
    priorities: List[str] = []
    types: set = set()
    for item in findings:
        if not isinstance(item, dict):
            continue
        if item.get("test_priority") in PRIORITY_ORDER:
            priorities.append(item["test_priority"])
        if item.get("compatibility_type"):
            types.add(item["compatibility_type"])
    top = max(priorities, key=lambda p: PRIORITY_ORDER[p]) if priorities else None
    predicted = len(findings) > 0
    return {
        "predicted": predicted,
        "findings": len(findings),
        "top_priority": top,
        "compatibility_types": sorted(types),
        "summary": (
            f"compatibility_change={str(predicted).lower()}; "
            f"findings={len(findings)}; top_priority={top or 'none'}"
        ),
    }


def extract_test_info(summary_path: Path) -> Dict[str, Any]:
    """从 test-summary.json 提取测试聚合信息（状态/覆盖率/gate/兼容性结论）。"""
    with open(summary_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    coverage = data.get("coverage_report") if isinstance(data.get("coverage_report"), dict) else {}
    gate = coverage.get("gate") if isinstance(coverage.get("gate"), dict) else {}
    conclusion = data.get("conclusion") if isinstance(data.get("conclusion"), dict) else {}
    status = data.get("status")
    rate = data.get("patch_line_coverage_rate")
    gate_met = gate.get("met", conclusion.get("coverage_gate_met"))
    conclusion_value = conclusion.get("backward_compatibility")
    return {
        "status": status,
        "coverage_rate": rate,
        "coverage_gate_met": gate_met,
        "backward_compatibility": conclusion_value,
        "has_coverage_report": data.get("coverage_report") is not None,
        "summary": (
            f"test_status={status}; coverage_rate={rate}; "
            f"gate_met={gate_met}; compatibility={conclusion_value}"
        ),
    }


def parse_summary_line(run_log: Path) -> Optional[Dict[str, Any]]:
    """解析 run.log 中最后一行 `SUMMARY json: {...}`（仅供速览/矛盾标注）。"""
    text = tail_text(run_log, max_bytes=65536)
    match = None
    for line in text.splitlines():
        m = SUMMARY_LINE_RE.search(line)
        if m:
            match = m
    if match is None:
        return None
    try:
        value = json.loads(match.group(1))
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# 进度事件流（progress.jsonl）
# ---------------------------------------------------------------------------

class ProgressLog:
    """append-only 事件流，与 batch_state.json 的原子写互不竞争。"""

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def emit(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        record: Dict[str, Any] = {"ts": now_iso(), "event": event}
        if payload:
            record.update(payload)
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except OSError as exc:
                print(f"警告：无法写入进度事件 {self.path}: {exc}", file=sys.stderr)


def last_heartbeat_age_sec(progress_path: Path) -> Optional[float]:
    text = tail_text(progress_path, max_bytes=131072)
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("event") != "heartbeat":
            continue
        ts = parse_iso(record.get("ts"))
        if ts is not None:
            return max(0.0, (datetime.now().astimezone() - ts).total_seconds())
    return None


# ---------------------------------------------------------------------------
# 状态（batch_state.json）
# ---------------------------------------------------------------------------

def compute_counts(state: Dict[str, Any]) -> Dict[str, int]:
    counts = {"total": 0, "done": 0, "failed": 0, "skipped": 0,
              "pending": 0, "running": 0, "interrupted": 0}
    for st in state.get("cases", {}).values():
        status = st.get("status")
        counts["total"] += 1
        if status in ("done", "already_done"):
            counts["done"] += 1
        elif status == "failed":
            counts["failed"] += 1
        elif status == "pending":
            counts["pending"] += 1
        elif status == "running":
            counts["running"] += 1
        elif status == "interrupted":
            counts["interrupted"] += 1
        if status in ("already_done", "skipped"):
            counts["skipped"] += 1
    return counts


def event_counts(state: Dict[str, Any]) -> Dict[str, int]:
    """progress.jsonl 事件中的 counts 字段（设计 §5.2.7 的四键）。"""
    counts = compute_counts(state)
    return {"done": counts["done"], "failed": counts["failed"],
            "pending": counts["pending"], "running": counts["running"]}


def load_state_file(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise BatchError(f"无法读取批次状态 {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("cases"), dict):
        raise BatchError(f"批次状态文件结构非法: {path}")
    return data


def make_batch_id(manifest_path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", manifest_path.stem).strip("-") or "batch"
    return f"{stem}-{datetime.now().strftime('%Y%m%d')}"


def fresh_state(cfg: BatchCfg, batch_id: str) -> Dict[str, Any]:
    g = cfg.global_cfg
    return {
        "schema_version": "1.0",
        "batch_id": batch_id,
        "manifest": str(cfg.path),
        "mode": g.mode,
        "model": g.model,
        "agent": g.agent,
        "runner_pid": os.getpid(),
        "concurrency": g.concurrency,
        "timeout_sec": g.timeout_sec,
        "retries": g.retries,
        "output_base": g.output_base,
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "finished_at": None,
        "abort_reason": None,
        "paused_reason": None,
        "counts": {},
        "cases": {
            case.id: {
                "status": "pending",
                "attempts": 0,
                "pid": None,
                "pgid": None,
                "started_at": None,
                "finished_at": None,
                "elapsed_sec": None,
                "result_dir": case.result_dir,
                "summary": None,
                "error": None,
                "interrupted_count": 0,
            }
            for case in cfg.cases
        },
    }


# ---------------------------------------------------------------------------
# 批次锁与进程探测（防止双 runner；孤儿回收时防 pid 复用误杀）
# ---------------------------------------------------------------------------

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _pid_cmdline(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            return fh.read().replace(b"\x00", b" ").decode("utf-8", errors="replace")
    except OSError:
        return ""


def _pid_is_runner(pid: int) -> bool:
    return "batch_runner" in _pid_cmdline(pid)


def _pid_is_opencode(pid: int) -> bool:
    return "opencode" in _pid_cmdline(pid)


class BatchLock:
    """批次锁：<state_path>.lock；存活 runner 持锁时拒绝启动，陈旧锁自动回收。"""

    def __init__(self, state_path: Path):
        self.path = state_path.with_name(state_path.name + ".lock")
        self._acquired = False

    def acquire(self) -> None:
        for _attempt in range(3):
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump({"pid": os.getpid(), "ts": now_iso()}, fh)
                self._acquired = True
                return
            except FileExistsError:
                try:
                    data = json.loads(self.path.read_text(encoding="utf-8"))
                    pid = int(data.get("pid") or 0)
                except (OSError, ValueError, json.JSONDecodeError):
                    pid = 0
                if pid and _pid_alive(pid) and _pid_is_runner(pid):
                    raise BatchError(
                        f"批次正在运行（runner pid={pid}，锁 {self.path}）。"
                        "请勿重复启动；如确认已停止可删除锁文件后重试。"
                    )
                try:
                    self.path.unlink()
                except OSError:
                    pass
        raise BatchError(f"无法获取批次锁 {self.path}")

    def release(self) -> None:
        if self._acquired:
            try:
                self.path.unlink()
            except OSError:
                pass
            self._acquired = False


# ---------------------------------------------------------------------------
# 仓库准备与两阶段预检
# ---------------------------------------------------------------------------

def prepare_repos(cfg: BatchCfg, log=print) -> List[Tuple[str, str]]:
    """URL 去重 → 串行 clone/fetch 到 repo_cache，成功后改写 case.repo 为本地路径。

    返回 (case_id, error) 列表（clone 失败的用例）。fetch 失败仅告警：
    若所需 commit 已在本地缓存中则不影响，否则由阶段二校验兜底。
    """
    g = cfg.global_cfg
    errors: List[Tuple[str, str]] = []
    url_to_cases: Dict[str, List[CaseCfg]] = {}
    for case in cfg.cases:
        if case.repo_is_url:
            url_to_cases.setdefault(case.repo, []).append(case)
    if not url_to_cases:
        return errors

    repo_cache = Path(g.repo_cache)
    repo_cache.mkdir(parents=True, exist_ok=True)

    for url, cases in url_to_cases.items():
        name = repo_url_name(url)
        dest = repo_cache / name
        if (dest / ".git").exists():
            log(f"[repo] fetch {name} -> {dest}")
            try:
                subprocess.run(["git", "-C", str(dest), "fetch", "--all", "--prune"],
                               check=True, capture_output=True, text=True,
                               timeout=FETCH_TIMEOUT_SEC)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
                log(f"[repo] 警告: fetch {name} 失败（若所需 commit 已存在则不影响）: {exc}")
        else:
            log(f"[repo] clone {url} -> {dest}")
            try:
                subprocess.run(["git", "clone", url, str(dest)],
                               check=True, capture_output=True, text=True,
                               timeout=CLONE_TIMEOUT_SEC)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
                detail = getattr(exc, "stderr", "") or str(exc)
                for case in cases:
                    errors.append((case.id, f"repo clone 失败: {str(detail)[:200]}"))
                continue
        for case in cases:
            case.repo = str(dest)
            case.repo_is_url = False
    return errors


def _commit_exists(repo: Path, rev: str) -> bool:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{rev}^{{commit}}"],
            capture_output=True, timeout=GIT_CHECK_TIMEOUT_SEC,
        )
        return proc.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def check_cases_phase2(cfg: BatchCfg, log=print) -> List[Tuple[str, str]]:
    """阶段二语义校验（repo 就绪后）：repo 存在 + base_commit 可解析为 commit。"""
    errors: List[Tuple[str, str]] = []
    commit_ok: Dict[str, bool] = {}
    for case in cfg.cases:
        repo = Path(case.repo)
        if not repo.is_dir():
            errors.append((case.id, f"repo 不存在: {case.repo}"))
            continue
        key = f"{repo}|{case.base_commit}"
        if key not in commit_ok:
            commit_ok[key] = _commit_exists(repo, case.base_commit)
        if not commit_ok[key]:
            errors.append((case.id, f"base_commit {case.base_commit} 在 {repo} 中不存在"))
    for case_id, err in errors:
        log(f"[preflight] 用例 {case_id}: {err}")
    return errors


def run_dependency_check(skill_dir: Path, log=print) -> None:
    script = skill_dir / "patch-compatibility-analysis" / "scripts" / "check_dependencies.py"
    if not script.is_file():
        raise BatchError(f"依赖检查脚本不存在: {script}")
    try:
        proc = subprocess.run([sys.executable, str(script), "--json"],
                              capture_output=True, text=True, timeout=DEP_CHECK_TIMEOUT_SEC)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise BatchError(f"依赖检查执行失败: {exc}") from exc
    if proc.returncode != 0:
        out = (proc.stdout or proc.stderr or "").strip()
        log(f"[preflight] 依赖检查未通过:\n{out[:2000]}")
        raise BatchError("PCAT 分析依赖检查未通过（见上方输出），批次中止")
    log("[preflight] 依赖检查通过")


def check_model_available(opencode_bin: str, model: Optional[str], log=print) -> List[str]:
    """模型/凭证预检：`opencode models` 可列出；模型名不在列表中时仅警告。"""
    warnings: List[str] = []
    try:
        proc = subprocess.run([opencode_bin, "models"],
                              capture_output=True, text=True, timeout=MODELS_CHECK_TIMEOUT_SEC)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise BatchError(f"无法运行 `{opencode_bin} models`（{exc}）；"
                         "请确认 opencode 已安装且在 PATH 中") from exc
    if proc.returncode != 0:
        raise BatchError(f"`{opencode_bin} models` 退出码 {proc.returncode}: "
                         f"{(proc.stderr or proc.stdout or '').strip()[:300]}")
    if model:
        listing = proc.stdout or ""
        provider = model.split("/", 1)[0]
        if model not in listing and provider not in listing:
            warnings.append(f"模型 {model!r} 未出现在 `opencode models` 列表中（自定义 provider 可能仍可用）")
    log("[preflight] 模型/凭证检查通过")
    return warnings


def check_disk_estimate(cfg: BatchCfg, log=print) -> None:
    g = cfg.global_cfg
    try:
        Path(g.output_base).mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise BatchError(f"无法创建 output_base {g.output_base}: {exc}") from exc
    try:
        free = shutil.disk_usage(g.output_base).free
    except OSError:
        log("[preflight] 磁盘：无法查询 output_base 所在卷剩余空间")
        return
    estimate = len(cfg.cases) * g.per_case_disk_estimate_gb * (1024 ** 3)
    free_gb = free / (1024 ** 3)
    need_gb = estimate / (1024 ** 3)
    if free < estimate:
        log(f"[preflight] 磁盘警告：剩余 {free_gb:.0f} GB < 预估需求 {need_gb:.0f} GB"
            f"（{len(cfg.cases)} 例 × {g.per_case_disk_estimate_gb} GB/例）；"
            "运行中低水位检查会暂停批次（watermark "
            f"{g.disk_low_watermark_gb} GB）")
    else:
        log(f"[preflight] 磁盘：剩余 {free_gb:.0f} GB，预估需求 {need_gb:.0f} GB")


# ---------------------------------------------------------------------------
# 子进程结果与 prompt 构造
# ---------------------------------------------------------------------------

@dataclass
class CaseOutcome:
    ok: bool = False
    rc: Optional[int] = None
    timed_out: bool = False
    interrupted: bool = False
    error_category: str = ""
    error_detail: str = ""
    analysis_info: Optional[Dict[str, Any]] = None
    test_info: Optional[Dict[str, Any]] = None

    def error_text(self) -> str:
        if self.timed_out:
            return self.error_detail or "timeout"
        if self.error_category == "exit" or self.error_category in (
                "prompt_missing_output_dir",):
            return self.error_detail[:300]
        if self.error_category:
            return f"{self.error_category}: {self.error_detail}"[:300]
        if self.rc is not None and self.rc != 0:
            return f"exit {self.rc}"
        return "unknown error"

    def signature(self) -> str:
        """熔断签名 = 错误类别 + 归一化的日志尾行。"""
        if self.timed_out:
            return "timeout"
        line = last_nonempty_line(self.error_detail)
        line = re.sub(r"\s+", " ", line).lower()[:100]
        return f"{self.error_category or 'exit'}|{line}"


def clean_case_dir(result_dir: Path, keep: Tuple[str, ...] = ("run.log",)) -> None:
    """清理用例产物目录（保留 run.log 供失败定位）。"""
    if not result_dir.is_dir():
        return
    for entry in result_dir.iterdir():
        if entry.name in keep:
            continue
        try:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                entry.unlink()
        except OSError:
            pass


def build_prompt(template_text: str, case: CaseCfg, result_dir: Path,
                 mode: str, keep_worktrees: bool) -> str:
    cleanup_worktree = "false" if (keep_worktrees or mode == "analysis-test") else "true"
    instructions = (ANALYSIS_TEST_MODE_INSTRUCTIONS if mode == "analysis-test"
                    else ANALYSIS_MODE_INSTRUCTIONS)
    variables = {
        "case_id": case.id,
        "repo": case.repo,
        "base_commit": case.base_commit,
        "patch": case.patch,
        "output_dir": str(result_dir),
        "profile": case.profile,
        "cleanup_worktree": cleanup_worktree,
        "batch_mode_instructions": instructions,
    }
    return render_template(template_text, variables)


def build_cmd(opencode_bin: str, cfg: BatchCfg, case: CaseCfg, prompt: str,
              workdir: Path) -> List[str]:
    g = cfg.global_cfg
    mode_label = "analysis-test" if g.mode == "analysis-test" else "analysis"
    cmd = [opencode_bin, "run"]
    if g.agent:
        cmd += ["--agent", g.agent]
    if g.model:
        cmd += ["--model", g.model]
    cmd += ["--auto", "--dir", str(workdir), "--title", f"{case.id} PCAT {mode_label}"]
    cmd.append(prompt)
    return cmd

# ---------------------------------------------------------------------------
# 调度器（状态机 + 并发槽 + 熔断/水位/进程组治理）
# ---------------------------------------------------------------------------

@dataclass
class ReportConfig:
    server: Optional[str] = None
    session: Optional[str] = None
    milestone: Optional[int] = None
    every_sec: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def enabled(self) -> bool:
        return bool(self.server and self.session)


class Runner:
    def __init__(self, cfg: BatchCfg, state: Dict[str, Any], state_path: Path,
                 progress: ProgressLog, pending: List[CaseCfg], *,
                 opencode_bin: str, validate_script: Path,
                 keep_worktrees: bool, report: ReportConfig,
                 test_finalize_script: Optional[Path] = None,
                 orchestrator_script: Optional[Path] = None):
        self.cfg = cfg
        self.g = cfg.global_cfg
        self.state = state
        self.state_path = state_path
        self.progress = progress
        self.pending = list(pending)
        self.opencode_bin = opencode_bin
        self.validate_script = validate_script
        self.test_finalize_script = test_finalize_script
        self.orchestrator_script = orchestrator_script
        self.keep_worktrees = keep_worktrees
        self.report = report

        template_path = Path(self.g.prompt_template) if self.g.prompt_template else DEFAULT_TEMPLATE
        if not template_path.is_file():
            raise BatchError(f"prompt 模板不存在: {template_path}")
        self.template_text = template_path.read_text(encoding="utf-8")

        self._futures: Dict[concurrent.futures.Future, CaseCfg] = {}
        self._pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.g.concurrency, thread_name_prefix="pcat-case")
        self._procs: Dict[str, subprocess.Popen] = {}
        self._procs_lock = threading.Lock()
        self._state_lock = threading.RLock()
        self._disk_lock = threading.Lock()

        self._stop_requested = False
        self._stop_kill_done = False
        self._circuit_broken = False
        self._paused_reason: Optional[str] = None
        self._fail_streak: List[str] = []
        self._monitor_stop = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._next_milestone: Optional[int] = self.report.milestone if (
            self.report.enabled and self.report.milestone) else None
        self._last_inject_ts = time.time()

    # -- 状态与事件 ---------------------------------------------------------

    def _save(self) -> None:
        with self._state_lock:
            self.state["updated_at"] = now_iso()
            self.state["runner_pid"] = os.getpid()
            self.state["counts"] = compute_counts(self.state)
            atomic_write_json(self.state_path, self.state)

    def _emit(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if payload and "counts" not in payload:
            payload = dict(payload)
            payload["counts"] = event_counts(self.state)
        self.progress.emit(event, payload)

    def _stdout(self, message: str) -> None:
        print(message, flush=True)

    # -- 通知（模式 D）与会话注入（模式 E） -----------------------------------

    def _notify(self, event: str) -> None:
        notify = self.g.notify
        if not notify or event not in notify["on"]:
            return
        counts = compute_counts(self.state)
        command = (notify["command"]
                   .replace("{{batch_id}}", str(self.state.get("batch_id", "")))
                   .replace("{{event}}", event)
                   .replace("{{counts}}",
                            f"done={counts['done']} failed={counts['failed']} "
                            f"pending={counts['pending']}"))
        try:
            subprocess.run(command, shell=True, capture_output=True, text=True,
                           timeout=NOTIFY_TIMEOUT_SEC, cwd=str(self.state_path.parent))
        except (subprocess.TimeoutExpired, OSError) as exc:
            self._emit("notify_failed", {"event": event, "error": str(exc)[:200]})

    def _inject(self, text: str) -> bool:
        if not self.report.enabled:
            return True
        url = f"{self.report.server.rstrip('/')}/session/{self.report.session}/prompt_async"
        body = json.dumps({"parts": [{"type": "text", "text": text}]}).encode("utf-8")
        headers = {"content-type": "application/json"}
        password = self.report.password or os.environ.get("OPENCODE_SERVER_PASSWORD")
        username = self.report.username or os.environ.get("OPENCODE_SERVER_USERNAME") or "opencode"
        if password:
            token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
            headers["Authorization"] = f"Basic {token}"
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=INJECT_TIMEOUT_SEC):
                pass
            return True
        except (urllib.error.URLError, OSError, ValueError) as exc:
            self._emit("report_failed", {"error": f"{type(exc).__name__}: {exc}"[:200]})
            return False

    def _progress_percent(self) -> float:
        counts = compute_counts(self.state)
        if counts["total"] == 0:
            return 0.0
        completed = counts["done"] + counts["failed"]
        return completed * 100.0 / counts["total"]

    def _maybe_inject_milestone(self, force: bool = False) -> None:
        if not self.report.enabled:
            return
        pct = self._progress_percent()
        label = None
        if force:
            label = "批次结束"
        elif self._next_milestone is not None and pct >= self._next_milestone:
            label = f"里程碑 {self._next_milestone}%"
            self._next_milestone += self.report.milestone or 10
        elif self.report.every_sec and (time.time() - self._last_inject_ts) >= self.report.every_sec:
            label = "定时汇报"
        if label is None:
            return
        self._last_inject_ts = time.time()
        snapshot = render_progress_snapshot(self.state, self.state_path)
        text = (f"[批量扫描] 批次 {self.state.get('batch_id')} {label}：\n"
                f"{snapshot}\n"
                "（本消息由 batch_runner 自动注入，请向用户转述当前进度。）")
        self._inject(text)

    # -- 磁盘水位 -----------------------------------------------------------

    def _check_disk(self, log_event: bool = True) -> None:
        with self._disk_lock:
            try:
                free = shutil.disk_usage(self.g.output_base).free
            except OSError:
                return
            watermark = self.g.disk_low_watermark_gb * (1024 ** 3)
            low = free < watermark
            if low and self._paused_reason is None:
                self._paused_reason = "disk_low"
                self.state["paused_reason"] = "disk_low"
                if log_event:
                    self._emit("paused", {
                        "reason": "disk_low",
                        "free_gb": round(free / (1024 ** 3), 1),
                        "watermark_gb": self.g.disk_low_watermark_gb,
                    })
                    self._notify("disk_low")
                self._stdout(f"[水位] 磁盘剩余 {free / (1024 ** 3):.1f} GB 低于 "
                             f"{self.g.disk_low_watermark_gb} GB，暂停分派（running 自然收尾）")
            elif not low and self._paused_reason == "disk_low":
                self._paused_reason = None
                self.state["paused_reason"] = None
                if log_event:
                    self._emit("paused", {"reason": "disk_low", "recovered": True})
                self._stdout("[水位] 磁盘空间已恢复，继续分派")

    # -- 监视线程（心跳 + 磁盘水位检查） --------------------------------------

    def _monitor_loop(self) -> None:
        last_heartbeat = time.time()
        last_disk = time.time()
        while not self._monitor_stop.wait(1.0):
            now = time.time()
            if (self.g.progress_interval_sec > 0
                    and now - last_heartbeat >= self.g.progress_interval_sec):
                last_heartbeat = now
                running_detail = []
                for case_id, st in self.state["cases"].items():
                    if st.get("status") != "running":
                        continue
                    elapsed = iso_elapsed(st.get("started_at"), now_iso()) or 0
                    running_detail.append({
                        "case": case_id,
                        "elapsed_sec": int(elapsed),
                        "timeout_sec": self._effective_timeout(),
                    })
                self._emit("heartbeat", {"running_detail": running_detail})
            if now - last_disk >= self.g.disk_check_interval_sec:
                last_disk = now
                self._check_disk()

    def _effective_timeout(self) -> int:
        if self.g.mode == "analysis-test":
            return self.g.timeout_sec * TEST_TIMEOUT_MULTIPLIER
        return self.g.timeout_sec

    # -- 进程注册表与进程组治理 -------------------------------------------------

    def _register_proc(self, case_id: str, proc: subprocess.Popen) -> None:
        with self._procs_lock:
            self._procs[case_id] = proc
        with self._state_lock:
            st = self.state["cases"][case_id]
            st["pid"] = proc.pid
            st["pgid"] = proc.pid  # start_new_session=True → pgid == pid
            self._save()

    def _unregister_proc(self, case_id: str) -> None:
        with self._procs_lock:
            self._procs.pop(case_id, None)

    @staticmethod
    def _kill_group(proc: subprocess.Popen, graceful: bool) -> None:
        try:
            os.killpg(proc.pid, signal.SIGTERM if graceful else signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            return
        if graceful:
            deadline = time.time() + KILL_GRACE_SEC
            while proc.poll() is None and time.time() < deadline:
                time.sleep(0.1)
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass

    def _kill_all_children(self) -> None:
        with self._procs_lock:
            procs = list(self._procs.values())
        for proc in procs:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                continue
        deadline = time.time() + KILL_GRACE_SEC
        for proc in procs:
            while proc.poll() is None and time.time() < deadline:
                time.sleep(0.1)
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass

    # -- 分派与回收 ---------------------------------------------------------

    def _dispatch(self, case: CaseCfg) -> None:
        st = self.state["cases"][case.id]
        clean_case_dir(Path(case.result_dir))
        workdir = Path(case.result_dir) / "workdir"
        workdir.mkdir(parents=True, exist_ok=True)
        st["status"] = "running"
        st["started_at"] = now_iso()
        st["finished_at"] = None
        st["elapsed_sec"] = None
        st["error"] = None
        st["summary"] = None
        st["pid"] = None
        st["pgid"] = None
        self._save()
        self._emit("dispatch", {"case": case.id})
        future = self._pool.submit(self._run_case, case)
        self._futures[future] = case

    def _run_case(self, case: CaseCfg) -> CaseOutcome:
        result_dir = Path(case.result_dir)
        workdir = result_dir / "workdir"
        log_path = result_dir / "run.log"
        try:
            prompt = build_prompt(self.template_text, case, result_dir,
                                  self.g.mode, self.keep_worktrees)
            if str(result_dir) not in prompt:
                return CaseOutcome(error_category="prompt_missing_output_dir",
                                   error_detail=f"渲染后的 prompt 未包含 output_dir={result_dir}")
            cmd = build_cmd(self.opencode_bin, self.cfg, case, prompt, workdir)
        except BatchError as exc:
            return CaseOutcome(error_category="prompt_render_error", error_detail=str(exc))

        with open(log_path, "ab") as log:
            try:
                proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                        cwd=str(workdir), start_new_session=True)
            except OSError as exc:
                return CaseOutcome(error_category="launch_error", error_detail=str(exc))
            self._register_proc(case.id, proc)
            try:
                if self._stop_requested:
                    self._kill_group(proc, graceful=True)
                timeout = self._effective_timeout()
                try:
                    rc = proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self._kill_group(proc, graceful=False)
                    try:
                        proc.wait(timeout=KILL_GRACE_SEC)
                    except subprocess.TimeoutExpired:
                        pass
                    return CaseOutcome(timed_out=True,
                                       error_category="timeout",
                                       error_detail=f"timeout after {timeout}s")
            finally:
                self._unregister_proc(case.id)

        if self._stop_requested:
            return CaseOutcome(interrupted=True)
        if rc != 0:
            detail = last_nonempty_line(tail_text(log_path, max_bytes=8192))
            return CaseOutcome(rc=rc, error_category="exit",
                               error_detail=f"exit {rc}: {detail}" if detail else f"exit {rc}")

        analysis_path = result_dir / "analysis.json"
        if not analysis_path.is_file():
            return CaseOutcome(rc=rc, error_category="missing_artifact",
                               error_detail="analysis.json 不存在（子会话假结束）")
        ok, err = validate_analysis_file(self.validate_script, analysis_path,
                                         require_affected_scope=True)
        if not ok:
            return CaseOutcome(rc=rc, error_category="invalid_artifact",
                               error_detail=f"validate_analysis.py --require-affected-scope: {err}")
        scope_path = result_dir / AFFECTED_SCOPE_FILENAME
        if not scope_path.is_file():
            return CaseOutcome(rc=rc, error_category="invalid_artifact",
                               error_detail=f"{AFFECTED_SCOPE_FILENAME} 不存在"
                                            "（Phase 7.1 影响范围未生成）")
        try:
            info = extract_analysis_info(analysis_path)
        except (OSError, json.JSONDecodeError) as exc:
            return CaseOutcome(rc=rc, error_category="invalid_artifact",
                               error_detail=f"analysis.json 解析失败: {exc}")

        test_info: Optional[Dict[str, Any]] = None
        if self.g.mode == "analysis-test":
            test_dir = result_dir / TEST_RESULT_SUBDIR
            summary_path = test_dir / "test-summary.json"
            if not summary_path.is_file():
                return CaseOutcome(rc=rc, error_category="missing_test_artifact",
                                   error_detail="test-summary.json 不存在（测试阶段未完成）")
            if self.test_finalize_script is None or not self.test_finalize_script.is_file():
                return CaseOutcome(rc=rc, error_category="invalid_test_artifact",
                                   error_detail=f"finalize_test_report.py 不存在: {self.test_finalize_script}")
            ok, err = validate_test_summary(self.test_finalize_script, summary_path)
            if not ok:
                return CaseOutcome(rc=rc, error_category="invalid_test_artifact",
                                   error_detail=f"finalize_test_report.py --validate-only: {err}")
            for report_name in ("TEST_REPORT.md",):
                if not (test_dir / report_name).is_file():
                    return CaseOutcome(rc=rc, error_category="missing_test_artifact",
                                       error_detail=f"{TEST_RESULT_SUBDIR}/{report_name} 不存在")
            try:
                test_info = extract_test_info(summary_path)
            except (OSError, json.JSONDecodeError) as exc:
                return CaseOutcome(rc=rc, error_category="invalid_test_artifact",
                                   error_detail=f"test-summary.json 解析失败: {exc}")
            # COVERAGE_REPORT.md 仅在产生覆盖率报告时必需：测试失败时
            # test-summary.json 的 coverage_report=null，不生成覆盖率报告。
            if test_info is None or test_info.get("has_coverage_report", True):
                if not (test_dir / "COVERAGE_REPORT.md").is_file():
                    return CaseOutcome(rc=rc, error_category="missing_test_artifact",
                                       error_detail=f"{TEST_RESULT_SUBDIR}/COVERAGE_REPORT.md 不存在")
        return CaseOutcome(ok=True, rc=rc, analysis_info=info, test_info=test_info)

    def _collect(self, future: concurrent.futures.Future) -> None:
        case = self._futures.pop(future)
        try:
            outcome = future.result()
        except Exception as exc:  # worker 内部异常兜底
            outcome = CaseOutcome(error_category="internal_error", error_detail=repr(exc))
        st = self.state["cases"][case.id]
        st["finished_at"] = now_iso()
        st["elapsed_sec"] = iso_elapsed(st.get("started_at"), st.get("finished_at"))
        st["pid"] = None
        st["pgid"] = None

        if outcome.interrupted or (self._stop_requested and not outcome.ok):
            st["interrupted_count"] = st.get("interrupted_count", 0) + 1
            st["status"] = "pending"  # 中断不是用例的错：不消耗 attempts，待 --resume/本轮重派
            st["error"] = "interrupted (dispatcher stopping)"
            self._emit("case_interrupted", {"case": case.id})
            self._save()
            return

        if outcome.ok and outcome.analysis_info is not None:
            info = outcome.analysis_info
            st["status"] = "done"
            st["error"] = None
            st["summary"] = info["summary"]
            if outcome.test_info is not None:
                st["test"] = outcome.test_info
            self._fail_streak = []
            self._emit("case_done", {"case": case.id,
                                     "elapsed_sec": st.get("elapsed_sec")})
            detail = f" {outcome.test_info['summary']}" if outcome.test_info else ""
            self._stdout(f"[完成] {case.id} done "
                         f"({human_duration(st.get('elapsed_sec'))}) {info['summary']}{detail}")
            self._save()
            self._maybe_inject_milestone()
            return

        st["attempts"] = st.get("attempts", 0) + 1
        error = outcome.error_text()
        st["error"] = error
        self._register_failure(outcome.signature())
        self._emit("case_failed", {"case": case.id, "error": error})
        if st["attempts"] <= self.g.retries:
            clean_case_dir(Path(case.result_dir))
            st["status"] = "pending"
            self.pending.append(case)
            self._emit("retry", {"case": case.id, "attempt": st["attempts"], "error": error})
            self._stdout(f"[重试] {case.id} 第 {st['attempts']} 次失败: {error}")
        else:
            st["status"] = "failed"
            self._stdout(f"[失败] {case.id} 重试耗尽: {error}")
        self._save()

        if (not self._circuit_broken
                and len(self._fail_streak) >= self.g.consecutive_fail_limit):
            self._circuit_broken = True
            reason = (f"{len(self._fail_streak)} 个连续同签名失败: "
                      f"{self._fail_streak[0]}")
            self.state["abort_reason"] = reason
            self._emit("circuit_break", {"reason": reason})
            self._stdout(f"[熔断] {reason}；暂停分派，未完成用例保持 pending，"
                         "排障后可用 --resume 续跑")
            self._notify("circuit_break")

    def _register_failure(self, signature: str) -> None:
        """连续同签名失败计数；签名不同即重置（用例级失败不误触发熔断）。"""
        if self._fail_streak and self._fail_streak[0] == signature:
            self._fail_streak.append(signature)
        else:
            self._fail_streak = [signature]

    # -- 主循环 ---------------------------------------------------------------

    def _request_stop(self, signum: int, _frame: Any) -> None:
        self._stop_requested = True

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self._request_stop)
        signal.signal(signal.SIGINT, self._request_stop)
        self.state["finished_at"] = None
        self.state["abort_reason"] = None
        self._save()
        self._emit("batch_start", {
            "batch_id": self.state.get("batch_id"),
            "total": len(self.state["cases"]),
            "concurrency": self.g.concurrency,
            "mode": self.g.mode,
            "model": self.g.model,
        })
        self._monitor_thread = threading.Thread(target=self._monitor_loop,
                                                name="pcat-monitor", daemon=True)
        self._monitor_thread.start()

        try:
            while True:
                if self._stop_requested and not self._stop_kill_done:
                    self._stop_kill_done = True
                    self._emit("stopping", {"reason": "signal"})
                    self._kill_all_children()
                self._check_disk(log_event=True)

                while (not self._stop_requested and not self._circuit_broken
                       and self._paused_reason is None and self.pending
                       and len(self._futures) < self.g.concurrency):
                    self._dispatch(self.pending.pop(0))

                if not self._futures:
                    if self._stop_requested or self._circuit_broken:
                        break
                    if self.pending and self._paused_reason == "disk_low":
                        self._check_disk(log_event=True)
                        if self._paused_reason == "disk_low":
                            break  # 已收尾且仍低水位：结束本轮，待 --resume
                        continue    # 水位恢复：继续分派
                    break

                done, _ = concurrent.futures.wait(list(self._futures.keys()),
                                                  timeout=POLL_SEC)
                for future in done:
                    self._collect(future)
        finally:
            self._monitor_stop.set()
            if self._monitor_thread is not None:
                self._monitor_thread.join(timeout=3)
            self._pool.shutdown(wait=True)

        for case_id, st in self.state["cases"].items():
            if st.get("status") == "running":
                st["interrupted_count"] = st.get("interrupted_count", 0) + 1
                st["status"] = "pending"
                if st.get("error") is None:
                    st["error"] = "interrupted"
        self.state["finished_at"] = now_iso()
        counts = compute_counts(self.state)
        batch_elapsed = iso_elapsed(self.state.get("started_at"),
                                    self.state.get("finished_at"))
        self._save()

        summary_path = self.state_path.parent / SUMMARY_FILENAME
        report_path = self.state_path.parent / REPORT_FILENAME
        try:
            aggregate(self.state, self.cfg, summary_path, report_path)
        except Exception as exc:  # 聚合失败不丢弃批次结果
            self._stdout(f"[警告] 汇总报告生成失败: {exc}")

        self._emit("batch_done", {"elapsed_sec": batch_elapsed,
                                  "complete": counts["pending"] == 0
                                              and counts["running"] == 0})
        self._notify("batch_done")
        self._maybe_inject_milestone(force=True)
        self._save()

        if self._stop_requested:
            exit_code = 130
        elif self._circuit_broken:
            exit_code = 3
        elif self._paused_reason == "disk_low":
            exit_code = 4
        elif counts["failed"] > 0:
            exit_code = 2
        else:
            exit_code = 0
        self._stdout(
            f"[结束] 批次 {self.state.get('batch_id')}："
            f"done {counts['done']} · failed {counts['failed']} · "
            f"skipped {counts['skipped']} · pending {counts['pending']} · "
            f"总耗时 {human_duration(batch_elapsed)}（退出码 {exit_code}）\n"
            f"  汇总: {summary_path}\n  报告: {report_path}")
        return exit_code

# ---------------------------------------------------------------------------
# 进度快照渲染（--progress / 注入回调共用；权威状态以 batch_state.json 为准）
# ---------------------------------------------------------------------------

def _human_eta(seconds: float) -> str:
    if seconds >= 3600:
        return f"{seconds / 3600:.1f} 小时"
    if seconds >= 60:
        return f"{seconds / 60:.0f} 分钟"
    return f"{seconds:.0f} 秒"


def render_progress_snapshot(state: Dict[str, Any], state_path: Path) -> str:
    counts = state.get("counts") or compute_counts(state)
    total = counts["total"]
    completed = counts["done"] + counts["failed"]
    pct = completed * 100.0 / total if total else 0.0
    filled = int(round(BAR_WIDTH * completed / total)) if total else 0
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    concurrency = state.get("concurrency", "?")
    lines = [
        f"批次 {state.get('batch_id', '?')}  [{bar}] {completed}/{total} "
        f"({pct:.0f}%)  并发 {counts['running']}/{concurrency}"
    ]

    running_parts: List[Tuple[float, str]] = []
    now = now_iso()
    for case_id, st in state.get("cases", {}).items():
        if st.get("status") != "running":
            continue
        elapsed = iso_elapsed(st.get("started_at"), now) or 0.0
        minutes = int(elapsed // 60)
        label = f"{minutes}m" if minutes < 60 else f"{minutes // 60}h{minutes % 60:02d}m"
        running_parts.append((elapsed, f"{case_id}({label})"))
    running_parts.sort(key=lambda item: item[0], reverse=True)
    detail = " ".join(part for _, part in running_parts[:8])

    line2 = (f"  done {counts['done']} · failed {counts['failed']} · "
             f"pending {counts['pending']}")
    if counts["skipped"]:
        line2 += f" · skipped {counts['skipped']}"
    if detail:
        line2 += f" · 运行中: {detail}"
    elif counts["running"]:
        line2 += f" · 运行中: {counts['running']} 例"
    lines.append(line2)

    started = parse_iso(state.get("started_at"))
    elapsed_sec = ((datetime.now().astimezone() - started).total_seconds()
                   if started else None)
    done_elapsed = [st.get("elapsed_sec") for st in state.get("cases", {}).values()
                    if st.get("status") == "done" and st.get("elapsed_sec")]
    avg = sum(done_elapsed) / len(done_elapsed) if done_elapsed else None
    parts: List[str] = []
    if elapsed_sec and elapsed_sec > 60:
        parts.append(f"吞吐 {completed / (elapsed_sec / 3600):.1f} 例/小时")
    remaining = counts["pending"] + counts["running"]
    if avg and remaining and isinstance(concurrency, int):
        parts.append(f"ETA {_human_eta(remaining * avg / concurrency)}")
    if avg:
        parts.append(f"按已完成平均 {avg / 60:.1f} min/例 ÷ 并发 {concurrency}")
    lines.append("  " + " · ".join(parts) if parts else "  吞吐/ETA: 估算中（尚无已完成用例）")

    last_failure = ""
    for case_id, st in state.get("cases", {}).items():
        if st.get("status") == "failed" and st.get("error"):
            last_failure = f"{case_id}: {str(st['error'])[:60]}"
    disk_text = "未知"
    output_base = state.get("output_base")
    if output_base:
        try:
            disk_text = f"{shutil.disk_usage(output_base).free / (1024 ** 3):.0f} GB"
        except OSError:
            pass
    hb = last_heartbeat_age_sec(state_path.parent / PROGRESS_FILENAME)
    hb_text = ("无事件" if hb is None else
               "刚刚" if hb < 60 else f"{int(hb // 60)} min 前")
    lines.append(f"  最近失败: {last_failure or '无'} · 磁盘剩余: {disk_text} · 心跳: {hb_text}")

    if state.get("abort_reason"):
        lines.append(f"  ⚠ 熔断: {state['abort_reason']}")
    if state.get("paused_reason"):
        lines.append("  ⏸ 暂停: disk_low（清理空间后 --resume 续跑）")
    if state.get("finished_at"):
        lines.append(f"  ✔ 本轮已结束: {state['finished_at']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 孤儿回收（--resume 启动时；§7.2 恢复协议）
# ---------------------------------------------------------------------------

def reap_orphans(state: Dict[str, Any], progress: ProgressLog, log=print) -> None:
    running = [(cid, st) for cid, st in state.get("cases", {}).items()
               if st.get("status") == "running"]
    if not running:
        return
    log(f"[恢复] 发现 {len(running)} 个 running 残留用例，执行孤儿回收")
    output_base = state.get("output_base") or ""
    for case_id, st in running:
        pid = st.get("pid") or 0
        if pid and _pid_alive(pid):
            cmdline = _pid_cmdline(pid)
            # 防 pid 复用误杀：必须是 opencode 且命令行包含本批次 output_base
            if "opencode" in cmdline and output_base and output_base in cmdline:
                log(f"[恢复] {case_id}: pid {pid} 仍存活，killpg 整组回收")
                try:
                    os.killpg(pid, signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass
                deadline = time.time() + KILL_GRACE_SEC
                while _pid_alive(pid) and time.time() < deadline:
                    time.sleep(0.2)
                if _pid_alive(pid):
                    try:
                        os.killpg(pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
            else:
                log(f"[恢复] {case_id}: pid {pid} 存活但非本批次 opencode 进程"
                    "（疑似 pid 复用），跳过 kill 仅重置状态")
        st["interrupted_count"] = st.get("interrupted_count", 0) + 1
        st["status"] = "pending"
        st["pid"] = None
        st["pgid"] = None
        progress.emit("case_interrupted", {"case": case_id,
                                           "counts": event_counts(state)})
    log("[恢复] 回收完成：全部残留 running → pending（不消耗 attempts）")


# ---------------------------------------------------------------------------
# 结果聚合（batch_summary.json + batch_report.md）
# ---------------------------------------------------------------------------

def compute_metrics(rows: List[Tuple[bool, bool]]) -> Dict[str, Any]:
    tp = tn = fp = fn = 0
    for predicted, gold in rows:
        if gold and predicted:
            tp += 1
        elif gold and not predicted:
            fn += 1
        elif not gold and predicted:
            fp += 1
        else:
            tn += 1
    total = tp + tn + fp + fn

    def div(a: float, b: float) -> float:
        return a / b if b else 0.0

    precision = div(tp, tp + fp)
    recall = div(tp, tp + fn)
    specificity = div(tn, tn + fp)
    mcc_denom = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    return {
        "accuracy": round(div(tp + tn, total), 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "f1": round(div(2 * precision * recall, precision + recall), 4),
        "balanced_accuracy": round((recall + specificity) / 2, 4),
        "mcc": round(div(tp * tn - fp * fn, mcc_denom), 4),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "evaluated": total,
    }


def aggregate(state: Dict[str, Any], cfg: Optional[BatchCfg],
              summary_path: Path, report_path: Path) -> Dict[str, Any]:
    expected_map = cfg.expected_map() if cfg else {}
    order = [case.id for case in cfg.cases] if cfg else list(state["cases"].keys())
    case_rows: Dict[str, Dict[str, Any]] = {}
    metric_rows: List[Tuple[bool, bool]] = []

    for case_id in order:
        st = state["cases"].get(case_id)
        if st is None:
            continue
        row: Dict[str, Any] = {
            "status": st.get("status"),
            "elapsed_sec": st.get("elapsed_sec"),
            "attempts": st.get("attempts", 0),
            "error": st.get("error"),
            "result_dir": st.get("result_dir"),
            "compatibility": None,
            "findings": None,
            "top_priority": None,
            "compatibility_types": [],
            "summary_mismatch": None,
            "test": st.get("test"),
        }
        if st.get("status") in ("done", "already_done"):
            result_dir = Path(st.get("result_dir") or "")
            analysis_path = result_dir / "analysis.json"
            predicted: Optional[bool] = None
            try:
                info = extract_analysis_info(analysis_path)
                predicted = info["predicted"]
                row.update(compatibility=predicted,
                           findings=info["findings"],
                           top_priority=info["top_priority"],
                           compatibility_types=info["compatibility_types"])
            except (OSError, json.JSONDecodeError):
                row["error"] = "analysis.json 缺失或不可读（产物被移动/删除？）"
            parsed_summary = parse_summary_line(result_dir / "run.log")
            if parsed_summary is not None and predicted is not None:
                reported_compat = parsed_summary.get("compatibility")
                reported_findings = parsed_summary.get("findings")
                mismatch = None
                if isinstance(reported_compat, bool) and reported_compat != predicted:
                    mismatch = "compatibility"
                elif (isinstance(reported_findings, int) and row["findings"] is not None
                      and reported_findings != row["findings"]):
                    mismatch = "findings"
                row["summary_mismatch"] = mismatch
            expected = expected_map.get(case_id)
            if expected is not None and predicted is not None:
                metric_rows.append((predicted, bool(expected["is_compatibility_change"])))
        case_rows[case_id] = row

    counts = compute_counts(state)
    summary: Dict[str, Any] = {
        "batch_id": state.get("batch_id"),
        "manifest": state.get("manifest"),
        "mode": state.get("mode"),
        "model": state.get("model"),
        "agent": state.get("agent"),
        "concurrency": state.get("concurrency"),
        "started_at": state.get("started_at"),
        "finished_at": state.get("finished_at") or now_iso(),
        "abort_reason": state.get("abort_reason"),
        "paused_reason": state.get("paused_reason"),
        "counts": counts,
        "cases": case_rows,
        "metrics": compute_metrics(metric_rows) if metric_rows else None,
    }
    atomic_write_json(summary_path, summary)
    report_path.write_text(render_report(summary), encoding="utf-8")
    return summary


def render_report(summary: Dict[str, Any]) -> str:
    counts = summary["counts"]
    rows = summary["cases"]
    executed_done = [r for r in rows.values() if r["status"] == "done"]
    already_done = [r for r in rows.values() if r["status"] == "already_done"]
    env_skipped = [r for r in rows.values() if r["status"] == "skipped"]
    failed_rows = [r for r in rows.values() if r["status"] == "failed"]
    avg = (sum(r["elapsed_sec"] for r in executed_done if r["elapsed_sec"])
           / max(1, len([r for r in executed_done if r["elapsed_sec"]])))

    out: List[str] = []
    out.append(f"# 批量扫描报告（batch: {summary['batch_id']}）")
    out.append("")
    out.append(f"- 清单：`{summary['manifest']}`")
    out.append(f"- 模式：{summary['mode']} · 模型：{summary['model'] or '默认'} · "
               f"并发：{summary['concurrency']}")
    out.append(f"- 开始：{summary['started_at']} · 结束：{summary['finished_at']}")
    if summary.get("abort_reason"):
        out.append(f"- ⚠ 熔断中止：{summary['abort_reason']}（未完成用例可 --resume 续跑）")
    if summary.get("paused_reason"):
        out.append(f"- ⏸ 暂停：{summary['paused_reason']}（空间恢复后 --resume 续跑）")

    out.append("")
    out.append("## 1. 概览")
    out.append("")
    out.append("| 状态 | 数量 | 平均耗时 |")
    out.append("|---|---:|---|")
    out.append(f"| 总用例 | {counts['total']} | - |")
    out.append(f"| 成功（本轮执行） | {len(executed_done)} | "
               f"{'%.1f min' % (avg / 60) if executed_done else '-'} |")
    out.append(f"| 成功（已有产物跳过） | {len(already_done)} | - |")
    if env_skipped:
        out.append(f"| 环境未授权跳过 | {len(env_skipped)} | - |")
    out.append(f"| 失败 | {len(failed_rows)} | - |")
    if counts["pending"]:
        out.append(f"| 未完成（pending） | {counts['pending']} | - |")

    out.append("")
    out.append("## 2. 结果明细")
    out.append("")
    out.append("| 用例 | 状态 | 兼容性变更 | findings | 最高优先级 | 类型 | 耗时 | 产物 |")
    out.append("|---|---|:---:|---:|---|---|---|---|")
    for case_id, row in rows.items():
        status = row["status"]
        if status in ("done", "already_done"):
            compat = "✓" if row["compatibility"] else "✗"
            if row["compatibility"] is None:
                compat = "?"
            findings = row["findings"] if row["findings"] is not None else "-"
            priority = row["top_priority"] or "-"
            types = "+".join(row["compatibility_types"]) or "-"
            mark = " ⚠" if row["summary_mismatch"] else ""
            out.append(f"| {case_id}{mark} | {status} | {compat} | {findings} | "
                       f"{priority} | {types} | {human_duration(row['elapsed_sec'])} | "
                       f"`{row['result_dir']}` |")
        elif status == "failed":
            out.append(f"| {case_id} | failed | - | - | - | - | - | "
                       f"`{row['result_dir']}` |")
        elif status == "skipped":
            out.append(f"| {case_id} | skipped | - | - | - | - | - | - |")
        else:
            out.append(f"| {case_id} | {status} | - | - | - | - | - | - |")
    mismatch_ids = [cid for cid, r in rows.items() if r["summary_mismatch"]]
    if mismatch_ids:
        out.append("")
        out.append(f"> ⚠ SUMMARY 与 analysis.json 矛盾（以 analysis.json 为准，"
                   f"建议人工抽查 run.log）：{', '.join(mismatch_ids)}")

    test_rows = [(cid, r) for cid, r in rows.items()
                 if r["status"] in ("done", "already_done") and r.get("test")]
    if test_rows:
        out.append("")
        out.append("### 测试与覆盖率（analysis-test）")
        out.append("")
        out.append("| 用例 | 测试状态 | 覆盖率 | Gate | 兼容性结论 |")
        out.append("|---|---|---:|:---:|---|")
        for case_id, row in test_rows:
            t = row["test"] or {}
            rate = t.get("coverage_rate")
            rate_text = f"{rate}%" if isinstance(rate, (int, float)) else "-"
            gate = t.get("coverage_gate_met")
            gate_text = "✓" if gate is True else ("✗" if gate is False else "-")
            out.append(f"| {case_id} | {t.get('status') or '-'} | {rate_text} | "
                       f"{gate_text} | {t.get('backward_compatibility') or '-'} |")

    out.append("")
    out.append("## 3. 失败清单")
    out.append("")
    if failed_rows:
        out.append("| 用例 | 尝试次数 | 失败原因 | 日志 |")
        out.append("|---|---:|---|---|")
        for case_id, row in rows.items():
            if row["status"] != "failed":
                continue
            out.append(f"| {case_id} | {row['attempts']} | {row['error'] or '-'} | "
                       f"`{row['result_dir']}/run.log` |")
    else:
        out.append("无失败用例。")

    out.append("")
    out.append("## 4. 指标")
    out.append("")
    metrics = summary.get("metrics")
    if metrics:
        out.append(f"- Accuracy: {metrics['accuracy']} · Precision: {metrics['precision']} · "
                   f"Recall: {metrics['recall']} · Specificity: {metrics['specificity']} · "
                   f"F1: {metrics['f1']}")
        out.append(f"- Balanced Accuracy: {metrics['balanced_accuracy']} · MCC: {metrics['mcc']}")
        out.append(f"- TP {metrics['tp']} · TN {metrics['tn']} · FP {metrics['fp']} · "
                   f"FN {metrics['fn']}（共 {metrics['evaluated']} 例带 expected）")
        not_evaluated = len(failed_rows)
        if not_evaluated:
            out.append(f"- 注：另有 {not_evaluated} 例失败未计入指标")
    else:
        out.append("清单未提供 expected（或无可用预测），跳过评测指标。")
    out.append("")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# CLI 命令
# ---------------------------------------------------------------------------

def resolve_state_path(args: argparse.Namespace) -> Path:
    if getattr(args, "state", None):
        return Path(args.state).expanduser().absolute()
    if getattr(args, "manifest", None):
        return (Path(args.manifest).expanduser().resolve().parent / STATE_FILENAME)
    raise BatchError("--progress/--report-only/--cleanup 需要 --manifest 或 --state")


def apply_cli_overrides(cfg: BatchCfg, args: argparse.Namespace) -> None:
    g = cfg.global_cfg
    if args.concurrency:
        g.concurrency = _as_int(args.concurrency, "--concurrency", 1, HARD_CONCURRENCY_CAP)
    if args.mode:
        mode = "analysis-test" if args.mode == "test" else args.mode
        if mode not in ("analysis", "analysis-test"):
            raise BatchError(f"--mode 非法: {args.mode!r}")
        g.mode = mode


def build_report_config(args: argparse.Namespace, g: GlobalCfg) -> ReportConfig:
    report_to = g.report_to or {}
    server = args.report_server or report_to.get("server")
    session = args.report_session
    milestone_raw = args.report_milestone or report_to.get("milestone")
    every_raw = args.report_every or report_to.get("every")
    milestone: Optional[int] = None
    if milestone_raw is not None:
        try:
            milestone = int(str(milestone_raw).rstrip("%"))
        except ValueError:
            raise BatchError(f"--report-milestone 非法: {milestone_raw!r}（示例：10 或 10%）")
        if not 1 <= milestone <= 100:
            raise BatchError("--report-milestone 取值范围 [1, 100]")
    every_sec: Optional[int] = None
    if every_raw:
        every_sec = parse_duration(str(every_raw))
    if server and session and milestone is None and every_sec is None:
        milestone = 10
    config = ReportConfig(server=server, session=session, milestone=milestone,
                          every_sec=every_sec,
                          username=args.report_username, password=args.report_password)
    if (args.report_session or args.report_server) and not config.enabled:
        print("警告：模式 E 注入需要同时提供 --report-server 与 --report-session，已禁用",
              file=sys.stderr)
    return config


def _check_opencode_bin(opencode_bin: str) -> None:
    if Path(opencode_bin).is_file() or shutil.which(opencode_bin):
        return
    raise BatchError(f"找不到 opencode 可执行文件: {opencode_bin}"
                     "（可用 --opencode-bin 指定路径）")


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_manifest(Path(args.manifest))
    apply_cli_overrides(cfg, args)
    g = cfg.global_cfg
    _check_opencode_bin(args.opencode_bin)
    skill_dir = resolve_skill_dir(g.skill_dir)
    validate_script = (skill_dir / "patch-compatibility-analysis" / "scripts"
                       / "validate_analysis.py")
    orchestrator_script = (skill_dir / "patch-compatibility-analysis" / "scripts"
                           / "orchestrator.py")
    test_finalize_script = (skill_dir / "patch-compatibility-testing" / "scripts"
                            / "finalize_test_report.py")

    state_path = (Path(args.state).expanduser().absolute() if args.state
                  else cfg.path.parent / STATE_FILENAME)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    progress = ProgressLog(state_path.parent / PROGRESS_FILENAME)

    run_dependency_check(skill_dir)
    for warning in check_model_available(args.opencode_bin, g.model):
        print(f"[警告] {warning}")

    lock = BatchLock(state_path)
    lock.acquire()
    try:
        if state_path.exists() and not args.force:
            state = load_state_file(state_path)
            manifest_ids = {case.id for case in cfg.cases}
            state_ids = set(state["cases"].keys())
            if manifest_ids != state_ids:
                only_manifest = sorted(manifest_ids - state_ids)
                only_state = sorted(state_ids - manifest_ids)
                raise BatchError(
                    "状态文件与清单用例集不一致"
                    f"（清单独有: {only_manifest[:5]}；状态独有: {only_state[:5]}）。"
                    "请修正清单，或使用 --force 全新重跑")
            state["manifest"] = str(cfg.path)
            state.update(mode=g.mode, model=g.model, agent=g.agent,
                         concurrency=g.concurrency, timeout_sec=g.timeout_sec,
                         retries=g.retries, output_base=g.output_base)
            print(f"[续跑] 加载已有批次状态 {state_path}（batch_id={state.get('batch_id')}）；"
                  "已有有效产物的用例自动跳过，全部重跑请用 --force")
        else:
            old_batch_id = None
            if state_path.exists():
                try:
                    old_batch_id = load_state_file(state_path).get("batch_id")
                except BatchError:
                    old_batch_id = None
            batch_id = make_batch_id(cfg.path)
            if batch_id == old_batch_id:
                batch_id = f"{batch_id}-r{int(time.time()) % 100000}"
            state = fresh_state(cfg, batch_id)
            old_progress = state_path.parent / PROGRESS_FILENAME
            if old_progress.exists():
                suffix = old_batch_id or str(int(time.time()))
                rotated = old_progress.with_name(f"{PROGRESS_FILENAME}.{suffix}")
                try:
                    old_progress.replace(rotated)
                    print(f"[全新] 旧进度事件流已轮转: {rotated}")
                except OSError:
                    pass
            print(f"[全新] 初始化批次 {batch_id}（--force 或首次运行）")

        # 孤儿回收必须先于任何状态重置：否则被 --ids/--retry-failed 改写成
        # pending 的 running 残留会逃过回收，导致孤儿与新派进程双写产物目录
        reap_orphans(state, progress)

        selected: Optional[set] = None
        if args.ids:
            wanted = [item.strip() for item in args.ids.split(",") if item.strip()]
            all_ids = {case.id for case in cfg.cases}
            unknown = [item for item in wanted if item not in all_ids]
            if unknown:
                raise BatchError(f"--ids 含未知用例: {unknown}（清单共 {len(all_ids)} 例）")
            selected = set(wanted)
            print(f"[子集] 本次只复跑指定用例: {sorted(selected)}")

        if args.retry_failed:
            count = 0
            for st in state["cases"].values():
                if st.get("status") == "failed":
                    st.update(status="pending", attempts=0, error=None)
                    count += 1
            print(f"[重试] 重置 {count} 个 failed 用例（attempts 清零）")

        if selected:
            for case_id in selected:
                state["cases"][case_id].update(
                    status="pending", attempts=0, error=None,
                    summary=None, elapsed_sec=None)

        for st in state["cases"].values():
            if st.get("status") == "interrupted":
                st["status"] = "pending"

        for case_id, error in prepare_repos(cfg):
            state["cases"][case_id].update(status="failed", attempts=0,
                                           error=f"preflight: {error}")

        pending_now = {cid for cid, st in state["cases"].items()
                       if st.get("status") == "pending"}
        phase2_cases = [case for case in cfg.cases if case.id in pending_now]
        for case_id, error in check_cases_phase2(BatchCfg(
                path=cfg.path, schema_version=cfg.schema_version,
                global_cfg=cfg.global_cfg, cases=phase2_cases)):
            state["cases"][case_id].update(status="failed", attempts=0,
                                           error=f"preflight: {error}")

        for case in cfg.cases:
            st = state["cases"][case.id]
            if st.get("status") != "pending":
                continue
            if selected and case.id in selected:
                continue
            analysis_path = Path(case.result_dir) / "analysis.json"
            if not analysis_path.is_file():
                continue
            ok, _err = validate_analysis_file(validate_script, analysis_path,
                                              require_affected_scope=True)
            if not ok:
                # 半成品 analysis.json：保留 pending，本轮重新分派完成分析
                continue
            if not (Path(case.result_dir) / AFFECTED_SCOPE_FILENAME).is_file():
                # 断点自愈：analysis 有效但影响范围产物缺失（会话中断等），
                # 用 Skill 命令补全而不是整例重跑。
                repaired, detail = try_repair_affected_scope(
                    orchestrator_script, analysis_path,
                    cleanup_after=(not args.keep_worktrees and g.mode != "analysis-test"))
                if repaired:
                    progress.emit("case_repaired",
                                  {"case": case.id, "artifact": AFFECTED_SCOPE_FILENAME,
                                   "counts": event_counts(state)})
                    print(f"[自愈] {case.id}: 已补全 {AFFECTED_SCOPE_FILENAME}")
                    if detail:
                        print(f"[自愈] {case.id}: 警告: {detail}")
                else:
                    progress.emit("repair_failed",
                                  {"case": case.id, "error": detail,
                                   "counts": event_counts(state)})
                    print(f"[自愈] {case.id} 补全失败（{detail}）；保留 pending 重新分析")
                    continue
            st["status"] = "already_done"
            try:
                st["summary"] = extract_analysis_info(analysis_path)["summary"]
            except (OSError, json.JSONDecodeError):
                pass

        if g.mode == "analysis-test":
            for case in cfg.cases:
                st = state["cases"][case.id]
                if st.get("status") != "pending":
                    continue
                authorized = (case.env_authorized
                              if case.env_authorized is not None else g.env_authorized)
                if not authorized:
                    st["status"] = "skipped"
                    st["error"] = ("env_not_authorized（analysis-test 模式需要"
                                   "用例级或全局 env_authorized: true）")
                    progress.emit("case_skipped", {"case": case.id,
                                                   "counts": event_counts(state)})

        check_disk_estimate(cfg)

        order = list(cfg.cases)
        if args.group_by_repo:
            order = sorted(order, key=lambda case: case.repo)
        pending = [case for case in order
                   if state["cases"][case.id].get("status") == "pending"
                   and (selected is None or case.id in selected)]
        if args.limit and args.limit > 0:
            pending = pending[:args.limit]
            print(f"[限流] --limit {args.limit}：本次最多分派 {len(pending)} 例")

        state["finished_at"] = None
        state["abort_reason"] = None
        state["paused_reason"] = None
        state["counts"] = compute_counts(state)
        atomic_write_json(state_path, state)

        report = build_report_config(args, g)
        runner = Runner(cfg, state, state_path, progress, pending,
                        opencode_bin=args.opencode_bin,
                        validate_script=validate_script,
                        keep_worktrees=args.keep_worktrees,
                        report=report,
                        test_finalize_script=test_finalize_script,
                        orchestrator_script=orchestrator_script)
        return runner.run()
    finally:
        lock.release()


def cmd_dry_run(args: argparse.Namespace) -> int:
    cfg = load_manifest(Path(args.manifest))
    apply_cli_overrides(cfg, args)
    g = cfg.global_cfg

    print(f"=== 清单 ===\n{cfg.path}\n用例 {len(cfg.cases)} 个 · 模式 {g.mode} · "
          f"并发 {g.concurrency} · 超时 {g.timeout_sec}s · 重试 {g.retries} · "
          f"模型 {g.model or '默认'}")
    print(f"output_base: {g.output_base}\nrepo_cache: {g.repo_cache}")

    try:
        skill_dir = resolve_skill_dir(g.skill_dir)
        print(f"skill_dir: {skill_dir}")
    except BatchError as exc:
        print(f"[预检失败] {exc}")
        return 1

    url_cases = [case for case in cfg.cases if case.repo_is_url]
    local_cases = [case for case in cfg.cases if not case.repo_is_url]
    local_missing = [case for case in local_cases if not Path(case.repo).is_dir()]
    print(f"\n=== 仓库准备计划（dry-run 不执行 clone/fetch） ===")
    print(f"本地仓库用例: {len(local_cases)}（缺失 {len(local_missing)}） · "
          f"URL 用例: {len(url_cases)}（将克隆到 repo_cache）")
    for case in local_missing[:5]:
        print(f"  [缺失] {case.id}: {case.repo}")
    if len(local_missing) > 5:
        print(f"  ... 共 {len(local_missing)} 个")
    urls = sorted({case.repo for case in url_cases})
    for url in urls[:10]:
        print(f"  [克隆计划] {url} -> {g.repo_cache}/{repo_url_name(url)}")
    if len(urls) > 10:
        print(f"  ... 共 {len(urls)} 个仓库")

    missing_commits: List[str] = []
    checked: Dict[str, bool] = {}
    for case in local_cases:
        if not Path(case.repo).is_dir():
            continue
        key = f"{case.repo}|{case.base_commit}"
        if key not in checked:
            checked[key] = _commit_exists(Path(case.repo), case.base_commit)
        if not checked[key]:
            missing_commits.append(case.id)
    if missing_commits:
        print(f"[预检失败] base_commit 不存在（本地仓库可校验部分）: {missing_commits[:10]}"
              f"{' ...' if len(missing_commits) > 10 else ''}")
    else:
        print("[预检] base_commit 校验通过（本地仓库部分；URL 仓库克隆后才能校验）")

    try:
        run_dependency_check(skill_dir)
    except BatchError as exc:
        print(f"[预检失败] {exc}")
        return 1
    try:
        _check_opencode_bin(args.opencode_bin)
        check_model_available(args.opencode_bin, g.model)
    except BatchError as exc:
        print(f"[预检失败] {exc}")
        return 1
    try:
        check_disk_estimate(cfg)
    except BatchError as exc:
        print(f"[预检失败] {exc}")
        return 1

    already_done = 0
    for case in cfg.cases:
        if Path(case.result_dir, "analysis.json").is_file():
            already_done += 1
    print(f"\n=== 计划 ===\n已有 analysis.json 的用例: {already_done}"
          "（正式运行时需 analysis.json 通过 --require-affected-scope 校验且 "
          f"{AFFECTED_SCOPE_FILENAME} 存在才跳过）")
    if g.mode == "analysis-test":
        print(f"analysis-test 完成口径: 另需 {TEST_RESULT_SUBDIR}/test-summary.json "
              "通过 finalize_test_report.py 校验且 TEST_REPORT.md / COVERAGE_REPORT.md 存在")

    order = list(cfg.cases)
    if args.group_by_repo:
        order = sorted(order, key=lambda case: case.repo)
    runnable = order
    if args.ids:
        wanted = {item.strip() for item in args.ids.split(",") if item.strip()}
        runnable = [case for case in order if case.id in wanted]
    if args.limit and args.limit > 0:
        runnable = runnable[:args.limit]
    preview = " ".join(case.id for case in runnable[:10])
    print(f"计划分派 {len(runnable)} 例，顺序（前 10）: {preview}"
          f"{' ...' if len(runnable) > 10 else ''}")

    if runnable:
        first = runnable[0]
        template_path = Path(g.prompt_template) if g.prompt_template else DEFAULT_TEMPLATE
        template_text = template_path.read_text(encoding="utf-8")
        prompt = build_prompt(template_text, first, Path(first.result_dir),
                              g.mode, args.keep_worktrees)
        if str(first.result_dir) not in prompt:
            print("[预检失败] 渲染后的 prompt 未包含 output_dir（调度不变式）")
            return 1
        workdir = Path(first.result_dir) / "workdir"
        cmd = build_cmd(args.opencode_bin, cfg, first, prompt, workdir)
        print(f"\n=== 首例命令示例 ===\n{shlex.join(cmd)}")
    print("\n[dry-run] 未执行任何 clone/子进程/状态写入。")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args)
    if not state_path.exists():
        raise BatchError(f"未找到批次状态文件 {state_path}（批次可能尚未启动；"
                         "也可用 --state 指定路径）")
    if not args.follow:
        state = load_state_file(state_path)
        print(render_progress_snapshot(state, state_path))
        return 0
    try:
        while True:
            state = load_state_file(state_path)
            if sys.stdout.isatty():
                print("\x1b[2J\x1b[H", end="")
            print(render_progress_snapshot(state, state_path))
            if state.get("finished_at"):
                print("\n批次本轮已结束，--follow 退出（Ctrl+C 可随时退出，不影响批次）")
                return 0
            time.sleep(FOLLOW_REFRESH_SEC)
    except KeyboardInterrupt:
        return 0


def cmd_report_only(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args)
    state = load_state_file(state_path)
    cfg: Optional[BatchCfg] = None
    manifest = args.manifest or state.get("manifest")
    if manifest and Path(manifest).is_file():
        try:
            cfg = load_manifest(Path(manifest))
        except BatchError as exc:
            print(f"[警告] 无法加载清单（指标将不可用）: {exc}")
    else:
        print("[警告] 未找到清单文件，跳过 expected 指标")
    summary_path = state_path.parent / SUMMARY_FILENAME
    report_path = (Path(args.output).expanduser().absolute() if args.output
                   else state_path.parent / REPORT_FILENAME)
    aggregate(state, cfg, summary_path, report_path)
    counts = compute_counts(state)
    print(f"batch_id: {state.get('batch_id')} · done {counts['done']} · "
          f"failed {counts['failed']} · skipped {counts['skipped']} · "
          f"pending {counts['pending']}")
    print(f"汇总: {summary_path}\n报告: {report_path}")
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    state_path = resolve_state_path(args)
    state = load_state_file(state_path)
    if args.cleanup != state.get("batch_id"):
        raise BatchError(f"batch_id 不匹配：状态文件为 {state.get('batch_id')!r}，"
                         f"传入 {args.cleanup!r}")
    counts = compute_counts(state)
    if counts["running"]:
        raise BatchError("批次仍在运行；请先 kill -TERM <runner_pid> 停止后再清理")
    freed = 0
    cleaned = 0
    for case_id, st in state["cases"].items():
        result_dir = st.get("result_dir")
        if not result_dir:
            continue
        result_dir = Path(result_dir)
        if args.purge:
            if result_dir.exists():
                freed += dir_size_bytes(result_dir)
                shutil.rmtree(result_dir, ignore_errors=True)
                cleaned += 1
        else:
            for sub in ("_worktrees", "workdir"):
                target = result_dir / sub
                if target.exists():
                    freed += dir_size_bytes(target)
                    shutil.rmtree(target, ignore_errors=True)
                    cleaned += 1
    action = "整目录（--purge，含 analysis.json）" if args.purge else "worktree/workdir"
    print(f"批次 {state.get('batch_id')}：已清理 {cleaned} 个用例的 {action}，"
          f"释放 {human_bytes(freed)}")
    return 0


# ---------------------------------------------------------------------------
# 参数解析与入口
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="batch_runner.py",
        description="PCAT 自动批量扫描调度器（无人值守批量补丁兼容性分析）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  batch_runner.py --manifest batch_manifest.yaml --dry-run\n"
            "  batch_runner.py --manifest batch_manifest.yaml --resume\n"
            "  batch_runner.py --progress --follow --manifest batch_manifest.yaml\n"
            "  batch_runner.py --manifest batch_manifest.yaml --ids PCAT-P001,PCAT-P005\n"
            "  batch_runner.py --report-only --manifest batch_manifest.yaml\n"
            "  batch_runner.py --cleanup <batch_id> --manifest batch_manifest.yaml\n"
            "\n"
            "退出码: 0 正常(含子集运行) · 1 用法/预检错误 · 2 存在失败用例 ·\n"
            "        3 熔断中止 · 4 磁盘低水位暂停 · 130 被信号终止"
        ),
    )
    parser.add_argument("--manifest", help="批量清单 batch_manifest.yaml 路径")
    parser.add_argument("--concurrency", type=int,
                        help="覆盖 global.concurrency（硬上限 16）")
    parser.add_argument("--mode", choices=["analysis", "test", "analysis-test"],
                        help="覆盖 global.mode")
    parser.add_argument("--resume", action="store_true",
                        help="显式续跑（状态文件存在时默认即为幂等续跑）")
    parser.add_argument("--force", action="store_true",
                        help="忽略已有状态与 already_done，全部重跑（生成新 batch_id）")
    parser.add_argument("--retry-failed", action="store_true",
                        help="将 failed 用例重置为 pending（attempts 清零）后重跑")
    parser.add_argument("--limit", type=int, help="本次最多分派 N 个用例（调试）")
    parser.add_argument("--ids", help="只跑指定用例（逗号分隔，子集复跑，忽略 already_done）")
    parser.add_argument("--group-by-repo", action="store_true",
                        help="同仓库用例相邻分派（利用文件系统缓存暖性）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印计划与预检结果，不执行 clone/子进程/状态写入")
    parser.add_argument("--keep-worktrees", action="store_true",
                        help="保留每用例 _worktrees（analysis 模式默认清理）")
    parser.add_argument("--state", help="覆盖状态文件路径（默认 <manifest目录>/batch_state.json）")
    parser.add_argument("--opencode-bin", default="opencode",
                        help="opencode 可执行文件（默认 PATH 中的 opencode；测试可用 mock 替换）")
    parser.add_argument("--progress", action="store_true",
                        help="只读渲染当前进度一屏快照后退出")
    parser.add_argument("--follow", action="store_true",
                        help="配合 --progress 持续跟随（Ctrl+C 不影响批次）")
    parser.add_argument("--report-only", action="store_true",
                        help="由 batch_state.json 重新生成汇总与报告")
    parser.add_argument("--output", help="--report-only 的报告输出路径")
    parser.add_argument("--cleanup", metavar="BATCH_ID",
                        help="批次统一清理入口（清理 _worktrees/workdir；配合 --purge 删除整目录）")
    parser.add_argument("--purge", action="store_true",
                        help="配合 --cleanup：删除整个用例产物目录（含 analysis.json，慎用）")
    parser.add_argument("--report-server", help="模式 E：OpenCode server 地址（如 http://localhost:4096）")
    parser.add_argument("--report-session", help="模式 E：注入目标会话 id（启动批次的 Agent 会话）")
    parser.add_argument("--report-milestone",
                        help="模式 E 节流：按进度里程碑注入（如 10 或 10%%，默认 10）")
    parser.add_argument("--report-every", help="模式 E 节流：按时间注入（如 30m）")
    parser.add_argument("--report-username", help="模式 E basic auth 用户名（默认 opencode）")
    parser.add_argument("--report-password", help="模式 E basic auth 密码（默认 OPENCODE_SERVER_PASSWORD）")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.follow and not args.progress:
            raise BatchError("--follow 需要与 --progress 一起使用")
        if args.purge and not args.cleanup:
            raise BatchError("--purge 需要与 --cleanup 一起使用")
        if args.progress or args.report_only or args.cleanup:
            if not args.manifest and not args.state:
                raise BatchError("该模式需要 --manifest 或 --state")
        elif not args.manifest:
            raise BatchError("需要 --manifest（除非使用 --progress/--report-only/--cleanup 且提供 --state）")

        if args.progress:
            return cmd_progress(args)
        if args.cleanup:
            return cmd_cleanup(args)
        if args.report_only:
            return cmd_report_only(args)
        if args.dry_run:
            return cmd_dry_run(args)
        return cmd_run(args)
    except BatchError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已中断", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
