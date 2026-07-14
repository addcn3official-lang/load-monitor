#!/usr/bin/env python3
"""
convert_excel.py
-----------------
Converts the source Excel workbook (sheets "SUM" and "PROVINCE") into the two
JSON files the dashboard (index.html) loads at runtime:

    data/sum_data.json
    data/province_data.json

USAGE
-----
1. Put this script in the same folder as your Excel file (or pass a path).
2. Run:
       python3 convert_excel.py ZZZZ.xlsx
   (or just `python3 convert_excel.py` if the file is named ZZZZ.xlsx in the
   same folder)
3. Commit + push the updated files in the data/ folder to GitHub.
   The HTML file itself does NOT need to change.

REQUIREMENTS
------------
    pip install pandas openpyxl

EXPECTED EXCEL STRUCTURE
-------------------------
Sheet "SUM":
    Columns: SUBSTATION, Voltage Level, TYPE FEEDER (ignored), Feeder,
             then one date column per month (Buddhist-era dates, e.g. 2569-01-01)
             containing that month's peak load per feeder, in MW.

Sheet "PROVINCE":
    Columns in order: MONTH (Buddhist-era date), SUM PROVINCE, PNB, NSN, LRI,
             CNT, SBR, UTI, SUM REG1, SUM REG4, DATE/TIME (peak timestamp text)
"""

import sys
import json
import pandas as pd
from pathlib import Path

DEFAULT_XLSX = "ZZZZ.xlsx"
OUT_DIR = Path(__file__).parent / "data"


def convert_sum_sheet(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name="SUM")
    ignore_cols = {"SUBSTATION", "Voltage Level", "TYPE FEEDER", "Feeder"}
    month_cols = [c for c in df.columns if c not in ignore_cols]
    month_cols = [c for c in month_cols if df[c].notna().any()]

    records = []
    for _, r in df.iterrows():
        records.append({
            "s": r["SUBSTATION"],
            "v": r["Voltage Level"],
            "f": r["Feeder"],
            "m": [round(float(r[c]), 3) if pd.notna(r[c]) else 0 for c in month_cols],
        })

    # Buddhist Era year -> Gregorian (subtract 543), formatted like "Jan 2026"
    months_labels = [c.strftime("%b") + " " + str(c.year - 543) for c in month_cols]

    return {"months": months_labels, "records": records}


def convert_province_sheet(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name="PROVINCE", header=0)
    df.columns = ["month_dt", "sum_province", "pnb", "nsn", "lri", "cnt", "sbr",
                  "uti", "sum_reg1", "sum_reg4", "peak_dt"]
    df = df.dropna(subset=["sum_province"])

    records = []
    for _, r in df.iterrows():
        dt = r["month_dt"]
        records.append({
            "label": dt.strftime("%b") + " " + str(dt.year),
            "total": round(float(r["sum_province"]), 2),
            "provinces": {
                "PNB": round(float(r["pnb"]), 2),
                "NSN": round(float(r["nsn"]), 2),
                "LRI": round(float(r["lri"]), 2),
                "CNT": round(float(r["cnt"]), 2),
                "SBR": round(float(r["sbr"]), 2),
                "UTI": round(float(r["uti"]), 2),
            },
            "reg1": round(float(r["sum_reg1"]), 2),
            "reg4": round(float(r["sum_reg4"]), 2),
            "peak": str(r["peak_dt"]),
        })

    return {"records": records}


def main():
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XLSX
    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        print(f"ERROR: could not find '{xlsx_path}'.")
        print("Usage: python3 convert_excel.py [path-to-excel-file.xlsx]")
        sys.exit(1)

    OUT_DIR.mkdir(exist_ok=True)

    print(f"Reading '{xlsx_path}' ...")

    sum_data = convert_sum_sheet(xlsx_path)
    sum_out = OUT_DIR / "sum_data.json"
    sum_out.write_text(json.dumps(sum_data, separators=(",", ":")), encoding="utf-8")
    print(f"  -> wrote {sum_out}  ({len(sum_data['records'])} feeders, "
          f"{len(sum_data['months'])} months)")

    province_data = convert_province_sheet(xlsx_path)
    province_out = OUT_DIR / "province_data.json"
    province_out.write_text(json.dumps(province_data, separators=(",", ":"), ensure_ascii=False),
                             encoding="utf-8")
    print(f"  -> wrote {province_out}  ({len(province_data['records'])} months)")

    print("\nDone. Commit and push the 'data' folder to GitHub to update the live dashboard.")


if __name__ == "__main__":
    main()
