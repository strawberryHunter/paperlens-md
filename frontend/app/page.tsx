"use client";

import { useRef, useState, type ChangeEvent, type DragEvent, type KeyboardEvent } from "react";

type Method = {
  id: string;
  field: string;
  value: string;
  page: number;
  excerpt: string;
  grouping_status: string;
  verification: string;
  system_hint?: string | null;
  stage_hint?: string | null;
};
type ReviewItem = { field: string; value: string; page: number; reason: string };
type Flag = { code: string; title: string; level: string; explanation: string };
type Analysis = {
  schema_version: string;
  document: { filename: string; pages: number };
  method_candidates: Method[];
  review_items: ReviewItem[];
  scientific_flags: Flag[];
  disclaimer: string;
};

const API = process.env.NEXT_PUBLIC_PAPERLENS_API_URL || (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");
const MAX_BYTES = 20 * 1024 * 1024;

const samples = [
  {
    id: "gromacs",
    label: "GROMACS",
    subtitle: "standard MD",
    color: "blue",
    title: "Synthetic GROMACS example",
    lines: [
      ["MD engine", "GROMACS 2024.1", "Production simulations were performed using GROMACS 2024.1 with the CHARMM36m force field.", 1],
      ["Force field", "CHARMM36m", "Production simulations were performed using GROMACS 2024.1 with the CHARMM36m force field.", 1],
      ["Water model", "TIP3P", "The system was solvated in TIP3P water and equilibrated at 300 K.", 1],
      ["Temperature", "300 K", "The system was solvated in TIP3P water and equilibrated at 300 K.", 1],
      ["Time step", "2 fs", "A 2 fs timestep was used during production.", 2],
    ] as Array<[string, string, string, number]>,
  },
  {
    id: "openmm",
    label: "OpenMM",
    subtitle: "replica runs",
    color: "teal",
    title: "Synthetic OpenMM example",
    lines: [
      ["MD engine", "OpenMM 8.0", "The production simulations used OpenMM 8.0 with CHARMM36m.", 1],
      ["Force field", "CHARMM36m", "The production simulations used OpenMM 8.0 with CHARMM36m.", 1],
      ["Temperature", "310 K", "Five independent replicas were simulated at 310 K.", 1],
      ["Replicas", "5 independent replicas", "Five independent replicas were simulated at 310 K.", 1],
      ["Simulation duration", "100 ns", "Each replica was run for 100 ns.", 2],
    ] as Array<[string, string, string, number]>,
  },
  {
    id: "multiple",
    label: "WT & E41A",
    subtitle: "two systems",
    color: "violet",
    title: "Synthetic multi-system example",
    lines: [
      ["Temperature", "300 K", "WT production simulations were performed at 300 K.", 1],
      ["Temperature", "310 K", "E41A production simulations were performed at 310 K.", 1],
      ["Force field", "CHARMM36m", "WT simulations used the CHARMM36m force field.", 2],
      ["Force field", "AMBER ff19SB", "E41A simulations used the AMBER ff19SB force field.", 2],
    ] as Array<[string, string, string, number]>,
  },
  {
    id: "enhanced",
    label: "Umbrella",
    subtitle: "sampling",
    color: "orange",
    title: "Synthetic enhanced-sampling example",
    lines: [
      ["Enhanced sampling", "umbrella sampling", "Umbrella sampling windows were used to calculate a potential of mean force.", 1],
      ["Temperature", "323 K", "All windows were simulated at 323 K.", 1],
      ["Simulation duration", "20 ns", "The sampling duration was 20 ns per window.", 2],
    ] as Array<[string, string, string, number]>,
  },
] as const;

function makeSample(sample: (typeof samples)[number]): Analysis {
  const records = sample.lines.map(([field, value, excerpt, page], index): Method => ({
    id: sample.id + "-" + index, field, value, page, excerpt,
    grouping_status: "unassigned", verification: "synthetic_demo_only",
    system_hint: null, stage_hint: null,
  }));
  return {
    schema_version: "1.0",
    document: { filename: sample.title, pages: Math.max(...sample.lines.map((line) => line[3])) },
    method_candidates: records,
    review_items: [],
    scientific_flags: sample.id === "multiple" ? [{
      code: "MULTIPLE_SYSTEMS", title: "Multiple simulation systems",
      level: "review", explanation: "WT and E41A belong to different experiments. This preview displays independent evidence rows; it does not reconstruct protocols.",
    }] : [],
    disclaimer: "Synthetic demonstration only — not an uploaded research paper. These values illustrate the interface; verify every real extraction against the original PDF.",
  };
}

function isAnalysis(value: unknown): value is Analysis {
  if (!value || typeof value !== "object") return false;
  const record = value as Partial<Analysis>;
  return record.schema_version === "1.0"
    && !!record.document && typeof record.document.filename === "string"
    && typeof record.document.pages === "number"
    && Array.isArray(record.method_candidates)
    && record.method_candidates.every((item) => item && typeof item.field === "string"
      && typeof item.value === "string" && typeof item.excerpt === "string"
      && typeof item.page === "number" && typeof item.id === "string")
    && Array.isArray(record.review_items) && Array.isArray(record.scientific_flags)
    && typeof record.disclaimer === "string";
}

function EvidenceQuote({ text, value }: { text: string; value: string }) {
  const start = text.toLocaleLowerCase().indexOf(value.toLocaleLowerCase());
  if (start === -1) return <p className="evidence-quote">{text}</p>;
  return <p className="evidence-quote">
    {text.slice(0, start)}<mark>{text.slice(start, start + value.length)}</mark>{text.slice(start + value.length)}
  </p>;
}

function ArrowIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 16V3m0 0L7.5 7.5M12 3l4.5 4.5"/><path d="M4 15.5v3A2.5 2.5 0 006.5 21h11a2.5 2.5 0 002.5-2.5v-3"/>
  </svg>;
}
function SparkleIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2.5l1.7 6 6 1.7-6 1.8-1.7 6-1.7-6-6-1.8 6-1.7zM19 16l.9 2.8L22.5 20l-2.6.9L19 23.5l-.9-2.6L15.5 20l2.6-1.2z"/>
  </svg>;
}
function ArrowRight() {
  return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14m-6-6l6 6-6 6"/></svg>;
}
function FileIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M7 2h7l5 5v14H5V4a2 2 0 012-2z"/><path d="M14 2v6h5M8 13h8M8 17h6"/></svg>;
}

function download(name: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function escapeCsv(value: string | number) {
  return '"' + String(value).replace(/"/g, '""') + '"';
}
export default function Workspace() {
  const fileInput = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<Analysis | null>(null);
  const [sampleId, setSampleId] = useState<string | null>(null);
  const [selected, setSelected] = useState(0);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  function scrollToResults() {
    window.setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  }
  function chooseFile(next: File | null) {
    setDragging(false);
    setData(null);
    setSampleId(null);
    setSelected(0);
    setFile(next);
    setError("");
    if (next && (!next.name.toLowerCase().endsWith(".pdf") || next.size > MAX_BYTES || !next.size)) {
      setError("Please choose a nonempty PDF file up to 20 MB.");
    }
  }
  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    chooseFile(event.target.files?.[0] || null);
  }
  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    if (busy) return;
    chooseFile(event.dataTransfer.files[0] || null);
  }
  async function analyze() {
    if (!file || busy) return;
    if (!API) { setError("Live PDF analysis is not enabled on this deployment yet. Try the interactive samples."); return; }
    if (!file.name.toLowerCase().endsWith(".pdf") || file.size > MAX_BYTES || !file.size) {
      setError("Please choose a nonempty PDF file up to 20 MB.");
      return;
    }
    setBusy(true);
    setError("");
    setData(null);
    setSampleId(null);
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await fetch(API + "/api/v1/analyze", { method: "POST", body });
      const payload: unknown = await response.json();
      if (!response.ok) {
        let detail = "The analysis could not be completed.";
        if (payload && typeof payload === "object" && "detail" in payload
          && typeof (payload as { detail: unknown }).detail === "string") {
          detail = (payload as { detail: string }).detail;
        }
        throw new Error(detail);
      }
      if (!isAnalysis(payload)) throw new Error("The API response did not match the expected schema.");
      setData(payload);
      setSelected(0);
      scrollToResults();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Could not contact the local analysis server.");
    } finally {
      setBusy(false);
    }
  }
  function openSample(id: string) {
    const example = samples.find((item) => item.id === id);
    if (!example || busy) return;
    setData(makeSample(example));
    setSampleId(id);
    setFile(null);
    if (fileInput.current) fileInput.current.value = "";
    setError("");
    setSelected(0);
    scrollToResults();
  }
  function exportCsv() {
    if (!data || sampleId) return;
    const headers = ["field", "value", "page", "excerpt", "grouping_status", "verification"];
    const lines = [headers.map(escapeCsv).join(",")];
    for (const item of data.method_candidates) {
      lines.push(headers.map((key) => escapeCsv(String(item[key as keyof Method] ?? ""))).join(","));
    }
    download("paperlens_methods.csv", "\uFEFF" + lines.join("\n"), "text/csv;charset=utf-8");
  }
  const active = data?.method_candidates[selected];

  return <>
    <header className="site-header">
      <div className="nav-inner">
        <a className="brand" href="/" aria-label="PaperLens home">
          <span className="brand-symbol"><svg viewBox="0 0 30 30" fill="none" aria-hidden="true">
            <path d="M4 19l6-8 6 5 5-9 5 4" stroke="white" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"/>
          </svg></span>
          <span className="brand-name">PaperLens</span><span className="beta">BETA</span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="https://github.com/strawberryHunter/paperlens-md" target="_blank" rel="noopener noreferrer">GitHub <span aria-hidden="true">↗</span></a>
        </nav>
      </div>
    </header>

    <main>
      <section className="hero">
        <div className="hero-inner">
          <div className="eyebrow"><span className="sparkle"><SparkleIcon /></span> Evidence-first molecular dynamics research</div>
          <h1>Every MD paper.<br/><span>One clear view.</span></h1>
          <p className="hero-copy">Drop a scientific PDF. PaperLens finds simulation settings, shows the supporting text, and helps you review methods with their source evidence.</p>

          <div className={"dropzone" + (dragging ? " drag-active" : "")} onDragOver={(e) => { e.preventDefault(); if (!busy) setDragging(true); }} onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node)) setDragging(false); }} onDrop={onDrop}>
            <input ref={fileInput} id="paper-file" type="file" accept=".pdf,application/pdf" onChange={onFileChange} className="visually-hidden" aria-label="Choose a research PDF" />
            <div className="upload-icon"><ArrowIcon /></div>
            {file ? <>
              <div className="upload-title selected-title"><FileIcon /><span>{file.name}</span></div>
              <p className="upload-helper">{(file.size / (1024 * 1024)).toFixed(2)} MB <span aria-hidden="true">·</span> <button className="link-button" type="button" onClick={() => fileInput.current?.click()} disabled={busy}>choose another PDF</button></p>
              <button className="analyze-button" type="button" onClick={analyze} disabled={busy || !!error || !API} aria-busy={busy}>
                {busy ? "Analyzing PDF…" : API ? "Analyze PDF" : "PDF analysis coming soon"} {!busy && <ArrowRight />}
              </button>
            </> : <>
              <h2 className="upload-title">Drop a PDF here</h2>
              <p className="upload-helper">or <button type="button" className="link-button" onClick={() => fileInput.current?.click()} disabled={busy}>browse files</button> <span aria-hidden="true">·</span> .pdf <span aria-hidden="true">·</span> up to 20 MB</p>
              <p className="upload-detail">Text-based research papers · no scanned PDF support yet{!API ? " · online analysis not enabled yet" : ""}</p>
            </>}
          </div>
          {error && <div className="error-banner" role="alert">{error}{error.toLowerCase().includes("fetch") || error.toLowerCase().includes("network") ? " Make sure the FastAPI backend is running." : ""}</div>}

          <div className="samples">
            <p className="samples-heading">OR TRY A SAMPLE</p>
            <div className="sample-buttons" role="group" aria-label="Synthetic demonstration samples">
              {samples.map((sample) => <button className={"sample-chip " + (sampleId === sample.id ? "chip-selected " : "") + sample.color} type="button" onClick={() => openSample(sample.id)} disabled={busy} key={sample.id}>
                <span className="chip-dot" aria-hidden="true"/><strong>{sample.label}</strong><span>{sample.subtitle}</span>
              </button>)}
            </div>
            <p className="sample-note">Samples use synthetic example text — no scientific results are implied.</p>
          </div>
          <div className="hero-bottom">Scroll to explore <span aria-hidden="true">↓</span></div>
        </div>
      </section>

      {data && <section ref={resultsRef} className="results-section" id="results" aria-live="polite">
        <div className="section-inner">
          <div className="results-topline">
            <div><p className="section-kicker">ANALYSIS WORKSPACE</p><h2>Extracted methods</h2>
              <p className="results-subtitle">{data.document.filename} <span aria-hidden="true">·</span> {data.document.pages} page(s) <span aria-hidden="true">·</span> {data.method_candidates.length} candidate(s)</p>
            </div>
            {sampleId ? <span className="result-tag demo-tag">SYNTHETIC SAMPLE</span> : <span className="result-tag">PDF ANALYZED</span>}
          </div>

          <div className="results-grid">
            <div className="result-card paper-card">
              <div className="card-heading"><h3>Paper evidence</h3><span className="card-hint">Source excerpt</span></div>
              {active ? <>
                <div className="evidence-meta"><span>PDF PAGE {active.page}</span><span>{active.field}</span></div>
                <EvidenceQuote text={active.excerpt} value={active.value}/>
                <p className="small-note">The phrase appears in extracted PDF text. This is not a full-page PDF viewer or independent scientific verification.</p>
              </> : <p className="placeholder-text">No candidate matches were found. Check the paper and supplementary information manually.</p>}
            </div>
            <div className="result-card methods-card">
              <div className="card-heading"><h3>Method candidates</h3><span className="card-hint">{data.method_candidates.length} items</span></div>
              <div className="method-list">
                {data.method_candidates.map((method, index) => <button type="button" key={method.id} className={"method-row" + (index === selected ? " chosen" : "")} onClick={() => setSelected(index)} aria-pressed={index === selected}>
                  <span className="method-description"><span className="method-field">{method.field}</span><strong>{method.value}</strong></span>
                  <span className="method-page">p. {method.page}</span>
                  <span className="method-arrow" aria-hidden="true">↗</span>
                </button>)}
              </div>
            </div>
          </div>
          <div className="audit-card">
            <div className="audit-head"><div><h3>Review & export</h3><p>{data.disclaimer}</p></div>
              {!sampleId && <div className="export-buttons">
                <button type="button" onClick={exportCsv}>Download CSV <span aria-hidden="true">↗</span></button>
                <button type="button" onClick={() => data && download("paperlens_methods.json", JSON.stringify(data, null, 2), "application/json")}>Download JSON <span aria-hidden="true">↗</span></button>
              </div>}
            </div>
            {data.scientific_flags.map((flag, i) => <div className="audit-note" key={flag.code + "-" + i}><span className="flag-dot" aria-hidden="true"/><strong>{flag.title}</strong><span>{flag.explanation}</span></div>)}
            {data.review_items.map((item, i) => <div className="audit-note" key={"held-" + i}><span className="flag-dot" aria-hidden="true"/><strong>Context review: {item.value}</strong><span>Page {item.page} · {item.reason}</span></div>)}
            {!data.review_items.length && !data.scientific_flags.length && <p className="small-note">No rule-based warnings were returned. This does not certify the methods or their completeness.</p>}
          </div>
        </div>
      </section>}

      <section className="how-section" id="how-it-works">
        <div className="section-inner">
          <p className="section-kicker">HOW IT WORKS</p>
          <h2>From paper to evidence, in three steps.</h2>
          <div className="steps">
            <div><span className="step-index">01</span><h3>Upload your PDF</h3><p>Choose a text-based research article. The preview accepts PDFs up to 20 MB.</p></div>
            <div><span className="step-index">02</span><h3>Inspect candidates</h3><p>See detected simulation settings with source excerpts and PDF page numbers.</p></div>
            <div><span className="step-index">03</span><h3>Review & export</h3><p>Check the evidence, review warnings, and export candidate results as CSV or JSON.</p></div>
          </div>
        </div>
      </section>
    </main>
    <footer className="site-footer"><div><strong>PaperLens</strong><span>Research preview · Not an independently validated scientific reviewer</span></div><p>Do not upload confidential manuscripts. Public deployment and multi-protocol reconstruction are not yet available.</p></footer>
  </>;
}
