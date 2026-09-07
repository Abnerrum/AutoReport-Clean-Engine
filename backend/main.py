import uuid
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from wrangling import read_file, clean_data, generate_summary, generate_excel

app = FastAPI(title="DataWrangler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory report storage (sufficient for dev)
reports: dict[str, bytes] = {}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = read_file(contents, file.filename)
        df, cleaning_info = clean_data(df)
        summary = generate_summary(df, cleaning_info)
        excel_bytes = generate_excel(df, summary)

        report_id = str(uuid.uuid4())
        reports[report_id] = excel_bytes

        preview_rows = df.head(50).fillna("").astype(str).values.tolist()
        preview = {
            "columns": df.columns.tolist(),
            "rows": preview_rows,
            "total_rows": len(df),
        }

        return {
            "report_id": report_id,
            "preview": preview,
            "summary": summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@app.get("/api/download/{report_id}")
async def download_report(report_id: str):
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return Response(
        reports[report_id],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=relatorio_limpo.xlsx"
        },
    )
