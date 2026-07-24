#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

from analysis_core.backend import default_cache_base, managed_ctags, platform_key
from common import SKILL_DIR, emit


MANIFEST_PATH = SKILL_DIR / "manifests" / "universal-ctags.json"
MAX_DOWNLOAD_BYTES = 32 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a pinned Universal Ctags binary.")
    parser.add_argument("--cache-dir", type=Path, help="Override the patch-intent-analysis cache directory.")
    parser.add_argument("--force", action="store_true", help="Replace an existing managed binary.")
    return parser.parse_args()


def fail(code: str, message: str) -> None:
    emit({"ok": False, "error": {"code": code, "message": message}}, stream=sys.stderr)
    raise SystemExit(2)


def load_manifest() -> dict[str, object]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("version"), str) or not isinstance(data.get("platforms"), dict):
        raise RuntimeError("invalid Universal Ctags manifest")
    return data


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def download(url: str, destination: Path) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise RuntimeError("manifest download URL must use https://github.com")
    request = urllib.request.Request(url, headers={"User-Agent": "patch-intent-analysis-installer/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if urllib.parse.urlparse(response.geturl()).scheme != "https":
            raise RuntimeError("download redirected to a non-HTTPS URL")
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_DOWNLOAD_BYTES:
            raise RuntimeError("download exceeds size limit")
        total = 0
        with destination.open("wb") as output:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > MAX_DOWNLOAD_BYTES:
                    raise RuntimeError("download exceeds size limit")
                output.write(block)


def extract_member(bundle: tarfile.TarFile, member_name: str, destination: Path) -> None:
    try:
        member = bundle.getmember(member_name)
    except KeyError as error:
        raise RuntimeError(f"archive member not found: {member_name}") from error
    if not member.isfile():
        raise RuntimeError(f"archive member is not a regular file: {member_name}")
    source = bundle.extractfile(member)
    if source is None:
        raise RuntimeError(f"could not extract archive member: {member_name}")
    with source, destination.open("wb") as output:
        shutil.copyfileobj(source, output)


def verify(binary: Path) -> str:
    binary.chmod(0o755)
    try:
        version_result = subprocess.run(
            [str(binary), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError(f"ctags executable verification failed: {error}") from error
    version = version_result.stdout.strip().splitlines()[0] if version_result.stdout.strip() else ""
    if "Universal Ctags" not in version:
        raise RuntimeError("downloaded executable is not Universal Ctags")

    with tempfile.TemporaryDirectory(prefix="ctags-probe-") as raw:
        sample = Path(raw) / "probe.py"
        sample.write_text("def probe():\n    return True\n", encoding="utf-8")
        probe = subprocess.run(
            [str(binary), "--output-format=json", "--fields=+neK", "--sort=no", str(sample)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if probe.returncode not in {0, 1} or '"_type": "tag"' not in probe.stdout:
            raise RuntimeError("downloaded ctags lacks required JSON output")
    return version


def main() -> None:
    args = parse_args()
    lock: Path | None = None
    try:
        manifest = load_manifest()
        key = platform_key()
        platforms = manifest["platforms"]
        assert isinstance(platforms, dict)
        item = platforms.get(key)
        if not isinstance(item, dict):
            fail("E_UNSUPPORTED_PLATFORM", f"no managed Universal Ctags build for {key}")
        version = str(manifest["version"])
        cache_base = args.cache_dir.expanduser().resolve() if args.cache_dir else default_cache_base()
        target = managed_ctags(SKILL_DIR, cache_base=cache_base, version=version, platform=key)
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not args.force:
            installed_version = verify(target)
            emit(
                {
                    "ok": True,
                    "status": "already-installed",
                    "platform": key,
                    "version": version,
                    "ctags_version": installed_version,
                    "path": str(target),
                }
            )
            return

        lock_path = target.parent / ".install-lock"
        try:
            lock_path.mkdir()
        except FileExistsError:
            fail("E_INSTALL_LOCKED", f"another installation is using {lock_path}")
        lock = lock_path

        with tempfile.TemporaryDirectory(prefix="ctags-install-", dir=target.parent) as raw:
            temporary = Path(raw)
            archive = temporary / "ctags.tar.xz"
            staged_binary = temporary / "ctags"
            staged_license = temporary / "COPYING"
            download(str(item["url"]), archive)
            actual = digest(archive)
            expected = str(item["sha256"])
            if actual != expected:
                raise RuntimeError(f"checksum mismatch: expected {expected}, got {actual}")
            with tarfile.open(archive, mode="r:xz") as bundle:
                extract_member(bundle, str(item["binary"]), staged_binary)
                extract_member(bundle, str(item["license"]), staged_license)
            installed_version = verify(staged_binary)
            os.replace(staged_binary, target)
            os.replace(staged_license, target.parent / "COPYING")

        emit(
            {
                "ok": True,
                "status": "installed",
                "platform": key,
                "version": version,
                "ctags_version": installed_version,
                "path": str(target),
                "sha256": expected,
            }
        )
    except (OSError, ValueError, KeyError, RuntimeError, tarfile.TarError) as error:
        fail("E_INSTALL_FAILED", str(error))
    finally:
        if lock is not None:
            try:
                lock.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    main()
