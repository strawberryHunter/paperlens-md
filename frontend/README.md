# PaperLens Web — Screenshot-inspired preview

A polished landing and paper-review interface for **PDF-based molecular dynamics Methods extraction**. The supplied MDLens screenshot is a visual reference for the composition, typography, soft gradient and large file drop zone; PaperLens does **not** parse .xvg, .log, .out, or other raw trajectory/log output formats.

## Landing interaction

- Full-width quiet product navigation, pastel hero, bold headline, dotted PDF drag-and-drop area.
- Browse a PDF or drag one into the drop zone; explicitly click **Analyze PDF** before upload.
- Four clickable **synthetic** demonstration cases: GROMACS, OpenMM, WT & E41A, umbrella sampling. These run without a backend and are never described as published research or real extracted results.
- Results appear below the hero: left source excerpt with safe React-highlighted phrase, right separately selectable method candidates, review flags, export for **real analyses only**.
- Responsive mobile layout; no unsupported accuracy promises.

## Local preview

Use Node.js 22:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://127.0.0.1:3000

The synthetic sample chips work without Python running. **Real PDF analysis** requires the FastAPI service from the separate `web/backend-fastapi` branch on http://127.0.0.1:8000. Frontend and backend have passed independent build/API tests; a deployed end-to-end integration with real PDF is still **not verified**.

## Verification

```bash
npm run typecheck
npm run build
npx playwright install chromium
npm run test:e2e
```

Playwright checks the desktop hero, synthetic samples, mobile layout and an HTTP route-mocked PDF upload; it is *not* a live integrated backend test. GitHub Actions uploads screenshots under the `paperlens-browser-evidence` artifact.

## Boundaries

- PDF up to 20 MB, selectable text only; OCR and scanned PDFs unsupported.
- Sample content is synthetic. Source PDF page image/viewer is not implemented in this Next.js preview — shown evidence is a quote with a PDF page index.
- Multiple simulation protocols are **not auto-grouped** in the current FastAPI response; every value remains an individual candidate, with `unassigned` system/stage.
- No authentication, production protections against abusive PDF uploads, scientific benchmark, or deployed browser acceptance yet. Keep the FastAPI endpoint local during development; do not upload sensitive manuscripts to an unvetted host.
