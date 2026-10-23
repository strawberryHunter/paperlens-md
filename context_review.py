"""Conservative context screening for lexical MD parameter candidates.

This is a heuristic; detected context issues are held for human review.
"""
import re

NEGATION = re.compile(r"\b(?:not|never|without|instead of|rather than)\b", re.I)
CLAUSE_BREAK = re.compile(r"[.;:]|\b(?:but|however|whereas)\b", re.I)
POST_NEGATION = re.compile(
    r"^\s+(?:(?:force field|water model|model|water|thermostat|barostat|engine|software)\s+)?"
    r"(?:was|were|is|are)\s+(?:not|never)\s+(?:used|employed|applied|selected)\b",
    re.I,
)
# Only pair explicit quotation marks; an apostrophe within a word is not a quote.
QUOTED_SPAN = re.compile(r'''"[^"\n]*"|“[^”\n]*”|‘[^’\n]*’|(?<!\w)'[^'\n]*'(?!\w)''')


def context_screen(record):
    """Return (status, reason). This does NOT establish scientific truth."""
    text = record.excerpt
    # Whole-token matching avoids treating TIP3P2 as another occurrence of TIP3P.
    matches = list(re.finditer(r"(?<!\w)" + re.escape(record.value) + r"(?!\w)", text, re.I))
    if not matches:
        return "review", "Matched value not found in excerpt"
    # Without occurrence binding, different mentions may have conflicting contexts.
    if len(matches) > 1:
        return "review", "Repeated value in excerpt; verify each mention against its original context"
    match = matches[0]

    # Quoted values can describe other work rather than the current simulation.
    # A clipped excerpt with a quote immediately adjacent to the value is also held.
    if (any(span.start() <= match.start() and match.end() <= span.end()
            for span in QUOTED_SPAN.finditer(text))
        or text[match.start()-1:match.start()] in {'"', "'", "“", "‘"}
        or text[match.end():match.end()+1] in {'"', "'", "”", "’"}):
        return "review", "Value appears in or next to quotation marks; verify source context"

    # Check language immediately after the quoted method term.
    suffix = text[match.end():match.end() + 110]
    if POST_NEGATION.search(suffix):
        return "review", "Explicit post-mention negation; confirm in original context"

    # Check the current clause, not a preceding sentence or unrelated clause.
    prefix = text[:match.start()]
    clause = CLAUSE_BREAK.split(prefix)[-1]
    near = " ".join(clause.split()[-9:])
    if NEGATION.search(near):
        return "review", "Potential pre-mention negation; confirm in original context"

    return "candidate", "No simple negation detected; context remains unverified"
