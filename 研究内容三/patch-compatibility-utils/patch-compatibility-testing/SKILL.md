---
name: patch-compatibility-testing
description: "基于经过校验的 PCA analysis.json 执行分析驱动的补丁动态测试：为 API/ABI、输入/返回/错误、副作用/输出、proc/sys、syscall、ioctl/netlink、配置/CLI、资源生命周期及性能/超时/重试语义等兼容性变化生成 finding 专属入口和多维输入，准备 before/after 环境，执行契约、采集补丁行覆盖率，并从固定 JSON 确定性生成报告。当请求包含兼容性测试、验证兼容性变更、定向测试、测试入口、回归验证、契约验证、前后对比、覆盖率、复现、跑测试、directed testing、test entry、regression verification、contract verification、before/after comparison、reproducer 或 patch coverage 等词时使用。若用户只提供补丁但明确要求测试，先运行 patch-compatibility-analysis。"
---

# Patch Compatibility Testing

Conduct end-to-end patch-directed testing from a completed compatibility analysis through environment setup, test input generation, contract comparison, coverage execution, and final reporting.

The central questions this skill answers are: **"Does the patch preserve the
affected compatibility contract, and did the tests actually reach the changed
code?"**

## Input and analysis dependency

Testing is independently invocable but always depends on analysis output.

Set `TEST_SKILL_DIR` to the directory containing this `SKILL.md`; resolve all bundled scripts and the sibling analysis skill from that absolute path rather than from the caller's current directory.

1. Prefer an existing `<ANALYSIS_RESULT_DIR>/analysis.json`. Validate it with `../patch-compatibility-analysis/scripts/validate_analysis.py --allow-legacy-ids` before testing. This accepts historical `PCIA-*` IDs while new analysis output remains strict `PCA-*`.
2. If the user supplies only a repo plus patch/diff/commit, read and execute `../patch-compatibility-analysis/SKILL.md` first. Because the user already asked to test, continue automatically after analysis rather than asking again.
3. Do not rerun analysis when a valid `analysis.json` is supplied unless the user requests it or its repo/patch identity conflicts with the requested target.
4. Treat `test_entry_artifacts` or finding-level `test_entries[]` in older analysis files as legacy draft input only. New entry artifacts belong exclusively to `TEST_RESULT_DIR`.

Read these fields from `analysis.json`: `repo`, `analysis_repo`, `artifact_dir`, `base_commit`, `patch_id`, and `findings[]`. Read legacy `test_entry_artifacts` only as optional provenance. If `analysis_repo` is missing or marked `cleaned`, run:

```bash
python3 "<TEST_SKILL_DIR>/../patch-compatibility-analysis/scripts/orchestrator.py" \
  --ensure-worktree "<ANALYSIS_RESULT_DIR>/analysis.json"
```

Use `<ANALYSIS_RESULT_DIR>/compatibility-testing/` as `TEST_RESULT_DIR` unless the user specifies an output directory. Never place dynamic test artifacts inside the source checkout.

## Workflow Overview

```
 Phase 1       Phase 1.5       Phase 2       Phase 3       Phase 4       Phase 5
┌────────┐    ┌──────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ Ingest │ →  │ Entries  │ →  │ Env    │ →  │ Inputs │ →  │ Run +  │ →  │ Report │
│Analysis│    │ Plan/Gen │    │ Setup  │    │ Refine │    │Coverage│    │        │
└────────┘    └──────────┘    └────────┘    └────────┘    └────────┘    └────────┘
```

---

## Phase 1: Ingest Compatibility Analysis

Validate and normalize the analysis result into the test work directory. Do not perform a second, competing compatibility classification.

### Accepted inputs

1. **Preferred**: a PCA `analysis.json` or its containing directory/archive.
2. **Fallback**: raw patch/diff, commit hash, or commit URL together with the target repo; first generate `analysis.json` with the sibling analysis skill.

### Ingest steps

Parse the validated analysis output into a structured impact map. Preserve each PCA finding ID so test evidence can be traced back to the analysis report.

For each finding, record:
- `file` — source file path
- `new_lines` — the changed line range `[start, end]`
- `symbol` — the function/symbol name
- `compatibility_type` — classification (SIDE_EFFECT_CHANGE, INPUT_CONTRACT_CHANGE, etc.)
- `test_priority` and `test_recommendation` — analysis-owned testing guidance
- `static_call_chains` — sequences from public entry points to changed code
- legacy entry/input references, when present, as provenance only

Reject an unknown `compatibility_type`; do not silently route it through a
generic fallback. The accepted 13-type set is defined by
`scripts/compatibility_types.py` and the analysis schema.

Save to `<TEST_RESULT_DIR>/phase1_impact/impact_map.json`. If there are no confirmed findings, record that state and use patch-changed executable lines from `patch.diff` as coverage targets only when the user still wants coverage testing; do not invent compatibility findings.

---

## Phase 1.5: Plan and Generate Test Entries

Own all executable-entry generation in the testing stage. Keep `analysis.json` immutable.

1. Generate deterministic tasks from validated findings. Default to `high`; use `all` only when the user requests full finding coverage:

   ```bash
   python3 "<TEST_SKILL_DIR>/scripts/test_entry_planner.py" \
     --analysis "<ANALYSIS_RESULT_DIR>/analysis.json" \
     --result-dir "<TEST_RESULT_DIR>" \
     --min-priority high
   ```

   This writes `<TEST_RESULT_DIR>/test-entry-tasks.json` and `test-entry-plan.md`.

2. Read `<TEST_SKILL_DIR>/pca-test-entry-generator/SKILL.md` completely. Generate or refine one finding-specific runnable entry bundle under `<TEST_RESULT_DIR>/test-entry-work/` for every selected task.
3. Preserve legacy analysis-stage entries only as provenance. Copy or rewrite usable artifacts into `TEST_RESULT_DIR`; never rely on paths that point back into the analysis artifact root.
4. Require each generated/refined entry to contain `artifact_path`, `run_command`, `expected_signal`, `reachability_signal`, `execution.cwd`, input strategy, a type-specific `contract_probe` (or concrete blocker), prerequisites, and limitations.
5. For every High finding, attempt one safe narrow verification when runnable. Otherwise record `needs_refinement`, `needs_env`, `unsafe_not_run`, or `static_valid_not_run` with a concrete reason.
6. For autotools changes, run regeneration/configure only in a clean copy under `<TEST_RESULT_DIR>/test-entry-work/<finding_id>/runs/`; never configure `analysis_repo` in place.

Write entry metadata to `<TEST_RESULT_DIR>/test-entry-work/test-entries.json` and verification results to `test-entry-verification.json`/`.md`.

---

## Phase 2: Environment Setup

Determine what environment is needed to build and test the patched code, then set it up.

Prefer isolated worktrees, containers, or disposable VMs. The request to test authorizes normal builds and test execution in the supplied workspace, but does not by itself authorize host package installation, privileged commands, large image downloads, or modifying persistent services. Explain those requirements and obtain confirmation before such actions when they are necessary.

Read `references/environment_setup.md` for host, daemon, VM, and coverage setup.
Use a host/container for ordinary tools and libraries, and matched disposable
VMs for kernel, proc/sys, syscall, ioctl/netlink, or privileged-service probes.
Use `scripts/setup_qemu_vm.sh` only as a template. Discover project dependencies
from its build files; do not install packages or download images without the
authorization described above.

---

## Phase 3: Test Input Generation

Start from the concrete Phase 1.5 entries, then expand them across branch,
boundary, environment, concurrency, and protocol dimensions. Do not replace a
finding-specific entry with generic `BINARY --help` placeholders. Read
`references/compatibility_type_test_matrix.md` and
`references/test_input_strategies.md`; read
`references/testing-scope-and-entry-generation-plan.md` when selecting project
test sources.

### Input Generation Algorithm

For each finding from Phase 1:

1. **Trace the call chain** from the public entry point to the changed code. Read the source along the entire chain.

2. **Perform constraint-intention analysis** (adapted from `constraint-intention-analysis-skill`):
   - For each function in the call chain, extract branch conditions, input validation, and error checks
   - Summarize the intention of each constraint in natural language
   - Identify which inputs would satisfy each constraint and which would violate it
   - Identify which constraints are path-critical (must pass to reach target) vs. path-irrelevant

3. **Map constraints to input dimensions**:
   - CLI argument values/combinations
   - Protocol versions (v0/v1/v2)
   - Transport types (file://, https://, bundle)
   - Configuration options
   - Network packet contents
   - sysfs/proc values
   - Signal injection (SIGALRM, etc.)
   - Environment variables

4. **Generate inputs per branch**: For each if/else, switch/case, or #ifdef in the changed code, generate at least one input that takes each branch.

5. **Generate inputs per protocol/path variant**: If the code has separate paths for different protocols or transports, generate one input per variant.

6. **Generate fault-injection inputs** (adapted from `cpp-fault-inject-skill`):
   - For error-handling paths unreachable with normal inputs, source-level fault injection may be needed
   - Only use this when normal input variation cannot reach the target

### Input Documentation Format

For each generated test input, document:

```json
{
  "input_id": "I1",
  "finding_id": "PCA-0001",
  "target_lines": ["builtin/fetch.c:1629", "fetch-pack.c:496"],
  "branch_targeted": "v0 protocol path (else branch at fetch-pack.c:495)",
  "input_type": "cli_command",
  "command": "git -c protocol.version=0 fetch --negotiation-include=refs/tags/alpha_1 origin alpha_s",
  "expected_output": "Successful fetch, have line for alpha_1 in GIT_TRACE_PACKET",
  "reachability_signal": "grep 'fetch> have <oid>' trace output",
  "setup_required": "Dual-history repos (alpha+beta branches)",
  "dependencies": ["git binary at <path>"]
}
```

Save all inputs to `<TEST_RESULT_DIR>/phase3_inputs/test_inputs.json`.

### Input Diversity Checklist

Before proceeding to Phase 4, verify that inputs cover:

- [ ] Each compatibility type finding has at least one input
- [ ] Each conditional branch (if/else) has an input for each direction
- [ ] Each protocol version variant has an input (if applicable)
- [ ] Each transport type has an input (if applicable)
- [ ] Valid and invalid input values are tested
- [ ] Boundary and extreme values are included
- [ ] Error injection paths are covered (fault injection if needed)
- [ ] Different build configurations are considered (#ifdef guards)
- [ ] The type-specific oracle and minimum axes from `compatibility_type_test_matrix.md` are represented

### Input Dimension Matrix

To maximize behavioral coverage, generate applicable inputs across the 6
runtime dimensions below in addition to the mandatory type-contract axes. Do
not fabricate CLI or `BINARY` variants for library, ABI, proc/sys, syscall, or
ioctl/netlink findings that require a dedicated harness.

| Dimension | Description | Strategy | Examples |
|-----------|-------------|----------|---------|
| 1. CLI Arguments | Argument value/flag combinations | Cartesian product + boundary values | `cmd -a`, `cmd -a -b`, `cmd --verbose`, `cmd --help`, `cmd ''` |
| 2. Data Scale | Input size gradient | 0 → 1 → small → medium → large → MAX | empty input, single element, 1K, 1M, 1G of data |
| 3. Environment | Runtime condition variants | Terminal vs non-terminal, root vs user, online vs offline | `script -q -c 'cmd'` (pty), `cmd \| cat` (pipe), `sudo cmd` |
| 4. Abnormal Inputs | Edge-case and malformed values | Empty strings, overlong values, special characters, null bytes | `cmd ''`, `cmd $(printf '\x00')`, `cmd $(python3 -c 'print("A"*65536)')` |
| 5. Concurrency | Parallel execution and signal injection | Concurrent processes, signal delivery, timeouts | `cmd & cmd & wait`, `kill -ALRM $pid`, `timeout 1 cmd` |
| 6. Protocol Variants | Protocol version, transport, serialization | Each protocol version, each transport type, each output format | `cmd -o protocol=v2`, `cmd --json`, `cmd --xml`, `cmd file://` |

Generate the matrix with:

```bash
python3 "<TEST_SKILL_DIR>/scripts/input_dimensions.py" \
  --findings "<ANALYSIS_RESULT_DIR>/analysis.json" \
  --entries "<TEST_RESULT_DIR>/test-entry-work/test-entries.json" \
  --output "<TEST_RESULT_DIR>/phase3_inputs/test_inputs.json"
```

Review placeholder commands before execution, then run the matrix with `scripts/input_matrix.sh`.

---

## Phase 3.5: Compatibility Contract Verification

**Goal**: Before executing coverage tests, verify that the patch does not break behavioral contracts for each compatibility type. A "contract" is an executable assertion about observable behavior that must hold before AND after the patch.

**Prerequisites**: Requires baseline and patched builds prepared from `analysis.json.base_commit`, `patch.diff`, and `analysis_repo`. Build them in isolated directories during Phase 2.

**Steps**:

1. **Load findings** from Phase 1 (`impact_map.json`). Each finding has a `compatibility_type` that determines which contracts to apply.

2. **Select contract templates** by exact type using
   `references/compatibility_type_test_matrix.md`. It defines executable probes,
   minimum axes, canonical observations, and comparison rules for all 13 types.
   Do not use output equality as a substitute for ABI layout, syscall compat,
   resource lifetime, or performance-semantic evidence.

3. **For each contract**:
   - Determine test inputs (from Phase 3 dimension matrix)
   - Run BEFORE binary with each input → record output, exit code, strace
   - Run AFTER binary with the same input → record same
   - Compare results → PASS if identical, BREACH if different
   - For BREACH: classify the severity (HIGH if user-triggerable, MEDIUM if edge case)

4. **Record results** in `contract_verification.json`:
   ```json
   {
     "summary": { "total": 8, "passed": 7, "breached": 1 },
     "breaches": [
       {
         "finding_id": "PCA-0001",
         "contract": "output_format_stability",
         "input": "cmd --format aix",
         "before": "PID 1 /sbin/init",
         "after": "PID 1 /sbin/init ",
         "severity": "MEDIUM"
       }
     ]
   }
   ```

5. **Report**: Include contract verification results in the Phase 5 report. Zero contract breaches are necessary but not sufficient for a `compatible` conclusion; also require executed evidence, no blockers, and the configured coverage gate.

Run the type-aware executor after entries and inputs are finalized:

```bash
"<TEST_SKILL_DIR>/scripts/run_contracts.sh" \
  --findings "<ANALYSIS_RESULT_DIR>/analysis.json" \
  --entries "<TEST_RESULT_DIR>/test-entry-work/test-entries.json" \
  --test-inputs "<TEST_RESULT_DIR>/phase3_inputs/test_inputs.json" \
  --before-dir "<BEFORE_BUILD_DIR>" \
  --after-dir "<AFTER_BUILD_DIR>" \
  --output "<TEST_RESULT_DIR>/phase3_contracts"
```

The runner rejects unknown types. For supported types requiring a custom
harness, a missing probe becomes a precise `SKIP` and blocker rather than an
`UNSUPPORTED` result. `scripts/contract_templates.sh` remains a low-level
legacy library; type routing is owned by `scripts/compatibility_types.py` and
`scripts/run_contracts.py`.

---

## Phase 4: Execute with Coverage Instrumentation

### Step 4a: Instrumented Build

**CRITICAL: Always use `-O0` optimization.** Without `-O0`, the compiler may inline functions, reorder code, or eliminate branches, causing gcov to report misleading line numbers and false "uncovered" results. A line showing as uncovered under `-O2` may actually have been executed but reported at a different line number due to optimization.

If `-O0` causes build failures in some subsystems (common in kernel code), try `-Og` as a fallback. Document the optimization level used in the coverage report so line number accuracy caveats are clear.

**GCC (gcov) — user-space projects:**
```bash
make CFLAGS="-fprofile-arcs -ftest-coverage -O0 -g" LDFLAGS="-lgcov --coverage"
```

**GCC (gcov) — kernel modules:**
```bash
make KCFLAGS="-fprofile-arcs -ftest-coverage -O0 -g"
```
> **WARNING for kernel**: Some kernel subsystems will not build with `-O0` due to reliance on compiler optimizations (e.g., inline assembly constraints, `__builtin_constant_p`). If the build fails, fall back to `-Og`. If that also fails, use default `-O2` and document the caveat in the coverage report. Per-subsystem `KCFLAGS` (e.g., `make M=fs/f2fs KCFLAGS="-O0"`) may work where full-kernel `-O0` fails.

**Clang (llvm-cov)** — use if the project already uses clang:
```bash
make CFLAGS="-fprofile-instr-generate -fcoverage-mapping -O0 -g"
```

**Kernel-specific coverage setup**: See `references/kernel_gcov_guide.md` for the complete kernel gcov workflow — it requires Kconfig setup (`CONFIG_GCOV_KERNEL=y`), per-subsystem Makefile annotations (`GCOV_PROFILE_xxx.o := y`), debugfs mount in the VM, and `echo 0 > /sys/kernel/debug/gcov/reset` between tests.

Before running tests, clear any stale coverage data:
```bash
# User-space
find . -name "*.gcda" -delete

# Kernel (inside VM)
sudo su -c 'echo 0 > /sys/kernel/debug/gcov/reset'
```

### Step 4b: Execute Test Inputs

Run each test input from Phase 3 sequentially against the instrumented build. For each input:

1. Create a clean test environment (temp directory, no stale state)
2. Execute the input command/script
3. Capture stdout, stderr, and exit code
4. Verify the reachability signal appears in the output
5. Record the input's success/failure in `<TEST_RESULT_DIR>/phase4_execution/results.json`
6. If the input triggers a daemon or service, ensure cleanup (kill, stop)

### Step 4c: Collect Coverage Data

After all test inputs have executed:

**Using gcov:**
```bash
# For each changed source file
gcov -o <object_directory> <source_file>
# Extract coverage for specific lines
grep "<line>:" <source_file>.gcov
```

**Using llvm-cov** (adapted from `cpp-directed-input-verification-skill`):
```bash
llvm-profdata merge -o merged.profdata *.profraw
llvm-cov export <binary> -instr-profile=merged.profdata > coverage.json
```

**Coverage line interpretation:**
- `N: line` — N executions (COVERED)
- `#####: line` — 0 executions (NOT COVERED)
- `-: line` — non-executable (macro, comment, string continuation)

### Step 4c.5: Coverage Gate and Iteration Loop

**Goal**: Evaluate whether patch-line coverage meets the ≥80% threshold. If not, automatically loop back to Phase 3 to generate new inputs targeting the uncovered lines.

**Rationale**: A single pass of Phase 3 → Phase 4 rarely achieves full patch coverage. Complex guard conditions, protocol variants, and error-handling paths require multiple iterations. This gate closes the feedback loop automatically.

**Coverage calculation**: Patch impact coverage = `covered_executable_lines / total_executable_lines`. Exclude macro declarations, comments, blank lines, and architecturally unreachable lines.

**Iteration loop**:

1. **Calculate coverage** from gcov output of Step 4c.
2. **If ≥ 80%**: Proceed to Step 4d.
3. **If < 80%**:
   a. Identify uncovered lines (#####: prefix in gcov within patch range)
   b. For each uncovered line: constraint-intention analysis → classify as **coverable** / **architecturally unreachable** / **fault-injection needed**
   c. Generate new test inputs for each coverable line
   d. Execute only the new inputs (Step 4b procedure)
   e. Re-collect coverage (gcov merges counters automatically)
   f. Re-check gate (return to step 1)
4. **Maximum 3 iterations**. After 3, document remaining uncovered lines with root cause analysis.

Record results in `phase4_execution/coverage_iterations.json`.

### Step 4d: Behavior Comparison (Before/After)

**Goal**: Run every test input against BOTH the baseline (before) and patched (after) binaries, then compare outputs with the full Phase 3 input matrix.

**Rationale**: The full 6-dimension input matrix includes edge cases, abnormal inputs, protocol variants, and environment condition variants. A behavior diff that only checks simple inputs will miss the most interesting compatibility effects.

**Steps**:

1. **Prepare before binary**: Build a baseline from `base_commit` in a separate worktree; use patch reversal only when the repository metadata makes that safe and unambiguous:
   ```bash
   git apply -R <patch.diff> || git checkout HEAD~1 -- <changed_files>
   make -j$(nproc) CFLAGS="-O0 -g"
   cp <binary> <TEST_RESULT_DIR>/binary.before
   ```

2. **For each test input** from Phase 3's `test_inputs.json`:
   - Run BEFORE binary with input → capture stdout, stderr, exit code
   - Run AFTER (patched) binary with same input → capture same
   - Compare:
     ```bash
     diff <(./binary.before $args 2>&1) <(./binary.after $args 2>&1)
     ```

3. **Classify each diff** with the owning finding's validated
   `compatibility_type`. Output or exit-code symptoms alone must not reclassify
   an ABI, syscall, ioctl/netlink, resource, or performance finding. If one
   observation proves a distinct additional type, add a separately evidenced
   behavior difference and send it back to analysis rather than mutating the
   original finding.

4. **Cross-reference with coverage**: For each discovered behavioral diff, check gcov coverage to confirm:
   - Is the changed code path actually exercised? (gcov hit count > 0)
   - Is the diff caused by the patch? (gcov shows the changed lines were executed)

5. **Record results** in `phase4_execution/behavior_diff.json`:
   ```json
   {
     "input_id": "I3",
     "binary": "scp",
     "diff_type": "SIDE_EFFECT_CHANGE",
     "gcov_confirmed": true,
     "patch_lines_hit": ["scp.c:458"]
   }
   ```

Prefer `scripts/input_matrix.sh` with separately prepared before/after directories. The legacy `scripts/compare_behavior.sh` reverses a patch in place and therefore refuses to run unless `PCA_DISPOSABLE_WORKTREE=1`; use it only inside a dedicated disposable worktree. The comparison must answer which inputs cause observable changes and whether the relevant patch lines were actually reached.

---

## Phase 5: Coverage Report

Treat `<TEST_RESULT_DIR>/test-summary.json` as the only final result source. Do not hand-write the Markdown report. Populate the JSON from actual entry verification, input execution, contract, behavior-diff, and coverage artifacts, then run the deterministic formatter described below.

### Coverage Rate Calculation

**Patch impact coverage** = `covered_executable_lines / total_executable_lines`

Count only executable lines. Exclude:
- Macro declarations (OPT_STRING_LIST, etc.) — note as "compile-time covered"
- Comments
- String literal continuations from previous lines
- Blank lines

---

## Deterministic JSON output and report rendering

Follow `<TEST_SKILL_DIR>/schemas/test_output_schema.json`. Write all required fields, including target/environment metadata, exact summary counts, per-finding entries/contracts/coverage/behavior differences, blockers, artifact paths, and the compatibility conclusion. Both `finding_results[].compatibility_type` and `behavior_differences[].diff_type` must be one of the registered 13 types.

Use percentage values in `[0, 100]` for `patch_line_coverage_rate` and per-finding `coverage.rate`. Default `coverage_gate` to `80`.

Status rules:

- `passed`: all requested testing completed, zero contract breaches, no blockers, and the coverage gate passed.
- `failed`: an executed assertion, build, or contract failed; record the evidence.
- `partial`: some meaningful tests ran, but requested entries, environments, or coverage remain incomplete.
- `blocked`: no meaningful execution was possible and `blocked_or_not_run` explains the external requirement.

Keep `conclusion.backward_compatibility` separate from execution status. Use `compatible` only with sufficient executed evidence; use `incompatible` for confirmed observable contract breaches; otherwise use `inconclusive`. Coverage alone never proves compatibility.

After writing JSON, always run:

```bash
python3 "<TEST_SKILL_DIR>/scripts/finalize_test_report.py" \
  "<TEST_RESULT_DIR>/test-summary.json" \
  --output "<TEST_RESULT_DIR>/COVERAGE_REPORT.md"
```

The formatter validates count arithmetic, coverage rate, coverage gate, status consistency, finding structure, blockers, and artifact fields before rendering. If it fails, fix `test-summary.json` and rerun; never bypass validation or manually patch the Markdown output.

Set `report_language` to the user's language (`zh-CN` by default). The formatter automatically emits Chinese headings for `zh*` and English headings otherwise while preserving natural-language evidence from JSON.

At completion, report the paths to both files, the overall status, compatibility conclusion, contract breaches, coverage rate, and every blocked/not-run item.

---

## Key Principles

1. **Never speculate about code you haven't read.** Before claiming an input covers a line, read the source and verify the call chain actually reaches it.

2. **Different code paths need different inputs.** A single "happy path" test cannot cover error-handling branches, protocol variants, or transport-specific code. Think adversarially about what conditions each branch requires.

3. **Honest assessment over fabricated coverage.** If a line genuinely cannot be reached (dead code, hardware-dependent), document this clearly. Never fake coverage.

4. **Environment setup is part of the skill.** Do not silently skip required infrastructure. Set up isolated dependencies when authorized; otherwise record the exact requirement and request the needed confirmation.

5. **Coverage-guided refinement.** If Phase 4 reveals uncovered lines, go back to Phase 3 and generate new inputs targeting those specific lines. Iterate until no more lines can be covered with available environments.

6. **Document input diversity contribution.** For each input, document which previously-uncovered lines it newly covers. This shows the value of having diverse test inputs.
