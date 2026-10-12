"""Conservative sentence-local lexical negation screening for MD candidates."""
import re

NEGATION = re.compile(r"\b(?:not|never|without|instead of|rather than|neither)\b", re.I)
POST_NEGATION = re.compile(
    r"^\s+(?:(?:force field|water model|thermostat|barostat|engine|software)\s+)?"
    r"(?:was|were|is|are)\s+not\s+(?:used|employed|applied|selected|chosen)\b", re.I
)


def context_screen(record, source_sentence=None):
    text = source_sentence if source_sentence is not None else record.excerpt
    match = re.search(re.escape(record.value), text, re.I)
    if match is None:
        return "review", "Exact candidate not found within selected sentence"
    prefix = text[:match.start()]
    suffix = text[match.end():]
    if POST_NEGATION.search(suffix):
        return "review", "Post-mention negation in source sentence"
    if NEGATION.search(" ".join(prefix.split()[-10:])):
        return "review", "Negation before candidate within source sentence"
    return "candidate", "No direct negation found; scientific use remains unverified"
