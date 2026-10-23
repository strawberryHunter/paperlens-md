# PaperLens MD — Quality Gates (v1.0)

**Scope:** scientific MD-methods PDF extraction. Quality gates override cosmetic features. A green build is NOT evidence of research accuracy.

## Gate 1 — Stability: every PR
- Clean installation on supported Python versions, no incompatible dependencies (pip check).
- Compile every Python module. All unit tests, PDF integration tests, and Streamlit UI smoke tests must pass on CI.
- Test valid, empty/scanned, damaged, no-match, oversized and multi-page PDFs, plus export paths.
- Fail gracefully; never silently invent values. No known P0/P1 issue in upload -> evidence -> export.
- Provide actual CI run link and commit SHA. Missing results are UNKNOWN, not PASS.

## Gate 2 — Correctness: every parser edit
- Every candidate needs its exact PDF page and matching source text.
- Do not combine WT vs mutant, equilibration vs production, or different independent experiments.
- Negated, quoted, or contextually ambiguous mentions must be held for review rather than accepted automatically.
- Add a positive, negative and boundary test for each extraction rule.
- Preserve original reported values/units. Convert only with explicitly checked dimensions.
- Until protocol grouping is validated, results are separate CANDIDATES, never an inferred single protocol.

## Gate 3 — Scientific reliability: before public accuracy claims
- Clearly differentiate NOT DETECTED vs NOT REPORTED and REVIEW vs WRONG.
- No numerical confidence score without independently measured calibration.
- Build a licensed, human-annotated gold set of at least 30 research papers for initial evaluation, covering SI, references, negation, multiple simulations, unusual units and scanned PDFs.
- Maintain held-out papers never used to tune rules. Report per-field precision, recall, F1, denominators and error examples. Define TP/FP/FN.
- PROPOSED FUTURE TARGETS, NOT ACHIEVED: essential-field precision >= 0.95, recall >= 0.85 on held-out evaluation, and no critical evidence misattribution. Disable or label experimental any failing field.
- A passing unit test does not prove accuracy on actual research literature.

## Gate 4 — Product quality: before public release
- Upload -> inspect -> select candidate -> original page evidence -> review -> export works in a real browser on the deployed version.
- Check responsive/narrow screens, accessibility, empty/error states, long PDFs and repeated user actions.
- Escape PDF text before HTML rendering, constrain input and memory use, do not persist source documents in app code.
- Disclose hosting-provider data processing and exclude confidential manuscripts from tests.
- Maintain calm, document-first UI. Never manufacture scientific scores, counters or results.
- Verify the published URL and revision; provide a rollback plan.

## Mandatory change protocol
1. Document problem, files to change, tests, risks and explicit non-goals.
2. Create small feature/quality branch; do not push unverified changes to main.
3. Add reproducible regression tests. Run actual code where environment permits.
4. Open a draft PR with the precise test outcome and known limitations.
5. Confirm GitHub Actions checks and manual UI checks. Unavailable evidence = hold.
6. Merge only after successful gates and approval. If required GitHub branch protection is not configured, never imply that it is.
7. Include changelog and safe rollback instructions for any user-facing changes.

## Status when introduced
Automated tests exist but no independent per-field benchmark, calibrated confidence or deployed browser acceptance evidence has been established. Results remain heuristic review candidates.
