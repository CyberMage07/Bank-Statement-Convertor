# FinDoc AI

Production-oriented monorepo scaffold for a Financial Document Intelligence SaaS.

## Quick start

```bash
docker compose up --build
```

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
