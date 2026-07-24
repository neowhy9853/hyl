from __future__ import annotations

from dataclasses import dataclass
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True, slots=True)
class CtagsBackend:
    executable: str | None
    source: str
    version: str
    compatible: bool


def platform_key() -> str:
    system = platform.system().lower()
    system = {"darwin": "macos"}.get(system, system)
    machine = platform.machine().lower()
    machine = {"amd64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    return f"{system}-{machine}"


def bundled_ctags(skill_dir: Path) -> Path:
    name = "ctags.exe" if os.name == "nt" else "ctags"
    return skill_dir / "bin" / platform_key() / name


def default_cache_base() -> Path:
    override = os.environ.get("PATCH_INTENT_CACHE")
    if override:
        return Path(override).expanduser().resolve()
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".cache"
    return (base / "patch-intent-analysis").resolve()


def manifest_version(skill_dir: Path) -> str | None:
    path = skill_dir / "manifests" / "universal-ctags.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = data.get("version")
    return str(value) if value else None


def managed_ctags(
    skill_dir: Path,
    *,
    cache_base: Path | None = None,
    version: str | None = None,
    platform: str | None = None,
) -> Path:
    selected_version = version or manifest_version(skill_dir) or "unknown"
    selected_platform = platform or platform_key()
    name = "ctags.exe" if os.name == "nt" else "ctags"
    return (
        (cache_base or default_cache_base())
        / "universal-ctags"
        / selected_version
        / selected_platform
        / name
    )


def command_version(command: list[str], *, timeout: float = 5.0) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else ""


def find_ctags(skill_dir: Path) -> CtagsBackend:
    candidates: list[tuple[str, str]] = []
    override = os.environ.get("PATCH_INTENT_CTAGS")
    if override:
        candidates.append((str(Path(override).expanduser()), "environment"))
    managed = managed_ctags(skill_dir)
    if managed.is_file() and os.access(managed, os.X_OK):
        candidates.append((str(managed), "managed-cache"))
    system = shutil.which("ctags")
    if system:
        candidates.append((system, "system"))
    bundled = bundled_ctags(skill_dir)
    if bundled.is_file() and os.access(bundled, os.X_OK):
        candidates.append((str(bundled), "bundled"))

    incompatible: CtagsBackend | None = None
    for executable, source in candidates:
        version = command_version([executable, "--version"])
        backend = CtagsBackend(
            executable=executable,
            source=source,
            version=version,
            compatible="Universal Ctags" in version,
        )
        if backend.compatible:
            return backend
        if incompatible is None:
            incompatible = backend
    return incompatible or CtagsBackend(executable=None, source="missing", version="", compatible=False)
