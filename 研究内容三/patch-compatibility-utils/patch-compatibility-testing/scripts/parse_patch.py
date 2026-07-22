#!/usr/bin/env python3
"""
Parse a patch diff file and extract structured metadata about changed symbols.

Usage:
    python parse_patch.py <patch_file> [--repo <repo_path>] [--format json|text]

Output: JSON or text summary of changed files, functions, and line ranges.
"""
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path

def parse_diff(filepath):
    """Parse a unified diff file and extract changed symbols."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    changed_files = []
    current_file = None
    current_hunks = []

    # Match file headers: --- a/path\n+++ b/path or diff --git a/path b/path
    for line in content.split('\n'):
        # New file
        m = re.match(r'^diff --git a/(.+) b/(.+)$', line)
        if m:
            if current_file:
                changed_files.append({
                    'path': current_file['new_path'],
                    'old_path': current_file['old_path'],
                    'hunks': current_hunks
                })
            current_file = {'old_path': m.group(1), 'new_path': m.group(2)}
            current_hunks = []
            continue

        # Hunk header: @@ -old_start,old_count +new_start,new_count @@ context
        m = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\s*(.*)', line)
        if m and current_file:
            old_start = int(m.group(1))
            old_count = int(m.group(2)) if m.group(2) else 1
            new_start = int(m.group(3))
            new_count = int(m.group(4)) if m.group(4) else 1
            context = m.group(5).strip()
            current_hunks.append({
                'old_start': old_start,
                'old_count': old_count,
                'new_start': new_start,
                'new_count': new_count,
                'context': context,
                'added_lines': [],
                'removed_lines': []
            })
            continue

        # Track added/removed lines within current hunk
        if current_hunks:
            if line.startswith('+') and not line.startswith('+++'):
                current_hunks[-1]['added_lines'].append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                current_hunks[-1]['removed_lines'].append(line[1:])

    # Don't forget the last file
    if current_file:
        changed_files.append({
            'path': current_file['new_path'],
            'old_path': current_file['old_path'],
            'hunks': current_hunks
        })

    return changed_files

def extract_symbols(changed_files, repo_path=None):
    """For each changed file, identify the enclosing function for each hunk."""
    for f in changed_files:
        f['symbols'] = []

        # Try to get the actual file content for context
        file_content = None
        if repo_path:
            filepath = Path(repo_path) / f['path']
            if filepath.exists():
                file_content = filepath.read_text(errors='replace').split('\n')

        for hunk in f['hunks']:
            # Search backward from hunk start to find enclosing function
            func_name = find_enclosing_function(hunk['new_start'], file_content)
            if func_name:
                f['symbols'].append({
                    'name': func_name,
                    'old_lines': [hunk['old_start'], hunk['old_start'] + hunk['old_count'] - 1],
                    'new_lines': [hunk['new_start'], hunk['new_start'] + hunk['new_count'] - 1]
                })

    return changed_files

def find_enclosing_function(line_num, file_content):
    """Find the function definition that contains the given line."""
    if not file_content:
        return None

    # Common function definition patterns
    patterns = [
        r'^(?:static\s+)?(?:inline\s+)?(?:const\s+)?(?:virtual\s+)?'
        r'(?:[\w:*&<>\s]+)\s+(\w+)\s*\([^)]*\)\s*(?:const\s*)?\{',
        r'^(?:static\s+)?(?:inline\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*$',
    ]

    # Search backward from the given line
    best_name = None
    best_line = 0
    for i in range(min(line_num, len(file_content)) - 1, -1, -1):
        line = file_content[i]
        for pat in patterns:
            m = re.match(pat, line.strip())
            if m:
                name = m.group(1)
                # Skip keywords that look like function names
                if name in ('if', 'while', 'for', 'switch', 'return', 'sizeof', 'typeof'):
                    continue
                if i > best_line:
                    best_name = name
                    best_line = i
                    break
        if best_name:
            break

    return best_name

def main():
    parser = argparse.ArgumentParser(description='Parse patch diff and extract changed symbols')
    parser.add_argument('patch_file', help='Path to the patch diff file')
    parser.add_argument('--repo', '-r', help='Path to the source repository for context')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text',
                        help='Output format (default: text)')
    args = parser.parse_args()

    changed_files = parse_diff(args.patch_file)
    changed_files = extract_symbols(changed_files, args.repo)

    if args.format == 'json':
        print(json.dumps({
            'total_changed_files': len(changed_files),
            'changed_files': changed_files
        }, indent=2))
    else:
        print(f"Changed files: {len(changed_files)}")
        for f in changed_files:
            print(f"\n  {f['path']}:")
            print(f"    hunks: {len(f['hunks'])}")
            if f.get('symbols'):
                for s in f['symbols']:
                    print(f"    symbol: {s['name']} (old: {s['old_lines']}, new: {s['new_lines']})")

if __name__ == '__main__':
    main()
