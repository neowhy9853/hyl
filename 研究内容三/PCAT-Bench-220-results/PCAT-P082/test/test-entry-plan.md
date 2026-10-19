# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P022/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/cpython`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P022/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P022/compatibility-testing`
- Patch ID: `6ca5cdba185aeb3b7f72ae0dd61b6a9685d8c416`
- Task count: 3

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `ABI_CHANGE`
- API: `struct_type` `PyCriticalSection / PyCriticalSection2 struct layout`
- Target: `Include/critical_section.h:4-94` `PyCriticalSection / PyCriticalSection2`
- Entry kind: `abi_dump_and_consumer_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `binary_abi_compatibility` / `success`
- Observation: symbol/version manifest plus size, alignment, offset, enum, and calling ABI
- Input axes: exported symbols, symbol versions, type layouts, old binary consumer

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0002 / PCA-0002

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `exported_function` `PyCriticalSection_Begin / PyCriticalSection_End / PyCriticalSection2_Begin / PyCriticalSection2_End`
- Target: `Include/critical_section.h:59-69` `PyCriticalSection_Begin / PyCriticalSection_End / PyCriticalSection2_Begin / PyCriticalSection2_End`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

## PCA-TE-0003 / PCA-0003

- Priority: `high`
- Type: `API_SIGNATURE_CHANGE`
- API: `macro` `Py_BEGIN_CRITICAL_SECTION / Py_END_CRITICAL_SECTION / Py_BEGIN_CRITICAL_SECTION2 / Py_END_CRITICAL_SECTION2`
- Target: `Include/critical_section.h:71-97` `Py_BEGIN_CRITICAL_SECTION / Py_END_CRITICAL_SECTION / Py_BEGIN_CRITICAL_SECTION2 / Py_END_CRITICAL_SECTION2`
- Entry kind: `downstream_compile_link_harness`
- Preferred artifact: project-native regression test or minimal command
- Trigger surface: use the nearest public entry point or existing test fixture that reaches the changed symbol
- Contract: `api_signature_compatibility` / `success`
- Observation: old downstream source compiles and links against both versions
- Input axes: old declarations, language modes, compiler flags, link modes

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

