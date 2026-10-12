"""PaperLens MD — evidence-first methods reading workspace."""
import json

import fitz
import pandas as pd
import streamlit as st

from analyzer import analyze_pages, checklist, export_records
from validation import report


st.set_page_config(
    page_title="PaperLens — Methods workspace",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* Light editorial UI. Content and source evidence, not decorative dashboards. */
[data-testid="stAppViewContainer"] {background: #fbfcfd;}
[data-testid="stHeader"] {background: rgba(251,252,253,.94);}
.block-container {max-width: 1420px; padding-top: 1.65rem; padding-bottom: 3.25rem;}
h1, h2, h3 {font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
             letter-spacing: -0.035em !important; color: #172331 !important;}
h1 {font-size: 1.85rem !important; font-weight: 680 !important;}
h2 {font-size: 1.13rem !important;}
[data-testid="stSidebar"] {background:#f3f5f7; border-right:1px solid #e5e9ed;}
[data-testid="stSidebar"] hr {border-color:#e0e6ed;}
[data-testid="stMetric"] {background:transparent;border:0;}
[data-testid="stMetricLabel"] {font-size:.78rem;}
[data-testid="stMetricValue"] {font-size:1.45rem;}
[data-testid="stFileUploaderDropzone"] {background:#fff;border:1px dashed #b9c6d3;border-radius:8px;}
[data-testid="stDataFrame"] {border:1px solid #e5e9ed;border-radius:7px;}
[data-testid="stExpander"] {border-radius:7px;}
[data-testid="stAlert"] {border-radius:8px;}
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {border-radius:7px;}
[data-baseweb="tab-list"] {gap:1rem;}
[data-baseweb="tab"] {font-size:.93rem;}
.brand-row {font-size:.80rem;letter-spacing:.01em;color:#637184;margin-bottom:.7rem;}
.brand-row strong {color:#25364a;font-weight:750;font-size:.91rem;}
.workspace-note {color:#667689;font-size:.84rem;line-height:1.6;margin:.4rem 0 1.25rem;}
.stage-label {font-size:.75rem;font-weight:650;color:#647489;letter-spacing:.015em;margin-top:1rem;}
.review-dot {display:inline-block;background:#ad7737;width:7px;height:7px;border-radius:50%;margin-right:6px;}
.footer-rule {border-top:1px solid #e5e9ed;margin-top:1.6rem;padding-top:1rem;
              font-size:.77rem;color:#758194;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand-row"><strong>paperlens</strong> &nbsp; / &nbsp; METHODS WORKSPACE</div>',
    unsafe_allow_html=True,
)
st.title("Read the methods. Check the evidence.")
st.markdown(
    '<div class="workspace-note">Extract molecular-dynamics settings with a direct path back to their source. '
    'Candidate matches are not confirmed experimental facts.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Workspace")
    st.caption("PaperLens MD · v0.5")
    st.markdown("**Document input**")
    upload = st.file_uploader("Select a text-based PDF", type="pdf", help="Max 50 MB · 100 PDF pages")
    use_demo = st.toggle("Use synthetic example", value=upload is None)
    st.divider()
    st.markdown("**Reading guide**")
    st.caption("1. Choose a PDF and page range.\n\n2. Select a candidate to inspect its evidence.\n\n3. Review context warnings before exporting.")
    st.divider()
    st.link_button("GitHub source", "https://github.com/strawberryHunter/paperlens-md")
    st.caption("Rule-based research prototype, not a scientific validator.")

demo = (
    "Molecular dynamics simulations were performed using GROMACS 2024.1 and "
    "the CHARMM36m force field. The TIP3P water model was used. "
    "Following NVT and NPT equilibration at 300 K and 1 bar, "
    "five independent replicas were run for 30 ns each. "
    "A time step of 4 fs was used with hydrogen mass repartitioning "
    "(HMR), LINCS, PME, Nose-Hoover and Parrinello-Rahman."
)

pdf_bytes = None
if upload is not None and not use_demo:
    pdf_bytes = upload.getvalue()
    if len(pdf_bytes) > 50 * 1024 * 1024:
        st.error("PDF exceeds the 50 MB upload limit.")
        st.stop()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            if len(doc) > 100:
                st.error("The current reader supports up to 100 PDF pages.")
                st.stop()
            pages = [p.get_text(sort=True) for p in doc]
    except Exception as exc:
        st.error(f"PDF could not be read: {exc}")
        st.stop()
elif use_demo:
    pages = [demo]
else:
    st.info("Choose a PDF from the left sidebar, or turn on the synthetic example.")
    st.stop()

if not any(page.strip() for page in pages):
    st.error("No machine-readable text was detected. OCR is not included in this version.")
    st.stop()

st.markdown('<div class="stage-label">DOCUMENT SCOPE</div>', unsafe_allow_html=True)
range_col, metadata_col = st.columns([2.5, 1], vertical_alignment="bottom")
with range_col:
    if len(pages) > 1:
        first, last = st.slider("PDF pages to scan", 1, len(pages), (1, len(pages)))
    else:
        first, last = (1, 1)
        st.caption("Scanning the one-page synthetic example.")
with metadata_col:
    st.caption(f"{len(pages)} PDF page(s) · pages {first}–{last} selected")
st.caption("Restrict the scan to Methods pages where possible. PDF indices may differ from printed journal page numbers.")

records = analyze_pages(pages[first - 1:last])
for item in records:
    item.page += first - 1
result = report(records, pages)
approved = result["valid"]
context_review = result["context_review"]
rejected = result["rejected"]
flags = result["findings"]

st.divider()
st.markdown("#### Review summary")
a, b, c = st.columns(3)
a.metric("Page-matched candidates", len(approved))
b.metric("Scientific review flags", result["summary"]["review_flags"])
c.metric("Context / provenance holds", len(context_review) + len(rejected))
st.caption(
    "Page-matched means the reported value occurs on the cited PDF page and passed "
    "a basic heuristic negation check. It does not prove that the method was used."
)
if rejected:
    st.error(f"{len(rejected)} source mismatches were removed from export.")
if context_review:
    st.warning(f"{len(context_review)} possibly negated or ambiguous matches are withheld for manual review.")

st.markdown("#### Methods & source")
methods_tab, review_tab, export_tab = st.tabs(["Reading desk", "Review queue", "Export"])

with methods_tab:
    table_col, evidence_col = st.columns([1.1, 1], gap="large")
    with table_col:
        st.markdown("**Extracted parameters**")
        if not approved:
            st.info("No candidates passed the current screening rules.")
        else:
            table = pd.DataFrame(export_records(approved))
            display = table[["field", "value", "page"]].rename(
                columns={"field": "Parameter", "value": "Candidate", "page": "PDF page"}
            )
            st.dataframe(display, hide_index=True, use_container_width=True, height=340)
        st.caption("Different stages or systems must not be combined without checking their contexts.")
    with evidence_col:
        st.markdown("**Source inspection**")
        if approved:
            options = list(range(len(approved)))
            selected_index = st.selectbox(
                "Select a candidate",
                options,
                format_func=lambda i: f"{approved[i].field} · {approved[i].value}  (p. {approved[i].page})",
            )
            selected = approved[selected_index]
            st.caption(f"PDF page {selected.page} · {selected.field}")
            st.text_area(
                "Nearby source text",
                selected.excerpt,
                height=150,
                disabled=True,
            )
            if pdf_bytes is not None:
                show_page = st.checkbox("Show source PDF page", value=False)
                if show_page:
                    try:
                        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                            pix = doc[selected.page - 1].get_pixmap(
                                matrix=fitz.Matrix(1.25, 1.25), alpha=False
                            )
                            st.image(pix.tobytes("png"), caption=f"PDF page {selected.page}", use_container_width=True)
                    except Exception as exc:
                        st.error(f"Cannot preview this page: {exc}")
            else:
                st.caption("Synthetic example — no PDF page image.")
        else:
            st.caption("Evidence will appear after a candidate is selected.")

with review_tab:
    if not flags and not context_review and not rejected:
        st.info("No rule-based review flags. This is not a scientific certification.")
    for finding in flags:
        with st.expander(f"{finding.title} · {finding.level.upper()}"):
            st.write(finding.explanation)
            st.caption("Referenced PDF pages: " + ", ".join(map(str, finding.pages)))
    if context_review:
        st.markdown("**Context holds — excluded from download**")
        for item in context_review:
            with st.expander(f"{item.field}: {item.value} · p. {item.page}"):
                st.write(item.excerpt)
    if rejected:
        st.markdown("**Provenance rejected**")
        st.caption(f"{len(rejected)} results have no verified matching value at their claimed PDF page.")
    st.markdown("**Reporting checklist**")
    st.dataframe(pd.DataFrame(checklist(approved)), hide_index=True, use_container_width=True)
    st.caption("Not detected means the parser did not find it. Inspect the source and supporting information.")

with export_tab:
    st.markdown("**Download reviewed evidence candidates**")
    st.caption(
        "Excluded contextual and provenance holds do not appear in these files. "
        "A reviewer must still assess relevance, experimental stage and scientific accuracy."
    )
    data = export_records(approved)
    table = pd.DataFrame(data, columns=["field", "value", "page", "excerpt"])
    st.download_button(
        "Download CSV",
        table.to_csv(index=False).encode("utf-8-sig"),
        "paperlens_methods.csv", "text/csv"
    )
    st.download_button(
        "Download JSON",
        json.dumps(data, ensure_ascii=False, indent=2),
        "paperlens_methods.json", "application/json"
    )

st.markdown(
    '<div class="footer-rule">PaperLens MD is a prototype. There is no independently measured extraction '
    'accuracy yet. The app code does not implement document persistence; hosting-provider handling '
    'must be evaluated separately. Do not upload confidential manuscripts.</div>',
    unsafe_allow_html=True,
)
