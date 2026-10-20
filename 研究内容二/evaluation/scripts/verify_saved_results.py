"""Verify compact case inputs, outputs and self-contained traces without model calls."""
import argparse
import base64
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath


def load(path):
    return json.loads(path.read_text())


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_trace(path):
    records = lines(path)
    manifest = records[0]
    assert manifest['record_type'] == 'manifest' and manifest['schema_version'] == 1
    events, artifacts = [], {}
    for record in records[1:]:
        if record['record_type'] == 'generation_event':
            assert record['index'] == len(events)
            events.append(record['event'])
        else:
            assert record['record_type'] == 'artifact'
            name = record['path']
            assert name not in artifacts and not PurePosixPath(name).is_absolute()
            assert '..' not in PurePosixPath(name).parts
            if 'content_ref' in record:
                assert 'content' not in record
                raw = artifacts[record['content_ref']]
            elif record['encoding'] == 'utf-8':
                raw = record['content'].encode('utf-8')
            else:
                assert record['encoding'] == 'base64'
                raw = base64.b64decode(record['content'], validate=True)
            assert len(raw) == record['bytes'] and digest(raw) == record['sha256'], name
            artifacts[name] = raw
    assert list(artifacts) == manifest['artifact_paths']
    assert len(artifacts) == manifest['artifact_count']
    assert len(events) == manifest['generation_event_count']
    assert digest(json.dumps(events, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode()) == manifest['generation_events_sha256']
    assert manifest['embedded_files'] == {
        'candidate.patch': 'result.json#/candidate_patch/text',
        'oracle.patch': 'input.json#/evaluation_reference/oracle_patch/text',
        'generation/prompt.txt': 'input.json#/task_input/prompt',
    }
    return manifest, events, artifacts


def verify(root, dataset_dir):
    counts = Counter()
    traces = reviews = attempts = reasoning_cases = same_tree = semantic_correct = artifact_count = 0
    for ds, filename, expected in [('linux', 'linux404.jsonl', 404),
                                    ('projects', 'feishu92.jsonl', 92)]:
        inputs = lines(dataset_dir / filename)
        originals = {str(row['case_id']): row for row in inputs}
        rows = lines(root / ds / 'results.jsonl')
        assert len(rows) == len(inputs) == len(originals) == expected
        assert {row['case_id'] for row in rows} == set(originals)
        assert {p.name for p in (root / ds / 'cases').iterdir()} == set(originals)
        verdicts, bases = Counter(), Counter()
        dataset_reviews = 0
        for result in rows:
            cid = result['case_id']
            assert result['dataset'] == ds and result['case_path'] == f'cases/{cid}'
            case = root / ds / result['case_path']
            assert {p.name for p in case.iterdir()} == {'input.json', 'result.json', 'trace.jsonl'}
            assert result == load(case / 'result.json') and result['trace_file'] == 'trace.jsonl'
            inp = load(case / 'input.json')
            assert inp['dataset'] == ds and inp['case_id'] == cid
            assert inp['task_type'] == 'security_patch_port'
            original = originals[cid]
            assert inp['provenance']['source_dataset_record'] == original
            task, gold = inp['task_input'], inp['evaluation_reference']
            assert task['source_commit'] == original['source_commit']
            assert task['repository']['target_ref'] == result['target_ref']
            assert task['repository']['target_tree'] == result['baseline_tree']
            assert digest(task['prompt'].encode()) == inp['provenance']['prompt_sha256']
            assert digest(task['reference_patch']['text'].encode()) == task['reference_patch']['sha256']
            if ds == 'projects':
                assert task['reference_patch']['sha256'] == original['reference_sha256']
            assert gold['purpose'] == 'independent_review_only_not_generator_input'
            assert gold['oracle_commit'] == original.get('oracle_commit')
            assert digest(gold['oracle_patch']['text'].encode()) == gold['oracle_patch']['sha256'] == result['oracle_sha256']
            patch = result['candidate_patch']
            assert patch['format'] == 'unified_diff'
            assert digest(patch['text'].encode()) == patch['sha256'] == result['candidate_sha256']
            assert bool(patch['text']) == result['candidate_nonempty']
            manifest, events, artifacts = read_trace(case / 'trace.jsonl')
            artifact_count += len(artifacts)
            assert manifest['dataset'] == ds and manifest['case_id'] == cid
            if gold['selected_review_task']:
                assert gold['selected_review_task'] in artifacts
            meta = manifest['metadata']
            assert meta['dataset'] == ds and meta['case_id'] == cid
            assert len(events) == meta['event_count']
            assert dict(Counter(e.get('type', 'unknown') for e in events)) == meta['event_types']
            tools = Counter(e.get('part', {}).get('tool', 'unknown') for e in events
                            if e.get('type') == 'tool_use')
            assert tools and dict(tools) == meta['tool_calls']
            assert meta['session_ids'] == sorted({e['sessionID'] for e in events if e.get('sessionID')})
            assert meta['generation_trace_available'] == result['generation_trace_available'] == True
            traces += 1
            comparison = json.loads(artifacts['comparison.json'])
            for key in ['candidate_sha256', 'oracle_sha256', 'target_ref', 'baseline_tree',
                        'candidate_tree', 'oracle_tree', 'candidate_nonempty', 'candidate_apply_passed']:
                assert comparison[key] == result[key], (ds, cid, key)
            saved = json.loads(artifacts['review/result.json'])
            if not result['candidate_nonempty']:
                assert result['verdict'] == 'generation_failed' and result['decision_basis'] == 'no_candidate'
            elif comparison['full_result_tree_identical']:
                same_tree += 1
                assert result['verdict'] == 'correct' and result['decision_basis'] == 'result_tree_identical'
                assert comparison['candidate_apply_passed'] and comparison['candidate_tree'] == comparison['oracle_tree']
            else:
                reviews += 1
                dataset_reviews += 1
                semantic_correct += result['verdict'] == 'correct'
                assert result['decision_basis'] == 'agent_semantic_review' and result['review_trace_available']
                for key in ['verdict', 'candidate_sha256', 'candidate_tree', 'oracle_tree']:
                    assert saved[key] == result[key]
                selected = 'review/attempts/' + meta['selected_review_attempt'] + '/result.json'
                assert json.loads(artifacts[selected]) == saved
                attempt_names = {name.split('/')[2] for name in artifacts if name.startswith('review/attempts/')}
                assert attempt_names
                has_reasoning = False
                for attempt in attempt_names:
                    attempts += 1
                    prefix = f'review/attempts/{attempt}/'
                    agent = prefix + 'agent-review/'
                    assert agent + 'task.json' in artifacts and agent + 'conversation.json' in artifacts
                    assert any(name.startswith(agent + 'round-') and name.endswith('-input.json') for name in artifacts)
                    attempt_result = json.loads(artifacts[prefix + 'result.json'])
                    if agent + 'observations.json' not in artifacts:
                        assert attempt_result['verdict'] == 'judge_error'
                        assert attempt_result['investigation']['queries'] == 0
                        assert attempt_result['investigation']['source_observations'] == 0
                    for name, raw in artifacts.items():
                        if name.startswith(agent + 'round-') and '-attempt-' in name and name.endswith('.json'):
                            response = json.loads(raw)
                            if isinstance(response, dict) and any(choice.get('message', {}).get('reasoning_content')
                                                                  for choice in response.get('choices', [])):
                                has_reasoning = True
                reasoning_cases += has_reasoning
            assert result['correct'] == (result['verdict'] == 'correct')
            assert saved['verdict'] == result['verdict']
            verdicts[result['verdict']] += 1
            bases[result['decision_basis']] += 1
            counts[result['verdict']] += 1
        metric = load(root / ds / 'metrics.json')
        assert metric['total'] == len(rows) and metric['correct'] == verdicts['correct']
        assert metric['accuracy'] == verdicts['correct'] / len(rows)
        assert metric['verdict_counts'] == {key: verdicts[key] for key in
                                           ['correct', 'incorrect', 'uncertain', 'judge_error', 'generation_failed']}
        assert metric['decision_basis_counts'] == {key: bases[key] for key in
                                                  ['result_tree_identical', 'agent_semantic_review', 'no_candidate']}
        assert metric['generation_traces'] == len(rows) and metric['semantic_review_traces'] == dataset_reviews
    assert sum(counts.values()) == traces == 496 and counts['correct'] == 480
    assert reviews == 129 and attempts == 137 and reasoning_cases == 129
    assert same_tree == 363 and semantic_correct == 117
    print(json.dumps({'verified_cases': traces, 'files_per_case': 3, 'correct': counts['correct'],
                      'accuracy': counts['correct'] / traces, 'generation_traces': traces,
                      'semantic_review_cases': reviews, 'review_attempts': attempts,
                      'semantic_cases_with_provider_reasoning': reasoning_cases,
                      'embedded_artifact_files': artifact_count}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=Path(__file__).resolve().parents[1] / 'results')
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parents[1] / 'data')
    args = parser.parse_args()
    verify(args.results, args.data)
