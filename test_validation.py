from dataclasses import replace
from analyzer import analyze_pages
from validation import verify_evidence,evaluate,report

def test_valid_provenance():
    pages=["GROMACS 2024.1 used at 300 K."]
    found=analyze_pages(pages)
    valid,rejected=verify_evidence(found,pages)
    assert valid and not rejected

def test_reject_forged_value_and_page():
    pages=["GROMACS 2024.1 at 300 K."]
    found=analyze_pages(pages)
    candidate=next(x for x in found if x.field=="Temperature")
    valid,rejected=verify_evidence([replace(candidate,value="500 K"),replace(candidate,page=200)],pages)
    assert not valid and len(rejected)==2

def test_large_timestep_review_not_error():
    pages=["The timestep was 4 fs with HMR and LINCS."]
    result=report(analyze_pages(pages),pages)
    assert any(x.code=="LARGE_TIMESTEP" and x.level=="review" for x in result["findings"])
    assert result["gate_passed"]

def test_differing_temperatures_flagged():
    pages=["Simulations used 300 K and 310 K."]
    result=report(analyze_pages(pages),pages)
    assert any(x.code=="MULTIPLE_VALUES" for x in result["findings"])

def test_absence_not_declared_failure():
    pages=["A simulation was performed."]
    result=report(analyze_pages(pages),pages)
    assert result["gate_passed"]
    assert result["summary"]["candidate_matches"]==0

def test_invalid_evidence_fails_gate():
    pages=["Temperature was 300 K."]
    rows=analyze_pages(pages)
    bad=[replace(rows[0],value="not in PDF")]
    assert not report(bad,pages)["gate_passed"]


def test_exact_offset_rejects_incorrect_location_even_if_value_on_page():
    from dataclasses import replace
    pages = ["WT ran at 300 K. E41A ran at 310 K."]
    values = analyze_pages(pages)
    wt = next(v for v in values if v.field == "Temperature" and v.value == "300 K")
    fake = replace(wt, source_start=pages[0].index("310 K"), source_end=pages[0].index("310 K") + 5)
    valid, rejected = verify_evidence([fake], pages)
    assert not valid
    assert len(rejected) == 1


def test_negation_in_previous_sentence_does_not_contaminate_current_sentence():
    pages = ["The TIP3P model was not used. Production was instead performed using SPC/E."]
    result = report(analyze_pages(pages), pages)
    assert any(item.value == "SPC/E" for item in result["valid"])
    assert any(item.value == "TIP3P" for item in result["context_review"])
