"""Write and verify one self-contained trace alongside one input and one result."""
import base64
from collections import Counter
import json
from pathlib import Path
from port_runtime import digest, save


def read_events(path):
    events, malformed = [], []
    if path.exists():
        for index, line in enumerate(path.read_text(errors='replace').splitlines()):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError('event is not an object')
                events.append(event)
            except ValueError:
                malformed.append({'line': index + 1, 'text': line})
    return events, malformed


def clean_bytes(raw, secrets):
    for secret in secrets:
        if secret:
            raw = raw.replace(secret.encode(), b'[REDACTED]')
    return raw


def write_case(destination, task, result, stages, artifacts, *, secrets=(), previous=None):
    """Artifacts map logical names to bytes; no paths outside the case mount are read here."""
    destination.mkdir(parents=True, exist_ok=True)
    save(destination / 'input.json', task)
    streams = []
    for stage, path in stages:
        raw = clean_bytes(path.read_bytes(), secrets) if path.exists() else b''
        parsed, invalid = [], []
        for index, line in enumerate(raw.decode('utf-8', errors='replace').splitlines()):
            try:
                if line.strip():
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError()
                    parsed.append(event)
            except ValueError:
                invalid.append({'line': index + 1, 'text': line})
        streams.append((stage, parsed))
        if invalid:
            artifacts[stage + '/malformed-events.json'] = json.dumps(invalid).encode()
    records = []
    # Preserve earlier infrastructure attempts when retrying; their contents are not used for scoring.
    if previous and previous.exists():
        records.append({'record_type': 'artifact', 'path': 'previous-attempt/trace.jsonl',
                        'raw': previous.read_bytes()})
    for stage, events in streams:
        for index, event in enumerate(events):
            records.append({'record_type': 'event', 'stage': stage, 'index': index, 'event': event})
    for name, raw in sorted(artifacts.items()):
        if name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('invalid artifact path')
        records.append({'record_type': 'artifact', 'path': name, 'raw': clean_bytes(raw, secrets)})
    emitted, contents = [], {}
    for record in records:
        if record['record_type'] == 'artifact':
            raw = record.pop('raw')
            sha = digest(raw)
            record.update(sha256=sha, bytes=len(raw))
            if sha in contents:
                record['content_ref'] = contents[sha]
            else:
                try:
                    record.update(encoding='utf-8', content=raw.decode('utf-8'))
                except UnicodeDecodeError:
                    record.update(encoding='base64', content=base64.b64encode(raw).decode())
                contents[sha] = record['path']
        emitted.append(record)
    body = ''.join(json.dumps(record, ensure_ascii=False, separators=(',', ':')) + '\n' for record in emitted)
    manifest = {'record_type': 'manifest', 'schema_version': 2, 'dataset': result['dataset'],
                'case_id': result['case_id'], 'method': result['method'],
                'event_counts': {stage: len(events) for stage, events in streams},
                'artifact_count': sum(record['record_type'] == 'artifact' for record in emitted),
                'records_sha256': digest(body.encode())}
    trace = (json.dumps(manifest, ensure_ascii=False) + '\n' + body).encode()
    temp = destination / 'trace.jsonl.tmp'
    temp.write_bytes(trace)
    temp.replace(destination / 'trace.jsonl')
    result.update(trace_file='trace.jsonl', trace_sha256=digest(trace),
                  input_sha256=digest((destination / 'input.json').read_bytes()))
    # Result is the completion marker and is written last.
    save(destination / 'result.json', result)
    return result


def verify_case(case):
    if {p.name for p in case.iterdir()} != {'input.json', 'result.json', 'trace.jsonl'}:
        raise ValueError('a completed case must contain exactly three files')
    inp = json.loads((case / 'input.json').read_text())
    result = json.loads((case / 'result.json').read_text())
    assert result['input_sha256'] == digest((case / 'input.json').read_bytes())
    raw = (case / 'trace.jsonl').read_bytes()
    assert result['trace_sha256'] == digest(raw)
    header, body = raw.split(b'\n', 1)
    manifest = json.loads(header)
    assert manifest['schema_version'] == 2 and manifest['records_sha256'] == digest(body)
    assert manifest['case_id'] == result['case_id'] == inp['case_id']
    assert manifest['dataset'] == result['dataset'] == inp['dataset']
    assert manifest['method'] == result['method']
    events, artifacts = Counter(), {}
    for line in body.splitlines():
        item = json.loads(line)
        if item['record_type'] == 'event':
            assert item['index'] == events[item['stage']]
            events[item['stage']] += 1
        else:
            assert item['record_type'] == 'artifact' and item['path'] not in artifacts
            if 'content_ref' in item:
                data = artifacts[item['content_ref']]
            else:
                data = item['content'].encode() if item['encoding'] == 'utf-8' else base64.b64decode(item['content'], validate=True)
            assert len(data) == item['bytes'] and digest(data) == item['sha256']
            artifacts[item['path']] = data
    assert {stage: events[stage] for stage in manifest['event_counts']} == manifest['event_counts']
    assert set(events) <= set(manifest['event_counts']) and len(artifacts) == manifest['artifact_count']
    patch = result['candidate_patch']
    assert digest(patch['text'].encode()) == patch['sha256']
    gold = inp.get('evaluation_reference', {})
    if gold.get('oracle_patch'):
        assert digest(gold['oracle_patch']['text'].encode()) == gold['oracle_patch']['sha256']
    assert result['correct'] == (result['verdict'] == 'correct')
    comparison = result.get('comparison', {})
    if result['decision_basis'] == 'result_tree_identical':
        assert patch['text'] and comparison['candidate_apply_passed']
        assert comparison['candidate_tree'] == comparison['oracle_tree'] and result['correct']
    if result['decision_basis'] == 'agent_semantic_review':
        review = result['review']
        assert review['verdict'] == result['verdict']
        assert events['review'] > 0 and comparison['candidate_apply_passed']
    return result
