# Patch Compatibility Analyzer Report Draft

- Source repo: `/home/soong/pca_benchmark/_repos/cpython`
- Patched analysis worktree: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/_worktrees/patched`
- Patch ID: `1d4e965829eef4cdb089a984fda21ca465a1f534`
- Base ref: `baf11a4e9a9d6542a1f3a891c670da36c89cbc96`
- Base commit: `baf11a4e9a9d6542a1f3a891c670da36c89cbc96`
- Patch apply status: `applied`
- Profile: `cpython`
- Effective profile: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/effective-profile.yaml`
- Low-context agent input: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis-context.json`
- Artifact dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016`
- Analysis mode: `heavy`
- Mode reason: soft threshold exceeded; candidates_json_bytes=114903 >= 100000
- Changed files: 5
- Candidate hunks: 23
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 13161 |
| `patch_lines` | 301 |
| `raw_hunks` | 23 |
| `candidate_hunks` | 23 |
| `changed_files` | 5 |
| `churn` | 94 |
| `candidate_context_bytes` | 52432 |
| `candidates_json_bytes` | 114903 |

## Heavy Shards

- Shard plan: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/shards.json`
- Shard workspace: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/shards`
- Shard count: 9

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `config_keys` | 1 | 1 | 2140 | `shards/shard-0001.json` |
| `SHARD-0002` | `internal_or_unknown` | 3 | 2 | 4432 | `shards/shard-0002.json` |
| `SHARD-0003` | `internal_or_unknown` | 3 | 1 | 7626 | `shards/shard-0003.json` |
| `SHARD-0004` | `public_headers` | 1 | 1 | 2747 | `shards/shard-0004.json` |
| `SHARD-0005` | `python_exceptions` | 2 | 1 | 5065 | `shards/shard-0005.json` |
| `SHARD-0006` | `tests` | 4 | 1 | 9370 | `shards/shard-0006.json` |
| `SHARD-0007` | `tests` | 5 | 2 | 10488 | `shards/shard-0007.json` |
| `SHARD-0008` | `user_visible_output` | 3 | 1 | 8370 | `shards/shard-0008.json` |
| `SHARD-0009` | `user_visible_output` | 1 | 1 | 2194 | `shards/shard-0009.json` |

## Source-Context Rules

- Post-patch source search/read root: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/_worktrees/patched`.
- Pre-patch source read command: `git -C /home/soong/pca_benchmark/_repos/cpython show baf11a4e9a9d6542a1f3a891c670da36c89cbc96:<path>`.
- Rebuild worktree: `/home/soong/miniconda3/bin/python3 /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/home/soong/miniconda3/bin/python3 /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `Include/internal/pycore_interp_structs.h` old `349-355` new `349-363` symbol `_import_state, The, set, stored, in, sys, PyState_AddModule` surface `public_headers, config_keys, c_api`
- `HUNK-0002` `Lib/test/test_lazy_import/__init__.py` old `38-45` new `38-44` symbol `test_basic_unused, self, assertIn, test, test_lazy_import, data` surface `tests, python_exceptions`
- `HUNK-0003` `Lib/test/test_lazy_import/__init__.py` old `49-55` new `48-54` symbol `test_sys_lazy_modules, self, assertIn, test, test_lazy_import, data` surface `tests, python_exceptions`
- `HUNK-0004` `Lib/test/test_lazy_import/__init__.py` old `677-684` new `676-683` symbol `my_filter, sys, lazy_modules, should, be, a` surface `tests, python_exceptions, user_visible_output, exceptions`
- `HUNK-0005` `Lib/test/test_lazy_import/__init__.py` old `687-694` new `686-692` symbol `test_lazy_modules_tracks_lazy_imports, assert, test, test_lazy_import, data, basic2` surface `tests, python_exceptions, user_visible_output`
- `HUNK-0006` `Lib/test/test_lazy_import/__init__.py` old `1137-1151` new `1135-1148` symbol `test_module_added_to_lazy_modules_on_lazy_import, assert, test, test_lazy_import, data, basic2` surface `tests, cli_options`
- `HUNK-0007` `Lib/test/test_lazy_import/__init__.py` old `1158-1165` new `1155-1162` symbol `test_module_added_to_lazy_modules_on_lazy_import, Basic, test, that, sys, lazy_modules, test_lazy_modules_is_per_interpreter` surface `tests, cli_options`
- `HUNK-0008` `Lib/test/test_lazy_import/__init__.py` old `1168-1177` new `1165-1170` symbol `test_lazy_module_without_children_is_tracked, assert, sys, lazy_modules, json, set, f` surface `tests, cli_options`
- `HUNK-0009` `Lib/test/test_lazy_import/__init__.py` old `1938-1944` new `1931-1937` symbol `create_lazy_imports, assert, isinstance, sys, lazy_modules, set` surface `tests, python_exceptions, user_visible_output`
- `HUNK-0010` `Lib/test/test_lazy_import/__main__.py` old `0--1` new `1-3` symbol `import, unittest, main, test, test_lazy_import` surface `tests, python_cli, cli`
- `HUNK-0011` `Misc/NEWS.d/next/Core_and_Builtins/2026-05-18-18-36-28.gh-issue-148587.-RD3z5.rst` old `0--1` new `1-1` symbol `sys, lazy_modules, is, now, a, set` surface `unknown`
- `HUNK-0012` `Python/import.c` old `94-99` new `94-101` symbol `_inittab, define, LAZY_PENDING_SUBMODULES, interp, imports, lazy_pending_submodules, is_interpreter_isolated` surface `config_keys`
- `HUNK-0013` `Python/import.c` old `271-278` new `273-283` symbol `import_get_module, assert, LAZY_MODULES, interp, NULL, LAZY_PENDING_SUBMODULES, _PyImport_InitLazyModules` surface `unknown`
- `HUNK-0014` `Python/import.c` old `280-285` new `285-291` symbol `Py_CLEAR, LAZY_PENDING_SUBMODULES, interp, _PyImport_ClearLazyModules` surface `unknown`
- `HUNK-0015` `Python/import.c` old `4338-4344` new `4344-4350` symbol `get_mod_dict, ensure_lazy_pending_submodules, PyDictObject, lazy_modules, PyObject, parent, PyObject_GetAttr` surface `user_visible_output`
- `HUNK-0016` `Python/import.c` old `4357-4362` new `4363-4371` symbol `ensure_lazy_submodules, Ensures, that, we, have, a, module, Py_END_CRITICAL_SECTION` surface `unknown`
- `HUNK-0017` `Python/import.c` old `4368-4383` new `4377-4392` symbol `register_lazy_on_parent, PyObject, lazy_pending_submodules, LAZY_PENDING_SUBMODULES, interp, assert, ensure_lazy_pending_submodules, LAZY_MODULES` surface `unknown`
- `HUNK-0018` `Python/import.c` old `4399-4406` new `4408-4415` symbol `register_lazy_on_parent, PyObject, lazy_submodules, ensure_lazy_pending_submodules, PyDictObject, lazy_pending_submodules, Py_XDECREF` surface `unknown`
- `HUNK-0019` `Python/import.c` old `4463-4468` new `4472-4485` symbol `register_from_lazy_on_parent, Add, the, module, name, to, LAZY_MODULES` surface `python_exceptions, exceptions`
- `HUNK-0020` `Python/import.c` old `4554-4559` new `4571-4583` symbol `_PyImport_LazyImportModuleLevelObject, Add, the, module, name, to, LAZY_MODULES, Py_DECREF` surface `user_visible_output`
- `HUNK-0021` `Python/import.c` old `4790-4795` new `4814-4820` symbol `_PyImport_ClearCore, Py_CLEAR, interp, imports, lazy_pending_submodules` surface `python_exceptions`
- `HUNK-0022` `Python/import.c` old `5637-5647` new `5662-5674` symbol `_imp__set_lazy_attributes_impl, PyObject, lazy_pending_modules, LAZY_PENDING_SUBMODULES, tstate, interp, assert, LAZY_MODULES` surface `user_visible_output`
- `HUNK-0023` `Python/import.c` old `5660-5667` new `5687-5693` symbol `_imp__set_lazy_attributes_impl, PyDict_DelItem, lazy_pending_modules, name, once, a, module, it, Py_END_CRITICAL_SECTION` surface `user_visible_output`

## Static Call Chains

- Not generated yet. Call chains are attached only after final findings exist.

## Agent Adjudication Requirements

- This report is deterministic evidence, not the final compatibility decision.
- Start from analysis-context.json. It is the bounded context for agent adjudication and includes focused source excerpts.
- Do not reopen large source files to locate a changed function already present in analysis-context.json.
- Do not scan repo roots, patch-list directories, output directories, or profile trees.
- Final findings must include only confirmed compatibility changes.
- Every finding must include code line locations and at least one evidence snippet.
- In heavy mode, analyze each shard independently, then aggregate shard results with:

`python /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis.json`

Validate final output with:

`python /home/soong/pca_benchmark/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P016/analysis.json`
