from analyzer import Evidence
from validation import verify_evidence

def test_newline_in_page():
    page = 'The TIP3P' + chr(10) + 'water model was used.'
    record = Evidence('Water model', 'TIP3P', 1, 'The TIP3P water model was used.')
    assert verify_evidence([record], [page]) == ([record], [])


def test_trimmed_excerpt_is_accepted():
    page = "x" * 140 + " TIP3P was used."
    record = Evidence("Water model", "TIP3P", 1, "x" * 110 + " TIP3P was used.")
    assert verify_evidence([record], [page]) == ([record], [])


def test_non_text_page_is_rejected():
    record = Evidence("Water model", "TIP3P", 1, "TIP3P was used.")
    assert verify_evidence([record], [None]) == ([], [record])
