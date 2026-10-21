"""Synthetic positive, negative, and boundary tests for post-mention 'model' negation.

Reproduce from repo root: python -m pytest -q test_model_negation_regression.py
No external papers or sensitive content are used.
"""
from types import SimpleNamespace

from context_review import context_screen


def _status(excerpt):
    return context_screen(SimpleNamespace(value="TIP3P", excerpt=excerpt))[0]


def test_model_was_not_used_is_held():
    assert _status("The TIP3P model was not used.") == "review"


def test_model_is_never_employed_is_held():
    assert _status("The TIP3P model is never employed.") == "review"


def test_model_was_used_remains_candidate():
    assert _status("The TIP3P model was used.") == "candidate"


def test_negated_longer_token_does_not_quarantine_valid_tip3p():
    assert _status("TIP3Pplus model was not used. TIP3P model was used.") == "candidate"
