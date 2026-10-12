# PaperLens FastAPI backend — preview

**API contract** (first implementation):
- `GET /api/v1/health` → JSON health response.
- `POST /api/v1/analyze` → multipart form field `file` (.pdf); returns candidate methods, source PDF page, excerpt, review flags. Schema version `1.0`.
- Hard limit **20 MB, 100 pages**. Does not store PDF using application code, but request upload handling may spool temporarily in the hosting runtime.
- Only CORS origin `http://localhost:3000` by default; comma-delimited `PAPERLENS_CORS_ORIGINS` for explicitly approved origins.
- **Do not deploy to an open public endpoint yet:** authentication, server-side rate limits, upload concurrency limits, PDF sandboxing, abuse control, data deletion policy, and independent scientific benchmark are not complete.

From repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
python -m pytest -q backend/tests
```

Interactive local docs: http://127.0.0.1:8000/docs

**Scientific disclaimer:** Existing rule-based extractor from `main` is intentionally reused without claiming scientific validation. The current backend assigns no simulation to a system or stage: all candidates are `unassigned`. Multi-protocol extraction improvements in another PR must pass separate quality review before integration.

Recommended later: integrate FastAPI service on a restricted preview host, then design auth, observability (no PDF text logging), and privacy review before public beta.
