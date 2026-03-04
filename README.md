# FinDoc AI

Production-oriented monorepo scaffold for a Financial Document Intelligence SaaS.

## Run with Docker (recommended)
=======
## Quick start

```bash
docker compose up --build
```

Services:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379

## Parse a bank statement PDF

```bash
curl -X POST "http://localhost:8000/api/v1/parse-document" \
  -F "file=@/absolute/path/to/statement.pdf"
```

Response fields:
- `document_id`
- `bank_name`
- `confidence_score` (0-100)
- `transactions[]`
- `needs_review`

## Run tests

```bash
pytest -q
```

## Phase 2 implemented

- Real PDF extraction with `pdfplumber`
- OCR fallback with `pytesseract` for low-text PDFs
- Bank detection engine (HDFC, ICICI, SBI, AXIS)
- Table-to-transaction normalization into canonical schema
- Rule-based categorization service
- Confidence scoring + human review threshold
- Duplicate transaction hashing
- Unit tests for parser pipeline components
=======
Backend: http://localhost:8000/docs  
Frontend: http://localhost:3000

## Phase 1 output in this commit

- Core architecture blueprint (`docs/system-architecture.md`)
- FastAPI skeleton with parse and export APIs
- Modular parsing pipeline scaffold
- Initial PostgreSQL schema migration
- Next.js landing page scaffold
- Docker compose setup for api + worker + db + redis + frontend
- Baseline parser unit tests
