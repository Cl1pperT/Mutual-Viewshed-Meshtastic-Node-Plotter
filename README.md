# Local Viewshed Explorer

Monorepo skeleton for a web app with a React + Vite + TypeScript frontend, a FastAPI backend, and shared types.

## Structure
- `frontend/` React + Vite + TypeScript app
- `backend/` FastAPI service
- `types/` Shared JSON schema and TypeScript types

## Dev Commands
Frontend (from repo root):
```bash
npm install
npm run dev:frontend
```

Backend (from repo root):
```bash
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
npm run dev:backend
```

## Notes
- The backend entry point is `backend/app/main.py`.
- Shared types live in `types/` and can be imported by the frontend via relative paths or set up as a workspace package.
