import json
import fitz
import pandas as pd
import streamlit as st
from analyzer import analyze_pages, checklist, advisory, export_records

st.set_page_config(page_title="PaperLens MD", page_icon="🔬",layout="wide")
st.title("🔬 PaperLens MD")
st.caption("PDF → MD simulation parameters → page evidence → reproducibility checklist")
st.warning("Prototype: pattern matches are candidates, not scientifically verified findings. Absence of a match is not evidence that a parameter was omitted.")
demo=("Molecular dynamics simulations were performed using GROMACS 2024.1 and the CHARMM36m force field. "
      "The TIP3P water model was used. Following NVT and NPT equilibration at 300 K and 1 bar, "
      "five independent replicas were run for 30 ns each. A time step of 4 fs was used with "
      "hydrogen mass repartitioning (HMR), LINCS, PME, Nosé–Hoover and Parrinello–Rahman.")
upload=st.file_uploader("Upload a text-based research PDF (up to 50 MB)", type="pdf")
use_demo=st.checkbox("Use synthetic example",value=upload is None)
if upload and not use_demo:
    data=upload.getvalue()
    if len(data)>50*1024*1024:
        st.error("File exceeds 50MB limit."); st.stop()
    try:
        with fitz.open(stream=data,filetype="pdf") as doc:
            if len(doc)>100:
                st.error("Maximum 100 pages in this MVP."); st.stop()
            pages=[p.get_text(sort=True) for p in doc]
    except Exception as exc:
        st.error(f"Could not parse PDF: {exc}"); st.stop()
elif use_demo:
    pages=[demo]
else:
    st.info("Upload a PDF or enable the demo."); st.stop()
if not any(p.strip() for p in pages):
    st.error("No selectable PDF text detected; scanned documents are not yet supported."); st.stop()
st.subheader("Analysis scope")
first,last=st.slider("PDF page range to examine",1,len(pages),(1,len(pages))) if len(pages)>1 else (1,1)
st.caption("Limit the scan to Methods pages to reduce false positives from Introduction or References. Page numbers are PDF indices, not printed journal page numbers.")
records=analyze_pages(pages[first-1:last])
for record in records:
    record.page += first-1

st.metric("Candidate evidence matches",len(records))
st.caption(f"Scanned PDF pages {first}–{last} of {len(pages)}. A match is not a verified method parameter.")
tab1,tab2,tab3=st.tabs(["📋 Extracted methods","⚠️ Review checklist","📖 PDF evidence"])
with tab1:
    st.info("Different systems and experiments may appear in one paper; do not combine all matches into a single simulation.")
    table=pd.DataFrame(export_records(records),columns=["field","value","page","excerpt"])
    st.dataframe(table,use_container_width=True,hide_index=True)
    st.download_button("Download CSV",table.to_csv(index=False).encode("utf-8-sig"),"paperlens_methods.csv","text/csv")
    st.download_button("Download JSON",json.dumps(export_records(records),ensure_ascii=False,indent=2),"paperlens_evidence.json","application/json")
with tab2:
    st.dataframe(pd.DataFrame(checklist(records)),use_container_width=True,hide_index=True)
    for note in advisory(records):
        st.write("• "+note)
with tab3:
    choices=["All"]+sorted({r.field for r in records})
    selected=st.selectbox("Parameter",choices)
    for index,item in enumerate(records):
        if selected!="All" and item.field!=selected: continue
        with st.expander(f"{item.field}: {item.value} — PDF page {item.page}",expanded=index<2):
            st.write(item.excerpt)
st.caption("No file persistence is implemented, but hosting provider privacy and logs require independent review. Upload only documents you may share.")
