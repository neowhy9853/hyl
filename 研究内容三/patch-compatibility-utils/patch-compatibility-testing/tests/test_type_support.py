from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from compatibility_types import (  # noqa: E402
    SUPPORTED_COMPATIBILITY_TYPES,
    TYPE_SUPPORT,
    validate_registry,
)
from input_dimensions import generate_for_finding  # noqa: E402
from finalize_test_report import validate_finding  # noqa: E402
from run_contracts import Observation, compare  # noqa: E402
from test_entry_planner import build_task  # noqa: E402


EXPECTED_TYPES = {
    "API_SIGNATURE_CHANGE",
    "ABI_CHANGE",
    "INPUT_CONTRACT_CHANGE",
    "RETURN_CONTRACT_CHANGE",
    "ERROR_EXCEPTION_CHANGE",
    "SIDE_EFFECT_CHANGE",
    "OUTPUT_FORMAT_CHANGE",
    "PROC_SYS_OUTPUT_CHANGE",
    "SYSCALL_SEMANTIC_CHANGE",
    "IOCTL_NETLINK_ABI_CHANGE",
    "CONFIG_CLI_BEHAVIOR_CHANGE",
    "RESOURCE_LIFETIME_CHANGE",
    "PERFORMANCE_RESOURCE_SEMANTIC_CHANGE",
}


def finding(compatibility_type: str, index: int) -> dict:
    return {
        "id": f"PCA-{index:04d}",
        "compatibility_type": compatibility_type,
        "test_priority": "high",
        "affected_api": {"kind": "public_function", "name": "probe"},
        "location": {"file": "src/probe.c", "new_lines": [1, 2], "symbol": "probe"},
    }


class TypeRegistryTests(unittest.TestCase):
    def test_registry_has_exact_analysis_type_set(self) -> None:
        self.assertEqual(set(SUPPORTED_COMPATIBILITY_TYPES), EXPECTED_TYPES)
        self.assertEqual(validate_registry(), [])

        schema = json.loads((SKILL_DIR / "schemas/test_output_schema.json").read_text())
        schema_types = set(schema["$defs"]["compatibilityType"]["enum"])
        self.assertEqual(schema_types, EXPECTED_TYPES)
        analysis_schema = json.loads(
            (SKILL_DIR.parent / "patch-compatibility-analysis/schemas/output_schema.json").read_text()
        )
        analysis_types = set(
            analysis_schema["properties"]["findings"]["items"]["properties"]
            ["compatibility_type"]["enum"]
        )
        self.assertEqual(analysis_types, EXPECTED_TYPES)
        for reference in (
            "references/compatibility_type_test_matrix.md",
            "references/impact_types.md",
            "references/test_input_strategies.md",
        ):
            text = (SKILL_DIR / reference).read_text(encoding="utf-8")
            for compatibility_type in EXPECTED_TYPES:
                self.assertIn(compatibility_type, text, f"{reference}: {compatibility_type}")

    def test_unknown_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported compatibility_type"):
            build_task(
                {"package_profile": "c_project"},
                finding("UNKNOWN_CHANGE", 1),
                0,
            )

    def test_every_type_plans_entry_contract_and_input_axes(self) -> None:
        analysis = {"package_profile": "c_project"}
        for index, compatibility_type in enumerate(SUPPORTED_COMPATIBILITY_TYPES, 1):
            item = finding(compatibility_type, index)
            task = build_task(analysis, item, index - 1)
            strategy = task["strategy"]
            support = TYPE_SUPPORT[compatibility_type]
            self.assertEqual(strategy["entry_kind"], support["entry_kind"])
            self.assertEqual(strategy["contract_id"], support["contract_id"])
            self.assertEqual(strategy["comparison"], support["comparison"])

            generated = generate_for_finding(item)
            axes = generated["dimensions"]["type_contract"]
            self.assertEqual(len(axes), len(support["input_axes"]))
            self.assertTrue(all(axis["contract_id"] == support["contract_id"] for axis in axes))
            for dimension, inputs in generated["dimensions"].items():
                if dimension not in {"finding_entries", "type_contract"}:
                    self.assertEqual(inputs, [], f"{compatibility_type} fabricated {dimension} inputs")

    def test_final_report_accepts_every_registered_type(self) -> None:
        for index, compatibility_type in enumerate(SUPPORTED_COMPATIBILITY_TYPES, 1):
            errors: list[str] = []
            validate_finding(
                {
                    "finding_id": f"PCA-{index:04d}",
                    "compatibility_type": compatibility_type,
                    "test_priority": "high",
                    "status": "not_run",
                    "target_location": {
                        "file": "src/probe.c",
                        "new_lines": [1, 2],
                        "symbol": "probe",
                    },
                    "entries": [],
                    "contracts": [],
                    "coverage": {
                        "executable_lines": 0,
                        "covered_lines": 0,
                        "uncovered_lines": [],
                        "rate": 0,
                    },
                    "behavior_differences": [
                        {
                            "input_id": "I1",
                            "diff_type": compatibility_type,
                            "before": "old",
                            "after": "new",
                            "evidence": "probe",
                        }
                    ],
                    "notes": [],
                },
                index - 1,
                errors,
            )
            self.assertEqual(errors, [], f"{compatibility_type}: {errors}")

    def test_type_aware_runner_executes_all_thirteen_contracts(self) -> None:
        findings = []
        entries = []
        for index, compatibility_type in enumerate(SUPPORTED_COMPATIBILITY_TYPES, 1):
            findings.append(finding(compatibility_type, index))
            comparison = TYPE_SUPPORT[compatibility_type]["comparison"]
            if comparison == "numeric_tolerance":
                command = "printf '{\"elapsed_ms\": 100, \"retries\": 2}\\n'"
            elif comparison == "error":
                command = "printf 'stable error\\n' >&2; exit 2"
            elif comparison == "exit_code":
                command = "exit 7"
            else:
                command = "printf 'stable\\n'"
            entries.append(
                {
                    "finding_id": f"PCA-{index:04d}",
                    "contract_probe": {
                        "probe_id": f"probe-{index}",
                        "command": command,
                        "comparison": comparison,
                    },
                }
            )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            before = root / "before"
            after = root / "after"
            output = root / "output"
            before.mkdir()
            after.mkdir()
            findings_path = root / "analysis.json"
            entries_path = root / "entries.json"
            findings_path.write_text(json.dumps({"findings": findings}), encoding="utf-8")
            entries_path.write_text(json.dumps({"entries": entries}), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "run_contracts.py"),
                    "--findings",
                    str(findings_path),
                    "--entries",
                    str(entries_path),
                    "--before-dir",
                    str(before),
                    "--after-dir",
                    str(after),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            summary = json.loads((output / "contract_summary.json").read_text())
            self.assertEqual(summary["total"], 13)
            self.assertEqual(summary["passed"], 13)
            self.assertEqual(summary["breached"], 0)
            self.assertEqual(summary["skipped"], 0)
            self.assertEqual(summary["supported_types"], 13)
            verification = json.loads((output / "contract_verification.json").read_text())
            self.assertEqual(len(verification["results"]), 13)
            self.assertEqual(verification["breaches"], [])

    def test_every_comparison_detects_a_breach(self) -> None:
        def observed(returncode: int = 0, stdout: str = "stable\n", stderr: str = "") -> Observation:
            return Observation("probe", "/tmp", returncode, stdout, stderr)

        cases = {
            "success": (observed(), observed(returncode=1)),
            "acceptance": (observed(), observed(returncode=1)),
            "exit_code": (observed(), observed(returncode=1)),
            "error": (observed(returncode=2, stderr="old"), observed(returncode=2, stderr="new")),
            "exact": (observed(stdout="old"), observed(stdout="new")),
            "set_no_additions": (observed(stdout="old\n"), observed(stdout="old\nnew\n")),
            "numeric_tolerance": (
                observed(stdout='{"elapsed_ms": 100}\n'),
                observed(stdout='{"elapsed_ms": 200}\n'),
            ),
        }
        for comparison, (before, after) in cases.items():
            status, _ = compare(comparison, before, after, 20.0)
            self.assertEqual(status, "BREACH", comparison)

    def test_input_matrix_runs_direct_probe_without_a_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            before = root / "before"
            after = root / "after"
            output = root / "output"
            before.mkdir()
            after.mkdir()
            inputs = root / "inputs.json"
            inputs.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "id": "PCA-0001",
                                "type": "PROC_SYS_OUTPUT_CHANGE",
                                "dimensions": {
                                    "finding_entries": [
                                        {
                                            "input_id": "direct",
                                            "command": "printf 'stable\\n'",
                                            "cwd": str(root),
                                        }
                                    ]
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPTS_DIR / "input_matrix.sh"),
                    "--inputs",
                    str(inputs),
                    "--before-dir",
                    str(before),
                    "--after-dir",
                    str(after),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            summary = json.loads((output / "matrix_summary.json").read_text())
            self.assertEqual(summary["executed"], 1)
            self.assertEqual(summary["skipped"], 0)

    def test_input_matrix_preserves_finding_type_for_behavior_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            before = root / "before"
            after = root / "after"
            output = root / "output"
            before.mkdir()
            after.mkdir()
            for directory, value in ((before, "old"), (after, "new")):
                binary = directory / "probe"
                binary.write_text(f"#!/bin/sh\nprintf '{value}\\n'\n", encoding="utf-8")
                binary.chmod(0o755)
            inputs = root / "inputs.json"
            inputs.write_text(
                json.dumps(
                    {
                        "findings": [
                            {
                                "id": "PCA-0001",
                                "type": "SYSCALL_SEMANTIC_CHANGE",
                                "dimensions": {
                                    "finding_entries": [
                                        {"input_id": "syscall", "command": "BINARY", "cwd": str(root)}
                                    ]
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPTS_DIR / "input_matrix.sh"),
                    "--inputs",
                    str(inputs),
                    "--before-dir",
                    str(before),
                    "--after-dir",
                    str(after),
                    "--output",
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            record = json.loads((output / "matrix_results.jsonl").read_text().strip())
            self.assertEqual(record["compatibility_type"], "SYSCALL_SEMANTIC_CHANGE")
            self.assertEqual(record["diff_type"], "SYSCALL_SEMANTIC_CHANGE")


if __name__ == "__main__":
    unittest.main()
