"""
convert_data.py — Convert between raw IMD formats and processed format.

Usage:
    python convert_data.py --input fengal_test.csv --output data/raw/New_Data.csv
    python convert_data.py --merge fengal_test.csv dithwa_test.csv gaja_test.csv
"""

import argparse
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_wind import fix


def convert_single(input_path: str, output_path: str):
    print(f"[convert] {input_path} → {output_path}")
    fix(input_path, output_path)


def merge_csvs(input_files: list, output_path: str):
    dfs = []
    for f in input_files:
        if not os.path.exists(f):
            print(f"[convert] WARNING: {f} not found, skipping")
            continue
        tmp_out = f.replace(".csv", "_fixed.csv")
        fix(f, tmp_out, verbose=False)
        dfs.append(pd.read_csv(tmp_out))
        os.remove(tmp_out)
        print(f"[convert] Merged: {f} ({len(dfs[-1])} rows)")

    if not dfs:
        print("[convert] No files to merge.")
        return

    merged = pd.concat(dfs, ignore_index=True).drop_duplicates()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    merged.to_csv(output_path, index=False)
    print(f"[convert] Total merged: {len(merged)} rows → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert/merge cyclone CSV files")
    parser.add_argument("--input",  nargs=1,    help="Single input CSV")
    parser.add_argument("--merge",  nargs="+",  help="Multiple CSVs to merge")
    parser.add_argument("--output", default=os.path.join("data", "raw", "New_Data.csv"))
    args = parser.parse_args()

    if args.merge:
        merge_csvs(args.merge, args.output)
    elif args.input:
        convert_single(args.input[0], args.output)
    else:
        # Default: merge all test CSVs in current directory
        test_files = [f for f in os.listdir(".") if f.endswith("_test.csv")]
        if test_files:
            print(f"[convert] Auto-merging: {test_files}")
            merge_csvs(test_files, args.output)
        else:
            parser.print_help()
