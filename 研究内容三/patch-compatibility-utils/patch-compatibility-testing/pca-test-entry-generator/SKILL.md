---
name: pca-test-entry-generator
description: "根据最终确认的 Patch Compatibility Analysis findings，生成或细化可运行的测试入口命令、复现程序或项目原生测试代码。在 patch-compatibility-testing 已校验 analysis.json 并生成 test-entry-tasks.json 后使用。"
---

# PCA Test Entry Generator

你的目标不是重新判断兼容性，而是为已经确认的
`analysis.json.findings[]` 生成真实可用的测试入口：一个命令、脚本、
程序或项目原生测试，能够触达到目标兼容性变更代码行或其生成后的行为。

## Inputs

- `analysis.json`: 已通过 `validate_analysis.py` 的最终分析结果。
- `<TEST_RESULT_DIR>/test-entry-tasks.json`: 测试子 skill 的 `scripts/test_entry_planner.py` 生成的任务清单。
- `<TEST_RESULT_DIR>/test-entry-work/test-entries.json`: 本子 skill 创建或细化的入口清单。
- `analysis_repo`: 已应用补丁的 worktree。源码读取和构建都以它为根。

如果 `analysis_worktree_status=cleaned` 或 `analysis_repo` 不存在，先运行：

```bash
python3 "<TEST_SKILL_DIR>/../patch-compatibility-analysis/scripts/orchestrator.py" \
  --ensure-worktree "<ANALYSIS_RESULT_DIR>/analysis.json"
```

## Required Output

所有产物写入 `<TEST_RESULT_DIR>/test-entry-work/`。不要修改输入 `analysis.json`，也不要把测试产物写回分析目录根部。

`test-entry-work/test-entries.json` 中每个 generated/refined entry 必须包含：

```json
{
  "finding_id": "PCA-0001",
  "entry_id": "PCA-TE-0001",
  "entry_kind": "cli_command|config_reproducer|api_harness|autotools_config_reproducer|...",
  "status": "generated|refined|draft_needs_refinement|manual_required|not_feasible",
  "artifact_path": "test-entry-work/PCA-0001/reproducer.sh",
  "build_command": "optional exact build command",
  "run_command": "exact command to run from the documented cwd",
  "target_location": {
    "file": "path/in/repo.c",
    "new_lines": [100, 120],
    "symbol": "target_symbol"
  },
  "reachability_signal": "how this command proves it reached the target line or generated behavior",
  "expected_signal": "the expected assertion, output, return code, errno, macro, symbol, log, crash, or sanitizer signal",
  "execution": {
    "cwd": "result_dir|analysis_repo|specific/path",
    "timeout_seconds": 120,
    "uses_clean_source_copy": false
  },
  "input_strategy": "inputs that exercise the old/new compatibility boundary",
  "contract_probe": {
    "probe_id": "stable probe name",
    "command": "version-neutral command using BINARY or {VERSION_DIR}",
    "before_command": "optional version-specific command",
    "after_command": "optional version-specific command",
    "comparison": "exact|acceptance|exit_code|error|success|set_no_additions|numeric_tolerance",
    "cwd": "version_dir or a relative path beneath each version directory",
    "timeout_seconds": 30,
    "tolerance_percent": 20
  },
  "limitations": "environment, dependency, service, privilege, corpus, or build constraints"
}
```

Read `../references/compatibility_type_test_matrix.md` before designing the
probe. Use the registered comparison unless the finding requires a more precise
one. `command` must work for both versions with `BINARY` or `{VERSION_DIR}`;
otherwise provide both `before_command` and `after_command`. Use
`numeric_tolerance` only when both commands print the same non-empty JSON object
whose values are numbers. Omit `tolerance_percent` for non-numeric comparisons.

If the entry is intended as fuzz seed material, also record provenance, seed
artifact path or seed-generation command, minimization status, mutation axes,
expected signal, and coverage/reachability signal.

## Entry Source Order

Use this order and stop when a real runnable entry is available:

1. `commit_message_reproducer`: exact command, PoC, crash trigger, sanitizer
   command, or explicit test invocation from the commit message.
2. `project_native_regression_test`: existing project test or a small addition
   to the nearest native test file.
3. `existing_fuzzer_or_corpus`: existing fuzz target, OSS-Fuzz/ClusterFuzz
   corpus, regression input, or added testdata.
4. `documentation_or_example`: command examples, man pages, sample configs, or
   repo docs.
5. `static_call_chain_entry`: entry inferred from call-chain artifacts.
6. `synthetic_harness`: standalone shell/C/Python/Go/Ruby harness. Use this
   only after the previous sources have been checked.

Always preserve commit-message commands verbatim in provenance. You may adapt
or minimize them, but do not erase the original command.

## Runnability Contract

A generated/refined entry is acceptable only if it has:

- an exact command or source artifact path;
- a concrete cwd;
- setup/build prerequisites;
- an expected signal distinguishing the old/new behavior;
- a reachability signal for `target_location.new_lines` or the generated
  behavior produced by that source line;
- a type-specific `contract_probe`, or a concrete reason it cannot run in the
  selected environment;
- a timeout suitable for one narrow reproduction;
- limitations that explain remaining environment or corpus requirements.

Do not mark prose, placeholders, or seed notes as `generated`. Use
`draft_needs_refinement`, `manual_required`, or `not_feasible` instead.

## Autotools Configure Changes

For `configure.ac` / `configure.in` compatibility changes, prefer the
deterministic planner-generated `autotools_config_reproducer` when present.
This script copies `analysis_repo` into a clean run directory under
`test-entry-work/<finding_id>/runs/`, then runs `autoreconf`, `configure`, and
optional `make` there. Do not run `autogen.sh` in `analysis_repo` or configure
the source tree in place.

For build-option default changes, the entry should compare:

- default configure invocation; and
- explicit opt-in or opt-out invocation such as `--with-foo=yes` or
  `--enable-foo=yes`.

The expected signal should use generated feature macros, config headers, exported
symbols, CLI help text, or a project-native assertion. Before checking symbols,
verify that the library or binary was actually built; a missing binary is not
proof that a symbol is absent.

## Safe Reproduction Attempt

For every Agent-final High entry, attempt one safe best-effort verification.
Run narrow commands under `timeout`, usually from `<TEST_RESULT_DIR>`:

```bash
timeout 900 bash test-entry-work/PCA-0001/reproducer.sh
```

You may build the patched worktree binary when needed. Installing host
dependencies, using sudo, downloading large images, or modifying persistent
services requires user confirmation; without it, record `needs_env`.

Do not run destructive commands, privileged operations, `git reset`, `git
clean`, `make install`, hardware-dependent tests, long-lived services,
external network traffic, full test suites, or fuzzing loops.

Write verification output to:

```text
test-entry-work/test-entry-verification.json
test-entry-work/test-entry-verification.md
```

Use one status per entry:

- `runnable_verified`: command ran and expected/reachability signal was observed.
- `ran_expected_signal_mismatch`: command ran, but the expected signal was not observed.
- `static_valid_not_run`: entry is structurally valid but not executed in this run.
- `needs_refinement`: command/artifact has placeholders, prose, or inconsistent metadata.
- `needs_env`: build dependency, binary, corpus, or test environment is missing.
- `unsafe_not_run`: command would require unsafe or long-running execution.

Record command, cwd, timeout, exit code if run, stdout/stderr tail, observed
signal, and reason.

## Completion Rule

For High findings, do not stop at a draft unless there is a concrete blocker.
Either produce a runnable verified entry, or record exactly why it cannot be
run yet and what dependency, corpus, or project-native fixture is missing.
