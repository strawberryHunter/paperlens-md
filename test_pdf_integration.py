"""Integration checks using an in-memory synthetic PDF. No external manuscripts."""
import fitz
from analyzer import analyze_pages
from validation import report

def test_pdf_to_evidence_end_to_end():
    doc=fitz.open()
    page=doc.new_page()
    page.insert_text((72,72),"GROMACS 2024.1 CHARMM36m at 300 K using TIP3P.")
    page.insert_text((72,92),"The timestep was 4 fs with HMR.")
    payload=doc.tobytes()
    doc.close()
    with fitz.open(stream=payload,filetype="pdf") as pdf:
        pages=[p.get_text(sort=True) for p in pdf]
    result=report(analyze_pages(pages),pages)
    assert result["gate_passed"]
    assert not result["rejected"]
    assert any(r.field=="MD engine" for r in result["valid"])
    assert any(r.field=="Force field" for r in result["valid"])
    assert any(r.field=="Temperature" for r in result["valid"])
    assert any(f.code=="LARGE_TIMESTEP" for f in result["findings"])

def test_lookalike_text_not_auto_certified():
    pages=["The CHARMM36m force field was not used."]
    result=report(analyze_pages(pages),pages)
    assert result["summary"]["candidate_matches"]==1
    # A vacuous all([]) assertion would pass without checking quarantine.
    assert not result["valid"]
    assert len(result["context_review"]) == 1
    assert result["context_review"][0].field == "Force field"
    assert result["context_review"][0].value.lower() == "charmm36m"
