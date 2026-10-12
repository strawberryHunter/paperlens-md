from analyzer import analyze_pages,checklist,advisory,export_records

def test_page_and_parameter():
    a=analyze_pages(["GROMACS 2024.1 with CHARMM36m.","The timestep was 4 fs with HMR."])
    assert any(x.field=="MD engine" and x.page==1 for x in a)
    assert any(x.field=="Time step" and x.page==2 for x in a)

def test_missing_does_not_mean_absence():
    rows=checklist(analyze_pages(["No relevant patterns here."]))
    assert all(row["Detection"]=="Not detected" for row in rows)

def test_no_spurious_replicas():
    assert not any(x.field=="Replicas" for x in analyze_pages(["Two samples were collected."]))

def test_export_and_advisory():
    a=analyze_pages(["The timestep was 4 fs; TIP3P TIP3P."])
    assert any("4–5 fs" in x for x in advisory(a))
    assert sum(x["field"]=="Water model" for x in export_records(a))==1


def test_timestep_grammatical_variants():
    forward = analyze_pages(["A timestep of 4 fs was used."])
    reverse = analyze_pages(["We applied a 4 fs timestep with HMR."])
    assert any(item.field == "Time step" and "4 fs" in item.value for item in forward)
    assert any(item.field == "Time step" and "4 fs" in item.value for item in reverse)
