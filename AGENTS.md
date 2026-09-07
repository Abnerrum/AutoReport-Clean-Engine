# DataWrangler — Development Notes

## Architecture
- **Frontend**: React + Vite (host port 3000 → container 5173)
- **Backend**: FastAPI + pandas (internal port 8000, not exposed to host)
- Vite dev server proxies `/api/*` to the backend container — single-origin setup

## Setup
```
docker compose -f docker-compose.base44.yml up -d --build
```

## Verification
- Frontend: `curl http://localhost:3000` → HTML page
- API health (via proxy): `curl http://localhost:3000/api/health` → `{"status":"ok"}`
- Upload test: `curl -F "file=@test.csv" http://localhost:8000/api/process` (from inside api container)

## Key Details
- Backend installs pip deps on each start (no pre-built image); first boot takes ~30s
- Frontend installs npm deps on each start (node_modules in named volume)
- Vite uses polling watch for bind-mount compatibility
- Reports stored in-memory (lost on API restart)
- Supported formats: CSV, Excel (.xlsx/.xls), PDF (table extraction via pdfplumber)
- No external secrets required — all local
