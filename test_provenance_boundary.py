from analyzer import Evidence
from validation import verify_evidence

def test_newline_in_page():
    page = 'The TIP3P' + chr(10) + 'water model was used.'
    record = Evidence('Water model', 'TIP3P', 1, 'The TIP3P water model was used.')
    assert verify_evidence([record], [page]) == ([record], [])
