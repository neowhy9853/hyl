# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/_worktrees/patched`
- Patch ID: `ae786f44ace1712be2b3899806202591cf074905`
- Base ref: `ae786f44ace1712be2b3899806202591cf074905^`
- Base commit: `07279b0c7e1eb3c931c1ae201574a58609e0f6bc`
- Patch apply status: `applied`
- Profile: `c_project`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049`
- Analysis mode: `heavy`
- Mode reason: hard threshold exceeded; patch_lines=1533 >= 1000; candidates_json_bytes=232251 >= 180000
- Changed files: 14
- Candidate hunks: 36
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 43514 |
| `patch_lines` | 1533 |
| `raw_hunks` | 36 |
| `candidate_hunks` | 36 |
| `changed_files` | 14 |
| `churn` | 1160 |
| `candidate_context_bytes` | 106783 |
| `candidates_json_bytes` | 232251 |

## Heavy Shards

- Shard plan: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/shards.json`
- Shard workspace: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/shards`
- Shard count: 14

| shard | surface | hunks | files | context bytes | artifact |
|---|---|---:|---:|---:|---|
| `SHARD-0001` | `callbacks` | 1 | 1 | 6861 | `shards/shard-0001.json` |
| `SHARD-0002` | `config_keys` | 3 | 2 | 6040 | `shards/shard-0002.json` |
| `SHARD-0003` | `config_keys` | 2 | 2 | 9842 | `shards/shard-0003.json` |
| `SHARD-0004` | `internal_or_unknown` | 5 | 2 | 8770 | `shards/shard-0004.json` |
| `SHARD-0005` | `internal_or_unknown` | 2 | 1 | 8723 | `shards/shard-0005.json` |
| `SHARD-0006` | `internal_or_unknown` | 3 | 1 | 11317 | `shards/shard-0006.json` |
| `SHARD-0007` | `internal_or_unknown` | 2 | 1 | 5515 | `shards/shard-0007.json` |
| `SHARD-0008` | `internal_or_unknown` | 2 | 2 | 2075 | `shards/shard-0008.json` |
| `SHARD-0009` | `logging` | 1 | 1 | 1595 | `shards/shard-0009.json` |
| `SHARD-0010` | `public_headers` | 4 | 4 | 7206 | `shards/shard-0010.json` |
| `SHARD-0011` | `public_headers` | 5 | 3 | 8109 | `shards/shard-0011.json` |
| `SHARD-0012` | `user_visible_output` | 3 | 1 | 14345 | `shards/shard-0012.json` |
| `SHARD-0013` | `user_visible_output` | 2 | 1 | 11232 | `shards/shard-0013.json` |
| `SHARD-0014` | `user_visible_output` | 1 | 1 | 5153 | `shards/shard-0014.json` |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup show 07279b0c7e1eb3c931c1ae201574a58609e0f6bc:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `ChangeLog` old `1-3` new `1-24` symbol `Dan, Winship, danw, gnome, org, libsoup` surface `config_keys, user_visible_output`
- `HUNK-0002` `configure.in` old `199-204` new `199-211` symbol `PKG_CHECK_MODULES, SQLITE, sqlite3, AC_MSG_ERROR, dnl, Could` surface `config_keys, user_visible_output`
- `HUNK-0003` `configure.in` old `207-212` new `214-221` symbol `AC_SUBST, SQLITE_CFLAGS, SQLITE_LIBS` surface `config_keys, user_visible_output`
- `HUNK-0004` `libsoup/Makefile.am` old `13-18` new `13-19` symbol `SQLITE_CFLAGS` surface `logging`
- `HUNK-0005` `libsoup/Makefile.am` old `56-61` new `57-63` symbol `soup, cookie, jar, text, h` surface `unknown`
- `HUNK-0006` `libsoup/Makefile.am` old `118-123` new `120-126` symbol `soup, cookie, jar, text, c` surface `unknown`
- `HUNK-0007` `libsoup/Makefile.am` old `161-166` new `164-170` symbol `soup, cookie, jar, sqlite, h` surface `unknown`
- `HUNK-0008` `libsoup/Makefile.am` old `168-176` new `172-183` symbol `libsoup_gnome_2_4_la_LIBADD, libsoup, la, SQLITE_LIBS, soup, cookie` surface `unknown`
- `HUNK-0009` `libsoup/soup-cookie-jar-sqlite.c` old `0--1` new `1-286` symbol `Mode, C, tab, width, indent, tabs` surface `callbacks, config_keys, user_visible_output, plugin_api`
- `HUNK-0010` `libsoup/soup-cookie-jar-sqlite.h` old `0--1` new `1-40` symbol `Mode, C, tab, width, indent, tabs, Copyright` surface `public_headers`
- `HUNK-0011` `libsoup/soup-cookie-jar-text.c` old `0--1` new `1-349` symbol `Mode, C, tab, width, indent, tabs` surface `config_keys, user_visible_output`
- `HUNK-0012` `libsoup/soup-cookie-jar-text.h` old `0--1` new `1-43` symbol `Mode, C, tab, width, indent, tabs, Copyright` surface `public_headers`
- `HUNK-0013` `libsoup/soup-cookie-jar.c` old `15-20` new `15-21` symbol `include, soup, marshal, h, Copyright` surface `config_keys`
- `HUNK-0014` `libsoup/soup-cookie-jar.c` old `45-55` new `46-77` symbol `G_DEFINE_TYPE_WITH_CODE, CHANGED, LAST_SIGNAL, guint, signals, PROP_0, constructed, set_property, G_IMPLEMENT_INTERFACE` surface `unknown`
- `HUNK-0015` `libsoup/soup-cookie-jar.c` old `59-64` new `81-94` symbol `soup_cookie_jar_init, constructed, GObject, object, SoupCookieJarPrivate, priv, SOUP_COOKIE_JAR_GET_PRIVATE` surface `unknown`
- `HUNK-0016` `libsoup/soup-cookie-jar.c` old `81-87` new `111-139` symbol `soup_cookie_jar_class_init, object_class, constructed, set_property, get_property, signals, g_signal_new, G_STRUCT_OFFSET, g_type_class_add_private` surface `unknown`
- `HUNK-0017` `libsoup/soup-cookie-jar.c` old `93-102` new `145-189` symbol `soup_cookie_jar_session_feature_init, set_property, GObject, object, guint, prop_id, SOUP_COOKIE_JAR_GET_PRIVATE` surface `unknown`
- `HUNK-0018` `libsoup/soup-cookie-jar.c` old `106-123` new `193-214` symbol `soup_cookie_jar_new, Does, nothing, obsolete, soup_cookie_jar_changed, SoupCookieJar, SOUP_COOKIE_JAR_GET_PRIVATE, g_object_new` surface `unknown`
- `HUNK-0019` `libsoup/soup-cookie-jar.c` old `148-153` new `239-245` symbol `soup_cookie_jar_get_cookies, GSList, new_head, cookies_to_remove, NULL, p` surface `user_visible_output`
- `HUNK-0020` `libsoup/soup-cookie-jar.c` old `161-174` new `253-275` symbol `soup_cookie_jar_get_cookies, new_head, domain_cookies, g_hash_table_lookup, priv, domains, cookie, g_return_val_if_fail` surface `user_visible_output`
- `HUNK-0021` `libsoup/soup-cookie-jar.c` old `176-181` new `277-290` symbol `soup_cookie_jar_get_cookies, p, cookies_to_remove, next, SoupCookie, cookie, soup_cookie_jar_changed, soup_cookie_free, g_slist_free, g_hash_table_insert` surface `user_visible_output`
- `HUNK-0022` `libsoup/soup-cookie-jar.c` old `185-247` new `294-364` symbol `soup_cookie_jar_get_cookies, soup_cookie_jar_add_cookie, jar, a, SoupCookieJar, cookie, g_slist_free` surface `user_visible_output`
- `HUNK-0023` `libsoup/soup-cookie-jar.c` old `264-271` new `381-388` symbol `soup_cookie_jar_set_cookie, will, steal, or, free, soup_cookie, soup_cookie_jar_add_cookie, g_return_if_fail` surface `user_visible_output`
- `HUNK-0024` `libsoup/soup-cookie-jar.c` old `277-283` new `394-400` symbol `process_set_cookie_header, soup_cookie_jar_add_cookie, jar, nc, data, set_cookie` surface `user_visible_output`
- `HUNK-0025` `libsoup/soup-cookie-jar.c` old `311-313` new `428-502` symbol `request_unqueued, soup_cookie_jar_all_cookies, jar, a, SoupCookieJar, Constructs, cookie` surface `unknown`
- `HUNK-0026` `libsoup/soup-cookie-jar.h` old `25-51` new `25-67` symbol `save, SoupCookieJar, jar, signals, changed, SoupCookie, Copyright` surface `public_headers`
- `HUNK-0027` `libsoup/soup-cookie.c` old `122-127` new `122-165` symbol `GType, soup_cookie_get_type, gsize, type_volatile, g_once_init_enter, type, g_intern_static_string, soup_cookie_copy, code` surface `unknown`
- `HUNK-0028` `libsoup/soup-cookie.c` old `132-137` new `170-177` symbol `domain_matches, g_ascii_strcasecmp, domain, host, TRUE` surface `unknown`
- `HUNK-0029` `libsoup/soup-cookie.c` old `883-887` new `923-938` symbol `soup_cookie_applies_to_uri, strncmp, cookie, path, uri, plen, soup_cookie_equal, g_return_val_if_fail` surface `unknown`
- `HUNK-0030` `libsoup/soup-cookie.h` old `20-25` new `20-28` symbol `_SoupCookie, GType, soup_cookie_get_type, define, SOUP_TYPE_COOKIE` surface `public_headers`
- `HUNK-0031` `libsoup/soup-cookie.h` old `32-37` new `35-41` symbol `soup_cookie_new, SoupCookie, soup_cookie_copy, cookie, soup_cookie_get_type` surface `public_headers`
- `HUNK-0032` `libsoup/soup-cookie.h` old `53-58` new `57-67` symbol `soup_cookie_set_http_only, gboolean, soup_cookie_applies_to_uri, SoupCookie, cookie, SoupURI, soup_cookie_equal` surface `public_headers`
- `HUNK-0033` `libsoup/soup-cookie.h` old `67-75` new `76-81` symbol `soup_cookies_free, gboolean, soup_cookie_applies_to_uri, SoupCookie, cookie, SoupURI` surface `public_headers`
- `HUNK-0034` `libsoup/soup-gnome.h` old `8-13` new `8-14` symbol `include, libsoup, soup, cookie, jar, sqlite, Copyright` surface `public_headers`
- `HUNK-0035` `libsoup/soup-marshal.list` old `4-7` new `4-8` symbol `NONE, BOXED` surface `unknown`
- `HUNK-0036` `libsoup/soup.h` old `17-22` new `17-23` symbol `include, libsoup, soup, cookie, jar, text, Copyright` surface `public_headers`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P049/analysis.json`
