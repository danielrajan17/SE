"""
fix_wind.py — Fix common issues in cyclone CSV files:
  - Rename '?P' / 'ΔP' column to 'dP'
  - Replace '-' with NaN in numeric columns
  - Fill missing CI values with median
  - Save cleaned file

Usage:
    python fix_wind.py
    python fix_wind.py --input data/raw/New_Data.csv --output data/raw/New_Data.csv
"""

import argparse
import pandas as pd
import numpy as np
import os

DEFAULT_IN  = os.path.join("data", "raw", "New_Data.csv")
DEFAULT_OUT = os.path.join("data", "raw", "New_Data.csv")


def fix(input_path: str, output_path: str, verbose: bool = True):
    print(f"[fix_wind] Reading: {input_path}")
    df = pd.read_csv(input_path)

    if verbose:
        print(f"  Original columns : {list(df.columns)}")
        print(f"  Original shape   : {df.shape}")

    # 1. Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    # 2. Rename ambiguous columns
    rename = {}
    for c in df.columns:
        if c in ("?P", "ΔP", "dP (hPa)", "Pressure Drop"):
            rename[c] = "dP_hPa"
        elif c == "ECP (hPa)":
            rename[c] = "ECP_hPa"
        elif c == "MSW (kt)":
            rename[c] = "MSW_kt"
        elif c == "C.I. No.":
            rename[c] = "CI_No"
        elif c == "Time (UTC)":
            rename[c] = "Time_UTC"
    df.rename(columns=rename, inplace=True)

    # 3. Replace '-' or empty strings with NaN in numeric cols
    num_cols = ["Latitude", "Longitude", "CI_No", "ECP_hPa", "dP_hPa", "MSW_kt"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].replace("-", np.nan)
            df[col] = df[col].replace("", np.nan)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Fill CI_No with median
    if "CI_No" in df.columns:
        median_ci = df["CI_No"].median()
        filled = df["CI_No"].isna().sum()
        df["CI_No"] = df["CI_No"].fillna(median_ci)
        if verbose:
            print(f"  CI_No: filled {filled} missing values with median={median_ci:.1f}")

    # 5. Fill dP_hPa with 0 if missing
    if "dP_hPa" in df.columns:
        filled = df["dP_hPa"].isna().sum()
        df["dP_hPa"] = df["dP_hPa"].fillna(0)
        if verbose:
            print(f"  dP_hPa: filled {filled} missing values with 0")

    # 6. Strip Category column
    if "Category" in df.columns:
        df["Category"] = df["Category"].astype(str).str.strip()

    if verbose:
        print(f"  Final columns    : {list(df.columns)}")
        print(f"  Final shape      : {df.shape}")
        print(f"  Nulls remaining  :\n{df.isnull().sum()}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[fix_wind] Saved → {output_path}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default=DEFAULT_IN)
    parser.add_argument("--output", default=DEFAULT_OUT)
    parser.add_argument("--quiet",  action="store_true")
    args = parser.parse_args()
    fix(args.input, args.output, verbose=not args.quiet)
