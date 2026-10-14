from analyzer import Evidence
from validation import verify_evidence

def test_excerpt_match():
    text = 'TIP3P was used.'
    record = Evidence('Water model', 'TIP3P', 1, text)
    assert verify_evidence([record], [text]) == ([record], [])
