# Patch Compatibility Analyzer Report Draft

- Source repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup`
- Patched analysis worktree: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/_worktrees/patched`
- Patch ID: `48f07d3fe9254520dc7371666fb517e7aa201aeb`
- Base ref: `48f07d3fe9254520dc7371666fb517e7aa201aeb^`
- Base commit: `c4c2cd113c7fa06c3573e8945f186abecb8fd278`
- Patch apply status: `applied`
- Profile: `libsoup`
- Effective profile: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/effective-profile.yaml`
- Low-context agent input: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/analysis-context.json`
- Artifact dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050`
- Analysis mode: `normal`
- Mode reason: below heavy thresholds
- Changed files: 3
- Candidate hunks: 8
- Static call chains: 0

## Patch Metrics

| metric | value |
|---|---:|
| `patch_bytes` | 3975 |
| `patch_lines` | 108 |
| `raw_hunks` | 8 |
| `candidate_hunks` | 8 |
| `changed_files` | 3 |
| `churn` | 27 |
| `candidate_context_bytes` | 15342 |
| `candidates_json_bytes` | 37405 |

## Source-Context Rules

- Post-patch source search/read root: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/_worktrees/patched`.
- Pre-patch source read command: `git -C /data2/wanghy/hyl_part3/PCIA-evaluate/repo/libsoup show c4c2cd113c7fa06c3573e8945f186abecb8fd278:<path>`.
- Rebuild worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --ensure-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/analysis.json`.
- Optional cleanup only when no later testing/fuzzing work needs the worktree: `/data2/wanghy/conda_dir/bin/python3 /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --cleanup-worktree /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/analysis.json`.

## Candidate Hunks

- `HUNK-0001` `libsoup/cookies/soup-cookie-jar.c` old `321-327` new `321-327` symbol `get_cookies, host` surface `user_visible_output, http_semantics`
- `HUNK-0002` `libsoup/cookies/soup-cookie-jar.c` old `330-337` new `330-343` symbol `get_cookies, host, domain, cur, g_strdup_printf, s` surface `user_visible_output, http_semantics`
- `HUNK-0003` `libsoup/cookies/soup-cookie.c` old `175-183` new `175-181` symbol `parse_one_cookie, SoupCookie, cookie, g_return_val_if_fail, origin, NULL` surface `http_semantics`
- `HUNK-0004` `libsoup/cookies/soup-cookie.c` old `394-400` new `392-398` symbol `soup_cookie_new, origin, nullable, of, the, cookie, cookie_new_internal` surface `user_visible_output, persistence_state, http_semantics`
- `HUNK-0005` `libsoup/cookies/soup-cookie.c` old `414-419` new `412-420` symbol `soup_cookie_new, g_return_val_if_fail, cookie, NULL, origin, g_uri_get_host, soup_cookie_parse` surface `user_visible_output, persistence_state, http_semantics`
- `HUNK-0006` `libsoup/cookies/soup-cookie.c` old `1061-1067` new `1062-1069` symbol `soup_cookie_applies_to_uri, g_return_val_if_fail, cookie, NULL, FALSE, uri` surface `http_semantics`
- `HUNK-0007` `libsoup/soup-message.c` old `1849-1855` new `1849-1855` symbol `soup_message_set_first_party, g_return_if_fail, first_party, NULL, SOUP_URI_IS_VALID` surface `http_semantics`
- `HUNK-0008` `libsoup/soup-message.c` old `1912-1918` new `1912-1917` symbol `soup_message_set_site_for_cookies, g_return_if_fail, site_for_cookies, NULL, SOUP_URI_IS_VALID` surface `network_protocol, http_semantics`

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

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/orchestrator.py --aggregate-shards /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/analysis.json`

Validate final output with:

`python /data2/wanghy/hyl_part3/PCIA-evaluate/.opencode/skills/patch-compatibility-utils/patch-compatibility-analysis/scripts/validate_analysis.py /data2/wanghy/hyl_part3/PCIA-evaluate/results/20260724_123944/PCIA-P050/analysis.json`
