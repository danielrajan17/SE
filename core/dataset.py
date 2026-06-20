import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import Config


def load_raw(path=None) -> pd.DataFrame:
    """Load raw CSV, handle multiple date formats and missing values."""
    path = path or Config.DATA_RAW
    df = pd.read_csv(path)

    # Rename columns to standard names
    rename_map = {}
    for col in df.columns:
        c = col.strip()
        cl = c.lower()
        if cl == "date":                                rename_map[col] = "Date"
        elif "time" in cl:                              rename_map[col] = "Time_UTC"
        elif cl in ("latitude", "lat"):                 rename_map[col] = "Latitude"
        elif cl in ("longitude", "lon"):                rename_map[col] = "Longitude"
        elif "c.i" in cl or cl in ("ci", "ci_no"):     rename_map[col] = "CI_No"
        elif "ecp" in cl:                               rename_map[col] = "ECP_hPa"
        elif c.startswith("?") or "dp" in cl or "δp" in cl or "ΔP" in c or "?p" in cl:
                                                        rename_map[col] = "dP_hPa"
        elif "msw" in cl:                               rename_map[col] = "MSW_kt"
        elif cl in ("category", "cat"):                 rename_map[col] = "Category"

    df.rename(columns=rename_map, inplace=True)

    # Cast numeric columns
    for col in ["Latitude", "Longitude", "CI_No", "ECP_hPa", "dP_hPa", "MSW_kt"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing critical columns, fill CI_No with median."""
    required = ["Latitude", "Longitude", "ECP_hPa", "MSW_kt", "Category"]
    df = df.dropna(subset=required).copy()
    df["CI_No"]   = df["CI_No"].fillna(df["CI_No"].median())
    df["dP_hPa"]  = df["dP_hPa"].fillna(0)
    df["Category"] = df["Category"].str.strip()
    # Keep only valid IMD categories
    valid = set(Config.CATEGORY_INFO.keys())
    df = df[df["Category"].isin(valid)]
    return df.reset_index(drop=True)


def save_processed(df: pd.DataFrame, path=None):
    path = path or Config.DATA_PROCESSED
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[dataset] Saved {len(df)} records → {path}")


def load_processed(path=None) -> pd.DataFrame:
    path = path or Config.DATA_PROCESSED
    if not os.path.exists(path):
        print("[dataset] Processed data not found — running clean pipeline...")
        df = clean(load_raw())
        save_processed(df)
        return df
    return pd.read_csv(path)


def get_stats(df: pd.DataFrame) -> dict:
    """Return summary stats for the dashboard."""
    return {
        "total"         : int(len(df)),
        "categories"    : df["Category"].value_counts().to_dict(),
        "lat_range"     : [float(df["Latitude"].min()), float(df["Latitude"].max())],
        "lon_range"     : [float(df["Longitude"].min()), float(df["Longitude"].max())],
        "msw_max"       : float(df["MSW_kt"].max()),
        "ecp_min"       : float(df["ECP_hPa"].min()),
    }


def to_geojson(df: pd.DataFrame) -> dict:
    """Convert dataframe to GeoJSON for Leaflet rendering."""
    features = []
    for _, row in df.iterrows():
        cat   = str(row.get("Category", "D"))
        info  = Config.CATEGORY_INFO.get(cat, {})
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["Longitude"]), float(row["Latitude"])]
            },
            "properties": {
                "category" : cat,
                "color"    : info.get("color", "#fff"),
                "date"     : str(row.get("Date", "")),
                "msw"      : float(row.get("MSW_kt", 0)),
                "ecp"      : float(row.get("ECP_hPa", 1000)),
                "dp"       : float(row.get("dP_hPa", 0)),
                "risk"     : info.get("risk", ""),
            }
        })
    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    df = clean(load_raw())
    save_processed(df)
    print(df.head())
    print(get_stats(df))
