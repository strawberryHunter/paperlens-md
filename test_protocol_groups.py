"""Boundary and multi-system labeling regression tests."""
from dataclasses import dataclass

from analyzer import analyze_pages
from protocol_groups import label_for, annotate

@dataclass
class ExampleRecord:
    value: str
    page: int
    excerpt: str
    source_start: int | None = None
    source_end: int | None = None


def record(value, text, occurrence=0):
    start=-1
    for _ in range(occurrence+1):
        start=text.index(value,start+1)
    return ExampleRecord(value,1,text,start,start+len(value))


def test_two_named_systems_with_same_numeric_value_remain_separate():
    page="WT production simulations ran at 300 K. E41A production simulations ran at 300 K."
    a=label_for(record("300 K",page),[page])
    b=label_for(record("300 K",page,1),[page])
    assert (a.system,b.system)==("WT","E41A")
    evidence=[x for x in analyze_pages([page]) if x.field=="Temperature"]
    assert len(evidence)==2  # no data loss from de-duplication
    assert [x.system for x in annotate(evidence,[page])]==["WT","E41A"]


def test_equilibration_is_not_merged_with_production():
    page="WT equilibration was performed at 300 K. WT production was performed at 310 K."
    assert label_for(record("300 K",page),[page]).stage=="Equilibration"
    assert label_for(record("310 K",page),[page]).stage=="Production"


def test_conflicting_systems_cannot_be_auto_assigned():
    page="Both WT and E41A mutants were simulated at 300 K."
    result=label_for(record("300 K",page),[page])
    assert result.system=="Ambiguous" and result.status=="Review"


def test_missing_experiment_label_remains_unassigned():
    page="The temperature was 300 K."
    assert label_for(record("300 K",page),[page]).system=="Unassigned"


def test_named_mutation_not_confused_with_generic_mutant_word():
    page="E41A mutant production simulations were performed at 300 K."
    assert label_for(record("300 K",page),[page]).system=="E41A"
