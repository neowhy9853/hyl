#!/usr/bin/env python3
"""
Input Dimension Matrix Generator (Phase 3 enhancement)

Generates type-specific contract axes plus diverse runtime dimensions for each
compatibility finding.
Outputs a structured JSON that input_matrix.sh uses for execution.

Usage:
    python3 input_dimensions.py --findings analysis.json \
        --entries test-entry-work/test-entries.json --output test_inputs.json
    python3 input_dimensions.py --demo  # Show example output
"""

import json
import argparse
import sys
from pathlib import Path

from compatibility_types import get_type_support, validate_registry


def has_generic_binary_surface(finding: dict) -> bool:
    """Return whether generic BINARY CLI variations are meaningful."""

    return finding.get("affected_api", {}).get("kind", "") in {
        "cli_command",
        "cli_option",
        "config_key",
        "env_variable",
    }


def generate_cli_args(finding: dict) -> list[dict]:
    """Dimension 1: CLI argument combinations."""
    inputs = []
    if not has_generic_binary_surface(finding):
        return []
    
    # Always include basic help/version
    inputs.append({"input_id": "cli_help", "command": "BINARY --help", 
                   "dimension": "cli_args", "description": "Help flag"})
    inputs.append({"input_id": "cli_version", "command": "BINARY --version", 
                   "dimension": "cli_args", "description": "Version flag"})
    inputs.append({"input_id": "cli_empty", "command": "BINARY", 
                   "dimension": "cli_args", "description": "Default (no args)"})
    
    # Extract known flags from finding description or affected_api
    known_flags = extract_flags(finding)
    for flag in known_flags[:4]:  # Limit to first 4
        inputs.append({
            "input_id": f"cli_flag_{flag.strip('-')}",
            "command": f"BINARY {flag}",
            "dimension": "cli_args",
            "description": f"Flag {flag}"
        })
    
    # Add invalid flag for error path
    inputs.append({"input_id": "cli_invalid", "command": "BINARY --nonexistent-flag",
                   "dimension": "cli_args", "description": "Invalid flag (error path)"})
    
    return inputs


def generate_data_scale(finding: dict) -> list[dict]:
    """Dimension 2: Input data size gradient."""
    if not has_generic_binary_surface(finding) or finding.get("compatibility_type") not in {
        "INPUT_CONTRACT_CHANGE",
        "OUTPUT_FORMAT_CHANGE",
        "SIDE_EFFECT_CHANGE",
        "RESOURCE_LIFETIME_CHANGE",
        "PERFORMANCE_RESOURCE_SEMANTIC_CHANGE",
        "SYSCALL_SEMANTIC_CHANGE",
        "IOCTL_NETLINK_ABI_CHANGE",
    }:
        return []
    return [
        {"input_id": "data_empty", "command": "BINARY", 
         "dimension": "data_scale", "description": "Empty/default input"},
        {"input_id": "data_small", "command": "BINARY small_input", 
         "dimension": "data_scale", "description": "Small input"},
        {"input_id": "data_large", "command": "BINARY large_input",
         "dimension": "data_scale", "description": "Large input (stress)"},
    ]


def generate_env_conditions(finding: dict) -> list[dict]:
    """Dimension 3: Environment condition variants."""
    comp_type = finding.get("compatibility_type", "")
    inputs = []
    if not has_generic_binary_surface(finding):
        return inputs
    
    # Terminal vs non-terminal (critical for OUTPUT_FORMAT_CHANGE)
    if "OUTPUT" in comp_type:
        inputs.append({"input_id": "env_terminal", "command": "script -q -c 'BINARY' /dev/null",
                       "dimension": "env_conditions", "description": "Terminal output (isatty=true)"})
        inputs.append({"input_id": "env_piped", "command": "BINARY | cat",
                       "dimension": "env_conditions", "description": "Piped output (isatty=false)"})
    
    if comp_type in {"CONFIG_CLI_BEHAVIOR_CHANGE", "ERROR_EXCEPTION_CHANGE", "OUTPUT_FORMAT_CHANGE"}:
        inputs.append({"input_id": "env_json", "command": "BINARY --json 2>/dev/null || BINARY -J 2>/dev/null || echo JSON N/A",
                       "dimension": "env_conditions", "description": "JSON output (if supported)"})
    
    return inputs


def generate_abnormal_inputs(finding: dict) -> list[dict]:
    """Dimension 4: Abnormal/malformed inputs."""
    if not has_generic_binary_surface(finding) or finding.get("compatibility_type") not in {
        "CONFIG_CLI_BEHAVIOR_CHANGE",
        "ERROR_EXCEPTION_CHANGE",
        "INPUT_CONTRACT_CHANGE",
        "OUTPUT_FORMAT_CHANGE",
        "RETURN_CONTRACT_CHANGE",
    }:
        return []
    return [
        {"input_id": "abnormal_empty", "command": "BINARY ''",
         "dimension": "abnormal_inputs", "description": "Empty string argument"},
        {"input_id": "abnormal_long", "command": f"BINARY $(python3 -c 'print(\"A\"*4096)' 2>/dev/null || echo long_input)",
         "dimension": "abnormal_inputs", "description": "Very long argument"},
        {"input_id": "abnormal_special", "command": "BINARY $'\\x00\\x01\\x02'",
         "dimension": "abnormal_inputs", "description": "Special/null bytes"},
    ]


def generate_concurrency(finding: dict) -> list[dict]:
    """Dimension 5: Concurrency/timing variants."""
    comp_type = finding.get("compatibility_type", "")
    if not has_generic_binary_surface(finding) or comp_type not in {
        "SIDE_EFFECT_CHANGE",
        "RESOURCE_LIFETIME_CHANGE",
        "PERFORMANCE_RESOURCE_SEMANTIC_CHANGE",
        "SYSCALL_SEMANTIC_CHANGE",
    }:
        return []
    return [
        {"input_id": "conc_parallel", "command": "BINARY & BINARY & wait",
         "dimension": "concurrency", "description": "Parallel execution"},
        {"input_id": "conc_signal", "command": "timeout 2 BINARY || true",
         "dimension": "concurrency", "description": "Timeout/signal injection"},
    ]


def generate_protocol_variants(finding: dict) -> list[dict]:
    """Dimension 6: Protocol/transport variants."""
    location = finding.get("location", {})
    file = location.get("file", "")
    # Only generate if the finding involves network/protocol code
    if has_generic_binary_surface(finding) and any(
        kw in file.lower() for kw in ["protocol", "transport", "sftp", "scp", "http", "dns", "dhcp", "netlink"]
    ):
        return [
            {"input_id": "proto_default", "command": "BINARY",
             "dimension": "protocol_variants", "description": "Default protocol"},
            {"input_id": "proto_alt", "command": "BINARY -O 2>/dev/null || BINARY --legacy 2>/dev/null || echo N/A",
             "dimension": "protocol_variants", "description": "Alternate protocol/transport"},
        ]
    return []


def extract_flags(finding: dict) -> list[str]:
    """Extract known CLI flags from finding text."""
    flags = []
    text = json.dumps(finding)
    # Common flag patterns
    import re
    found = re.findall(r'`(-\w)[,\s]*(--\w[-a-z]*)`', text, re.IGNORECASE)
    for short, long in found:
        flags.extend([short, long])
    # Also find standalone flags
    found = re.findall(r'`(-\w)`', text)
    for f in found:
        if f not in flags:
            flags.append(f)
    return flags


def entry_inputs(entries: list[dict]) -> list[dict]:
    """Use concrete generated/refined entries as the matrix's primary inputs."""
    inputs = []
    for index, entry in enumerate(entries):
        command = str(entry.get("run_command") or "").strip()
        if not command or entry.get("status") not in {"generated", "refined"}:
            continue
        execution = entry.get("execution") or {}
        inputs.append({
            "input_id": entry.get("entry_id") or f"entry_{index + 1}",
            "command": command,
            "cwd": execution.get("cwd", ""),
            "dimension": "finding_entries",
            "description": f"Finding-specific entry for {entry.get('finding_id', 'UNKNOWN')}",
            "expected_signal": entry.get("expected_signal", ""),
            "reachability_signal": entry.get("reachability_signal", ""),
            "artifact_path": entry.get("artifact_path", ""),
            "contract_probe": entry.get("contract_probe"),
        })
    return inputs


def generate_contract_axes(finding: dict) -> list[dict]:
    """Create type-specific planned inputs without inventing unsafe commands."""

    compatibility_type = str(finding.get("compatibility_type") or "")
    support = get_type_support(compatibility_type)
    planned = []
    for index, axis in enumerate(support["input_axes"], 1):
        planned.append(
            {
                "input_id": f"contract_axis_{index}",
                "command": "",
                "dimension": "type_contract",
                "description": str(axis),
                "status": "planned_needs_probe",
                "contract_id": support["contract_id"],
                "comparison": support["comparison"],
                "required_observation": support["observation"],
                "requires_explicit_probe": support["requires_explicit_probe"],
            }
        )
    return planned


def generate_for_finding(finding: dict, entries: list[dict] | None = None) -> dict:
    """Generate type-contract and applicable runtime dimensions for a finding."""
    dims = {}
    dims["finding_entries"] = entry_inputs(entries or [])
    dims["type_contract"] = generate_contract_axes(finding)
    dims["cli_args"] = generate_cli_args(finding)
    dims["data_scale"] = generate_data_scale(finding)
    dims["env_conditions"] = generate_env_conditions(finding)
    dims["abnormal_inputs"] = generate_abnormal_inputs(finding)
    dims["concurrency"] = generate_concurrency(finding)
    dims["protocol_variants"] = generate_protocol_variants(finding)
    
    # Assign input IDs sequentially
    counter = 0
    for dim_name, inputs in dims.items():
        for inp in inputs:
            counter += 1
            if "input_id" not in inp:
                inp["input_id"] = f"I{counter}"
    
    return {
        "id": finding.get("id", "UNKNOWN"),
        "type": finding.get("compatibility_type", "UNKNOWN"),
        "dimensions": dims,
        "total_inputs": sum(len(v) for v in dims.values())
    }


def load_entries(path: Path, analysis: dict) -> dict[str, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    entries = payload.get("entries", []) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return {}
    test_result_dir = path.parent.parent.resolve()
    analysis_repo = Path(str(analysis.get("analysis_repo") or ".")).resolve()
    by_finding: dict[str, list[dict]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        execution = entry.setdefault("execution", {})
        cwd = str(execution.get("cwd") or "")
        if cwd in {"result_dir", "test_result_dir"}:
            execution["cwd"] = str(test_result_dir)
        elif cwd == "analysis_repo":
            execution["cwd"] = str(analysis_repo)
        elif cwd and not Path(cwd).is_absolute():
            execution["cwd"] = str((analysis_repo / cwd).resolve())
        by_finding.setdefault(str(entry.get("finding_id") or "UNKNOWN"), []).append(entry)
    return by_finding


def main():
    parser = argparse.ArgumentParser(description="Test Input Dimension Matrix Generator")
    parser.add_argument("--findings", help="Path to PCA analysis.json or normalized findings JSON")
    parser.add_argument("--entries", help="Path to testing-owned test-entries.json")
    parser.add_argument("--output", default="test_inputs.json", help="Output path")
    parser.add_argument("--demo", action="store_true", help="Show demo output")
    args = parser.parse_args()

    registry_errors = validate_registry()
    if registry_errors:
        parser.error("invalid compatibility type registry: " + "; ".join(registry_errors))
    
    if args.demo:
        # Generate demo output
        demo_finding = {
            "id": "PCA-DEMO",
            "compatibility_type": "OUTPUT_FORMAT_CHANGE",
            "affected_api": {"kind": "cli_option", "name": "cli_tool --format"},
            "location": {"file": "src/output.c"}
        }
        result = generate_for_finding(demo_finding)
        print(json.dumps(result, indent=2))
        print(f"\nTotal inputs generated: {result['total_inputs']}")
        return
    
    if not args.findings:
        parser.print_help()
        sys.exit(1)
    
    with open(args.findings) as f:
        findings_data = json.load(f)

    entries_by_finding = {}
    if args.entries:
        entries_path = Path(args.entries).resolve()
        if not entries_path.is_file():
            parser.error(f"entries file not found: {entries_path}")
        analysis_for_paths = findings_data if isinstance(findings_data, dict) else {}
        entries_by_finding = load_entries(entries_path, analysis_for_paths)
    
    # Handle both list and {"findings": [...]} formats
    findings = findings_data
    if isinstance(findings_data, dict) and "findings" in findings_data:
        findings = findings_data["findings"]
    if not isinstance(findings, list):
        findings = [findings]
    
    results = []
    total = 0
    for finding in findings:
        gen = generate_for_finding(
            finding,
            entries_by_finding.get(str(finding.get("id") or "UNKNOWN"), []),
        )
        results.append(gen)
        total += gen["total_inputs"]
    
    output = {"findings": results, "total_inputs": total}
    
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {total} test inputs across {len(results)} findings")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
