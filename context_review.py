"""Conservative context screening for lexical MD methods matches.

Not a language model. Negation screening is deliberately narrow and ambiguous
cases are quarantined for manual review rather than called false findings.
"""
import re

NEGATION = re.compile(r"\b(?:not|never|without|instead of|rather than)\b",re.I)
CLAUSE_BREAK = re.compile(r"[.;:]|\b(?:but|however|whereas)\b",re.I)
def context_screen(record):
    """Return (status, reason). Only flags clear nearby negation in same clause."""
    text=record.excerpt
    match=re.search(re.escape(record.value),text,re.I)
    if not match:
        return "review", "Could not locate matching value inside excerpt"
    suffix=text[match.end():match.end()+95]
    if re.search(r"^(?:\\s+(?:force field|water model|thermostat|barostat|engine|software))?\\s+(?:was|were|is|are)\\s+not\\s+(?:used|employed|applied|selected)", suffix,re.I):
        return "review", "Explicit post-mention negation detected"
    prefix=text[:match.start()]
    clause=CLAUSE_BREAK.split(prefix)[-1]
    # Negations in the short phrase before the matched value can reverse its meaning.
    near=" ".join(clause.split()[-9:])
    if NEGATION.search(near):
        return "review", "Potential negation near method name; inspect original sentence"
    return "candidate", "No simple negation detected; context is NOT independently verified"
