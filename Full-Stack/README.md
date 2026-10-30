# DubaiEstate AI 360 — Full Stack Domain

## Overview

**DubaiEstate AI 360** is an Agentic AI-powered real estate investment, brokerage, and property management intelligence platform. The **Full Stack** domain provides the user-facing web applications, responsive dashboards, interactive property intelligence interfaces, and secure RESTful backend APIs that connect end users with agentic workflows and real estate data.

This directory contains the Full Stack foundation for **Week 1 Day 1 (Full Stack Architecture)**:
- A modular **FastAPI** backend skeleton.
- A responsive **React (Vite)** frontend skeleton.
- Safe, placeholder-only environment templates (`.env.example`).
- Comprehensive Windows PowerShell setup and startup documentation.
- Strict isolation protecting all other technical domains and shared dataset assets.

---

## Architecture Overview

### 1. Frontend Architecture (React + Vite)
- **Framework & Bundler:** React 18 with Vite 5 for fast Hot Module Replacement (HMR) and optimized static production builds.
- **Entry Point:** `src/main.jsx` mounting `<App />` to `index.html`.
- **Component Organization:**
  - `src/components/layout/`: Reusable application frame (`Header`, `Footer`, `MainLayout`, `Layout.css`).
  - `src/components/common/`: Reusable UI building blocks (`Card`, `StatusBadge`, `Common.css`).
- **Application Logic Separation:**
  - `src/services/api.js`: Network client abstracting backend REST calls, reading `VITE_API_BASE_URL` with a default of `http://127.0.0.1:8000`.
- **Styling:** Custom responsive CSS using CSS Custom Properties (variables) and mobile-friendly flexbox/grid layouts without heavy external UI dependencies.

### 2. Backend Architecture (Python FastAPI)
- **Framework & Server:** FastAPI with Uvicorn ASGI server.
- **Modular Directory Layout:**
  - `app/main.py`: ASGI application entry point, CORS middleware configuration, and root metadata endpoint (`/`).
  - `app/config.py`: Centralized environment configuration and path resolution with safe fallbacks.
  - `app/api/router.py`: Aggregates versioned API routes (`/api/v1`).
  - `app/api/v1/endpoints/`: Dedicated route controllers for future milestones (e.g., `/health` on Day 2, `/transactions` on Day 3).
  - `app/schemas/common.py`: Pydantic models for request and response validation.
  - `app/services/`: Encapsulated domain logic and read-only dataset querying (prepared for subsequent days).
  - `app/utils/logger.py`: Centralized standard logging utility.
  - `tests/`: Test suite directory (ready for Pytest).
- **Data Safety:** Configured for read-only access to the shared datasets located in `../../DataSets`. Original CSV datasets are never modified or written to.

---

## Directory Structure

```text
Full-Stack/
├── .env.example                # Domain-level environment template (safe placeholders)
├── .gitignore                  # Full-Stack git exclusions (ignores .env, venv, node_modules)
├── README.md                   # Full Stack documentation & setup guide
├── progress/
│   └── fullstack-aditya-arora.md # Dedicated Full Stack progress report
├── backend/
│   ├── .env.example            # Backend environment template
│   ├── requirements.txt        # Python dependencies
│   ├── tests/
│   │   └── __init__.py         # Test package placeholder
│   └── app/
│       ├── __init__.py         # Application package init
│       ├── main.py             # FastAPI entry point & CORS configuration
│       ├── config.py           # Settings management with safe defaults
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py       # API route aggregator (/api/v1)
│       │   └── v1/
│       │       ├── __init__.py
│       │       └── endpoints/
│       │           └── __init__.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── common.py       # Pydantic response models
│       ├── services/
│       │   └── __init__.py     # Business logic placeholder
│       └── utils/
│           ├── __init__.py
│           └── logger.py       # Standard logging configuration
└── frontend/
    ├── .env.example            # Frontend environment template
    ├── index.html              # HTML5 entry document
    ├── package.json            # Node.js dependencies & scripts
    ├── vite.config.js          # Vite build & dev server config
    └── src/
        ├── main.jsx            # React root mount
        ├── App.jsx             # Core application shell
        ├── App.css             # Page layout & hero section styles
        ├── index.css           # Global reset & CSS design tokens
        ├── components/
        │   ├── common/
        │   │   ├── Card.jsx
        │   │   ├── StatusBadge.jsx
        │   │   └── Common.css
        │   └── layout/
        │       ├── Header.jsx
        │       ├── Footer.jsx
        │       ├── MainLayout.jsx
        │       └── Layout.css
        └── services/
            └── api.js          # Network service layer
```

---

## Prerequisites & Software Requirements

- **Operating System:** Windows 10/11 (or macOS / Linux)
- **Terminal:** Windows PowerShell (or Bash)
- **Python:** 3.10+ (Verified on Python 3.12.4)
- **Node.js:** 18+ (Verified on Node.js 24.13.1, npm 11.8.0)
- **Git:** 2.40+ (Verified on Git 2.53.0)

---

## Installation & Setup Instructions

All commands below are demonstrated using **Windows PowerShell**.

### Step 1: Clone and Navigate to Repository
```powershell
# Navigate to the repository root
cd D:\Projects\DubaiEstate-AI-360-Agentic-AI-Powered-Real-Estate-Investment

# Verify active branch
git branch
```

### Step 2: Backend Setup
```powershell
# Navigate to the backend directory
cd Full-Stack\backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Create local environment configuration from template
Copy-Item .env.example .env
```

### Step 3: Frontend Setup
```powershell
# Open a new PowerShell terminal or navigate to frontend
cd D:\Projects\DubaiEstate-AI-360-Agentic-AI-Powered-Real-Estate-Investment\Full-Stack\frontend

# Install frontend dependencies
npm install

# Create local environment configuration from template
Copy-Item .env.example .env
```

---

## Running the Application

### 1. Start the Backend Server (FastAPI)
From `Full-Stack\backend` (with venv activated):
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Root Service Status:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2. Start the Frontend Development Server (Vite)
From `Full-Stack\frontend`:
```powershell
npm run dev
```
- **Frontend Application UI:** [http://localhost:5173/](http://localhost:5173/)

---

## Environment Configuration & Secrets Protection

- All configuration settings are managed via `.env` files loaded at runtime.
- **NEVER** commit actual secrets, API keys, or credentials to Git.
- Git ignore rules in `.gitignore` and `Full-Stack/.gitignore` explicitly block:
  - `.env`
  - `.env.*` (excluding `.env.example`)
  - `venv/`, `.venv/`
  - `node_modules/`
  - `__pycache__/`, `*.pyc`
  - `.pytest_cache/`
  - `dist/`, `build/`
- Only `.env.example` files containing non-sensitive placeholders are committed.

---

## Implementation Status (Day 1)

| Requirement | Status | Notes |
| :--- | :---: | :--- |
| **Frontend Skeleton** | Completed | React 18, Vite 5, reusable layout/common components, API service |
| **Backend Skeleton** | Completed | FastAPI, modular app structure (config, router, schemas, utils) |
| **Environment Template** | Completed | Non-sensitive `.env.example` at root, domain, backend, and frontend |
| **Setup Instructions** | Completed | Fully documented Windows PowerShell setup & startup steps |
| **Secrets Protection** | Completed | Comprehensive `.gitignore` preventing secrets and virtualenvs |
| **Domain Isolation** | Completed | Shared datasets & other domain files remain untouched |

---

## Known Limitations

1. **Day 1 Scope:** This is an architectural foundation skeleton. No real estate analytics, transaction browsing, or live database syncs are executed.
2. **Health Check Endpoint:** Reserved for Day 2 per the official curriculum.
3. **Transaction Ingestion & Filter APIs:** Scheduled for Day 3 and Day 4.
4. **Interactive Dashboard & Table UI:** Scheduled for Day 5.

---

## Future Scope

- **Week 1 Day 2:** Implement `/health` endpoint with status validation and Pytest unit tests.
- **Week 1 Day 3:** Build read-only CSV ingestion service reading from `DataSets/` and expose `/api/v1/transactions`.
- **Week 1 Day 4:** Add query parameters, pagination, filtering (by area, property type, price), and sorting.
- **Week 1 Day 5:** Build interactive data table in React with responsive filtering, metrics cards, and search.
