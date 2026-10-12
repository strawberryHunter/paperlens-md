"use client";

import { useState, type ChangeEvent, type FormEvent } from "react";

type Method = {
  id: string; field: string; value: string; page: number; excerpt: string;
  grouping_status: string; verification: string;
};
type ResponseData = {
  schema_version: string;
  document: {filename: string; pages: number};
  method_candidates: Method[];
  review_items: {field:string; value:string; page:number; reason:string}[];
  scientific_flags: {code:string; title:string; level:string; explanation:string}[];
  disclaimer:string;
};
const API = process.env.NEXT_PUBLIC_PAPERLENS_API_URL || "http://127.0.0.1:8000";
export default function Workspace() {
  const [file, setFile] = useState<File|null>(null);
  const [data, setData] = useState<ResponseData|null>(null);
  const [selected, setSelected] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  function changeFile(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] || null); setData(null); setError(""); setSelected(0);
  }
  async function analyze(event:FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy) return;
    if (!file.name.toLowerCase().endsWith(".pdf") || file.size > 20*1024*1024) {
      setError("Only PDF files up to 20 MB are supported."); return;
    }
    setBusy(true); setError(""); setData(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await fetch(API + "/api/v1/analyze", {method:"POST",body:form});
      const payload:unknown = await result.json();
      if (!result.ok) {
        const message = payload && typeof payload === "object" && "detail" in payload
          ? String((payload as {detail:unknown}).detail) : "Analysis request rejected";
        throw new Error(message);
      }
      if (!payload || typeof payload !== "object" || !("schema_version" in payload) ||
          payload.schema_version !== "1.0") throw new Error("Unexpected API response schema");
      setData(payload as ResponseData);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not contact the preview backend");
    } finally {setBusy(false);}
  }
  const evidence = data?.method_candidates[selected];
  return <main className="shell">
    <header className="header"><div className="brand"><span className="brand-mark">⌗</span>
      <strong>paperlens</strong><span className="muted">/ workspace</span></div>
      <a href="https://github.com/strawberryHunter/paperlens-md" target="_blank" rel="noreferrer">GitHub ↗</a>
    </header>
    <section className="heading"><div><p className="eyebrow">DOCUMENT / RESEARCH WORKSPACE</p>
      <h1>Simulation methods</h1>
      <p className="subtext">Evidence first. Every parameter should be checked against its source.</p></div>
      <span className="status">Preview</span></section>
    <form className="upload" onSubmit={analyze}>
      <label htmlFor="pdf">Upload a research PDF</label>
      <input id="pdf" type="file" accept=".pdf,application/pdf" onChange={changeFile}/>
      <button disabled={!file||busy}>{busy?"Analyzing…":"Analyze PDF"}</button>
      <span className="hint">Up to 20 MB · selectable-text PDFs</span>
    </form>
    {error && <div className="error" role="alert">{error}</div>}
    {data ? <>
      <p className="fileinfo">{data.document.filename} · {data.document.pages} pages · {data.method_candidates.length} candidates · {data.review_items.length} review holds</p>
      <div className="panels">
        <section className="panel"><h2>Paper evidence</h2>
          {evidence ? <><p className="meta">PDF page {evidence.page} / {evidence.field}</p>
            <div className="excerpt">{evidence.excerpt}</div>
            <p className="hint">Matched phrase on a PDF page. Scientific use is not verified.</p></>
            : <p className="hint">No candidate evidence was found.</p>}
        </section>
        <section className="panel"><h2>Extracted methods</h2>
          {data.method_candidates.map((method,i)=><button
            type="button" key={method.id}
            className={"method"+(selected===i?" active":"")}
            onClick={()=>setSelected(i)}>
            <span><small>{method.field}</small><strong>{method.value}</strong></span>
            <em>p. {method.page}</em>
          </button>)}
          {!data.method_candidates.length && <p className="hint">No candidate values extracted.</p>}
        </section>
      </div>
      <section className="panel review"><h2>Review notes</h2>
        <p className="subtext">{data.disclaimer}</p>
        {data.scientific_flags.map((note,i)=><article key={note.code+"-"+i}>
          <strong>{note.title}</strong><p>{note.explanation}</p></article>)}
        {data.review_items.map((note,i)=><article key={"hold-"+i}>
          <strong>Context hold: {note.value}</strong><p>Page {note.page} · {note.reason}</p></article>)}
      </section>
    </>:<div className="empty">Choose a PDF to inspect its candidate simulation methods and source evidence.</div>}
    <footer>Research preview only. No scientific accuracy benchmark yet. Do not upload confidential manuscripts.</footer>
  </main>;
}
