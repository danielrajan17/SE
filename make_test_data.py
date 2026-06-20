"""
make_test_data.py — Generate sample cyclone track test CSVs.

Usage:
    python make_test_data.py
    python make_test_data.py --name my_cyclone --out data/raw/my_cyclone.csv
"""

import argparse
import pandas as pd
import numpy as np
import os


SAMPLE_TRACKS = {
    "sample_cs": [
        ("01.01.2024", 600,  9.0, 84.0, 2.5, 1000, 8,  40, "CS"),
        ("01.01.2024", 1200, 9.5, 83.5, 2.5, 998,  10, 42, "CS"),
        ("02.01.2024", 0,    10.0,83.0, 2.5, 996,  12, 45, "CS"),
        ("02.01.2024", 600,  10.5,82.5, 3.0, 992,  14, 48, "SCS"),
        ("02.01.2024", 1200, 11.0,82.0, 3.0, 990,  15, 52, "SCS"),
        ("03.01.2024", 0,    11.5,81.5, 2.5, 994,  12, 46, "CS"),
        ("03.01.2024", 1200, 12.0,81.0, 2.0, 1000, 8,  35, "CS"),
        ("04.01.2024", 0,    12.5,80.5, 1.5, 1004, 4,  28, "DD"),
        ("04.01.2024", 1200, 13.0,80.0, 1.5, 1006, 2,  22, "D"),
    ],
    "sample_vscs": [
        ("05.05.2024", 0,    10.0, 72.0, 3.5, 985, 22, 60, "SCS"),
        ("05.05.2024", 1200, 10.5, 72.0, 4.0, 980, 25, 65, "VSCS"),
        ("06.05.2024", 0,    11.0, 71.8, 4.0, 975, 27, 70, "VSCS"),
        ("06.05.2024", 1200, 11.5, 71.5, 4.5, 968, 32, 78, "VSCS"),
        ("07.05.2024", 0,    12.0, 71.2, 4.5, 960, 38, 88, "VSCS"),
        ("07.05.2024", 1200, 12.5, 71.0, 5.0, 952, 45, 95, "ESCS"),
        ("08.05.2024", 0,    13.0, 71.2, 4.5, 960, 38, 85, "VSCS"),
        ("08.05.2024", 1200, 14.0, 71.8, 4.0, 978, 28, 68, "VSCS"),
        ("09.05.2024", 0,    15.0, 72.5, 3.0, 990, 18, 50, "SCS"),
    ],
}

COLUMNS = ["Date", "Time_UTC", "Latitude", "Longitude", "CI_No",
           "ECP_hPa", "dP_hPa", "MSW_kt", "Category"]


def make(name: str, output_path: str):
    track_key = name if name in SAMPLE_TRACKS else list(SAMPLE_TRACKS.keys())[0]
    rows = SAMPLE_TRACKS[track_key]
    df = pd.DataFrame(rows, columns=COLUMNS)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[make_test_data] Created: {output_path} ({len(df)} rows)")
    print(df.to_string(index=False))


def make_all(out_dir: str = "."):
    for name, rows in SAMPLE_TRACKS.items():
        df = pd.DataFrame(rows, columns=COLUMNS)
        path = os.path.join(out_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"[make_test_data] {path} — {len(df)} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="sample_cs",
                        choices=list(SAMPLE_TRACKS.keys()),
                        help="Which sample track to generate")
    parser.add_argument("--out",  default=os.path.join("data", "raw", "sample_test.csv"))
    parser.add_argument("--all",  action="store_true", help="Generate all sample CSVs")
    args = parser.parse_args()

    if args.all:
        make_all()
    else:
        make(args.name, args.out)
