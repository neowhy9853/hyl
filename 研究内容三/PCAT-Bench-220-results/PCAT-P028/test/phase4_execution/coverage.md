# GCOV Patch Coverage Report

**Project directory**: `/tmp/pca-git-after`

## midx-write.c

| Line | Status | Count | Code |
|------|--------|-------|------|
| 1248 | — NON-CODE | -1 | `const char *preferred_pack_name;` |
| 1250 | — NON-CODE | -1 | `const char *incremental_base;` |
| 1340 | ✅ COVERED | 66 | `if (opts->incremental_base) {` |
| 1341 | ✅ COVERED | 4 | `if (!strcmp(opts->incremental_base, "none")) {` |
| 1342 | ✅ COVERED | 1 | `ctx.base_midx = NULL;` |
| 1344 | ✅ COVERED | 5 | `while (ctx.base_midx) {` |
| 1345 | ✅ COVERED | 4 | `const char *cmp = midx_get_checksum_hex(ctx.base_midx);` |
| 1346 | ✅ COVERED | 4 | `if (!strcmp(opts->incremental_base, cmp))` |
| 1347 | ✅ COVERED | 2 | `break;` |
| 1349 | ✅ COVERED | 2 | `ctx.base_midx = ctx.base_midx->base_midx;` |
| 1352 | ✅ COVERED | 3 | `if (!ctx.base_midx) {` |
| 1353 | ✅ COVERED | 1 | `error(_("could not find base MIDX '%s'"),` |
| 1355 | ✅ COVERED | 1 | `goto cleanup;` |

**midx-write.c**: 11/11 (100.0%)

## builtin/multi-pack-index.c

| Line | Status | Count | Code |
|------|--------|-------|------|
| 68 | — NON-CODE | -1 | `const char *incremental_base;` |
| 157 | — NON-CODE | -1 | `OPT_STRING(0, "base", &opts.incremental_base, N_("check...` |
| 160 | — NON-CODE | -1 | `N_("write a new incremental MIDX"), MIDX_WRITE_INCREMEN...` |
| 161 | — NON-CODE | -1 | `OPT_NEGBIT(0, "write-chain-file", &opts.flags,` |
| 198 | ✅ COVERED | 57 | `if (opts.incremental_base &&` |
| 199 | ✅ COVERED | 3 | `!(opts.flags & MIDX_WRITE_NO_CHAIN)) {` |
| 200 | ✅ COVERED | 1 | `error(_("cannot use --base without --no-write-chain-fil...` |
| 201 | ✅ COVERED | 1 | `usage_with_options(builtin_multi_pack_index_write_usage...` |
| 214 | ✅ COVERED | 2 | `ret = write_midx_file_only(source, &packs,` |
| 215 | — NON-CODE | -1 | `opts.preferred_pack,` |
| 216 | ✅ COVERED | 2 | `opts.refs_snapshot,` |
| 217 | — NON-CODE | -1 | `opts.incremental_base, opts.flags);` |
| 245 | — NON-CODE | -1 | `OPT_STRING(0, "base", &opts.incremental_base, N_("check...` |
| 248 | — NON-CODE | -1 | `MIDX_WRITE_BITMAP | MIDX_WRITE_REV_INDEX),` |
| 249 | — NON-CODE | -1 | `OPT_BIT(0, "incremental", &opts.flags,` |
| 308 | ✅ COVERED | 11 | `ret = write_midx_file_compact(source, from_midx, to_mid...` |
| 309 | — NON-CODE | -1 | `opts.incremental_base, opts.flags);` |

**builtin/multi-pack-index.c**: 7/7 (100.0%)

## midx.h

⚠️ gcov file not found — not compiled with coverage flags?

## Summary

| File | Exec Lines | Covered | Rate |
|------|-----------|---------|------|
| midx-write.c | 11 | 11 | 100.0% |
| builtin/multi-pack-index.c | 7 | 7 | 100.0% |
| **Total** | **18** | **18** | **100.0%** |

**Patch impact coverage**: 18/18 (100.0%)