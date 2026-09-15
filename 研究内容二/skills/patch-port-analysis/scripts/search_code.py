#!/usr/bin/env python3
"""One model-selected, revision-bound filename query; no semantic ranking."""
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile


def search(repo, revision, pattern, paths=(), repo_role='target', max_results=30, max_bytes=8192):
    if repo_role not in ('reference', 'target'):
        raise ValueError('invalid repository role')
    if not 1 <= max_results <= 200 or not 1024 <= max_bytes <= 65536:
        raise ValueError('query limits must be 1..200 results and 1024..65536 output bytes')
    if not pattern or len(pattern.encode()) > 256 or '\n' in pattern or '\0' in pattern:
        raise ValueError('use a nonempty single literal pattern of at most 256 bytes')
    if len(paths) > 10:
        raise ValueError('at most 10 path scopes per query')
    for path in paths:
        if not path or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts or len(path.encode()) > 256:
            raise ValueError('path scope must be a bounded repository-relative literal path')
    repo = Path(repo).resolve()
    if revision.startswith('-'):
        raise ValueError('revision must not be an option')
    resolved = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', revision+'^{commit}'],
                              capture_output=True, text=True, timeout=10, check=True).stdout.strip()
    command = ['git', '--literal-pathspecs', '-C', str(repo), 'grep', '-l', '-z', '-I', '-F',
               '-e', pattern, resolved, '--', *paths]
    # Git emits filenames only, not source bodies. Spool its output so large
    # hit sets don't fill Python memory; scan time is bounded separately.
    with tempfile.TemporaryFile() as output:
        process = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, timeout=30)
        if process.returncode not in (0, 1):
            raise RuntimeError(process.stderr.decode(errors='replace')[:1000])
        size = output.tell()
        output.seek(0)
        raw = output.read(max_bytes + 1)
    truncated = size > len(raw)
    parts = raw.split(b'\0')
    if raw and not raw.endswith(b'\0'):
        truncated = True
    parts = parts[:-1]  # final empty or incomplete path
    names = [part.decode(errors='replace').partition(':')[2] for part in parts]
    truncated = truncated or len(names) > max_results
    result = {'repo_role':repo_role, 'repo':str(repo), 'revision':resolved,
              'pattern':pattern, 'scope':list(paths), 'paths':names[:max_results],
              'truncated':truncated, 'exit_code':process.returncode,
              'semantic_mapping_proven':False}
    while len(json.dumps(result, ensure_ascii=False).encode()) > max_bytes and result['paths']:
        result['paths'].pop()
        result['truncated'] = True
    if len(json.dumps(result, ensure_ascii=False).encode()) > max_bytes:
        raise ValueError('query metadata exceeds output budget; shorten the query/scope')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--repo-role', choices=['reference','target'], required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--pattern', required=True)
    parser.add_argument('--path', action='append', default=[])
    parser.add_argument('--max-results', type=int, default=30)
    parser.add_argument('--max-bytes', type=int, default=8192)
    args = parser.parse_args()
    try:
        result = search(args.repo, args.revision, args.pattern, args.path, args.repo_role,
                        args.max_results, args.max_bytes)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'failed','error':str(exc)[:1000]}))
        raise SystemExit(1)
