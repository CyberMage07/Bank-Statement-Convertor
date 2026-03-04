# FinDoc AI - System Architecture (Phase 1 Blueprint)

## 1) Full System Architecture

FinDoc AI is designed as a modular SaaS platform with service boundaries that can evolve into microservices.

### High-level components
- **Frontend (Next.js + Tailwind)**
  - Landing, auth, dashboard, upload, processing status, preview/edit, exports, analytics.
- **API Layer (FastAPI)**
  - Authentication, organizations/teams, document ingestion, parsing orchestration, exports, subscriptions, audit logs, API keys.
- **Processing Workers (Celery + Redis)**
  - Asynchronous pipeline execution for large uploads, OCR, template learning, export generation, reconciliation jobs.
- **Storage**
  - PostgreSQL for relational metadata.
  - S3-compatible object storage for encrypted originals and derived exports.
  - Redis for queue + transient cache + rate limit counters.
- **Billing**
  - Stripe or Razorpay subscriptions with webhook reconciliation.
- **Security controls**
  - JWT auth, signed download URLs, rate limiting, input validation, audit logs, configurable retention and auto-delete.

### Runtime request flow
1. User uploads file(s) from web or API.
2. API stores encrypted file in object storage and persists metadata.
3. API enqueues async parse task in Celery.
4. Worker runs modular pipeline (detect type → extract text/table → OCR fallback → normalize → score).
5. Parsed results stored in PostgreSQL as canonical records.
6. UI polls status and renders editable preview when parsing completes.
7. User exports in selected formats or pushes to accounting integration.

---

## 2) Proposed Folder Structure

```text
/ (repo root)
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST endpoints
│   │   ├── core/                # settings/security/common infra
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic contracts
│   │   ├── services/
│   │   │   ├── parsers/         # extraction + normalization pipeline
│   │   │   └── exports/         # xlsx/csv/docx/pdf/json/xml/tally adapters
│   │   ├── workers/             # Celery app + tasks
│   │   └── utils/               # shared helpers
│   ├── migrations/              # SQL/Alembic migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   ├── components/              # reusable UI components
│   └── lib/                     # client helpers/api wrappers
├── docker/
│   └── worker.Dockerfile
├── tests/
│   ├── backend/
│   └── fixtures/
├── docs/
│   └── system-architecture.md
└── docker-compose.yml
```

---

## 3) Database Schema (Core Entities)

### Multi-tenant SaaS
- `organizations` (tenant boundary)
- `users` (roles: owner/admin/member/auditor)
- `memberships` (optional separate table in phase 2+)

### Document intelligence
- `documents`
  - metadata, source hash, status, confidence, storage key
- `document_pages` (optional for OCR details)
- `transactions`
  - canonical transaction schema:
    - TransactionID, Date, Description, Debit, Credit, Balance, Currency, ReferenceID, AccountNumber, BankName, Category
- `gst_records`
  - GSTIN, invoice no, vendor, CGST/SGST/IGST, totals
- `templates`
  - user/org mapping templates for recurring document layouts

### Operations and compliance
- `jobs` (pipeline + export + reconciliation)
- `audit_logs` (who did what, when)
- `api_keys` (enterprise/API access)
- `subscriptions` and `invoices` (billing state)

---

## 4) Backend API Endpoints (v1)

### Auth & tenancy
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `GET /api/v1/organizations/{id}/members`

### Document pipeline
- `POST /api/v1/documents/upload`
- `POST /api/v1/parse-document` (single-step parsing endpoint)
- `GET /api/v1/documents/{id}`
- `GET /api/v1/documents/{id}/status`
- `GET /api/v1/documents/{id}/preview`
- `PATCH /api/v1/documents/{id}/preview` (human correction)

### Batch processing
- `POST /api/v1/batches`
- `GET /api/v1/batches/{id}`
- `POST /api/v1/batches/{id}/merge`

### Exports & integrations
- `POST /api/v1/exports/{document_id}`
- `GET /api/v1/exports/{export_id}/download`
- `POST /api/v1/integrations/tally/push`
- `POST /api/v1/integrations/quickbooks/push`

### Reconciliation & search
- `POST /api/v1/reconciliation/run`
- `GET /api/v1/reconciliation/{job_id}`
- `GET /api/v1/transactions/search`

### Billing
- `POST /api/v1/billing/checkout`
- `POST /api/v1/billing/webhook/stripe`
- `GET /api/v1/billing/subscription`

---

## 5) Frontend Layout (SaaS UX map)

- `/` Landing page (features, plans, CTA)
- `/login`, `/signup`
- `/dashboard`
  - upload widget
  - usage meter by plan
  - recent jobs
- `/documents`
  - status board: uploaded/processing/review/ready/failed
- `/documents/[id]/preview`
  - extracted table + inline edits
  - confidence indicators (highlight low confidence fields)
- `/exports`
  - format, column mapping, destination (download/integration)
- `/analytics`
  - spend categories, monthly cashflow, GST tax summaries
- `/settings`
  - team roles, templates, API keys, retention policy, billing

---

## 6) Document Parsing Pipeline (Modular)

### Pipeline stages
1. **Upload and validation**
   - mime/type checks, antivirus hook, file size limits.
2. **Type detection**
   - rules on extension/mime + content sampling + heuristics.
3. **Text extraction**
   - PDF text: `pdfplumber`
   - table extraction: `camelot` / `tabula`
4. **OCR fallback**
   - if low text density or scanned image: `pytesseract`
5. **Table & field extraction**
   - identify transaction rows, totals, GST fields.
6. **Normalization**
   - map to canonical schemas (transaction + tax)
7. **Confidence scoring**
   - per document and per field confidence.
8. **Human correction**
   - force review when confidence below threshold.
9. **Export engine**
   - xlsx/csv/docx/pdf/json/xml + accounting-specific adapters.

### Bank statement intelligence
- bank detection signals:
  - logo/OCR tokens
  - known headers (`debit`, `credit`, `balance`, etc.)
  - column order + layout fingerprints
- template registry architecture:
  - each bank parser plugin exposes:
    - `can_handle(document) -> score`
    - `extract(document) -> canonical rows`
  - highest confidence template selected, fallback to generic parser.

### Scalability strategy
- Queue all heavy workloads.
- Make parser workers stateless and horizontally scalable.
- Use object storage and signed URLs for large files.
- Add idempotency keys and source hashing for duplicate prevention.

