# PCA 测试入口挖掘任务

- Analysis: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P014/analysis.json`
- Repo: `/home/soong/pca_benchmark/_repos/cpython`
- Analysis repo: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P014/_worktrees/patched`
- Test result dir: `/home/soong/pca_benchmark/opencode-results/pcat-cpython-deepseek-v4-flash-max/PCAT-P014/compatibility-testing`
- Patch ID: `7de4fcd44585f572acbcee23f5c7018b2b3f0983`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `medium`
- Type: `OUTPUT_FORMAT_CHANGE`
- API: `public_method` `xml.etree.ElementTree.Element.itertext`
- Target: `Modules/_elementtree.c:2297-2307` `elementiter_next`
- Entry kind: `golden_output_probe`
- Preferred artifact: unit test, small linked program, or language-level test case
- Trigger surface: call the public API with old/new contract boundary inputs and assert behavior
- Contract: `output_format_stability` / `exact`
- Observation: byte-level stdout/stderr or parsed structured-output schema
- Input axes: machine format, human format, TTY/pipe, locale, extreme values

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

