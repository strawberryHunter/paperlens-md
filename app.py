"""PaperLens MD — calm reading workspace for evidence-grounded methods review."""
import json

import fitz
import pandas as pd
import streamlit as st

from analyzer import analyze_pages, checklist, export_records
from validation import report
from display_helpers import marked_excerpt, pdf_page_png

st.set_page_config(
    page_title="PaperLens — Simulation methods",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
/* Document-first product UI. No decorative hero, gradients, or fabricated scores. */
[data-testid="stAppViewContainer"] {background:#f7f8fa; color:#253247;}
[data-testid="stHeader"] {background:#f7f8fa;}
.block-container {max-width:1360px; padding-top:1.5rem; padding-bottom:3.2rem;}
h1,h2,h3 {font-family:system-ui,-apple-system,"Segoe UI",sans-serif!important;
             letter-spacing:-.025em!important; color:#202b3c!important;}
h1 {font-weight:650!important; font-size:1.65rem!important;}
h3 {font-size:1.03rem!important;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#dfe4ea!important; border-radius:10px!important; background:white;}
[data-testid="stFileUploaderDropzone"] {border:1px dashed #b8c5d2; background:#fff; border-radius:8px;}
[data-testid="stExpander"] {border-color:#e2e7ec; border-radius:8px;}
[data-testid="stDataFrame"] {border:1px solid #e4e8ed; border-radius:8px;}
[data-testid="stAlert"] {border-radius:8px;}
[data-testid="stMetric"] {border:0;}
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {border-radius:8px;}
button[kind="secondary"] {border-color:#dce3ea;}
button[kind="primary"] {background:#263b54; border-color:#263b54;}
[data-baseweb="tab"] {font-size:.9rem;}
.paperlens-brand {display:flex; align-items:center; gap:12px; padding:2px 0 14px;
                   border-bottom:1px solid #e1e6eb; margin-bottom:26px;}
.paperlens-symbol {background:#1d2b3e; width:33px; height:33px; border-radius:7px;
                   color:#fff; font-size:21px; display:inline-flex; align-items:center; justify-content:center;}
.paperlens-name {font-size:1.13rem; font-weight:750; color:#172234; letter-spacing:-.035em;}
.paperlens-location {color:#97a2b0; font-size:.9rem;}
.paperlens-kicker {font-size:.75rem; letter-spacing:.055em; color:#8492a5; margin-bottom:5px;}
.paperlens-sub {font-size:.85rem; color:#7a8799; margin:0 0 17px; line-height:1.5;}
.source-sheet {background:#f2f4f7; padding:14px 16px; border-radius:7px;
               color:#42536b; font-size:.92rem; line-height:1.7; overflow-wrap:anywhere;}
.source-sheet mark {background:#dceaf5; color:#27577e; border-radius:3px; padding:2px 3px;}
.footnote {color:#8390a1; font-size:.76rem; margin-top:8px;}
.micro-label {font-size:.78rem; font-weight:650; color:#718196;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="paperlens-brand"><span class="paperlens-symbol">⌗</span>'
    '<span class="paperlens-name">paperlens</span>'
    '<span class="paperlens-location">/ workspace</span></div>',
    unsafe_allow_html=True,
)

with st.expander("Document  ·  upload or try the example", expanded=True):
    input_left, input_right = st.columns([2, 1], gap="large")
    with input_left:
        uploaded = st.file_uploader("Research PDF", type="pdf", help="Text-based PDFs up to 50 MB; 100 pages maximum.")
    with input_right:
        st.caption("No PDF selected? The synthetic example appears automatically.")

DEMO = (
    "2.3 Molecular dynamics simulations\n"
    "Simulations were performed using GROMACS 2024.1 with CHARMM36m force field. "
    "The TIP3P water model was used. Production simulations were performed at 300 K "
    "and 1 bar using a 4 fs timestep with hydrogen mass repartitioning (HMR). "
    "Five independent replicas were run for 30 ns each. "
    "Trajectory analysis was performed for each independent simulation."
)
pdf_bytes = None
if uploaded is not None:
    pdf_bytes = uploaded.getvalue()
    if len(pdf_bytes) > 50 * 1024 * 1024:
        st.error("This PDF exceeds 50 MB.")
        st.stop()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            if len(doc) > 100:
                st.error("Current limit: 100 PDF pages.")
                st.stop()
            pages = [page.get_text(sort=True) for page in doc]
    except (ValueError, RuntimeError, fitz.FileDataError) as exc:
        st.error(f"Unable to parse PDF: {exc}")
        st.stop()
else:
    pages = [DEMO]

if not any(page.strip() for page in pages):
    st.error("No selectable text was found. Scanned PDFs are not supported yet.")
    st.stop()

if len(pages) > 1:
    with st.expander("Choose Methods page range", expanded=False):
        first, last = st.slider("PDF pages", 1, len(pages), (1, len(pages)))
        st.caption("To avoid unrelated citations, restrict the range to Methods where practical.")
else:
    first, last = (1, 1)

candidates = analyze_pages(pages[first - 1:last])
for candidate in candidates:
    candidate.page += first - 1
results = report(candidates, pages)
methods = results["valid"]
flags = results["findings"]
held = results["context_review"]
rejected = results["rejected"]

st.markdown('<div class="paperlens-kicker">LIBRARY / DOCUMENT 01</div>', unsafe_allow_html=True)
title_col, status_col = st.columns([4, 1], vertical_alignment="center")
with title_col:
    st.title("Simulation methods")
with status_col:
    st.caption(f"{len(methods)} candidates · {len(flags) + len(held) + len(rejected)} to review")
st.markdown(
    '<div class="paperlens-sub">Inspect each extracted parameter alongside its exact source. '
    'Text matches are not confirmation that the method was used.</div>',
    unsafe_allow_html=True,
)

if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = 0
if methods:
    st.session_state.selected_candidate = min(st.session_state.selected_candidate, len(methods) - 1)

paper_col, method_col = st.columns([1, 1], gap="small")
with paper_col:
    with st.container(border=True):
        st.subheader("Paper")
        if methods:
            selection = methods[st.session_state.selected_candidate]
            st.caption(f"PDF page {selection.page} · evidence for {selection.field}")
            if pdf_bytes is not None:
                try:
                    st.image(pdf_page_png(pdf_bytes, selection.page, selection.value), use_container_width=True)
                except (ValueError, RuntimeError, fitz.FileDataError) as exc:
                    st.info(f"PDF preview unavailable: {exc}")
            st.markdown(marked_excerpt(selection.excerpt, selection.value), unsafe_allow_html=True)
            st.markdown('<div class="footnote">Source match highlighted · review the full Methods and SI for context.</div>', unsafe_allow_html=True)
        else:
            st.info("No candidate matches. Try another page range.")

with method_col:
    with st.container(border=True):
        st.subheader("Extracted methods")
        if methods:
            for i, item in enumerate(methods):
                col_a, col_b = st.columns([5, 1], vertical_alignment="center")
                with col_a:
                    if st.button(
                        f"{item.field}  ·  {item.value}",
                        key=f"candidate_{i}",
                        type="primary" if i == st.session_state.selected_candidate else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state.selected_candidate = i
                        st.rerun()
                with col_b:
                    st.caption(f"p. {item.page}")
        else:
            st.caption("No methods detected.")
        st.divider()
        st.caption("Select any row to inspect the original PDF page and the supporting excerpt.")

st.markdown('<div class="footnote">A candidate is a matched term on a PDF page, not an independently verified simulation setting.</div>', unsafe_allow_html=True)

review_tab, export_tab = st.tabs(["Review notes", "Export & audit"])
with review_tab:
    if not flags and not held and not rejected:
        st.info("No rule-based flags. This does not certify scientific reliability.")
    for flag in flags:
        with st.expander(f"{flag.title} · {flag.level}"):
            st.write(flag.explanation)
            st.caption("Source PDF pages: " + ", ".join(map(str, flag.pages)))
    if held:
        st.warning(f"{len(held)} potentially negated or ambiguous candidate(s) withheld from export.")
        for record in held:
            with st.expander(f"Context review: {record.field} · {record.value}"):
                st.write(record.excerpt)
                st.caption(f"PDF page {record.page}")
    if rejected:
        st.error(f"{len(rejected)} candidate(s) rejected: original value/page mismatch.")
    with st.expander("Reporting checklist"):
        st.dataframe(pd.DataFrame(checklist(methods)), hide_index=True, use_container_width=True)
        st.caption("Not detected ≠ unreported. Supporting information may contain additional Methods details.")
with export_tab:
    table = pd.DataFrame(export_records(methods), columns=["field", "value", "page", "excerpt"])
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", table.to_csv(index=False).encode("utf-8-sig"), "paperlens_methods.csv", "text/csv")
    st.download_button("Download JSON", json.dumps(export_records(methods), ensure_ascii=False, indent=2), "paperlens_methods.json", "application/json")
    st.caption("Held and rejected matches are excluded. Verify every exported candidate manually.")

st.divider()
st.caption("PaperLens MD · prototype · no independent accuracy benchmark yet. Only upload documents you are authorized to process.")
