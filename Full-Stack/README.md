# Full-Stack: DubaiEstate AI 360

Week 1 Full Stack work: a FastAPI backend and a React (Vite) frontend that show Dubai transaction data
from `DataSets/` (read-only; originals are never modified).

## Structure
```
Full-Stack/
├── backend/            FastAPI app (app/), tests/, requirements.txt
├── frontend/           React + Vite app (src/)
├── .env.example        Environment template (copy to backend/.env)
└── README.md
```

## Prerequisites
Python 3.10+, Node.js 18+, Git.

## Setup: backend
```bash
cd Full-Stack/backend
python -m venv venv
venv\Scripts\activate          # Windows PowerShell; on macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env
uvicorn app.main:app --reload  # http://127.0.0.1:8000  (docs at /docs)
```

## Setup: frontend
```bash
cd Full-Stack/frontend
npm install
copy .env.example .env         # macOS/Linux: cp .env.example .env
npm run dev                    # http://localhost:5173
```

## Run tests (backend)
```bash
cd Full-Stack/backend
pytest
```

## Architecture
React UI --(HTTP/JSON)--> FastAPI --(pandas, read-only)--> `DataSets/*.csv`

## Rules followed
- No secrets in the repo; only `.env.example` files are committed.
- Virtual environments and `node_modules` are git-ignored.
- Original CSVs are read-only.

## Status
- [x] Day 1: project skeleton, env templates, setup docs
- [ ] Day 2: `/health` endpoint + test
- [ ] Day 3+: transactions API, filters, table, dashboard

## Known limitations
Week 1 prototype for learning; not an investment advisory system.
