# Local Viewshed Explorer

Monorepo skeleton for a web app with a React + Vite + TypeScript frontend, a FastAPI backend, and shared types.

## Structure
- `frontend/` React + Vite + TypeScript app
- `backend/` FastAPI service
- `types/` Shared JSON schema and TypeScript types

## Dev Commands
One command to run both frontend and backend (from repo root):
```bash
npm install
npm run dev
```

Frontend only (from repo root):
```bash
npm run dev:frontend
```

Backend only (from repo root):
```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
npm run dev:backend
```

## Prefetch DEM Tiles
You can predownload geography data (Terrarium DEM tiles) into the cache:
```bash
source backend/.venv/bin/activate
python backend/scripts/prefetch_dem.py --state utah --preset fast
```

Options:
```bash
python backend/scripts/prefetch_dem.py --help
```

## Notes
- The backend entry point is `backend/app/main.py`.
- Shared types live in `types/` and can be imported by the frontend via relative paths or set up as a workspace package.
