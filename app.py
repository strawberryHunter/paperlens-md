import json
import fitz
import pandas as pd
import streamlit as st
from analyzer import analyze_pages, checklist, export_records
from validation import report

st.set_page_config(page_title="PaperLens | Methods Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] {font-family:'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background:#0b1120;color:#e7effb;}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1220px;padding-top:1.8rem;padding-bottom:4rem;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;color:#f1f6ff!important;}
h1 {font-size:2.4rem!important;}
p, label, .stMarkdown {color:#c1cee0;}
.hero {background:linear-gradient(120deg,#132b42 0%,#162041 70%,#251c43 100%);border:1px solid #293b57;border-radius:20px;padding:27px 30px;margin-bottom:20px;}
.eyebrow {color:#80dfe2;letter-spacing:.17em;font-size:.72rem;font-weight:700;margin-bottom:10px;}
.hero-title {font-size:2.1rem;line-height:1.15;color:#f4f8ff;font-weight:700;letter-spacing:-.045em;font-family:'Space Grotesk',sans-serif;}
.hero-sub {color:#a4bad3;margin-top:10px;line-height:1.5;}
.kpi {border:1px solid #2c3b54;background:#141f33;border-radius:15px;padding:18px 20px;min-height:102px;}
.kpi-name {color:#90a6c3;font-size:.77rem;}
.kpi-number {font-size:1.9rem;font-weight:700;letter-spacing:-.04em;color:#f1f8ff;}
.kpi-number.warn {color:#f6c97f;}
[data-testid="stFileUploader"] {border:1px solid #34445f;border-radius:14px;padding:12px;background:#131d31;}
[data-testid="stFileUploaderDropzone"] {background:#17253a;border-color:#405273;}
[data-baseweb="tab-list"] {gap:10px;}
button[data-baseweb="tab"] {background:#16253a;border-radius:9px;color:#d2def0;padding:9px 15px;}
button[data-baseweb="tab"][aria-selected="true"] {background:#294965;color:#fff;}
[data-testid="stDataFrame"], [data-testid="stExpander"] {border:1px solid #2d4059;border-radius:12px;}
[data-testid="stAlert"] {border-radius:12px;}
.small-note {font-size:.79rem;color:#91a6c3;margin:12px 0;}
</style>
""",unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">◈ PAPERLENS / SCIENTIFIC INTELLIGENCE</div><div class="hero-title">Methods Intelligence</div><div class="hero-sub">Turn research PDFs into traceable simulation evidence, scientific review flags and structured reports.</div></div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("About PaperLens")
    st.write("Evidence-first PDF methods scanner. Pattern matches are candidates, never validated scientific conclusions.")
    st.link_button("View source on GitHub","https://github.com/strawberryHunter/paperlens-md")
    st.caption("v0.3 · Rule-based prototype")
demo=("Molecular dynamics simulations were performed using GROMACS 2024.1 and the CHARMM36m force field. "
      "The TIP3P water model was used. Following NVT and NPT equilibration at 300 K and 1 bar, "
      "five independent replicas were run for 30 ns each. A time step of 4 fs was used with "
      "hydrogen mass repartitioning (HMR), LINCS, PME, Nose-Hoover and Parrinello-Rahman.")

left,right=st.columns([2,1],gap="large")
with left:
    st.subheader("01 / Document")
    upload=st.file_uploader("Choose a text-based research PDF (max 50 MB)",type="pdf")
with right:
    st.subheader("Analysis mode")
    use_demo=st.toggle("Synthetic sample",value=upload is None)
    st.caption("Try the workflow without uploading a manuscript.")
if upload is not None and not use_demo:
    data=upload.getvalue()
    if len(data)>50*1024*1024:
        st.error("The PDF exceeds 50 MB.");st.stop()
    try:
        with fitz.open(stream=data,filetype="pdf") as doc:
            if len(doc)>100:
                st.error("Limit of 100 PDF pages per run.");st.stop()
            pages=[p.get_text(sort=True) for p in doc]
    except Exception as exc:
        st.error(f"PDF extraction failed: {exc}");st.stop()
elif use_demo:
    pages=[demo]
else:
    st.info("Upload a PDF or enable the synthetic demo.");st.stop()
if not any(p.strip() for p in pages):
    st.error("No machine-readable text found. Scanned PDFs need OCR, which is not supported yet.");st.stop()

st.subheader("02 / Analysis scope")
first,last=st.slider("Scan PDF pages",1,len(pages),(1,len(pages))) if len(pages)>1 else (1,1)
st.caption("Select Methods pages to reduce citations and background false positives. Pages are PDF indices, not printed article pagination.")
selected_pages=pages[first-1:last]
records=analyze_pages(selected_pages)
for item in records: item.page+=first-1
result=report(records,pages)
approved=result["valid"]; flags=result["findings"]; context_review=result["context_review"]
m1,m2,m3,m4=st.columns(4,gap="small")
for col,label,value,warn in [
    (m1,"CANDIDATE MATCHES",len(records),False),
    (m2,"EVIDENCE VERIFIED",len(approved),False),
    (m3,"REVIEW FLAGS",result["summary"]["review_flags"],True),
    (m4,"REJECTED EVIDENCE",len(result["rejected"]),bool(result["rejected"]))]:
    with col:
        st.markdown(f'<div class="kpi"><div class="kpi-name">{label}</div><div class="kpi-number {"warn" if warn else ""}">{value}</div></div>',unsafe_allow_html=True)

st.markdown(f'<div class="small-note">Evidence verified = matching PDF-page value passing a basic negation screen, not scientific confirmation. {len(context_review)} ambiguous candidate(s) quarantined for review.</div>',unsafe_allow_html=True)
if not result["gate_passed"]:
    st.error("Evidence provenance gate failed. Rejected values are excluded from all downloads.")
st.subheader("03 / Results workspace")
tab1,tab2,tab3=st.tabs(["◈ Protocol Explorer","⚑ Scientific Review","▣ Evidence Audit"])
with tab1:
    st.caption("Do not merge values from different systems or stages. Verify extracted results against the original paper and supporting information.")
    table=pd.DataFrame(export_records(approved),columns=["field","value","page","excerpt"])
    if table.empty: st.info("No candidate methods found. Try narrowing or changing the PDF page range.")
    else:
        filter_field=st.selectbox("Method category",["All"]+sorted(table.field.unique().tolist()))
        shown=table if filter_field=="All" else table[table.field==filter_field]
        st.dataframe(shown,use_container_width=True,hide_index=True)
    st.download_button("↓ Export evidence CSV",table.to_csv(index=False).encode("utf-8-sig"),"paperlens_methods.csv","text/csv")
    st.download_button("↓ Export evidence JSON",json.dumps(export_records(approved),ensure_ascii=False,indent=2),"paperlens_methods.json","application/json")
with tab2:
    if not flags: st.success("No rule-based review flags from detected candidates. This does not certify the simulation.")
    for f in flags:
        with st.container(border=True):
            st.markdown(f"**{f.title}** · `{f.level.upper()}`")
            st.write(f.explanation)
            st.caption("Evidence pages: "+", ".join(map(str,f.pages)))
    if context_review:
        st.warning(f"{len(context_review)} potentially negated or ambiguous candidate(s) withheld from exports. Review the original PDF before accepting them.")
        for item in context_review:
            with st.expander(f"Context review: {item.field} / {item.value} · p.{item.page}"):
                st.write(item.excerpt)
    st.markdown("**Methods reporting checklist**")
    st.dataframe(pd.DataFrame(checklist(approved)),use_container_width=True,hide_index=True)
    st.warning("Not detected means parser did not find it; it does NOT mean the authors failed to report it.")
with tab3:
    if not approved: st.info("No verified PDF text matches yet.")
    for i,item in enumerate(approved):
        with st.expander(f"{item.field}  /  {item.value}  ·  PDF p.{item.page}",expanded=i==0):
            st.markdown(f"**Source page {item.page}**")
            st.write(item.excerpt)
    if result["rejected"]:
        st.error(f"{len(result['rejected'])} candidate(s) rejected because page-value provenance could not be established.")
st.divider()
st.caption("Prototype release · No independent benchmark accuracy available yet. No manuscript storage implemented in the app code; hosting-provider handling is separate. Upload only material permitted by its confidentiality policy.")
