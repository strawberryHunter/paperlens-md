"""PaperLens MD — calm reading workspace for evidence-grounded methods review."""
import json
import hashlib

import fitz
import pandas as pd
import streamlit as st

from analyzer import analyze_pages, checklist, export_records
from validation import report
from protocol_groups import annotate
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
st.title("Simulation methods")
st.markdown(
    '<div class="paperlens-sub">Source evidence on the left. Explicitly labeled systems and stages on the right. '
    'Unlabeled candidates are never merged into a reconstructed protocol.</div>',
    unsafe_allow_html=True,
)

contexts = annotate(methods, pages)
pairs = list(zip(methods, contexts))
system_labels = ["All systems"] + sorted({context.system for context in contexts})
selection_left, selection_right = st.columns([1, 2], vertical_alignment="bottom")
with selection_left:
    system_filter = st.selectbox("System filter", system_labels, help="Labels are only assigned when explicitly stated in the same sentence.")
with selection_right:
    st.caption(f"{len(methods)} candidate(s) · {len(held)} context hold(s) · {len(rejected)} source mismatch(es)")
    st.caption("A method may occur in more than one experiment; rows remain independent source candidates.")

visible = [i for i, ctx in enumerate(contexts) if system_filter == "All systems" or ctx.system == system_filter]
visible.sort(key=lambda i: (
    contexts[i].system in ("Unassigned", "Ambiguous"),
    contexts[i].system, contexts[i].stage, methods[i].page, methods[i].source_start or 0
))
paper_col, method_col = st.columns([1, 1], gap="small")
selected = None
selected_context = None
with method_col:
    with st.container(border=True):
        st.subheader("Extracted methods")
        st.caption("Click a row to inspect the supporting sentence and PDF page.")
        if visible:
            display = pd.DataFrame([
                {
                    "Parameter": methods[i].field,
                    "Value": methods[i].value,
                    "System": contexts[i].system,
                    "Stage": contexts[i].stage,
                    "Page": methods[i].page,
                    "Review": contexts[i].status,
                }
                for i in visible
            ])
            document_key = hashlib.sha256(
                pdf_bytes if pdf_bytes is not None else DEMO.encode("utf-8")
            ).hexdigest()[:12]
            key = f"evidence_{document_key}_{first}_{last}_{system_filter}"
            event = st.dataframe(
                display,
                on_select="rerun",
                selection_mode="single-row",
                key=key,
                hide_index=True,
                use_container_width=True,
                height=min(520, max(170, len(display) * 35 + 52)),
            )
            selection_rows = event.selection.rows
            row_number = selection_rows[0] if selection_rows else 0
            selected_index = visible[row_number]
            selected, selected_context = pairs[selected_index]
        else:
            st.info("No source candidates for this system filter.")
        st.caption("Unassigned = not stated nearby. Ambiguous = multiple possible labels. Neither is an experimental grouping.")

with paper_col:
    with st.container(border=True):
        st.subheader("Paper")
        if selected is None:
            st.info("Choose an extracted method to view its evidence.")
        else:
            st.caption(f"PDF page {selected.page}  /  {selected.field}  /  {selected.value}")
            st.markdown(
                marked_excerpt(selected_context.source_sentence, selected.value),
                unsafe_allow_html=True,
            )
            st.caption(f"System: {selected_context.system}  ·  Stage: {selected_context.stage}  ·  {selected_context.status}")
            if pdf_bytes is not None and st.checkbox(
                "Preview original PDF page", value=False,
                key=f"page_preview_{document_key}_{selected.page}_{selected_index}"
            ):
                try:
                    st.image(
                        pdf_page_png(pdf_bytes, selected.page, selected.value),
                        use_container_width=True,
                        caption=f"PDF page {selected.page}"
                    )
                except (ValueError, RuntimeError, fitz.FileDataError) as exc:
                    st.info(f"PDF page preview unavailable: {exc}")
            elif pdf_bytes is None:
                st.caption("Synthetic example: no original PDF page image.")
            st.markdown(
                '<div class="footnote">A page-matched phrase is not proof of an experimental setting. '
                'Verify full context and Supporting Information.</div>',
                unsafe_allow_html=True,
            )

review_tab, export_tab = st.tabs(["Review notes", "Export & audit"])
with review_tab:
    ambiguous = [ctx for ctx in contexts if ctx.status == "Review"]
    if ambiguous:
        st.warning(f"{len(ambiguous)} candidate(s) mention conflicting systems or stages. They are NOT auto-assigned.")
    if not flags and not held and not rejected and not ambiguous:
        st.info("No rule-based flags. This does not certify scientific reliability.")
    for flag in flags:
        with st.expander(f"{flag.title} · {flag.level}"):
            st.write(flag.explanation)
            st.caption("Source PDF pages: " + ", ".join(map(str, flag.pages)))
    if held:
        st.warning(f"{len(held)} possibly negated or uncertain candidate(s) withheld from export.")
        for record in held:
            with st.expander(f"Context review: {record.field} · {record.value}"):
                st.write(record.excerpt)
                st.caption(f"PDF page {record.page}")
    if rejected:
        st.error(f"{len(rejected)} candidate(s) rejected: original value/page mismatch.")
    with st.expander("Reporting checklist"):
        st.dataframe(pd.DataFrame(checklist(methods)), hide_index=True, use_container_width=True)
        st.caption("Not detected is NOT equivalent to not reported.")

with export_tab:
    data = [
        {
            **export_records([record])[0],
            "system_hint": context.system,
            "stage_hint": context.stage,
            "grouping_status": context.status,
            "source_sentence": context.source_sentence,
        }
        for record, context in pairs
    ]
    st.warning(
        "Exports are evidence CANDIDATES, not verified simulation protocols. "
        "System/stage fields are sentence-level hints and must not be used to automatically pool results."
    )
    table = pd.DataFrame(data)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", table.to_csv(index=False).encode("utf-8-sig"), "paperlens_methods.csv", "text/csv")
    st.download_button("Download JSON", json.dumps(data, ensure_ascii=False, indent=2), "paperlens_methods.json", "application/json")
    st.caption("Negated/rejected values are excluded; ambiguous labels require manual review.")

st.divider()
st.caption("PaperLens MD · prototype · no independent accuracy benchmark yet. Only upload documents you are authorized to process.")
