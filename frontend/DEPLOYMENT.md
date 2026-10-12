# PaperLens — hosted deployment checklist (not end-user setup)

Goal: open a publicly accessible HTTPS PaperLens URL without running a local terminal.

## Site: Vercel
- Import GitHub `strawberryHunter/paperlens-md`, select the **web/frontend-nextjs** branch as the deployed source, and set **Root Directory** to `frontend`.
- Framework: Next.js. No special build command required beyond the package.json scripts.
- The current `NEXT_PUBLIC_PAPERLENS_API_URL` variable is optional for landing + synthetic samples. If unset on a production build, live PDF analysis remains visibly unavailable (rather than accidentally calling visitors' localhost).
- Once a reviewed PDF analysis API is accessible by HTTPS with proper abuse protections, set the exact origin as `NEXT_PUBLIC_PAPERLENS_API_URL` and redeploy.
- Verify URL, HTTPS, hero, interactive samples, mobile layout and browser errors on the **deployed** revision; no production claims before this check.

## Python API: Render
- Source branch: **web/backend-fastapi**. Blueprint located at that branch's root `render.yaml`; Python server startup and health check are predefined.
- Upload processing defaults to **disabled** by `PAPERLENS_UPLOADS_ENABLED=false`.
- Do **not** change it to true on an unrestricted public service until authentication, rate limiting, concurrency/CPU/memory/time ceilings, isolated untrusted PDF parsing, logging minimization and privacy policy are reviewed and tested.
- Add allowed production origins to `PAPERLENS_CORS_ORIGINS` when the exact Vercel URL is known. CORS is NOT access control.
- API health: `/api/v1/health`. This checks server readiness, not scientific correctness.

## Acceptance criteria
1. A stable public HTTPS landing page works in browsers without a terminal.
2. Synthetic examples are identified as synthetic and remain fully navigable.
3. Production PDF upload is enabled only after backend protection; then check an actual licensed research PDF from upload through PDF extraction to source evidence and export.
4. Versioned rollback and reproducible logs are available for both deployments.
5. MD methods are presented as literature candidates, not reconstructed protocols or validated scientific measurements.

## Current blockers
- Hosting service accounts must be connected/authorized by the repository owner. Code changes alone cannot create a Vercel/Render live URL.
- Live cross-host PDF processing has not been exercised; the Vercel launch can initially be a **sample-only preview**.
