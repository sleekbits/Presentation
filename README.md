# PPTX Autofill Web App

Production-oriented template autofill application for PowerPoint (`.pptx`) built with **Next.js + FastAPI + python-pptx**.

## Features
- Upload PPTX templates with file-size and extension validation.
- Detect placeholders in text boxes, slide titles, tables, and optional notes.
- Supported tokens: `{{field}}`, `[[field]]`, `<<field>>` (including nested keys like `{{project.title}}`).
- Dynamic questionnaire UI generated from extracted placeholders.
- Mapping preview by slide/shape with context snippet and inferred field type.
- Fill and generate PPTX while preserving base run formatting (best-effort for split runs).
- Async-style job states: `uploaded -> parsed -> awaiting_input -> generating -> complete|failed`.
- API token authentication via `X-API-Token`.
- Audit log events for upload/parse/generate/download without content logging.
- TTL cleanup scaffold and Redis/Celery-ready docker-compose service.

## Project Structure

```text
/backend
  /models/job.py
  /routes/upload.py
  /routes/parse.py
  /routes/fill.py
  /routes/download.py
  /routes/sample.py
  /services/pptx_parser.py
  /services/pptx_filler.py
  /services/job_store.py
  /tests/test_pptx_parser.py
  /tests/test_pptx_filler.py
  main.py
/frontend
  /app/page.tsx
  /app/layout.tsx
  /lib/api.ts
  /lib/types.ts
Dockerfiles + docker-compose + .env.example
```

## Local Development

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3) Docker compose
```bash
docker compose up --build
```

## API Flow
1. `POST /api/upload` (or `POST /api/sample`)
2. `POST /api/parse/{job_id}`
3. `POST /api/fill/{job_id}`
4. `GET /api/download/{job_id}`

All API requests require header `X-API-Token`.

## Test
```bash
cd backend
pytest -q
```

## Limitations / V2 Notes
- Repeating sections (`{{#collection}}...{{/collection}}`) are scaffolded for v2 only.
- Split-placeholder replacement in heavily styled mixed runs uses paragraph reconstruction and may flatten run-level styling after replacement.
- Celery worker integration is prepared by adding Redis in compose; task queue wiring can be added in v2.
