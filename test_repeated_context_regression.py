"""Synthetic regression for repeated method values with different context.

Reproduce: python -m pytest -q test_repeated_context_regression.py
Baseline PR #1: 2 passed, 2 failed. A conservative review-on-repeat
mitigation should make all four tests pass.
"""
from types import SimpleNamespace
from context_review import context_screen


def record(excerpt, value="TIP3P"):
    return SimpleNamespace(excerpt=excerpt, value=value)


def test_single_positive_candidate():
    assert context_screen(record("The TIP3P water model was used."))[0] == "candidate"


def test_single_negative_held_for_review():
    assert context_screen(record("The TIP3P water model was not used."))[0] == "review"


def test_second_repeated_value_negated_requires_review():
    assert context_screen(record("TIP3P was used. TIP3P was not used."))[0] == "review"


def test_repeated_positive_without_occurrence_binding_requires_review():
    assert context_screen(record("TIP3P was used; TIP3P was used."))[0] == "review"
