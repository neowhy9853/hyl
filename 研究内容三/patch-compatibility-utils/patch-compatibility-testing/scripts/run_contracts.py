#!/usr/bin/env python3
"""Execute type-aware before/after compatibility contract probes.

The runner supports every compatibility type in compatibility_types.py. Simple
CLI findings can reuse reviewed BINARY inputs. Types whose evidence cannot be
inferred safely require an explicit ``contract_probe`` in test-entries.json;
missing probes are recorded as precise SKIP results, never as unsupported.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from compatibility_types import (
    SUPPORTED_COMPARISONS,
    get_type_support,
    validate_registry,
)


@dataclass
class Observation:
    command: str
    cwd: str
    returncode: int
    stdout: str
    stderr: str


def load_json(path: Path | None) -> Any:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_findings(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, dict):
        payload = payload.get("findings", [])
    if not isinstance(payload, list):
        raise ValueError("findings JSON must be a list or contain findings[]")
    findings = [item for item in payload if isinstance(item, dict)]
    for finding in findings:
        get_type_support(str(finding.get("compatibility_type") or ""))
    return findings


def load_entries(path: Path | None) -> dict[str, list[dict[str, Any]]]:
    if path is None:
        return {}
    payload = load_json(path)
    if isinstance(payload, dict):
        payload = payload.get("entries", [])
    if not isinstance(payload, list):
        raise ValueError("entries JSON must be a list or contain entries[]")
    by_finding: dict[str, list[dict[str, Any]]] = {}
    for entry in payload:
        if isinstance(entry, dict):
            by_finding.setdefault(str(entry.get("finding_id") or "UNKNOWN"), []).append(entry)
    return by_finding


def find_matched_binary(before_dir: Path, after_dir: Path) -> tuple[Path | None, Path | None]:
    if not before_dir.is_dir() or not after_dir.is_dir():
        return None, None
    for after in sorted(after_dir.iterdir()):
        before = before_dir / after.name
        if after.is_file() and before.is_file() and after.stat().st_mode & 0o111 and before.stat().st_mode & 0o111:
            return before.resolve(), after.resolve()
    return None, None


def expand_command(
    command: str,
    *,
    version_dir: Path,
    before_dir: Path,
    after_dir: Path,
    before_bin: Path | None,
    after_bin: Path | None,
    selected_bin: Path | None,
) -> str:
    replacements = {
        "{VERSION_DIR}": shlex.quote(str(version_dir)),
        "{BEFORE_DIR}": shlex.quote(str(before_dir)),
        "{AFTER_DIR}": shlex.quote(str(after_dir)),
        "{BEFORE_BIN}": shlex.quote(str(before_bin)) if before_bin else "",
        "{AFTER_BIN}": shlex.quote(str(after_bin)) if after_bin else "",
    }
    expanded = command
    for marker, value in replacements.items():
        expanded = expanded.replace(marker, value)
    if "BINARY" in expanded:
        if selected_bin is None:
            raise ValueError("probe uses BINARY but no matched before/after executable exists")
        expanded = expanded.replace("BINARY", shlex.quote(str(selected_bin)))
    return expanded


def resolve_cwd(value: str | None, version_dir: Path) -> Path:
    if not value or value in {"version_dir", "before_dir", "after_dir"}:
        return version_dir
    path = Path(value)
    if not path.is_absolute():
        path = version_dir / path
    return path.resolve()


def execute(command: str, cwd: Path, timeout: int) -> Observation:
    if not cwd.is_dir():
        raise ValueError(f"probe cwd does not exist: {cwd}")
    try:
        completed = subprocess.run(
            ["bash", "-o", "pipefail", "-c", command],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return Observation(command, str(cwd), completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return Observation(command, str(cwd), 124, stdout, stderr + "\nPCA_PROBE_TIMEOUT")


def concise(observation: Observation) -> str:
    stdout = observation.stdout.strip().replace("\n", "\\n")[:500]
    stderr = observation.stderr.strip().replace("\n", "\\n")[:500]
    return f"rc={observation.returncode}; stdout={stdout!r}; stderr={stderr!r}"


def numeric_payload(observation: Observation) -> dict[str, float]:
    payload = json.loads(observation.stdout)
    if not isinstance(payload, dict) or not payload:
        raise ValueError("numeric_tolerance probe stdout must be a non-empty JSON object")
    result: dict[str, float] = {}
    for key, value in payload.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"numeric_tolerance field {key!r} is not numeric")
        result[str(key)] = float(value)
    return result


def compare(
    comparison: str,
    before: Observation,
    after: Observation,
    tolerance_percent: float,
) -> tuple[str, str]:
    if comparison == "success":
        if before.returncode != 0:
            return "SKIP", "baseline probe failed; the downstream/ABI harness is not valid: " + concise(before)
        if after.returncode == 0:
            return "PASS", "probe succeeds against both versions"
        return "BREACH", "probe succeeded before and failed after: " + concise(after)
    if comparison == "acceptance":
        before_accepts = before.returncode == 0
        after_accepts = after.returncode == 0
        if before_accepts == after_accepts:
            return "PASS", f"acceptance stable: accepted={before_accepts}"
        return "BREACH", f"acceptance changed: before={before_accepts}, after={after_accepts}"
    if comparison == "exit_code":
        if before.returncode == after.returncode:
            return "PASS", f"return/exit status stable: {before.returncode}"
        return "BREACH", f"return/exit status changed: {before.returncode} -> {after.returncode}"
    if comparison == "error":
        before_error = (before.returncode, before.stderr, before.stdout)
        after_error = (after.returncode, after.stderr, after.stdout)
        if before_error == after_error:
            return "PASS", "error code/type/message observation is identical"
        return "BREACH", "error observation changed; before " + concise(before) + "; after " + concise(after)
    if comparison == "exact":
        before_value = (before.returncode, before.stdout, before.stderr)
        after_value = (after.returncode, after.stdout, after.stderr)
        if before_value == after_value:
            return "PASS", "canonical observation is identical"
        return "BREACH", "canonical observation changed; before " + concise(before) + "; after " + concise(after)
    if comparison == "set_no_additions":
        before_lines = {line for line in before.stdout.splitlines() if line}
        after_lines = {line for line in after.stdout.splitlines() if line}
        additions = sorted(after_lines - before_lines)
        if before.returncode == after.returncode and not additions:
            return "PASS", "no new manifest entries"
        return "BREACH", f"new manifest entries={additions}; rc {before.returncode}->{after.returncode}"
    if comparison == "numeric_tolerance":
        if before.returncode != 0 or after.returncode != 0:
            return "BREACH", "numeric probe command failed; before " + concise(before) + "; after " + concise(after)
        try:
            old = numeric_payload(before)
            new = numeric_payload(after)
        except (ValueError, json.JSONDecodeError) as exc:
            return "SKIP", str(exc)
        if old.keys() != new.keys():
            return "BREACH", f"measurement keys changed: {sorted(old)} -> {sorted(new)}"
        breaches = []
        for key in old:
            if old[key] == new[key]:
                continue
            if old[key] == 0:
                delta = math.inf
            else:
                delta = abs(new[key] - old[key]) * 100.0 / abs(old[key])
            if delta > tolerance_percent:
                breaches.append(f"{key}: {old[key]}->{new[key]} ({delta:.2f}%)")
        if breaches:
            return "BREACH", f"outside {tolerance_percent:.2f}% tolerance: " + "; ".join(breaches)
        return "PASS", f"all numeric observations within {tolerance_percent:.2f}% tolerance"
    raise ValueError(f"unsupported comparison {comparison!r}")


def explicit_probes(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for entry in entries:
        value = entry.get("contract_probe")
        if isinstance(value, dict):
            probes.append(value)
        elif isinstance(value, list):
            probes.extend(item for item in value if isinstance(item, dict))
    return probes


def simple_input_probes(
    inputs_payload: Any,
    finding_id: str,
    comparison: str,
) -> list[dict[str, Any]]:
    if not isinstance(inputs_payload, dict):
        return []
    probes: list[dict[str, Any]] = []
    for finding in inputs_payload.get("findings", []):
        if not isinstance(finding, dict) or str(finding.get("id")) != finding_id:
            continue
        for items in finding.get("dimensions", {}).values():
            for item in items:
                if not isinstance(item, dict):
                    continue
                command = str(item.get("command") or "").strip()
                if not command or "BINARY" not in command:
                    continue
                probes.append(
                    {
                        "probe_id": str(item.get("input_id") or f"input-{len(probes) + 1}"),
                        "command": command,
                        "comparison": comparison,
                    }
                )
                if len(probes) >= 8:
                    return probes
    return probes


def write_result(handle, result: dict[str, Any]) -> None:
    result["timestamp"] = dt.datetime.now(dt.timezone.utc).isoformat()
    handle.write(json.dumps(result, ensure_ascii=False) + "\n")
    handle.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PCA compatibility contracts for all supported types")
    parser.add_argument("--findings", required=True)
    parser.add_argument("--before-dir", required=True)
    parser.add_argument("--after-dir", required=True)
    parser.add_argument("--test-inputs")
    parser.add_argument("--entries")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    registry_errors = validate_registry()
    if registry_errors:
        parser.error("invalid compatibility type registry: " + "; ".join(registry_errors))

    findings_path = Path(args.findings).resolve()
    before_dir = Path(args.before_dir).resolve()
    after_dir = Path(args.after_dir).resolve()
    output_dir = Path(args.output).resolve()
    entries_path = Path(args.entries).resolve() if args.entries else None
    inputs_path = Path(args.test_inputs).resolve() if args.test_inputs else None
    for optional in (entries_path, inputs_path):
        if optional is not None and not optional.is_file():
            parser.error(f"input file not found: {optional}")

    try:
        findings = load_findings(findings_path)
        entries = load_entries(entries_path)
        inputs_payload = load_json(inputs_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "contracts.jsonl"
    before_bin, after_bin = find_matched_binary(before_dir, after_dir)
    counts = {"PASS": 0, "BREACH": 0, "SKIP": 0}

    with results_path.open("w", encoding="utf-8") as handle:
        for finding in findings:
            finding_id = str(finding.get("id") or "UNKNOWN")
            compatibility_type = str(finding.get("compatibility_type") or "")
            support = get_type_support(compatibility_type)
            probes = explicit_probes(entries.get(finding_id, []))
            if not probes and not support["requires_explicit_probe"]:
                probes = simple_input_probes(inputs_payload, finding_id, support["comparison"])

            if not probes:
                result = {
                    "finding_id": finding_id,
                    "compatibility_type": compatibility_type,
                    "contract_id": f"CT-{finding_id}-{support['contract_id']}",
                    "status": "SKIP",
                    "detail": (
                        "Missing finding-specific contract_probe. Required observation: "
                        + str(support["observation"])
                    ),
                }
                write_result(handle, result)
                counts["SKIP"] += 1
                continue

            for index, probe in enumerate(probes, 1):
                comparison = str(probe.get("comparison") or support["comparison"])
                contract_id = f"CT-{finding_id}-{support['contract_id']}-{index}"
                if comparison not in SUPPORTED_COMPARISONS:
                    write_result(
                        handle,
                        {
                            "finding_id": finding_id,
                            "compatibility_type": compatibility_type,
                            "contract_id": contract_id,
                            "status": "SKIP",
                            "detail": f"Unknown comparison {comparison!r}",
                        },
                    )
                    counts["SKIP"] += 1
                    continue
                before_template = str(probe.get("before_command") or probe.get("command") or "").strip()
                after_template = str(probe.get("after_command") or probe.get("command") or "").strip()
                try:
                    if not before_template or not after_template:
                        raise ValueError("contract_probe requires command or both before_command/after_command")
                    before_command = expand_command(
                        before_template,
                        version_dir=before_dir,
                        before_dir=before_dir,
                        after_dir=after_dir,
                        before_bin=before_bin,
                        after_bin=after_bin,
                        selected_bin=before_bin,
                    )
                    after_command = expand_command(
                        after_template,
                        version_dir=after_dir,
                        before_dir=before_dir,
                        after_dir=after_dir,
                        before_bin=before_bin,
                        after_bin=after_bin,
                        selected_bin=after_bin,
                    )
                    before_cwd = resolve_cwd(probe.get("before_cwd") or probe.get("cwd"), before_dir)
                    after_cwd = resolve_cwd(probe.get("after_cwd") or probe.get("cwd"), after_dir)
                    timeout = int(probe.get("timeout_seconds") or args.timeout)
                    tolerance = float(
                        probe.get("tolerance_percent")
                        or support.get("default_tolerance_percent")
                        or 0.0
                    )
                    before_observation = execute(before_command, before_cwd, timeout)
                    after_observation = execute(after_command, after_cwd, timeout)
                    status, detail = compare(comparison, before_observation, after_observation, tolerance)
                    result = {
                        "finding_id": finding_id,
                        "compatibility_type": compatibility_type,
                        "contract_id": contract_id,
                        "probe_id": str(probe.get("probe_id") or index),
                        "comparison": comparison,
                        "status": status,
                        "detail": detail,
                        "before": concise(before_observation),
                        "after": concise(after_observation),
                    }
                except (OSError, ValueError) as exc:
                    result = {
                        "finding_id": finding_id,
                        "compatibility_type": compatibility_type,
                        "contract_id": contract_id,
                        "status": "SKIP",
                        "detail": f"Probe could not run: {exc}",
                    }
                write_result(handle, result)
                counts[result["status"]] += 1

    total = sum(counts.values())
    if counts["BREACH"]:
        summary_status = "CONTRACT_BREACH_DETECTED"
    elif counts["PASS"]:
        summary_status = "ALL_EXECUTED_CONTRACTS_PASS"
    else:
        summary_status = "NOT_EXECUTED"
    summary = {
        "total": total,
        "passed": counts["PASS"],
        "breached": counts["BREACH"],
        "skipped": counts["SKIP"],
        "status": summary_status,
        "supported_types": len({str(item.get("compatibility_type")) for item in findings}),
    }
    (output_dir / "contract_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    recorded_results = [
        json.loads(line)
        for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    verification = {
        "summary": summary,
        "results": recorded_results,
        "breaches": [item for item in recorded_results if item.get("status") == "BREACH"],
    }
    (output_dir / "contract_verification.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    print(f"Results: {results_path}")
    return 1 if counts["BREACH"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
