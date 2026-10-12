# PaperLens MD

Evidence-first Molecular Dynamics Methods scanner.

Upload a scientific PDF to extract **candidate** MD methods parameters (MD engine, force field, timestep, duration, water model, thermostats, etc.), view the supporting PDF page and nearby text, and export results as CSV/JSON. The reproducibility checklist is for manual review and is **not** a claim that missing values were omitted by the authors.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501 **only while the server is running**.

## Deploy

Go to https://share.streamlit.io/ and create an app from the public GitHub repo `strawberryHunter/paperlens-md`, branch `main`, main file `app.py`.

## Limits

Rule-based prototype, not an LLM or scientific reviewer. False positives (including References) and missed values are possible. PDF page numbers refer to PDF pages. Scanned PDFs and supplementary files may need separate processing. Do not upload confidential manuscripts without checking service policies.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

## References

- https://doi.org/10.1021/acs.jcim.3c00599
- https://doi.org/10.1038/s42003-023-04653-0


## Release gates (v0.3)
1. Input: reject corrupt/encrypted/non-text PDFs, pages >100, upload >50 MB.
2. Provenance: retain only candidates whose value is reproducibly present on the original PDF page.
3. Scientific review: mark multi-value parameters and large time steps for manual review; never auto-label these as proven errors.
4. CI: test parser, deliberate false provenance, sample PDFs and regression cases before release.

A green CI run shows only that programmed tests passed, not that extraction accuracy is high.
Before any accuracy claim, assemble a human-annotated, openly redistributable benchmark split into development/test sets, including positive and negative contexts, main text and supplementary documents. Report field-level precision, recall, F1, failure cases, and dataset version.

**Known limitations:** rule-based extraction can treat negation, citations, and other unrelated simulations as valid text matches. Page-level verification is necessary but NOT sufficient for scientific evidence. No cross-document or within-paper protocol grouping; scanned PDFs need OCR. Never represent the number of extracted fields as a scientific confidence percentage.


## v0.4 — Conservative context review
Negated candidate matches (e.g. 'CHARMM36m force field was not used' or 'did not use TIP3P') are withheld from downloadable protocols and shown separately for manual review. This is a heuristic, **not** a validated accuracy improvement. It can miss negations or flag valid statements. Evidence verification means page-level text support plus basic screening, not scientific fact checking.

Regression cases: `test_context_review.py`. Check GitHub Actions for an actual successful workflow run before claiming release validation.


## v0.5 — Reading workspace design
- Replaced the marketing-style dark dashboard with a restrained, light, editorial workspace.
- Moved document upload and guidance to the sidebar; the main view prioritizes extracted methods and their source evidence.
- Select a candidate to inspect its exact excerpt and (for uploaded PDFs) optionally preview its source page.
- Separated the reading desk, manual review queue, and export operations. Held/rejected matches remain excluded from downloads.
- Added `test_ui_smoke.py` using Streamlit AppTest to catch render-time exceptions on the synthetic demo.

**Verification:** Confirm an actual green GitHub Actions run and perform browser checks before describing this UI as production ready. Semantic extraction accuracy still requires an independently annotated dataset.

## v0.6 — Document-first workspace
- Simplified layout based on the PaperLens two-panel reading concept: paper / extracted methods.
- Clicking an extracted candidate synchronizes the highlighted excerpt and the original PDF page preview.
- Kept manual context holds and source-provenance rejects out of CSV/JSON exports.
- Source highlights escape untrusted PDF markup; in-memory PDF page rendering has regression tests.
- The default example loads when no PDF is supplied and is explicitly synthetic.
- MD timestep extraction now covers both "timestep of 4 fs" and "4 fs timestep".

**Release verification:** Python compilation and three local UI-helper regression tests passed during development, but the full Streamlit UI smoke test and public deployment have not yet been confirmed green. PDF page matches are evidence references, not scientific certification.
