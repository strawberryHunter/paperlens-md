"""Scientific checks on extracted *candidate* evidence.

Checks are advisories, not proofs of methodological errors. Never auto-fill unknowns.
"""
import re
from dataclasses import dataclass, asdict
from collections import defaultdict
from context_review import context_screen

@dataclass(frozen=True)
class Finding:
    code: str
    level: str
    title: str
    explanation: str
    pages: tuple

def verify_evidence(records, pages):
    """Only accept results whose quoted value exists on the cited PDF page."""
    valid, rejected = [], []
    for r in records:
        page = getattr(r, "page", 0)
        value = getattr(r, "value", "")
        if (not isinstance(page, int) or page < 1 or page > len(pages)
                or not value or not isinstance(value, str)
                or re.search(r"\s+".join(map(re.escape, value.split())), " ".join(pages[page-1].split()), re.I) is None):
            rejected.append(r)
        else:
            valid.append(r)
    return valid, rejected

def evaluate(records):
    by_field = defaultdict(list)
    for r in records:
        by_field[r.field].append(r)
    findings = []
    def add(code, level, title, explanation, records):
        findings.append(Finding(code,level,title,explanation,tuple(sorted({r.page for r in records}))))
    steps=by_field["Time step"]
    for r in steps:
        m=re.search(r"(\d+(?:\.\d+)?)\s*(fs|ps)\b",r.value,re.I)
        if m and float(m.group(1))*(1000 if m.group(2).lower()=="ps" else 1)>=4:
            add("LARGE_TIMESTEP","review","Large time step detected",
                "Check HMR, constraints, integrator, system type and stability; a large time step is not automatically wrong.",
                [r]+by_field["Constraints / HMR"])
    for field in ("Temperature","Pressure","Force field","Water model","MD engine","Time step"):
        vals={re.sub(r"\s+","",r.value).casefold() for r in by_field[field]}
        if len(vals)>1:
            add("MULTIPLE_VALUES","review",f"Multiple {field} values",
                "Values may refer to different systems or simulation stages. Do not combine them without reading their evidence.",
                by_field[field])
    if by_field["Ensemble"] and any("npt" in r.value.lower() for r in by_field["Ensemble"]) and not by_field["Barostat"]:
        add("MISSING_BAROSTAT_CANDIDATE","info","Barostat not detected",
            "The parser could not find a barostat; check the paper and supporting information.",
            by_field["Ensemble"])
    if by_field["Enhanced sampling"]:
        add("ENHANCED_SAMPLING","info","Enhanced sampling detected",
            "Inspect CV definition, bias protocol, convergence and uncertainty treatment.",
            by_field["Enhanced sampling"])
    return findings

def report(records,pages):
    valid,rejected=verify_evidence(records,pages)
    screened=[(r, *context_screen(r)) for r in valid]
    contextual_review=[r for r,status,_ in screened if status=='review']
    publishable=[r for r,status,_ in screened if status=='candidate']
    findings=evaluate(publishable)
    return {
        "valid":publishable,
        "context_review":contextual_review,
        "rejected":rejected,
        "findings":findings,
        "gate_passed":len(rejected)==0,
        "summary":{"candidate_matches":len(records),"evidence_verified":len(publishable),
                   "context_review":len(contextual_review),
                   "rejected":len(rejected),"review_flags":sum(f.level=="review" for f in findings)}
    }
