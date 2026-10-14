from analyzer import Evidence
from validation import verify_evidence

def test_excerpt_match():
    text = 'TIP3P was used.'
    record = Evidence('Water model', 'TIP3P', 1, text)
    assert verify_evidence([record], [text]) == ([record], [])


def test_negated_page_does_not_accept_different_quote():
    page = "The TIP3P water model was not used."
    record = Evidence("Water model", "TIP3P", 1, "The TIP3P water model was used.")
    assert verify_evidence([record], [page]) == ([], [record])


def test_other_page_with_same_value_is_rejected():
    pages = ["TIP3P was not used.", "TIP3P was used."]
    record = Evidence("Water model", "TIP3P", 1, pages[1])
    assert verify_evidence([record], pages) == ([], [record])


def test_value_must_occur_inside_excerpt():
    page = "TIP3P was used. GROMACS 2024.1 was used."
    record = Evidence("Water model", "TIP3P", 1, "GROMACS 2024.1 was used.")
    assert verify_evidence([record], [page]) == ([], [record])
