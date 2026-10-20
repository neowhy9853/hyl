#!/usr/bin/env python3
"""Recompute a one-click run's scores from the three files in every selected case."""
import argparse
from collections import Counter
import json
from pathlib import Path
from port_trace import verify_case


def verify(output):
    protocol = json.loads((output / 'protocol.json').read_text())
    cases = protocol['cases']
    assert len({(case['dataset'], case['case_id']) for case in cases}) == len(cases)
    verdicts = Counter()
    for ds in sorted({case['dataset'] for case in cases}):
        selected = [case for case in cases if case['dataset'] == ds]
        group = output / 'results' / ds
        expected = {case['case_id'] for case in selected}
        assert {path.name for path in (group / 'cases').iterdir()} == expected
        rows = [json.loads(line) for line in (group / 'results.jsonl').read_text().splitlines() if line.strip()]
        assert len(rows) == len(expected) and {row['case_id'] for row in rows} == expected
        indexed = {row['case_id']: row for row in rows}
        counts = Counter()
        for case in selected:
            row = verify_case(group / 'cases' / case['case_id'])
            assert row == indexed[case['case_id']] and row['method'] == protocol['method']
            inp = json.loads((group / 'cases' / case['case_id'] / 'input.json').read_text())
            assert inp['source_dataset_record'] == case['record']
            if 'source_recipe' in inp:
                assert inp['source_recipe'] == case['source']
            counts[row['verdict']] += 1
        metric = json.loads((group / 'metrics.json').read_text())
        assert metric['total'] == metric['completed'] == len(expected) and metric['pending'] == 0
        assert metric['correct'] == counts['correct'] and metric['accuracy'] == counts['correct'] / len(expected)
        assert metric['verdict_counts'] == dict(counts)
        verdicts.update(counts)
    summary = json.loads((output / 'summary.json').read_text())
    assert summary['complete'] and summary['total'] == summary['completed'] == len(cases)
    assert summary['correct'] == verdicts['correct'] and summary['accuracy'] == verdicts['correct'] / len(cases)
    assert summary['verdict_counts'] == dict(verdicts)
    assert summary['infrastructure_errors'] == sum(verdicts[key] for key in ['preparation_error', 'generation_error', 'judge_error'])
    print(json.dumps({'verified': len(cases), 'correct': verdicts['correct'],
                      'accuracy': verdicts['correct'] / len(cases), 'files_per_case': 3}))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    verify(parser.parse_args().output.resolve())
