"""Synthetic regression for repeated method values with different context.

Reproduce: python -m pytest -q test_repeated_context_regression.py
Covers positive, negative, repeated, case-insensitive, and token-boundary cases.
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


def test_case_insensitive_repetition_requires_review():
    assert context_screen(record("tip3p was used; TIP3P was used."))[0] == "review"


def test_similar_longer_prefix_token_does_not_create_false_negation():
    assert context_screen(record("TIP3Pplus was not used. TIP3P was used."))[0] == "candidate"


def test_similar_longer_suffix_token_does_not_create_false_repeat():
    assert context_screen(record("TIP3P was used. TIP3P2 was not used."))[0] == "candidate"


def test_only_similar_longer_token_is_not_valid_evidence():
    assert context_screen(record("TIP3Pplus was used."))[0] == "review"
