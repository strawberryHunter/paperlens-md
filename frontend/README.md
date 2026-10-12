# PaperLens Frontend (Next.js preview)

This branch is an isolated Next.js 16 + React 19 frontend. It can render a calm two-column evidence view and POST a selected PDF to the **local FastAPI backend preview**.

Run Node.js 20.9+:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Local URL: http://127.0.0.1:3000

Requires API at http://127.0.0.1:8000 from the separate `web/backend-fastapi` branch. Cross-branch integration is not yet a validated deployment. For true local end-to-end testing, use two checkout worktrees with each branch.

```bash
npm run typecheck
npm run build
```

No source PDF preview, authentication, rate limits, automated browser E2E or scientific benchmark yet. DO NOT deploy publicly. The frontend does not automatically send any data before user clicks Analyze PDF.
