"""File reading: TXT (UTF-16 LE), XLS, XLSX with encoding detection and date parsing."""

import pandas as pd
from pathlib import Path

from changereport.constants import HEADER_ALIASES


def load_change_data(filepath: str) -> pd.DataFrame:
    """Load change data from a TXT, XLS, or XLSX file."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix in (".xls", ".xlsx"):
        df = _load_excel(path)
    elif suffix in (".txt", ".tsv", ".csv"):
        df = _load_text(path)
    else:
        try:
            df = _load_text(path)
        except Exception:
            df = _load_excel(path)

    df = _normalize_columns(df)
    df = _clean_data(df)
    df = _parse_dates(df)
    return df


def _load_excel(path: Path) -> pd.DataFrame:
    """Read an Excel file."""
    return pd.read_excel(path, dtype=str, engine="openpyxl")


def _load_text(path: Path) -> pd.DataFrame:
    """Read a tab-delimited text file with auto encoding detection."""
    encoding = _detect_encoding(path)

    df = pd.read_csv(
        path,
        sep="\t",
        encoding=encoding,
        dtype=str,
        na_values=[""],
        keep_default_na=False,
    )
    return df


def _detect_encoding(path: Path) -> str:
    """Detect file encoding by checking BOM bytes."""
    with open(path, "rb") as f:
        bom = f.read(4)

    if bom[:2] == b"\xff\xfe":
        return "utf-16-le"
    elif bom[:2] == b"\xfe\xff":
        return "utf-16-be"
    elif bom[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    else:
        return "utf-8"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names using the alias mapping."""
    new_columns = []
    for col in df.columns:
        cleaned = col.strip().lower()
        # Remove extra internal whitespace
        cleaned = " ".join(cleaned.split())
        canonical = HEADER_ALIASES.get(cleaned)
        if canonical:
            new_columns.append(canonical)
        else:
            # Fallback: replace spaces/special chars with underscore
            fallback = cleaned.replace(" ", "_").replace("/", "_").replace("?", "")
            new_columns.append(fallback)
    df.columns = new_columns
    return df


def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and normalize text fields."""
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            # Replace 'nan' strings from str conversion of NaN
            df[col] = df[col].replace("nan", "")

    # Normalize common NA variants
    na_variants = ["N/A", "n/a", "NA", "None", "none", "-", ""]
    for col in ["assignee", "customer_name", "regions_affected",
                "pre_checks", "system_application"]:
        if col in df.columns:
            df[col] = df[col].replace(na_variants, "")

    return df


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse start/end date+time into datetime columns and compute duration."""
    if "start_date" in df.columns and "start_time" in df.columns:
        df["start_datetime"] = pd.to_datetime(
            df["start_date"] + " " + df["start_time"],
            format="%d-%m-%y %H:%M",
            errors="coerce",
            dayfirst=True,
        )
    else:
        df["start_datetime"] = pd.NaT

    if "end_date" in df.columns and "end_time" in df.columns:
        df["end_datetime"] = pd.to_datetime(
            df["end_date"] + " " + df["end_time"],
            format="%d-%m-%y %H:%M",
            errors="coerce",
            dayfirst=True,
        )
    else:
        df["end_datetime"] = pd.NaT

    # Calculate duration in hours
    mask = df["start_datetime"].notna() & df["end_datetime"].notna()
    df["duration_hours"] = pd.NA
    df.loc[mask, "duration_hours"] = (
        (df.loc[mask, "end_datetime"] - df.loc[mask, "start_datetime"])
        .dt.total_seconds() / 3600
    ).round(2)

    # Handle negative durations (end before start — likely overnight)
    neg_mask = df["duration_hours"].notna() & (df["duration_hours"] < 0)
    df.loc[neg_mask, "duration_hours"] = df.loc[neg_mask, "duration_hours"] + 24

    return df
