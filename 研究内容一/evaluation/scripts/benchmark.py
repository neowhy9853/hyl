"""Dataset, output contract, metrics and audit helpers; Python standard library only."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

METHOD = 'opencode_patch_intent_legacy5_v1'
LABELS = ['feat', 'fix', 'refactor', 'docs', 'test']
PATCH_TYPES = ['BugFix', 'CVE', 'Optimize', 'Feature', 'Refactor', 'CleanUp', 'Doc',
               'Typo修复', 'TestCode', '资源泄露&crash补丁', '其他']
TERMINAL = {'ok', 'unmapped', 'invalid_output'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + '.tmp')
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    pending.replace(path)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def dataset(directory, rounds, limit=None):
    rows = []
    for number in rounds:
        for index, row in enumerate(read_jsonl(Path(directory) / f'round_{number}_50x5.jsonl')):
            if limit is not None and index >= limit:
                break
            if row.get('tag') not in LABELS or not re.fullmatch('[0-9a-f]{40}', row.get('commit_id', '')):
                raise ValueError(f'invalid dataset row: round {number}, index {index}')
            if not re.fullmatch('[A-Za-z0-9_.-]+', row.get('repo', '')) or row['repo'] in ('.', '..'):
                raise ValueError('invalid repository key')
            rows.append({'round': number, 'case_id': f'case_{index + 1:03d}', 'source_index': index,
                         'repo': row['repo'], 'commit_id': row['commit_id'], 'oracle_label': row['tag']})
    if not rows:
        raise ValueError('empty dataset selection')
    return rows


def load_mapping(path):
    mapping = json.loads(Path(path).read_text())['mapping']
    if set(mapping) != set(PATCH_TYPES) or any(v is not None and v not in LABELS for v in mapping.values()):
        raise ValueError('mapping must cover exactly the 11 patch types with a legacy label or null')
    return mapping


def parse_answer(text):
    body = text.strip()
    if body.startswith('```') and body.endswith('```'):
        body = '\n'.join(body.splitlines()[1:-1]).strip()
    value = json.loads(body)
    if not isinstance(value, dict) or value.get('patch_type') not in PATCH_TYPES:
        raise ValueError('invalid patch_type')
    if value.get('severity') not in ('致命', '严重', '一般', '提示'):
        raise ValueError('invalid severity')
    confidence = value.get('confidence')
    if type(confidence) not in (float, int) or not 0 <= confidence <= 1:
        raise ValueError('invalid confidence')
    for key in ('full_feature', 'reason', 'severity_reason'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError('missing ' + key)
    factors = value.get('severity_factors')
    if not isinstance(factors, dict) or not all(isinstance(factors.get(k), str) and factors[k]
            for k in ('failure_mode', 'trigger_condition', 'runtime_exposure', 'blast_radius')):
        raise ValueError('missing severity_factors')
    details = value.get('detailed_analysis')
    if not isinstance(details, dict) or not all(isinstance(details.get(k), str) and details[k]
            for k in ('patch_description', 'impact_and_risk')):
        raise ValueError('missing detailed_analysis')
    items = value.get('intent_items')
    if not isinstance(items, list) or not items:
        raise ValueError('missing intent_items')
    for item in items:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k]
                for k in ('target', 'change', 'effect_or_reason')):
            raise ValueError('invalid intent item')
        if not isinstance(item.get('evidence'), list) or not item['evidence']:
            raise ValueError('missing intent evidence')
    return value


def inspect_events(path):
    events, malformed = [], 0
    for line in Path(path).read_text(errors='replace').splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
            else:
                malformed += 1
        except ValueError:
            malformed += 1
    sessions = sorted({e['sessionID'] for e in events if e.get('sessionID')})
    calls = [e for e in events if e.get('type') == 'tool_use']
    texts = [e.get('part', {}).get('text', '') for e in events if e.get('type') == 'text']
    stats = {'session_ids': sessions, 'tool_counts': dict(Counter(e.get('part', {}).get('tool') for e in calls)),
             'event_count': len(events), 'malformed_lines': malformed,
             'steps': sum(e.get('type') == 'step_finish' for e in events),
             'has_runtime_error': any(e.get('type') == 'error' for e in events),
             'finished': any(e.get('type') == 'step_finish' and e.get('part', {}).get('reason') == 'stop' for e in events)}
    return texts[-1] if texts else '', calls, stats


def metrics(rows, total=None):
    matrix = {g: {p: 0 for p in LABELS + ['invalid_or_failed']} for g in LABELS}
    for row in rows:
        prediction = row.get('predicted_label') if row.get('eval_status') == 'ok' else None
        matrix[row['oracle_label']][prediction if prediction in LABELS else 'invalid_or_failed'] += 1
    per_label = {}
    for label in LABELS:
        tp = matrix[label][label]
        support = sum(matrix[label].values())
        predicted = sum(matrix[g][label] for g in LABELS)
        precision, recall = tp / predicted if predicted else 0, tp / support if support else 0
        per_label[label] = {'total': support, 'correct': tp, 'precision': precision, 'recall': recall,
                            'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0}
    count = len(rows) if total is None else total
    correct = sum(matrix[g][g] for g in LABELS)
    return {'total': count, 'completed': len(rows), 'correct': correct,
            'accuracy': correct / count if count else None, 'confusion_matrix': matrix,
            'per_label': per_label, 'macro_f1': sum(v['f1'] for v in per_label.values()) / len(LABELS),
            'eval_status_counts': dict(Counter(r['eval_status'] for r in rows))}
