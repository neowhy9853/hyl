#!/usr/bin/env python3
"""Run one case through intent -> verified port -> compatibility analysis/tests.

Python 3.10+, Git and OpenCode. No third-party Python package required here.
Each child Skill retains its own dependency requirements and output contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
TAGS = {"BugFix", "CVE", "Optimize", "Feature", "Refactor", "CleanUp", "Doc",
        "Typo修复", "TestCode", "资源泄露&crash补丁", "其他"}
SKILLS = {
    "patch-intent-analysis": ROOT / "研究内容一/patch-intent-analysis",
    **{name: ROOT / "研究内容二/skills" / name for name in (
        "security-patch-port", "patch-port-analysis", "patch-port-apply",
        "patch-port-validation", "patch-dependency-discovery")},
    "patch-compatibility-utils": ROOT / "研究内容三/patch-compatibility-utils",
}
STAGES = ("intent", "port", "compatibility")


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"缺少普通产物文件：{path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"产物不是 JSON 对象：{path}")
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment():
    return {k: v for k, v in os.environ.items()
            if not k.startswith(("GIT_", "OPENCODE_"))}


def git(repo, *args, data=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=environment(), check=True, timeout=300).stdout


def resolve(repo, ref):
    return git(repo, "rev-parse", "--verify", "--end-of-options",
               ref + "^{commit}").decode().strip()


def snapshot(source, dest, commit):
    # clone --shared may still pack millions of objects for a shallow/worktree source.
    # A new Git database with an explicit alternate preserves history without that copy.
    dest.mkdir()
    git(dest, "init", "--quiet")
    common = Path(git(source, "rev-parse", "--git-common-dir").decode().strip())
    if not common.is_absolute():
        common = source / common
    common = common.resolve()
    (dest / ".git/objects/info/alternates").write_text(str(common / "objects") + "\n")
    if (common / "shallow").is_file():
        shutil.copyfile(common / "shallow", dest / ".git/shallow")
    refs = git(source, "for-each-ref", "--format=%(refname) %(objectname)").decode().splitlines()
    if refs:
        git(dest, "update-ref", "--stdin", data=("\n".join("update " + ref for ref in refs) + "\n").encode())
    git(dest, "update-ref", "refs/heads/pipeline-input", commit)
    git(dest, "config", "core.hooksPath", "/dev/null")
    git(dest, "config", "gc.auto", "0")
    git(dest, "checkout", "--detach", commit)


def inside(path, directory):
    return Path(path).resolve().is_relative_to(Path(directory).resolve())


def artifact(directory, relative):
    p = directory / relative
    if not inside(p, directory) or p.is_symlink() or not p.is_file():
        raise ValueError(f"无效的阶段产物：{p}")
    return p


def intent_gate(result):
    tag = result.get("patch_type")
    if not isinstance(tag, str) or tag not in TAGS:
        raise ValueError("意图分析缺少合法 patch_type；不能按非 CVE 正常退出")
    return tag == "CVE"


def port_gate(directory, target):
    result = read(artifact(directory, "final.json"))
    status = result.get("status")
    if status not in {"success", "no_change", "blocked", "failed"}:
        raise ValueError("补丁合入 final.json 状态无效")
    if status != "success":
        return status, result, None
    if result.get("target_commit") != target:
        raise ValueError("补丁合入目标 SHA 与本 case 不一致")
    if any(result.get("gates", {}).get(k) != "passed"
           for k in ("analysis", "application", "validation")):
        raise ValueError("补丁合入声称 success，但三个门禁未全部通过")
    patch = artifact(directory, "generated.patch")
    if not patch.read_bytes().strip():
        raise ValueError("成功合入缺少非空 generated.patch")
    analysis = read(artifact(directory, "port-analysis.json"))
    application = read(artifact(directory, "details/application.json"))
    validation = read(artifact(directory, "details/validation.json"))
    evidence = read(artifact(directory, "details/validation-evidence.json"))
    if (analysis.get("analysis_status") not in {"ready", "direct_apply_ready"}
            or analysis.get("inputs", {}).get("target_commit") != target
            or application.get("application_status") != "candidate_ready"
            or application.get("target_commit") != target
            or application.get("generated_patch_sha256") != digest(patch)
            or validation.get("validation_status") != "passed"
            or validation.get("target_commit") != target
            or validation.get("structural_integrity", {}).get("status") != "passed"
            or validation.get("failed_findings")
            or evidence.get("evidence_status") != "structurally_valid"
            or evidence.get("inputs", {}).get("patch_sha256") != digest(patch)
            or evidence.get("inputs", {}).get("target_commit") != target
            or evidence.get("inputs", {}).get("analysis_sha256") != digest(directory / "port-analysis.json")
            or evidence.get("inputs", {}).get("application_sha256") != digest(directory / "details/application.json")):
        raise ValueError("补丁合入门禁与阶段证据、目标版本或补丁哈希不一致")
    return status, result, patch


def compatibility_gate(directory, target, patch):
    analysis = read(artifact(directory, "analysis.json"))
    summary_path = artifact(directory, "compatibility-testing/test-summary.json")
    result = read(summary_path)
    target_repo = (directory.parent / "target-repo").resolve()
    if (Path(analysis.get("repo", "")).resolve() != target_repo
            or Path(result.get("target", {}).get("repo", "")).resolve() != target_repo
            or result.get("patch_id") != analysis.get("patch_id")
            or analysis.get("base_commit") != target
            or result.get("target", {}).get("base_commit") != target
            or (summary_path.parent / Path(result.get("analysis_json", ""))).resolve()
                != (directory / "analysis.json").resolve()
            or digest(artifact(directory, "patch.diff")) != digest(patch)):
        raise ValueError("兼容性分析/测试未使用本 case 的目标基线及实际合入补丁")
    status = result.get("status")
    verdict = result.get("conclusion", {}).get("backward_compatibility")
    if status not in {"passed", "failed", "partial", "blocked"}:
        raise ValueError("兼容性测试状态无效")
    if verdict not in {"compatible", "incompatible", "inconclusive"}:
        raise ValueError("兼容性结论无效")
    if status == "failed" or verdict == "incompatible":
        return "failed", result
    if status != "passed" or verdict != "compatible":
        return "blocked", result
    if (result.get("blocked_or_not_run")
            or result.get("conclusion", {}).get("coverage_gate_met") is not True
            or result.get("summary", {}).get("inputs_executed", 0) < 1
            or result.get("summary", {}).get("contracts_breached", 0) != 0):
        raise ValueError("兼容性声称通过，但执行证据或覆盖率门禁不满足")
    return "success", result


class Runner:
    def __init__(self, args, output):
        self.args, self.output = args, output
        self.workspace = output / "agent-workspace"
        self.workspace.mkdir()
        for name, source in SKILLS.items():
            shutil.copytree(source, self.workspace / ".opencode/skills" / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        permissions = {"*": "allow", "task": "deny", "question": "deny",
                       "webfetch": "deny", "websearch": "deny",
                       "external_directory": {"*": "deny", str(output) + "/*": "allow"}}
        agent = self.workspace / ".opencode/agents/case-pipeline.md"
        agent.parent.mkdir(parents=True)
        agent.write_text("---\ndescription: Execute one supplied pipeline stage\nmode: primary\n"
                         + "permission: " + json.dumps(permissions) + "\n---\n"
                         + "只执行当前阶段。读取指定 Skill 并遵守其产物契约。中文报告。\n"
                         + "所有源码变更与构建只能发生在当前 case 的隔离目录。禁止提交、推送、"
                         + "修改原始仓库、sudo、安装系统软件包或修改持久服务。\n"
                         + "不读取其他 case 或历史评测答案。依赖缺失请记录 blocked，不伪造通过。\n")

    def run(self, stage, prompt, model, expected_skill):
        folder = self.output / stage
        folder.mkdir(exist_ok=True)
        (folder / "prompt.txt").write_text(prompt)
        runtime = folder / "runtime"
        runtime.mkdir()
        env = environment()
        env.update(OPENCODE_CONFIG=str(self.args.config),
                   OPENCODE_DISABLE_AUTOUPDATE="1", OPENCODE_DISABLE_MODELS_FETCH="1",
                   OPENCODE_DISABLE_LSP_DOWNLOAD="1", OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER="1")
        for name in ("CONFIG", "DATA", "STATE", "CACHE"):
            env["XDG_" + name + "_HOME"] = str(runtime / name.lower())
        # Optional existing dependency cache. Do not repeatedly download ripgrep.
        if self.args.rg and self.args.rg.is_file():
            link = runtime / "cache/opencode/bin/rg"
            link.parent.mkdir(parents=True)
            link.symlink_to(self.args.rg)
        cmd = [str(self.args.opencode), "run", "--pure", "--format", "json", "--auto",
               "--agent", "case-pipeline", "--dir", str(self.workspace), "--model", model, prompt]
        start = time.monotonic()
        with (folder / "events.jsonl").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
            proc = subprocess.Popen(cmd, cwd=self.workspace, env=env, stdout=stdout,
                                    stderr=stderr, start_new_session=True)
            try:
                code = proc.wait(timeout=self.args.timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                raise
        save(folder / "execution.json", {"exit_code": code, "model": model,
                                          "elapsed_seconds": round(time.monotonic() - start, 2)})
        if code:
            raise ValueError(f"{stage} 运行退出码为 {code}，见该阶段日志")
        loaded, errors, texts, finishes = set(), [], [], []
        for line in (folder / "events.jsonl").read_text(errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                if line.strip():
                    errors.append("malformed_event")
                continue
            if not isinstance(event, dict):
                errors.append("invalid_event")
                continue
            if event.get("type") == "error":
                errors.append(event)
            part = event.get("part", {})
            if event.get("type") == "step_finish":
                finishes.append(part.get("reason"))
            if event.get("type") == "text":
                texts.append(part.get("text", ""))
            state = part.get("state", {})
            if part.get("tool") == "skill" and state.get("status") == "completed":
                loaded.add(state.get("input", {}).get("name"))
        if errors or expected_skill not in loaded or not finishes or finishes[-1] != "stop":
            raise ValueError(f"{stage} 运行错误、未正常结束或未实际加载 {expected_skill}，见 events.jsonl")
        if stage == "intent" and not (folder / "result.json").exists():
            # The original intent Skill returns JSON rather than writing a file.
            for text in reversed(texts):
                body = text.strip()
                if body.startswith("```json") and body.endswith("```"):
                    body = body[7:-3].strip()
                try:
                    value = json.loads(body)
                except ValueError:
                    continue
                if isinstance(value, dict) and "patch_type" in value:
                    save(folder / "result.json", value)
                    break


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-repo", type=Path, help="已有本地 Git 仓库")
    source.add_argument("--source-url", help="自动下载的上游 Git 仓库 URL")
    parser.add_argument("--commit", required=True, help="需要分类并迁移的原始补丁 commit")
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--target-repo", type=Path, help="已有下游仓库；默认同上游")
    target.add_argument("--target-url", help="自动下载的下游 Git 仓库 URL")
    parser.add_argument("--target-ref", required=True, help="合入前的目标版本")
    parser.add_argument("--output", required=True, type=Path, help="必须是仓库之外尚不存在的目录")
    parser.add_argument("--config", type=Path, help="OpenCode 配置文件（不复制或输出其中的凭据）")
    parser.add_argument("--opencode", type=Path, default=shutil.which("opencode"))
    parser.add_argument("--model", help="默认模型，或读取配置的 model")
    parser.add_argument("--intent-model")
    parser.add_argument("--port-model")
    parser.add_argument("--compatibility-model")
    parser.add_argument("--port-mode", choices=("history", "cross_repo_semantic"), default="history")
    parser.add_argument("--profile", default="auto")
    parser.add_argument("--timeout", type=int, default=3600, help="每个研究内容最大运行秒数")
    parser.add_argument("--rg", type=Path, help="已有 ripgrep 可执行文件，供隔离运行环境复用")
    parser.add_argument("--validation-command", action="append", default=[], help="内容二构建/测试命令，可重复")
    parser.add_argument("--dry-run", action="store_true", help="只解析输入、输出执行计划，不调用模型")
    parser.add_argument("--local", action="store_true", help="使用已准备好的本地仓库和原生 OpenCode；默认自动准备并使用 Docker")
    parser.add_argument("--target-bundle", help="额外目标基线 Git bundle 的本地路径或 HTTP(S) URL")
    parser.add_argument("--target-bundle-sha256", help="基线包 SHA-256；下载基线包时必填")
    parser.add_argument("--target-bundle-ref", help="基线包中的目标 ref；默认使用 target-ref")
    parser.add_argument("--target-tree", help="可选的目标源码树 SHA，用于精确校验")
    parser.add_argument("--network", choices=("bridge", "host"), default="bridge")
    parser.add_argument("--proxy", help="下载、镜像构建和运行容器使用的 HTTP(S) 代理")
    parser.add_argument("--rebuild", action="store_true", help="无缓存重建运行镜像并刷新基础镜像")
    parser.add_argument("--dockerfile", type=Path, help="需要额外项目依赖时使用自定义 Dockerfile")
    parser.add_argument("--prepare-only", action="store_true", help="准备源码和运行环境，不调用模型；同参数重跑可继续")
    parser.add_argument("--download-attempts", type=int, default=3)
    parser.add_argument("--download-timeout", type=int, default=7200, help="每次 Git 下载的超时秒数")
    args = parser.parse_args(argv)
    if not args.local:
        from bootstrap import run
        return run(args, parser)
    if not args.source_repo or args.target_url or args.target_bundle or args.prepare_only:
        parser.error("--local 需要已有本地仓库；URL、基线包及自动准备选项请使用默认 Docker 模式")
    args.source_repo = args.source_repo.resolve()
    args.target_repo = (args.target_repo or args.source_repo).resolve()
    args.output = args.output.resolve()
    if args.timeout <= 0:
        parser.error("--timeout 必须大于 0")
    if args.output.exists():
        parser.error("--output 已存在；请使用新的目录，避免复用旧产物")
    for repo in (args.source_repo, args.target_repo, ROOT):
        if inside(args.output, repo) or inside(repo, args.output):
            parser.error("--output 必须位于源码和工具仓库之外，且不能包含它们")
    result = {"schema_version": "1.0", "status": "running", "reason": "",
              "stopped_after": None, "stages": {name: {"status": "not_run"} for name in STAGES}}
    current = "input"
    args.output.mkdir(parents=True, mode=0o700)

    def finish(status, reason, code):
        result.update(status=status, reason=reason, stopped_after=current)
        save(args.output / "pipeline-result.json", result)
        print(json.dumps({"status": status, "reason": reason,
                          "result": str(args.output / "pipeline-result.json")}, ensure_ascii=False), flush=True)
        return code

    try:
        commit = resolve(args.source_repo, args.commit)
        parents = git(args.source_repo, "show", "-s", "--format=%P", commit).decode().split()
        if len(parents) != 1:
            raise ValueError("仅支持单父提交；root/merge commit 需先明确参考补丁范围")
        target = resolve(args.target_repo, args.target_ref)
        if args.port_mode == "history":
            if resolve(args.target_repo, commit) != commit:
                raise ValueError("history 模式要求目标仓库包含参考提交历史")
            git(args.target_repo, "merge-base", commit, target)
        result["input"] = {"source_repo": str(args.source_repo), "commit": commit,
                           "reference_parent": parents[0], "target_repo": str(args.target_repo),
                           "target_commit": target, "port_mode": args.port_mode, "profile": args.profile}
        if args.dry_run:
            result["plan"] = ["意图分析：patch_type == CVE 才继续",
                              "补丁合入：三个门禁通过且 status == success 才继续",
                              "兼容性：实际合入补丁 + 目标基线，先分析再测试"]
            return finish("planned", "输入已解析；未调用模型或修改源码", 0)
        if not args.config or not args.config.is_file():
            raise ValueError("需要有效的 --config")
        args.config = args.config.resolve()
        config = read(args.config)
        model = args.model or config.get("model")
        models = {name: getattr(args, name + "_model") or model for name in STAGES}
        if not all(isinstance(m, str) and "/" in m for m in models.values()):
            raise ValueError("请用 --model 或各阶段模型参数提供 provider/model")
        if not args.opencode or not Path(args.opencode).is_file():
            raise ValueError("找不到 OpenCode；请指定 --opencode")
        args.opencode = Path(args.opencode).resolve()
        if args.rg:
            args.rg = args.rg.resolve()
        for skill in SKILLS.values():
            if not (skill / "SKILL.md").is_file():
                raise ValueError(f"缺少 Skill：{skill}")
        result["models"] = models
        result["skill_hashes"] = {name: digest(path / "SKILL.md") for name, path in SKILLS.items()}
        save(args.output / "pipeline-result.json", result)
        runner = Runner(args, args.output)
        source = args.output / "source-repo"
        snapshot(args.source_repo, source, commit)
        reference = args.output / "reference.patch"
        reference.write_bytes(git(source, "diff", "--binary", parents[0], commit))
        if not reference.read_bytes().strip():
            raise ValueError("参考补丁为空")
        current = "intent"
        result["stages"][current] = {"status": "running"}
        save(args.output / "pipeline-result.json", result)
        print("[1/3] 意图分析", flush=True)
        runner.run(current, "使用 $patch-intent-analysis 分析下面的 commit。必须用 skill 工具加载。\n"
                   f"repo: {source}\ncommit: {commit}\n"
                   "读取原始 message、完整 diff 与此版本源码；不修改源码。"
                   "严格返回 Skill 约定的一个 JSON 对象。", models[current], "patch-intent-analysis")
        intent = read(args.output / "intent/result.json")
        is_cve = intent_gate(intent)
        result["stages"][current] = {"status": "completed", "patch_type": intent["patch_type"],
                                    "artifact": "intent/result.json"}
        if not is_cve:
            return finish("skipped_non_cve", f"patch_type={intent['patch_type']}，不执行补丁合入及兼容性测试", 0)
        target_repo = args.output / "target-repo"
        snapshot(args.target_repo, target_repo, target)
        current = "port"
        result["stages"][current] = {"status": "running"}
        save(args.output / "pipeline-result.json", result)
        print("[2/3] 补丁合入与独立验证", flush=True)
        port_dir = args.output / "port"
        inputs = {"repo": str(target_repo), "target_repo": str(target_repo),
                  "reference_repo": str(source), "reference_fix": commit,
                  "reference_parent": parents[0], "reference_patch": str(reference),
                  "target_ref": target, "port_mode": args.port_mode, "output_dir": str(port_dir),
                  "validation_commands": args.validation_command}
        runner.run(current, "使用 $security-patch-port 及其分析、实施、独立验证子 Skill，"
                   "通过 skill 工具加载并执行全部门禁。输入如下：\n" + json.dumps(inputs, ensure_ascii=False)
                   + "\n候选工作树保留在 output_dir 内。禁止修改参考源码或调用者仓库。"
                   "final.json、generated.patch、port-analysis.json 及 details 下阶段产物按 Skill 契约写入。"
                   "没有构建/测试证据不得编造通过。blocked、failed、no_change 均写入 final.json 后退出。",
                   models[current], "security-patch-port")
        status, port_result, patch = port_gate(port_dir, target)
        result["stages"][current] = {"status": status, "artifact": "port/final.json"}
        if status != "success":
            return finish(status, "补丁合入未成功，终止后续兼容性阶段：" + str(port_result.get("summary", status)),
                          {"failed": 1, "blocked": 2, "no_change": 0}[status])
        # Independently confirm the exact candidate can replay at the target baseline.
        replay = args.output / "replay-check"
        snapshot(args.target_repo, replay, target)
        git(replay, "apply", "--check", str(patch))
        git(replay, "apply", "--index", str(patch))
        git(replay, "diff", "--cached", "--check")
        candidate_hash = digest(patch)
        result["stages"][current]["patch_sha256"] = candidate_hash
        current = "compatibility"
        result["stages"][current] = {"status": "running"}
        save(args.output / "pipeline-result.json", result)
        print("[3/3] 兼容性分析与定向测试", flush=True)
        compatibility_dir = args.output / current
        inputs = {"repo": str(target_repo), "patch_file": str(patch), "base_ref": target,
                  "package_profile": args.profile, "output_dir": str(compatibility_dir),
                  "test_output_dir": str(compatibility_dir / "compatibility-testing")}
        runner.run(current, "使用 $patch-compatibility-utils，必须通过 skill 工具加载。"
                   "明确要求先执行静态兼容性分析，再执行定向动态测试，不在中间询问。\n"
                   + json.dumps(inputs, ensure_ascii=False)
                   + "\n分析对象是实际合入补丁，不是上游 reference.patch。"
                   "按指定 base_ref 建立 before/after，不以当前 HEAD 或候选已打补丁工作树作为基线。"
                   "output_dir 直接保存 analysis.json 和 patch.diff，"
                   "test_output_dir 保存 test-summary.json 与 COVERAGE_REPORT.md。"
                   "使用 validate_analysis.py 和 finalize_test_report.py 校验。"
                   "没有兼容性 finding 时仍按补丁改动执行覆盖测试，不编造 finding；"
                   "环境不足写 blocked/partial，不将未执行测试视为通过。禁止修改输入补丁。",
                   models[current], "patch-compatibility-utils")
        if digest(patch) != candidate_hash:
            raise ValueError("兼容性阶段修改了已验证的候选补丁")
        scripts = SKILLS["patch-compatibility-utils"]
        for script, argument in (
                (scripts / "patch-compatibility-analysis/scripts/validate_analysis.py", compatibility_dir / "analysis.json"),
                (scripts / "patch-compatibility-testing/scripts/finalize_test_report.py", compatibility_dir / "compatibility-testing/test-summary.json")):
            check = subprocess.run([sys.executable, str(script), str(argument)],
                                   capture_output=True, text=True, timeout=120,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            (compatibility_dir / (script.stem + ".log")).write_text(check.stdout + check.stderr)
            if check.returncode:
                raise ValueError(f"内容三产物未通过 {script.name} 校验")
        status, test_result = compatibility_gate(compatibility_dir, target, patch)
        result["stages"][current] = {"status": test_result["status"],
                                    "conclusion": test_result["conclusion"]["backward_compatibility"],
                                    "artifact": "compatibility/compatibility-testing/test-summary.json"}
        return finish(status, "兼容性测试：" + test_result["status"] + "；结论："
                      + test_result["conclusion"]["backward_compatibility"],
                      {"success": 0, "failed": 1, "blocked": 2}[status])
    except KeyboardInterrupt:
        if current in STAGES:
            result["stages"][current]["status"] = "interrupted"
        return finish("interrupted", "用户中断；已停止当前阶段，未启动后续阶段", 130)
    except subprocess.TimeoutExpired:
        if current in STAGES:
            result["stages"][current]["status"] = "timeout"
        return finish("blocked", "当前阶段超时，未启动后续阶段", 2)
    except (ValueError, TypeError, KeyError, AttributeError, OSError, subprocess.CalledProcessError) as exc:
        if current in STAGES:
            result["stages"][current]["status"] = "error"
        # Do not include captured subprocess output/config values which may contain credentials.
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__ + "；检查输入及阶段日志"
        return finish("error", message, 3)


if __name__ == "__main__":
    raise SystemExit(main())
