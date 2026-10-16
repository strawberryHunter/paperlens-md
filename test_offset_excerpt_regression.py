"""Regression tests for matching PDF excerpts to optional source offsets.

The offsets are relative to whitespace-normalized PDF page text, as in PR #2.
All inputs are synthetic; no confidential documents or external papers.
Reproduce: python -m pytest -q test_offset_excerpt_regression.py
"""
from types import SimpleNamespace

from validation import verify_evidence


def rec(page, excerpt, value, occurrence=None, **offsets):
    data = dict(page=1, excerpt=excerpt, value=value, **offsets)
    if occurrence is not None:
        start = -1
        for _ in range(occurrence + 1):
            start = page.index(value, start + 1)
        data.update(source_start=start, source_end=start + len(value))
    return SimpleNamespace(**data)


def assert_verdict(page, record, accepted):
    valid, rejected = verify_evidence([record], [page])
    assert (valid, rejected) == (([record], []) if accepted else ([], [record]))


def test_correct_offset_and_quote_accepted():
    page = "WT production ran at 300 K. E41A production ran at 300 K."
    record = rec(page, "E41A production ran at 300 K.", "300 K", occurrence=1)
    assert_verdict(page, record, True)


def test_wrong_system_excerpt_with_same_value_rejected():
    page = "WT production ran at 300 K. E41A production ran at 300 K."
    record = rec(page, "WT production ran at 300 K.", "300 K", occurrence=1)
    assert_verdict(page, record, False)


def test_offset_points_to_value_outside_cited_excerpt_rejected():
    page = "WT used TIP3P. E41A used TIP3P."
    record = rec(page, "WT used TIP3P.", "TIP3P", occurrence=1)
    assert_verdict(page, record, False)


def test_partial_offset_metadata_rejected():
    page = "TIP3P was used."
    record = rec(page, page, "TIP3P", source_start=0)
    assert_verdict(page, record, False)


def test_boolean_offset_rejected():
    page = "TIP3P was used."
    record = rec(page, page, "TIP3P", source_start=True, source_end=5)
    assert_verdict(page, record, False)


def test_offset_beyond_page_rejected():
    page = "TIP3P was used."
    record = rec(page, page, "TIP3P", source_start=0, source_end=999)
    assert_verdict(page, record, False)


def test_normalized_whitespace_offset_accepted():
    page = "WT used TIP3P\nwater."
    normalized = " ".join(page.split())
    record = rec(normalized, normalized, "TIP3P", occurrence=0)
    assert_verdict(page, record, True)


def test_legacy_record_without_offsets_still_accepted():
    page = "TIP3P was used."
    record = rec(page, page, "TIP3P")
    assert_verdict(page, record, True)


def test_repeated_identical_excerpt_at_second_offset_accepted():
    page = "TIP3P was used. TIP3P was used."
    record = rec(page, "TIP3P was used.", "TIP3P", occurrence=1)
    assert_verdict(page, record, True)
