"""Prepare Git inputs and a Docker runtime for the end-to-end patch workflow."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
PROXY_VARS = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy")


def save(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def environment():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "OPENCODE_"))}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    return env


def command(argv, *, env=None, timeout=300):
    p = subprocess.run([str(v) for v in argv], env=env or environment(),
                       capture_output=True, timeout=timeout)
    if p.returncode:
        raise ValueError(f"{argv[0]} 执行失败：" + p.stderr.decode(errors="replace")[-1800:])
    return p.stdout.decode().strip()


def git(repo, *args):
    return command(["git", "-C", repo, *args])


def resolve(repo, ref, kind="commit"):
    return git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{" + kind + "}")


def public_url(value):
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
        raise ValueError("仓库 URL 应使用 https://、ssh:// 或 git://；本地仓库用 --source-repo/--target-repo")
    if parsed.password or (parsed.username and parsed.scheme in {"http", "https"}) or parsed.query or parsed.fragment:
        raise ValueError("URL 不应含凭据、查询参数或片段；私有仓库请先在本地准备并用 --source-repo")
    return value


def download(argv, log, args):
    """Retries reuse only this invocation's object database; never borrow old case caches."""
    for attempt in range(1, args.download_attempts + 1):
        with log.open("ab") as stream:
            stream.write(f"\nattempt {attempt}\n".encode())
            try:
                p = subprocess.run([str(x) for x in argv], stdout=stream, stderr=stream,
                                   env=environment(), timeout=args.download_timeout)
                if p.returncode == 0:
                    return
            except subprocess.TimeoutExpired:
                stream.write(b"download timeout\n")
        print(f"下载未完成，尝试 {attempt}/{args.download_attempts}；日志：{log}", flush=True)
        if attempt < args.download_attempts:
            time.sleep(min(2 ** attempt, 10))
    raise ValueError(f"下载失败，可用相同命令继续准备；详情：{log}")


def fetch(repo, url, ref, name, args, logs):
    download(["git", "-C", repo, "fetch", "--no-tags", "--", url,
              f"{ref}:refs/heads/{name}"], logs / (name + ".log"), args)
    return resolve(repo, "refs/heads/" + name)


def repository(repo, local):
    if repo.exists():
        return
    if local:
        # --no-local creates a standalone object database, including for sources with alternates.
        command(["git", "clone", "--mirror", "--no-local", str(local.resolve()), repo], timeout=7200)
    else:
        command(["git", "init", "--bare", repo])
    git(repo, "config", "core.hooksPath", "/dev/null")
    git(repo, "config", "gc.auto", "0")


def known_baseline(args, commit):
    manifest = ROOT / "研究内容二/evaluation/config/sources.json"
    if args.target_url or args.target_repo or not manifest.is_file():
        return None
    projects = json.loads(manifest.read_text()).get("projects", {})
    matches = [v for v in projects.values() if v.get("source_commit") == commit
               and v.get("target_ref") == args.target_ref
               and (not args.source_url or v.get("upstream_url", "").rstrip("/") == args.source_url.rstrip("/"))]
    if len(matches) == 1 and matches[0].get("bundle"):
        return matches[0]
    return None


def import_bundle(repo, args, inputs, logs, recipe=None):
    bundle = args.target_bundle
    expected = args.target_bundle_sha256
    ref = args.target_bundle_ref or args.target_ref
    if recipe and not bundle:
        bundle = str(ROOT / "研究内容二/evaluation/data" / recipe["bundle"])
        expected = recipe["bundle_sha256"]
    if not bundle:
        return None
    destination = inputs / "target.bundle"
    if bundle.startswith(("http://", "https://")):
        public_url(bundle)
        if not expected or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            raise ValueError("远程 --target-bundle 必须提供 --target-bundle-sha256")
        if not destination.exists() or sha(destination) != expected.lower():
            for attempt in range(args.download_attempts):
                try:
                    with urllib.request.urlopen(bundle, timeout=min(args.download_timeout, 120)) as response:
                        with destination.with_suffix(".partial").open("wb") as output:
                            shutil.copyfileobj(response, output)
                    destination.with_suffix(".partial").replace(destination)
                    break
                except OSError:
                    if attempt + 1 == args.download_attempts:
                        raise ValueError("目标基线包下载失败")
                    time.sleep(2)
    else:
        original = Path(bundle).expanduser().resolve()
        if not original.is_file():
            raise ValueError("找不到目标基线包：" + str(original))
        shutil.copyfile(original, destination)
    actual = sha(destination)
    if expected and actual != expected.lower():
        raise ValueError("目标基线包 SHA-256 不匹配")
    git(repo, "bundle", "verify", str(destination))
    if not args.target_bundle_ref:
        heads = [line.split() for line in git(repo, "bundle", "list-heads", str(destination)).splitlines()]
        matching = [name for commit, name in heads if commit == args.target_ref or name == args.target_ref]
        if matching:
            ref = matching[0]
    fetch(repo, str(destination), ref, "pipeline-target", args, logs)
    return {"sha256": actual, "ref": ref, "source": bundle}


def prepare(args, output):
    inputs, logs = output / "inputs", output / "preparation"
    inputs.mkdir(exist_ok=True)
    logs.mkdir(exist_ok=True)
    source = inputs / "source.git"
    repository(source, args.source_repo)
    if args.source_url:
        commit = fetch(source, args.source_url, args.commit, "pipeline-source", args, logs)
    else:
        commit = resolve(source, args.commit)
    separate = bool(args.target_repo or args.target_url)
    target = inputs / "target.git" if separate else source
    recipe = known_baseline(args, commit)
    if separate:
        repository(target, args.target_repo)
    target_commit = None
    if args.target_url:
        target_commit = fetch(target, args.target_url, args.target_ref, "pipeline-target", args, logs)
    bundle = import_bundle(target, args, inputs, logs, recipe)
    if bundle:
        target_commit = resolve(target, "refs/heads/pipeline-target")
        if resolve(target, args.target_ref) != target_commit:
            raise ValueError("基线包 ref 与 --target-ref 指向不同提交")
    elif target_commit is None:
        try:
            target_commit = resolve(target, args.target_ref)
        except ValueError:
            if not args.source_url or separate:
                raise ValueError("目标提交不在仓库中，请提供下游仓库或 --target-bundle")
            target_commit = fetch(target, args.source_url, args.target_ref, "pipeline-target", args, logs)
    if args.port_mode == "history":
        # Shared-history repositories may not advertise the upstream fix on the downstream remote.
        if separate:
            fetch(target, str(source), commit, "pipeline-reference", args, logs)
        git(target, "merge-base", commit, target_commit)
    parents = git(source, "show", "-s", "--format=%P", commit).split()
    if len(parents) != 1:
        raise ValueError("仅支持单父修复提交")
    tree = resolve(target, target_commit, "tree")
    expected_tree = args.target_tree or (recipe or {}).get("target_tree")
    if expected_tree and tree != expected_tree:
        raise ValueError("目标源码树不匹配")
    result = {"source_repo": str(source), "target_repo": str(target), "source_commit": commit,
              "reference_parent": parents[0], "target_commit": target_commit, "target_tree": tree,
              "target_bundle": bundle, "port_mode": args.port_mode}
    save(output / "preparation.json", result)
    return result


def model_config(args):
    """Resolve credentials on the host; the saved config contains only environment references."""
    path = args.config.expanduser().resolve()
    original = json.loads(path.read_text())
    env, providers, models, metadata = {}, {}, {}, {}

    def value(v):
        if not isinstance(v, str) or not v:
            raise ValueError("模型配置需要 options.baseURL 和 options.apiKey")
        m = re.fullmatch(r"\{(env|file):([^}]+)\}", v)
        if not m:
            return v
        kind, key = m.groups()
        if kind == "env":
            if not os.environ.get(key):
                raise ValueError("缺少环境变量：" + key)
            return os.environ[key]
        f = Path(key).expanduser()
        return (f if f.is_absolute() else path.parent / f).read_text().strip()

    for stage in ("intent", "port", "compatibility"):
        requested = getattr(args, stage + "_model") or args.model or original.get("model")
        if not isinstance(requested, str) or "/" not in requested:
            raise ValueError("请配置 provider/model 格式的模型名")
        provider, name = requested.split("/", 1)
        selected = original.get("provider", {}).get(provider, {})
        options = selected.get("options", {})
        definition = selected.get("models", {}).get(name, {})
        api_name = definition.get("id", name)
        if provider == "deepseek" and api_name == "deepseek-v4-flash":
            api_name = "deepseek-flash"
        if not re.fullmatch(r"[A-Za-z0-9_.:/-]+", api_name):
            raise ValueError("无效 API 模型名")
        prefix = "PIPELINE_" + stage.upper()
        env[prefix + "_KEY"] = value(options.get("apiKey"))
        env[prefix + "_URL"] = value(options.get("baseURL"))
        if not env[prefix + "_URL"].startswith(("http://", "https://")):
            raise ValueError("只支持 HTTP(S) OpenAI-compatible 模型端点")
        providers[stage] = {"npm": "@ai-sdk/openai-compatible",
                            "models": {api_name: {"name": api_name, "limit": definition.get("limit", {"context": 65536, "output": 8192})}},
                            "options": {"apiKey": "{env:" + prefix + "_KEY}", "baseURL": "{env:" + prefix + "_URL}"}}
        models[stage] = stage + "/" + api_name
        metadata[stage] = {"requested": requested, "api_model": api_name}
    config = {"$schema": "https://opencode.ai/config.json", "model": models["intent"],
              "small_model": models["intent"], "provider": providers, "share": "disabled", "autoupdate": False}
    return config, env, models, metadata


def build(args, output):
    dockerfile = (args.dockerfile or ROOT / "end_to_end_workflow/Dockerfile").resolve()
    tag = "hyl-pipeline:" + sha(dockerfile)[:16]
    inspect = subprocess.run(["docker", "image", "inspect", tag], capture_output=True)
    if args.rebuild or inspect.returncode:
        context = output / "runtime/build"
        context.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dockerfile, context / "Dockerfile")
        argv = ["docker", "build", "--tag", tag]
        if args.network == "host":
            argv += ["--network", "host"]
        if args.rebuild:
            argv += ["--pull", "--no-cache"]
        for key in PROXY_VARS:
            if os.environ.get(key):
                argv += ["--build-arg", key]
        argv.append(str(context))
        print("构建运行环境；日志：" + str(output / "build.log"), flush=True)
        with (output / "build.log").open("wb") as log:
            p = subprocess.run(argv, stdout=log, stderr=log, env=environment())
        if p.returncode:
            raise ValueError("镜像构建失败；检查 build.log 后可用相同命令重试")
    return command(["docker", "image", "inspect", "--format", "{{.Id}}", tag])


def tool_snapshot(output):
    from run_case import SKILLS
    dest = output / "runtime/tool"
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "end_to_end_workflow").mkdir(parents=True)
    for name in ("run_case.py", "bootstrap.py"):
        shutil.copyfile(ROOT / "end_to_end_workflow" / name, dest / "end_to_end_workflow" / name)
    for source in SKILLS.values():
        shutil.copytree(source, dest / source.relative_to(ROOT),
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    return dest


def run(args, parser):
    if args.timeout <= 0 or args.download_timeout <= 0 or args.download_attempts < 1:
        parser.error("超时和下载尝试次数必须为正数")
    for key in ("source_repo", "target_repo", "config", "dockerfile"):
        if getattr(args, key):
            setattr(args, key, getattr(args, key).expanduser().resolve())
    if args.target_bundle and not args.target_bundle.startswith(("http://", "https://")):
        args.target_bundle = str(Path(args.target_bundle).expanduser().resolve())
    output = args.output.expanduser().resolve()
    for p in [ROOT, args.source_repo, args.target_repo]:
        if p:
            p = p.resolve()
            if output == p or p in output.parents or output in p.parents:
                parser.error("--output 必须位于工具及输入仓库之外")
    for value in (args.source_url, args.target_url):
        if value:
            try:
                public_url(value)
            except ValueError as exc:
                parser.error(str(exc))
    if args.proxy:
        if not args.proxy.startswith(("http://", "https://")):
            parser.error("--proxy 需要 HTTP(S) 地址")
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            os.environ[key] = args.proxy
    if not args.prepare_only and not args.dry_run and not args.config:
        parser.error("执行模型需要 --config")
    selection = {k: str(getattr(args, k)) if isinstance(getattr(args, k), Path) else getattr(args, k)
                 for k in ("source_repo", "source_url", "target_repo", "target_url", "commit", "target_ref",
                           "target_bundle", "target_bundle_ref", "target_bundle_sha256", "target_tree", "port_mode")}
    if args.dry_run:
        print(json.dumps({"mode": "docker", "inputs": selection, "output": str(output),
                          "steps": ["准备源码和目标基线", "构建运行镜像", "意图分析", "迁移及验证", "兼容性分析与测试"],
                          "note": "仅展示计划；未下载或验证远程提交，未创建输出"}, ensure_ascii=False, indent=2))
        return 0
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = output / ".bootstrap.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        parser.error("已有准备/运行进程持锁；若异常断电，先确认无进程运行再删除 .bootstrap.lock")
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    status = {"status": "preparing", "inputs": selection}
    name = "hyl-pipeline-" + uuid.uuid4().hex[:16]
    started = time.monotonic()
    secrets = []
    accepted = False
    try:
        previous = output / "bootstrap.json"
        if previous.exists():
            old = json.loads(previous.read_text())
            if old.get("inputs") != selection:
                raise ValueError("准备输入变化，请使用新输出目录")
        elif any(p.name != lock.name for p in output.iterdir()):
            raise ValueError("输出目录非空且不属于此入口，请使用新目录")
        if (output / "run").exists():
            raise ValueError("模型运行目录已存在；查看 run/pipeline-result.json，重新执行请换输出目录")
        accepted = True
        save(previous, status)
        command(["docker", "version", "--format", "{{.Server.Version}}"])
        config = model_config(args) if not args.prepare_only else None
        print("[准备] 下载源码与目标基线", flush=True)
        prepared = prepare(args, output)
        print("[准备] 源码与目标版本校验通过", flush=True)
        image = build(args, output)
        tool = tool_snapshot(output)
        status.update(image=image, status="prepared")
        save(previous, status)
        if args.prepare_only:
            print("准备完成；使用相同参数移除 --prepare-only 继续", flush=True)
            return 0
        cfg, credentials, models, metadata = config
        secrets = [v for k, v in credentials.items() if k.endswith("_KEY")]
        runtime = output / "runtime"
        save(runtime / "opencode.json", cfg)
        for part in ("home", "tmp"):
            (runtime / part).mkdir(exist_ok=True)
        argv = ["docker", "run", "--rm", "--init", "--name", name, "--network", args.network,
                "--user", f"{os.getuid()}:{os.getgid()}", "--workdir", "/opt/hyl",
                "--mount", f"type=bind,src={tool},dst=/opt/hyl,readonly",
                "--mount", f"type=bind,src={output},dst=/pipeline-work",
                "--mount", f"type=bind,src={output / 'inputs'},dst=/pipeline-work/inputs,readonly",
                "-e", "HOME=/pipeline-work/runtime/home", "-e", "TMPDIR=/pipeline-work/runtime/tmp"]
        for key in [*credentials, *PROXY_VARS]:
            if key in credentials or os.environ.get(key):
                argv += ["-e", key]
        inner = ["python3", "/opt/hyl/end_to_end_workflow/run_case.py", "--local",
                 "--source-repo", "/pipeline-work/inputs/source.git",
                 "--target-repo", "/pipeline-work/inputs/" + Path(prepared["target_repo"]).name,
                 "--commit", prepared["source_commit"], "--target-ref", prepared["target_commit"],
                 "--config", "/pipeline-work/runtime/opencode.json", "--output", "/pipeline-work/run",
                 "--opencode", "/usr/local/bin/opencode", "--rg", "/usr/bin/rg",
                 "--port-mode", args.port_mode, "--profile", args.profile, "--timeout", str(args.timeout)]
        for stage, model in models.items():
            inner += ["--" + stage + "-model", model]
        for cmd in args.validation_command:
            inner += ["--validation-command", cmd]
        argv += ["--entrypoint", "python3", image, *inner[1:]]
        status.update(status="running", models=metadata)
        save(previous, status)
        save(output / "command.json", {"argv": argv, "credentials": "environment variables; values not recorded"})
        print("[运行] 端到端补丁工作流；输出：" + str(output / "run"), flush=True)
        with (output / "pipeline.log").open("wb") as log:
            process = subprocess.Popen(argv, stdout=log, stderr=log, env={**environment(), **credentials})
            try:
                code = process.wait()
            except KeyboardInterrupt:
                subprocess.run(["docker", "stop", "--time", "10", name], capture_output=True)
                process.wait(timeout=30)
                raise
        final = output / "run/pipeline-result.json"
        result = json.loads(final.read_text()) if final.is_file() else {}
        status.update(status=result.get("status", "error"), exit_code=code,
                      result="run/pipeline-result.json", elapsed_seconds=round(time.monotonic() - started, 2))
        save(previous, status)
        print(json.dumps(status, ensure_ascii=False), flush=True)
        return code if code else (0 if result else 3)
    except KeyboardInterrupt:
        status.update(status="interrupted")
        if accepted:
            save(output / "bootstrap.json", status)
        return 130
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        reason = str(exc)
        for secret in secrets:
            reason = reason.replace(secret, "[REDACTED]")
        status.update(status="error", reason=reason)
        if accepted:
            save(output / "bootstrap.json", status)
        print(json.dumps({"status": "error", "reason": reason}, ensure_ascii=False), flush=True)
        return 3
    finally:
        # Model keys should never be persisted by the wrapper; redact accidental model echoes as well.
        if secrets:
            for folder in [output / "run"]:
                for name_pattern in ("events.jsonl", "stderr.log", "prompt.txt"):
                    for path in folder.rglob(name_pattern):
                        if path.is_symlink():
                            continue
                        data = path.read_bytes()
                        redacted = data
                        for secret in secrets:
                            redacted = redacted.replace(secret.encode(), b"[REDACTED]")
                        if redacted != data:
                            path.write_bytes(redacted)
        lock.unlink(missing_ok=True)
