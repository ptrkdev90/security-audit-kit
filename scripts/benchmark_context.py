#!/usr/bin/env python3
"""Measure instruction text proxies and optional paired real audit usage observations."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/security-audit/skills/software-security-audit'


def context_metrics():
    baseline = json.loads((ROOT / 'docs/context-baseline.json').read_text())
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    return {'baseline': baseline, 'current': {'characters': len(text), 'words': len(text.split()), 'utf8_bytes': len(text.encode())},
            'entry_character_reduction_percent': round(100 * (1 - len(text) / baseline['characters']), 2),
            'limits': ['Text-size proxy only; not actual token usage.', 'Required phase/stack references add context.', 'No security quality or token savings claim without paired live measurements.']}


def paired_measurements(samples):
    groups = defaultdict(dict)
    if not isinstance(samples, list) or not samples: raise ValueError('Nonempty sample array required')
    for sample in samples:
        key = tuple(sample[k] for k in ('case', 'model', 'prompt_sha256', 'environment_sha256', 'trial'))
        variant = sample['variant']
        if variant not in {'baseline', 'candidate'} or variant in groups[key]: raise ValueError('Unique baseline/candidate pairs required')
        for field in ('input_tokens', 'output_tokens', 'missed_high_impact', 'false_positives', 'expected_checks', 'reviewed_checks'):
            if not isinstance(sample[field], int) or isinstance(sample[field], bool) or sample[field] < 0: raise ValueError('Nonnegative integer metrics required')
        if sample['reviewed_checks'] > sample['expected_checks']: raise ValueError('Reviewed checks exceed expected checks')
        groups[key][variant] = sample
    rows = []
    for key, pair in groups.items():
        if set(pair) != {'baseline', 'candidate'}: raise ValueError('Incomplete measurement pair')
        a, b = pair['baseline'], pair['candidate']
        if a['expected_checks'] != b['expected_checks']: raise ValueError('Coverage denominators differ')
        original = a['input_tokens'] + a['output_tokens']; candidate = b['input_tokens'] + b['output_tokens']
        if original == 0: raise ValueError('Baseline token total must be positive')
        rows.append({'case': key[0], 'trial': key[-1], 'baseline_total_tokens': original, 'candidate_total_tokens': candidate,
                     'reduction_percent': round(100 * (1 - candidate / original), 2),
                     'quality_regression': b['missed_high_impact'] > a['missed_high_impact'] or b['false_positives'] > a['false_positives'] or b['reviewed_checks'] < a['reviewed_checks'],
                     'candidate_missed_high_impact': b['missed_high_impact'], 'candidate_false_positives': b['false_positives']})
    return {'pairs': rows, 'mean_pair_reduction_percent': round(mean(r['reduction_percent'] for r in rows), 2),
            'quality_regression': any(r['quality_regression'] for r in rows),
            'limits': ['Requires actual host/provider usage and independently assessed expected outcomes.', 'Paired observations do not establish general detection accuracy.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--samples'); parser.add_argument('--output')
    args = parser.parse_args()
    try:
        result = {'context': context_metrics(), 'live_measurements': paired_measurements(json.loads(Path(args.samples).read_text())) if args.samples else None}
        serialized = json.dumps(result, indent=2) + '\n'
        if args.output:
            with Path(args.output).open('x', encoding='utf-8') as stream: stream.write(serialized)
        else: print(serialized, end='')
    except (OSError, ValueError, KeyError, TypeError) as exc: parser.exit(2, 'Benchmark failed: ' + type(exc).__name__ + '\n')

if __name__ == '__main__': main()
