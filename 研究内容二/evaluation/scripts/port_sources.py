"""Download public source history and restore frozen project target commits."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
from port_runtime import command, digest, environment, save


def git(repo, *args, data=None, env=None, timeout=7200, check=True):
    return command(['git', '--no-replace-objects', '-c', 'core.hooksPath=' + os.devnull,
                    '-c', 'core.autocrlf=false', '-C', repo, *args],
                   data=data, env=env, timeout=timeout, check=check)


def resolve(repo, ref):
    return git(repo, 'rev-parse', '--verify', ref).stdout.decode().strip()


def load_cases(data_dir, sources, datasets=('linux', 'projects'), case_ids=None):
    cases = []
    for dataset, filename in [('linux', 'linux404.jsonl'), ('projects', 'feishu92.jsonl')]:
        if dataset not in datasets:
            continue
        rows = [json.loads(line) for line in (data_dir / filename).read_text().splitlines() if line.strip()]
        expected = 404 if dataset == 'linux' else 92
        if len(rows) != expected or len({str(row['case_id']) for row in rows}) != expected:
            raise ValueError('invalid dataset coverage: ' + dataset)
        for row in rows:
            cid = str(row['case_id'])
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', cid):
                raise ValueError('unsafe case identifier')
            for key in ['source_commit'] + (['oracle_commit'] if dataset == 'linux' else ['target_ref', 'target_tree']):
                if not re.fullmatch(r'[0-9a-f]{40}', row[key]):
                    raise ValueError('expected full Git object ID: ' + key)
            if dataset == 'projects' and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', row['package']):
                raise ValueError('unsafe package identifier')
            if case_ids and cid not in case_ids:
                continue
            recipe = sources['linux'] if dataset == 'linux' else sources['projects'][cid]
            if dataset == 'projects':
                for key in ['source_commit', 'target_ref', 'target_tree']:
                    if recipe[key] != row[key]:
                        raise ValueError(f'source recipe disagrees: {cid}/{key}')
                for role in ['reference', 'oracle']:
                    if digest((data_dir / row[role + '_patch']).read_bytes()) != row[role + '_sha256']:
                        raise ValueError(f'patch hash mismatch: {cid}/{role}')
            cases.append({'dataset': dataset, 'case_id': cid, 'record': row, 'source': recipe,
                          'repository': 'linux' if dataset == 'linux' else 'project-' + row['package']})
    if not cases or (case_ids and set(case_ids) != {row['case_id'] for row in cases}):
        raise ValueError('empty selection or unknown case IDs')
    return cases


def fetch_commit(repo, url, commit):
    if not url.startswith(('https://', 'http://', 'file://')):
        raise ValueError('source URL must be HTTP(S) or explicit file:// mirror')
    if git(repo, 'cat-file', '-e', commit + '^{commit}', check=False).returncode:
        last = None
        for _ in range(3):
            last = git(repo, 'fetch', '--no-tags', '--no-recurse-submodules', url, commit, check=False)
            if last.returncode == 0:
                break
        if last.returncode:
            raise RuntimeError('Git fetch failed: ' + url + ' ' + commit + '\n' + last.stderr.decode(errors='replace')[-1000:])
    if resolve(repo, commit + '^{commit}') != commit:
        raise ValueError('source commit identity changed')
    git(repo, 'update-ref', 'refs/source/' + commit, commit)



def batch_fetch(repo, url, commits):
    if not url.startswith(('https://', 'http://', 'file://')):
        raise ValueError('source URL must be HTTP(S) or explicit file:// mirror')
    commits = sorted(set(commits))
    existing = git(repo, 'cat-file', '--batch-check=%(objectname) %(objecttype)',
                   data=('\n'.join(commits) + '\n').encode()).stdout.decode().splitlines()
    missing = [commit for commit, info in zip(commits, existing) if info.endswith(' missing')]
    if not missing:
        return
    specs = [commit + ':refs/source/' + commit for commit in missing]
    print(json.dumps({'phase': 'fetch', 'repository': repo.name, 'commits': len(missing), 'url': url}), flush=True)
    outcome = git(repo, 'fetch', '--no-tags', '--no-recurse-submodules', url, *specs, check=False)
    if outcome.returncode:
        # Individual fetching below attributes unavailable commits to affected cases.
        print(json.dumps({'phase': 'fetch_retry_individually', 'repository': repo.name}), flush=True)


def prepare_repository(name, cases, data_dir, output):
    repo = output / 'cache' / name
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / 'HEAD').exists():
        git(repo, 'init', '--bare', '--quiet')
    for key, value in [('gc.auto', '0'), ('user.name', 'Patch Port Evaluation'),
                       ('user.email', 'evaluation@example.invalid')]:
        git(repo, 'config', key, value)
    if (repo / 'shallow').exists() or (repo / 'objects/info/alternates').exists():
        raise ValueError('source cache must contain independent complete history')
    requests = {}
    for case in cases:
        row, recipe = case['record'], case['source']
        if case['dataset'] == 'linux':
            requests.setdefault(recipe['url'], set()).update([row['source_commit'], row['oracle_commit']])
        else:
            requests.setdefault(recipe['upstream_url'], set()).add(row['source_commit'])
            requests.setdefault(recipe.get('target_url') or recipe['upstream_url'], set()).add(recipe['base_commit'])
    for url, commits in requests.items():
        batch_fetch(repo, url, commits)
    # Speed up repeated ancestry checks on complete kernel histories. This index
    # is optional: source identity and scoring never depend on its availability.
    graph = git(repo, 'commit-graph', 'write', '--reachable', check=False)
    if graph.returncode:
        print(json.dumps({'phase': 'commit_graph_unavailable', 'repository': name}), flush=True)
    prepared, failures = {}, {}
    for case in cases:
        cid, row, recipe = case['case_id'], case['record'], case['source']
        try:
            if case['dataset'] == 'linux':
                fetch_commit(repo, recipe['url'], row['source_commit'])
                fetch_commit(repo, recipe['url'], row['oracle_commit'])
            else:
                fetch_commit(repo, recipe['upstream_url'], row['source_commit'])
                seed_url = recipe.get('target_url') or recipe['upstream_url']
                fetch_commit(repo, seed_url, recipe['base_commit'])
                if recipe.get('bundle'):
                    bundle = data_dir / recipe['bundle']
                    if digest(bundle.read_bytes()) != recipe['bundle_sha256']:
                        raise ValueError('baseline bundle hash mismatch')
                    git(repo, 'bundle', 'verify', str(bundle))
                    git(repo, 'fetch', '--no-tags', str(bundle),
                        f'refs/heads/{cid}:refs/targets/{cid}')
                if resolve(repo, row['target_ref'] + '^{tree}') != row['target_tree']:
                    raise ValueError('frozen target tree does not match')
            prepared[cid] = prepare_case(case, repo, data_dir)
        except Exception as exc:
            failures[cid] = str(exc)
        save(output / 'preparation' / (name + '.json'),
             {'repository': name, 'prepared': prepared, 'failures': failures})
    return prepared, failures


def patch_tree(repo, baseline, patch):
    # The private index leaves the repository refs and working tree untouched.
    with tempfile.TemporaryDirectory(prefix='port-index-') as directory:
        env = environment()
        env['GIT_INDEX_FILE'] = str(Path(directory) / 'index')
        git(repo, 'read-tree', baseline, env=env)
        applied = git(repo, 'apply', '--cached', '--binary', '--whitespace=nowarn', '-', data=patch,
                      env=env, check=False)
        if applied.returncode:
            raise ValueError('patch does not apply: ' + applied.stderr.decode(errors='replace')[-1500:])
        return git(repo, 'write-tree', env=env).stdout.decode().strip()


def prepare_case(case, repo, data_dir):
    row = case['record']
    parents = git(repo, 'show', '-s', '--format=%P', row['source_commit']).stdout.decode().split()
    if len(parents) != 1:
        raise ValueError('reference fix must have exactly one parent')
    if case['dataset'] == 'linux':
        targets = git(repo, 'show', '-s', '--format=%P', row['oracle_commit']).stdout.decode().split()
        if len(targets) != 1:
            raise ValueError('oracle fix must have exactly one parent')
        target = targets[0]
        reference = git(repo, 'diff', '--binary', '--full-index', parents[0], row['source_commit']).stdout
        oracle = git(repo, 'diff', '--binary', '--full-index', target, row['oracle_commit']).stdout
        oracle_commit = row['oracle_commit']
    else:
        target = row['target_ref']
        reference = (data_dir / row['reference_patch']).read_bytes()
        oracle = (data_dir / row['oracle_patch']).read_bytes()
        recipe = case['source']
        if recipe.get('oracle_replay_patch'):
            oracle = (data_dir / recipe['oracle_replay_patch']).read_bytes()
            if digest(oracle) != recipe['oracle_replay_sha256']:
                raise ValueError('canonical oracle replay hash mismatch')
        oracle_tree = patch_tree(repo, target, oracle)
        env = environment()
        env.update(GIT_AUTHOR_DATE='2000-01-01T00:00:00Z', GIT_COMMITTER_DATE='2000-01-01T00:00:00Z')
        oracle_commit = git(repo, 'commit-tree', oracle_tree, '-p', target,
                            data=b'Private evaluation oracle\n', env=env).stdout.decode().strip()
    baseline_tree = resolve(repo, target + '^{tree}')
    oracle_tree = (resolve(repo, oracle_commit + '^{tree}') if case['dataset'] == 'linux'
                   else patch_tree(repo, target, oracle))
    if case['dataset'] == 'projects' and oracle_tree != case['source']['oracle_tree']:
        raise ValueError('oracle replay differs from frozen evaluation tree')
    if resolve(repo, oracle_commit + '^{tree}') != oracle_tree:
        raise ValueError('oracle replay differs from expected tree')
    if case['dataset'] == 'projects' and baseline_tree != row['target_tree']:
        raise ValueError('target baseline mismatch')
    if case['dataset'] == 'projects' and patch_tree(repo, parents[0], reference) != resolve(repo, row['source_commit'] + '^{tree}'):
        raise ValueError('reference patch does not reconstruct its upstream commit')
    for endpoint in [target, row['source_commit']]:
        ancestry = git(repo, 'merge-base', '--is-ancestor', oracle_commit, endpoint, check=False)
        if ancestry.returncode != 1:
            raise ValueError('oracle exclusion could not be established')
    return {'reference_fix': row['source_commit'], 'reference_parent': parents[0],
            'target_ref': target, 'target_tree': baseline_tree, 'oracle_commit': oracle_commit,
            'oracle_tree': oracle_tree, 'reference_patch': reference.decode('utf-8'),
            'oracle_patch': oracle.decode('utf-8'), 'repository': str(repo)}


def prepare_all(cases, data_dir, output, workers):
    groups = {}
    for case in cases:
        groups.setdefault(case['repository'], []).append(case)
    prepared, failures = {}, {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(prepare_repository, name, group, data_dir, output): (name, group)
                   for name, group in groups.items()}
        for future in as_completed(futures):
            name, group = futures[future]
            try:
                ready, failed = future.result()
            except Exception as exc:
                ready, failed = {}, {case['case_id']: str(exc) for case in group}
            prepared.update(ready)
            failures.update(failed)
            print(json.dumps({'phase': 'source_ready', 'repository': name, 'ready': len(ready),
                              'failed': len(failed)}), flush=True)
    save(output / 'preparation.json', {'selected': len(cases), 'ready': len(prepared), 'failures': failures})
    return prepared, failures


def export_repository(source, destination, prepared):
    """Export only allowed original ancestry; the generator never mounts the private cache."""
    destination.mkdir(parents=True, exist_ok=False)
    git(destination, 'init', '--quiet')
    refs = (prepared['reference_fix'] + '\n' + prepared['target_ref'] + '\n').encode()
    with tempfile.TemporaryFile() as err:
        producer = subprocess.Popen(['git', '--no-replace-objects', '-C', str(source),
            'pack-objects', '--revs', '--stdout', '--delta-base-offset', '--threads=2'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, env=environment())
        consumer = subprocess.Popen(['git', '-C', str(destination), 'index-pack', '--stdin', '--strict'],
            stdin=producer.stdout, stdout=subprocess.DEVNULL, stderr=err, env=environment())
        producer.stdout.close()
        try:
            producer.stdin.write(refs)
            producer.stdin.close()
            producer.wait(timeout=7200)
            status = consumer.wait(timeout=7200)
            if producer.returncode or status:
                err.seek(0)
                raise RuntimeError('allowed-history export failed: ' + err.read().decode(errors='replace')[-1500:])
        finally:
            for proc in [producer, consumer]:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
    for name, commit in [('reference', prepared['reference_fix']), ('target', prepared['target_ref'])]:
        git(destination, 'update-ref', 'refs/heads/' + name, commit)
    git(destination, 'config', 'user.name', 'Patch Port Evaluation')
    git(destination, 'config', 'user.email', 'evaluation@example.invalid')
    git(destination, 'config', 'gc.auto', '0')
    git(destination, 'checkout', '--detach', '--quiet', prepared['target_ref'])
    if not git(destination, 'cat-file', '-e', prepared['oracle_commit'] + '^{commit}', check=False).returncode:
        raise ValueError('oracle object leaked into generation repository')
    if resolve(destination, 'HEAD^{tree}') != prepared['target_tree']:
        raise ValueError('export target tree changed')
    return destination
