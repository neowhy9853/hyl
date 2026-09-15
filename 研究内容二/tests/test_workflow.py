"""Regression checks for porting gates and packaged evaluation data."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


APPLY = load_module("port_apply", ROOT / "skills/patch-port-apply/scripts/candidate_workspace.py")
VALIDATE = load_module("port_validate", ROOT / "skills/patch-port-validation/scripts/validate_candidate.py")
EVALUATE = load_module("port_evaluate", ROOT / "evaluation/evaluate_linux.py")


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PortWorkflowTests(unittest.TestCase):
    def setUp(self):
        # The test runner can select a writable filesystem through TMPDIR.
        self.temporary = tempfile.TemporaryDirectory(prefix="port-regression-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Regression Test")
        self.git("config", "user.email", "test@example.invalid")
        self.source = self.repo / "a.c"
        self.original = "int value(int n) {\n    return n;\n}\n"
        self.fixed = "int value(int n) {\n    if (n < 0) return 0;\n    return n;\n}\n"
        self.source.write_text(self.original)
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.target = self.git("rev-parse", "HEAD").stdout.strip()
        self.source.write_text(self.fixed)
        self.patch = self.base / "generated.patch"
        self.patch.write_bytes(self.git("diff", text=False).stdout)
        self.source.write_text(self.original)
        self.analysis_evidence = self.base / "analysis-evidence.json"
        write_json(self.analysis_evidence, {"queries": []})
        self.analysis_path = self.base / "port-analysis.json"
        self.analysis = {
            "analysis_status": "ready", "port_mode": "history", "missing_context": [],
            "inputs": {"repo": str(self.repo), "target_commit": self.target,
                       "analysis_evidence": str(self.analysis_evidence),
                       "analysis_evidence_sha256": digest(self.analysis_evidence)},
            "change_units": [{"id": "CU-1", "mandatory": True, "map_status": "direct",
                              "target_location": {"path": "a.c"}}],
            "approved_new_paths": [],
        }
        write_json(self.analysis_path, self.analysis)
        self.application_evidence = self.base / "application-evidence.json"
        write_json(self.application_evidence, {
            "target_commit": self.target, "generated_patch_sha256": digest(self.patch),
            "analysis_path": str(self.analysis_path),
        })
        self.application_path = self.base / "application.json"
        self.application = {
            "application_status": "candidate_ready", "target_commit": self.target,
            "analysis_path": str(self.analysis_path), "generated_patch": str(self.patch),
            "generated_patch_sha256": digest(self.patch),
            "application_evidence": str(self.application_evidence),
            "application_evidence_sha256": digest(self.application_evidence),
        }
        write_json(self.application_path, self.application)

    def git(self, *args, text=True):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, check=True, text=text)

    def validate(self, commands=()):
        return VALIDATE.validate(
            repo=self.repo, target_ref=self.target, patch_path=self.patch,
            analysis_path=self.analysis_path, application_path=self.application_path,
            commands=list(commands), timeout=5)

    def test_valid_candidate_replays_but_requires_semantic_review(self):
        result = self.validate()
        self.assertEqual(result["evidence_status"], "structurally_valid")
        self.assertEqual(result["recommended_validation_status"], "partial")
        self.assertEqual(self.source.read_text(), self.original)

    def test_input_mismatch_blocks_before_replay_or_test_commands(self):
        self.application["generated_patch_sha256"] = "0" * 64
        write_json(self.application_path, self.application)
        with mock.patch.object(VALIDATE, "run_command") as run, \
                mock.patch.object(VALIDATE.tempfile, "TemporaryDirectory",\
                                  side_effect=AssertionError("replay must not start")) as clone:
            result = self.validate(["must-not-run"])
        self.assertEqual(result["evidence_status"], "blocked")
        self.assertEqual(result["recommended_validation_status"], "blocked")
        run.assert_not_called()
        clone.assert_not_called()

    def test_stale_analysis_evidence_blocks(self):
        self.analysis_evidence.write_text('{"queries": ["changed"]}')
        result = self.validate()
        self.assertEqual(result["evidence_status"], "blocked")

    def test_stale_application_evidence_blocks(self):
        self.application_evidence.write_text('{"changed": true}')
        result = self.validate()
        self.assertEqual(result["evidence_status"], "blocked")

    def test_unready_application_blocks(self):
        self.application["application_status"] = "blocked"
        write_json(self.application_path, self.application)
        self.assertEqual(self.validate()["evidence_status"], "blocked")

    def test_missing_command_preserves_not_run_evidence(self):
        result = self.validate([str(self.base / "missing-build-tool")])
        self.assertEqual(result["evidence_status"], "structurally_valid")
        self.assertEqual(result["recommended_validation_status"], "partial")
        self.assertEqual(result["commands"][0]["status"], "not_run")
        self.assertIsNone(result["commands"][0]["exit_code"])

    def test_malformed_command_preserves_not_run_evidence(self):
        result = self.validate(['"unterminated'])
        self.assertEqual(result["evidence_status"], "structurally_valid")
        self.assertEqual(result["recommended_validation_status"], "partial")
        self.assertEqual(result["commands"][0]["status"], "not_run")

    def test_actual_test_failure_remains_failed(self):
        command = subprocess.list2cmdline([sys.executable, "-c", "raise SystemExit(3)"])
        result = self.validate([command])
        self.assertEqual(result["evidence_status"], "failed")
        self.assertEqual(result["commands"][0]["exit_code"], 3)

    def test_prepare_requires_ready_history_analysis(self):
        self.analysis["analysis_status"] = "blocked"
        write_json(self.analysis_path, self.analysis)
        worktree = self.base / "candidate"
        with self.assertRaises(APPLY.CandidateError):
            APPLY.prepare(self.repo, self.target, worktree, None, self.analysis_path)
        self.assertFalse(worktree.exists())

    def test_prepare_rejects_changed_target(self):
        self.git("commit", "--allow-empty", "-qm", "another target")
        worktree = self.base / "candidate"
        with self.assertRaises(APPLY.CandidateError):
            APPLY.prepare(self.repo, "HEAD", worktree, None, self.analysis_path)
        self.assertFalse(worktree.exists())

    def test_prepare_apply_finalize_roundtrip(self):
        worktree = self.base / "candidate"
        APPLY.prepare(self.repo, self.target, worktree, None, self.analysis_path)
        APPLY.apply_direct(worktree, self.patch, "strict")
        result = APPLY.finalize(worktree, self.analysis_path,
                                self.base / "roundtrip.patch", self.base / "roundtrip.json")
        self.assertEqual(result["evidence_status"], "structurally_ready")
        self.assertEqual((worktree / "a.c").read_text(), self.fixed)
        self.assertEqual(self.source.read_text(), self.original)


    def test_cli_persists_blocked_report(self):
        self.application["generated_patch_sha256"] = "0" * 64
        write_json(self.application_path, self.application)
        output = self.base / "validation.json"
        report = self.base / "report.md"
        result = subprocess.run([
            sys.executable, "-B", str(Path(VALIDATE.__file__)),
            "--repo", str(self.repo), "--target-ref", self.target,
            "--patch", str(self.patch), "--analysis", str(self.analysis_path),
            "--application", str(self.application_path), "--output", str(output),
            "--report", str(report),
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "blocked")
        self.assertEqual(json.loads(output.read_text())["structural_checks"]["status"], "not_run")
        self.assertIn("Input checks failed", report.read_text())

    def test_hashes_bind_raw_json_bytes(self):
        text = json.dumps(self.application, indent=2).replace("\\n", "\\r\\n")
        self.application_path.write_bytes(text.encode())
        result = self.validate()
        self.assertEqual(result["inputs"]["application_sha256"], digest(self.application_path))

    def test_cross_repo_prepare_still_accepts_confirmed_mapping(self):
        reference = self.base / "reference"
        reference.mkdir()
        subprocess.run(["git", "-C", str(reference), "init", "-q"], check=True)
        self.analysis["port_mode"] = "cross_repo_semantic"
        self.analysis["inputs"].update(reference_repo=str(reference), target_repo=str(self.repo))
        self.analysis["change_units"][0]["semantic_mapping"] = {
            "status": "confirmed", "evidence_ids": ["E-1"],
            "targets": [{"repo_role": "target", "commit": self.target, "path": "a.c"}],
        }
        write_json(self.analysis_path, self.analysis)
        result = APPLY.prepare(self.repo, self.target, self.base / "candidate",
                               None, self.analysis_path)
        self.assertEqual(result["status"], "prepared")

    def test_evaluation_export_excludes_oracle(self):
        self.source.write_text(self.fixed)
        self.git("commit", "-qam", "reference fix")
        reference_fix = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("checkout", "-qb", "target-branch", self.target)
        (self.repo / "target.txt").write_text("target-specific context")
        self.git("add", ".")
        self.git("commit", "-qm", "target baseline")
        target = self.git("rev-parse", "HEAD").stdout.strip()
        self.source.write_text(self.fixed)
        self.git("commit", "-qam", "target fix oracle")
        oracle = self.git("rev-parse", "HEAD").stdout.strip()
        exported = EVALUATE.create_full_repository(
            source_repo=self.repo, destination=self.base / "exported",
            reference_fix=reference_fix, reference_parent=self.target,
            target=target, oracle_commit=oracle, timeout=15)
        self.assertTrue(EVALUATE.inspect_isolation(exported.path, oracle)["passed"])
        self.assertEqual((exported.path / "a.c").read_text(), self.original)


class DistributionTests(unittest.TestCase):
    def test_feishu_patch_hashes_and_format(self):
        root = ROOT / "evaluation"
        rows = [json.loads(line) for line in (root / "feishu92.jsonl").read_text().splitlines()]
        self.assertEqual(len({row["case_id"] for row in rows}), len(rows))
        for row in rows:
            for role in ("reference", "oracle"):
                with self.subTest(case=row["case_id"], role=role):
                    path = root / row[role + "_patch"]
                    self.assertEqual(digest(path), row[role + "_sha256"])
                    result = subprocess.run(["git", "apply", "--numstat", str(path)],
                                            cwd=tempfile.gettempdir(),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(result.stdout.strip())

    def test_runtime_preflight_accepts_stderr_help(self):
        with tempfile.TemporaryDirectory(prefix="runtime-check-") as name:
            executable = Path(name) / "opencode"
            executable.write_text("fixture")
            help_text = "--pure --auto --agent --dir --format --model --title"
            responses = [
                subprocess.CompletedProcess([], 0, "", help_text),
                subprocess.CompletedProcess([], 0, "test-version", ""),
            ]
            with mock.patch.object(EVALUATE.subprocess, "run", side_effect=responses):
                result = EVALUATE.inspect_runtime(executable)
            self.assertEqual(result["sha256"], digest(executable))
            self.assertEqual(result["version"], "test-version")

    def test_runtime_preflight_rejects_missing_flags(self):
        with mock.patch.object(EVALUATE.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], 0, "--model", "")):
            with self.assertRaises(ValueError):
                EVALUATE.inspect_runtime(Path("/missing-runtime-fixture"))

    def test_linux_dataset_loads(self):
        self.assertTrue(EVALUATE.load_cases(ROOT / "evaluation/linux404.jsonl"))


if __name__ == "__main__":
    unittest.main()
