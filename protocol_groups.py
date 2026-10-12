"""Conservative within-sentence context labels for MD parameter candidates.

No inferred experimental grouping: a label is assigned only when the same
sentence as the matched value explicitly names one system or stage.
Conflicting or missing labels are clearly marked for manual review.
"""
from dataclasses import dataclass
import re

SYSTEM_RE = re.compile(r"\b(?:WT|wild[ -]?type|mutant|mutants|variant|variants|[A-Z]\d{1,4}[A-Z])\b", re.I)
STAGE_RE = re.compile(r"\b(?:production|equilibrat(?:ion|ing|ed)|minimiz(?:ation|ing|ed)|heating)\b", re.I)
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])|;\s*")
MUTATION = re.compile(r"^[A-Z]\d{1,4}[A-Z]$")


@dataclass(frozen=True)
class Context:
    system: str
    stage: str
    status: str
    source_sentence: str


def sentence_for(record, pages):
    if not 1 <= record.page <= len(pages):
        return record.excerpt
    clean = " ".join(pages[record.page - 1].split())
    position = getattr(record, "source_start", None)
    end = getattr(record, "source_end", None)
    if position is None or end is None or clean[position:end].casefold() != record.value.casefold():
        return record.excerpt
    boundaries = [0]
    for delim in SENTENCE_END.finditer(clean):
        boundaries.append(delim.end())
    boundaries.append(len(clean))
    for i in range(len(boundaries) - 1):
        if boundaries[i] <= position < boundaries[i + 1]:
            return clean[boundaries[i]:boundaries[i + 1]].strip()
    return record.excerpt


def label_for(record, pages):
    sentence = sentence_for(record, pages)
    systems = []
    for token in SYSTEM_RE.findall(sentence):
        label = token.upper() if MUTATION.fullmatch(token.upper()) else (
            "WT" if token.lower().replace("-", "").replace(" ", "") in ("wt", "wildtype")
            else "Mutant (unspecified)"
        )
        if label not in systems:
            systems.append(label)
    if any(MUTATION.fullmatch(label) for label in systems) and "Mutant (unspecified)" in systems:
        systems.remove("Mutant (unspecified)")
    stages = []
    for token in STAGE_RE.findall(sentence):
        low = token.lower()
        label = ("Production" if low == "production"
                 else "Equilibration" if low.startswith("equilibrat")
                 else "Minimization" if low.startswith("minimiz") else "Heating")
        if label not in stages:
            stages.append(label)
    system = systems[0] if len(systems) == 1 else ("Ambiguous" if systems else "Unassigned")
    stage = stages[0] if len(stages) == 1 else ("Ambiguous" if stages else "Unassigned")
    status = ("Review" if "Ambiguous" in (system, stage)
              else "Partial" if "Unassigned" in (system, stage) else "Explicit")
    return Context(system, stage, status, sentence)


def annotate(records, pages):
    return [label_for(record, pages) for record in records]
