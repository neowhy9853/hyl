#!/usr/bin/env python3
"""Probe for itertext() behavior change with Comment and PI elements.

Tests:
1. itertext() on element with Comment child - should skip comment text
2. itertext() on element with PI child - should skip PI text
3. comment.itertext() - should return empty string
4. pi.itertext() - should return empty string
"""

import sys
import xml.etree.ElementTree as ET


def test_comment_in_itertext():
    """itertext() on element with Comment child."""
    e = ET.Element('root')
    e.text = 'before'
    comment = ET.Comment('comment')
    comment.tail = 'after'
    e.append(comment)
    result = ''.join(e.itertext())
    return result, result == 'beforeafter'


def test_pi_in_itertext():
    """itertext() on element with ProcessingInstruction child."""
    e = ET.Element('root')
    e.text = 'before'
    pi = ET.PI('test', 'instruction')
    pi.tail = 'after'
    e.append(pi)
    result = ''.join(e.itertext())
    return result, result == 'beforeafter'


def test_comment_itertext():
    """itertext() directly on a Comment element."""
    comment = ET.Comment('comment')
    result = ''.join(comment.itertext())
    return result, result == ''


def test_pi_itertext():
    """itertext() directly on a PI element."""
    pi = ET.PI('test', 'instruction')
    result = ''.join(pi.itertext())
    return result, result == ''


def test_mixed_content():
    """itertext() with multiple children including comments and PIs."""
    root = ET.Element('root')
    root.text = 'start'
    child = ET.SubElement(root, 'child')
    child.text = 'middle'
    child.tail = 'middle_tail'
    comment = ET.Comment('hidden')
    comment.tail = 'after_hidden'
    root.append(comment)
    pi = ET.PI('proc', 'data')
    pi.tail = 'after_pi'
    root.append(pi)
    result = ''.join(root.itertext())
    # Expected: 'start' + 'middle' + 'middle_tail' + 'after_hidden' + 'after_pi' = 'startmiddlemiddle_tailafter_hiddenafter_pi'
    return result


if __name__ == '__main__':
    results = []

    # Test 1: Comment child in itertext
    r, ok = test_comment_in_itertext()
    results.append(('comment_child', r, ok, "'beforeafter'" if ok else f"'{r}'"))

    # Test 2: PI child in itertext
    r, ok = test_pi_in_itertext()
    results.append(('pi_child', r, ok, "'beforeafter'" if ok else f"'{r}'"))

    # Test 3: Comment.itertext()
    r, ok = test_comment_itertext()
    results.append(('comment_self', r, ok, "''" if ok else f"'{r}'"))

    # Test 4: PI.itertext()
    r, ok = test_pi_itertext()
    results.append(('pi_self', r, ok, "''" if ok else f"'{r}'"))

    # Test 5: Mixed content
    r = test_mixed_content()
    expected = 'startmiddlemiddle_tailafter_hiddenafter_pi'
    ok = r == expected
    results.append(('mixed', r, ok, f"'{expected}'" if ok else f"'{r}'"))

    print("=" * 60)
    print("itertext() Compatibility Probe Results")
    print("=" * 60)
    all_ok = True
    for name, value, ok, expected in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  [{status}] {name}: got '{value}', expected {expected}")

    print()
    if all_ok:
        print("RESULT: PATCHED BEHAVIOR - itertext skips Comment/PI text")
        sys.exit(0)
    else:
        print("RESULT: BASELINE BEHAVIOR - itertext includes Comment/PI text")
        sys.exit(1)
