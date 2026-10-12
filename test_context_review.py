from analyzer import analyze_pages
from validation import report

def test_negated_forcefield_quarantined():
    pages=["The CHARMM36m force field was not used."]
    result=report(analyze_pages(pages),pages)
    assert len(result["context_review"])==1
    assert not result["valid"]
    assert result["gate_passed"]

def test_negated_prefix_quarantined():
    pages=["We did not use TIP3P water in production."]
    result=report(analyze_pages(pages),pages)
    assert len(result["context_review"])==1

def test_positive_stays_candidate():
    pages=["Simulations used the TIP3P water model."]
    result=report(analyze_pages(pages),pages)
    assert len(result["valid"])==1
    assert not result["context_review"]

def test_explicit_limitation_kept_in_report():
    pages=["GROMACS 2024.1 was used. The CHARMM36m force field was not used."]
    result=report(analyze_pages(pages),pages)
    assert any(x.field=="MD engine" for x in result["valid"])
    assert any(x.field=="Force field" for x in result["context_review"])
