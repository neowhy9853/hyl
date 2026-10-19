# PCA 测试入口挖掘任务

- Analysis: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/analysis.json`
- Repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/repo/go`
- Analysis repo: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/_worktrees/patched`
- Test result dir: `/data2/wanghy/hyl_part3/PCIA-evaluate/results/20260723_222955/PCIA-P038/compatibility-testing`
- Patch ID: `5bbd22ff78daf010c5bd19c466a0c45ac78503d4`
- Task count: 1

所有补丁后源码检索都必须使用 Analysis repo。清理后的 worktree 需要先用同级分析子 skill 的 orchestrator.py --ensure-worktree 重建。

## PCA-TE-0001 / PCA-0001

- Priority: `high`
- Type: `SIDE_EFFECT_CHANGE`
- API: `config_key` `net/http.Server.ReadHeaderTimeout`
- Target: `src/net/http/server.go:1970-1980` `c.serve`
- Entry kind: `state_and_side_effect_probe`
- Preferred artifact: temporary config file plus command invocation
- Trigger surface: load a minimal config/env setting that reaches the changed parser or behavior
- Contract: `side_effect_manifest_stability` / `exact`
- Observation: canonical before/after state, I/O, process, network, and concurrency manifest
- Input axes: normal path, error path, state snapshot, concurrency, signal interruption

Expected agent output: command or code artifact, setup/build steps, reachability signal, input values, contract_probe, and limitations.

