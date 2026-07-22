---
name: package-profile-generator
description: "通过检查仓库布局、语言和领域接口面、远程仓库、分支、公共头文件以及 CLI、配置和协议文件，为代码仓库生成 Patch Compatibility Analyzer 包 Profile，并在 profiles/packages 下写入可审查的 YAML。当用户要求为仓库创建或更新 PCA 包 Profile、package profile 或软件包兼容性分析配置时使用。"
---

# Package Profile Generator

Use this subskill when the user asks to generate a new package profile for a
repository or reduce the cost of supporting many repos/branches.

## Inputs

- `repo`: local repository path, required.
- `profile_name`: optional. If omitted, infer from origin remote or repo folder.
- `install`: optional. If true, write to
  `patch-compatibility-analysis/profiles/packages/<profile_name>.yaml`.
- `output`: optional explicit YAML path.

## Workflow

1. Run the deterministic generator:

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/profile_generator.py" \
     --repo "<repo>" \
     --name "<profile_name>" \
     --install
   ```

   Omit `--install` to print the draft to stdout. Use `--output <path>` to
   write elsewhere.

2. Review the generated `extends` list:

   - C/C++ repos should usually include `default`, `c_family`, and `cli_tool`.
   - Python repos should include `default` and `python_base`.
   - Go repos should include `default` and `go_base`.
   - Ruby repos should include `default` and `ruby_base`.
   - Daemons, servers, protocol stacks, DBus services, and network tools should
     include `daemon_network`.
   - Kernel-like repos with `include/uapi` and Kconfig/kernel layout should
     include `kernel_base`.

3. Review generated `api_surfaces`:

   - Narrow overly broad `paths`.
   - Replace placeholder patterns such as `API`, `EXPORT`, or `PUBLIC` with real
     project macros/functions.
   - Set `public: false` for internal-only directories.
   - Set `test_priority` by downstream testing value, not by bug likelihood.
   - Add `variants` for downstream remotes/branches instead of cloning the whole
     profile.

4. Validate that the profile resolves:

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/profile_loader.py" \
     --show "<profile_name>" \
     --repo "<repo>" \
     --output "<tmp-effective-profile.yaml>"
   ```

5. Smoke test on a real patch:

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/diff_parser.py" \
     --repo "<repo>" \
     --patch "<patch.diff>" \
     --profile "<profile_name>" \
     --output "<tmp-candidates.json>"
   ```

6. If the generated profile is installed, mention the exact path and summarize:

   - inherited layers
   - package-specific surfaces
   - detected variants
   - manual review items

## Rules

- The generated profile is a draft. Do not claim it is complete until it has
  been reviewed against package docs, installed headers, CLI help, ABI metadata,
  and representative patches.
- Prefer variants for branch/downstream differences. Do not create a separate
  full profile when an overlay is enough.
- Do not put generated profiles in `profiles/base`, `profiles/languages`,
  `profiles/domains`, or `profiles/platforms`; package-specific output belongs
  in `profiles/packages`.
