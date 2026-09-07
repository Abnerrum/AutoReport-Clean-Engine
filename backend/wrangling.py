import io
import re
import pandas as pd
import pdfplumber


def read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read a raw file into a DataFrame based on its extension."""
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "csv":
        return _read_csv(file_bytes)
    if ext in ("xlsx", "xls"):
        return pd.read_excel(io.BytesIO(file_bytes))
    if ext == "pdf":
        return _read_pdf(file_bytes)
    raise ValueError(f"Formato não suportado: .{ext}")


def _read_csv(file_bytes: bytes) -> pd.DataFrame:
    """Try common encodings and delimiters to handle messy CSVs."""
    for encoding in ("utf-8", "latin-1", "iso-8859-1"):
        for sep in (",", ";", "\t", "|"):
            try:
                df = pd.read_csv(
                    io.BytesIO(file_bytes), encoding=encoding, sep=sep, nrows=5
                )
                if len(df.columns) > 1:
                    return pd.read_csv(
                        io.BytesIO(file_bytes), encoding=encoding, sep=sep
                    )
            except Exception:
                continue
    # Fallback: let pandas sniff the delimiter
    return pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8", sep=None)


def _read_pdf(file_bytes: bytes) -> pd.DataFrame:
    """Extract the first table found in the PDF."""
    tables = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if table and len(table) > 1:
                    header = table[0]
                    rows = table[1:]
                    df = pd.DataFrame(rows, columns=header)
                    tables.append(df)
    if not tables:
        raise ValueError("Não foi possível extrair tabelas do PDF.")
    return pd.concat(tables, ignore_index=True)


def _clean_column_name(name: str) -> str:
    name = str(name).strip().lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply wrangling: normalize headers, drop empties, infer types."""
    original_shape = df.shape

    # Normalize column names
    df.columns = [_clean_column_name(c) for c in df.columns]

    # Remove duplicate column names
    seen = {}
    new_cols = []
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols

    # Remove completely empty rows and columns
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)

    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    # Remove rows that are entirely whitespace
    df = df.dropna(how="all")

    # Infer better data types
    df = df.infer_objects()
    for col in df.columns:
        if df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            non_null = df[col].notna().sum()
            if non_null > 0:
                converted_non_null = converted.notna().sum()
                if converted_non_null >= non_null * 0.8:
                    df[col] = converted

    df = df.reset_index(drop=True)
    duplicates = int(df.duplicated().sum())

    info = {
        "original_rows": int(original_shape[0]),
        "original_cols": int(original_shape[1]),
        "cleaned_rows": int(df.shape[0]),
        "cleaned_cols": int(df.shape[1]),
        "duplicates": duplicates,
    }
    return df, info


def generate_summary(df: pd.DataFrame, cleaning_info: dict) -> dict:
    """Build a per-column summary for the report."""
    summary = {**cleaning_info, "columns": []}
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "non_null": int(df[col].count()),
            "null": int(df[col].isna().sum()),
            "unique": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]) and not df[col].isna().all():
            col_info["min"] = float(df[col].min())
            col_info["max"] = float(df[col].max())
            col_info["mean"] = round(float(df[col].mean()), 2)
        summary["columns"].append(col_info)
    return summary


def generate_excel(df: pd.DataFrame, summary: dict) -> bytes:
    """Produce a multi-sheet Excel report in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Dados Limpos", index=False)

        overview = pd.DataFrame(
            [
                {"Métrica": "Linhas originais", "Valor": summary["original_rows"]},
                {"Métrica": "Colunas originais", "Valor": summary["original_cols"]},
                {"Métrica": "Linhas após limpeza", "Valor": summary["cleaned_rows"]},
                {"Métrica": "Colunas após limpeza", "Valor": summary["cleaned_cols"]},
                {"Métrica": "Duplicatas detectadas", "Valor": summary["duplicates"]},
            ]
        )
        overview.to_excel(writer, sheet_name="Resumo", index=False)

        col_rows = []
        for c in summary["columns"]:
            row = {
                "Coluna": c["name"],
                "Tipo": c["dtype"],
                "Não nulos": c["non_null"],
                "Nulos": c["null"],
                "Únicos": c["unique"],
            }
            if "min" in c:
                row["Mínimo"] = c["min"]
                row["Máximo"] = c["max"]
                row["Média"] = c["mean"]
            col_rows.append(row)
        pd.DataFrame(col_rows).to_excel(writer, sheet_name="Info Colunas", index=False)

    output.seek(0)
    return output.getvalue()
