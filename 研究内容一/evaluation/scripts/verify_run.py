#!/usr/bin/env python3
"""Recompute a new run's results and metrics from frozen inputs and original traces."""
import argparse
import json
from pathlib import Path

from benchmark import METHOD, TERMINAL, inspect_events, metrics, parse_answer, read_jsonl


def verify(output):
    output = Path(output).resolve()
    protocol = json.loads((output / 'protocol.json').read_text())
    if protocol['method'] != METHOD:
        raise ValueError('unknown evaluation method; expected a run produced by run_evaluation.py')
    expected = {(r['round'], r['case_id']): r for r in protocol['rows']}
    all_rows, rounds = [], []
    for number in sorted({r['round'] for r in protocol['rows']}):
        folder = output / f'round_{number}'
        rows = read_jsonl(folder / 'results.jsonl')
        if len(rows) != sum(k[0] == number for k in expected):
            raise ValueError(f'round {number} incomplete')
        seen = set()
        for row in rows:
            key = (number, row['case_id'])
            if key in seen or key not in expected:
                raise ValueError('duplicate or unexpected case')
            seen.add(key)
            for field, value in expected[key].items():
                if row.get(field) != value:
                    raise ValueError(f'input mismatch: {key} {field}')
            trace = (folder / row['trace_path']).resolve()
            if folder not in trace.parents:
                raise ValueError('trace escapes round directory')
            if json.loads((trace / 'metadata.json').read_text()) != row:
                raise ValueError('metadata mismatch')
            if json.loads((folder / 'traces' / row['case_id'] / 'result.json').read_text()) != row:
                raise ValueError('latest result mismatch')
            prediction = None
            if row['eval_status'] in ('ok', 'unmapped'):
                text, calls, stats = inspect_events(trace / 'events.jsonl')
                if row['runtime']['exit_code'] or row['runtime']['failure'] or stats['has_runtime_error'] or not stats['finished']:
                    raise ValueError('accepted failed runtime')
                value = parse_answer(text)
                if value != json.loads((trace / 'answer.json').read_text()):
                    raise ValueError('answer differs from original event stream')
                prediction = protocol['mapping'][value['patch_type']]
                if row['patch_type'] != value['patch_type'] or row['severity'] != value['severity']:
                    raise ValueError('classification mismatch')
                if (prediction is None) != (row['eval_status'] == 'unmapped'):
                    raise ValueError('mapping status mismatch')
                if stats != row['investigation'] or calls != json.loads((trace / 'tool-calls.json').read_text()):
                    raise ValueError('event accounting mismatch')
            if row.get('predicted_label') != prediction or row['match'] != (prediction == row['oracle_label']):
                raise ValueError('score mismatch')
        recomputed = {'round': number, **metrics(rows)}
        if json.loads((folder / 'metrics.json').read_text()) != recomputed:
            raise ValueError(f'round {number} metrics mismatch')
        rounds.append(recomputed)
        all_rows.extend(rows)
    summary = json.loads((output / 'summary.json').read_text())
    for key, value in metrics(all_rows).items():
        if summary[key] != value:
            raise ValueError('summary mismatch: ' + key)
    if summary['rounds'] != rounds or not summary['complete']:
        raise ValueError('incomplete or inconsistent summary')
    return {'verified': len(all_rows), 'correct': summary['correct'], 'accuracy': summary['accuracy'],
            'infrastructure_errors': sum(r['eval_status'] not in TERMINAL for r in all_rows),
            'status_counts': summary['eval_status_counts'], 'method': METHOD}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.output)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result['infrastructure_errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
