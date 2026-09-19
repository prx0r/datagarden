#!/usr/bin/env python3
"""
ASHE Earnings Data Parser

Parses Annual Survey of Hours and Earnings (ASHE) Table 15 XLS/XLSX files
containing earnings by occupation (SOC20 codes) and UK region.

Data lives at:
  forests/room/data/historical/ashe/{2021,2022,2023}/

Each year has SOC20 (3-digit) and SOC20 (4-digit) subdirectories.
We prefer SOC20 (4-digit) for finer granularity.

File layout:
  - Rows 0-3: title / metadata
  - Row 4:    headers (Description, Code, (thousand), Median, change, Mean, ...)
  - Row 5+:   data rows  "Region, Occupation Name"   SOC20 code   ...
  - Last rows: footnotes

Metrics extracted from table-numbered files:
  7a  median_annual_pay      1a  median_weekly_pay
  5a  median_hourly_pay      3a  basic_pay_including_other
  2a  median_weekly_ex_ot    6a  median_hourly_ex_ot
  8a  annual_pay_incentive   4a  overtime_pay
  9a  paid_hours_total       10a paid_hours_basic
  11a paid_hours_overtime
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ASHE_ROOT = Path(__file__).parent.parent / "forests" / "room" / "data" / "historical" / "ashe"
CANONICAL_DIR = Path(__file__).parent.parent / "canonical" / "ukgraph"

OBSERVED_AT = datetime.now(timezone.utc).isoformat()

TABLE_METRICS = {
    "7a": "median_annual_pay",
    "1a": "median_weekly_pay",
    "5a": "median_hourly_pay",
    "3a": "basic_pay_including_other",
    "2a": "median_weekly_excluding_overtime",
    "6a": "median_hourly_excluding_overtime",
    "8a": "annual_pay_incentive",
    "4a": "overtime_pay",
    "9a": "paid_hours_total",
    "10a": "paid_hours_basic",
    "11a": "paid_hours_overtime",
}

REGIONS = [
    "North East", "North West", "Yorkshire and The Humber",
    "East Midlands", "West Midlands", "South West", "East",
    "London", "South East", "Wales", "Scotland",
]

ASHE_SOURCE_URL = (
    "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/"
    "peopleinwork/earningsandworkinghours/datasets/"
    "regionbyoccupation4digitsoc2010ashetable15/ashe-table-15.xlsx"
)

YEARS = [2021, 2022, 2023]


def _hash_observation(source_id, entity_ref, metric, effective_at, region):
    content = json.dumps({
        "source_id": source_id,
        "entity_ref": entity_ref,
        "metric": metric,
        "effective_at": effective_at,
        "region": region,
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _safe_float(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s in ("", "x", ":", "..", "X"):
        return None
    try:
        return float(s.replace(",", ""))
    except (ValueError, TypeError):
        return None


def _parse_description(desc):
    cleaned = desc.strip()
    if not cleaned:
        return ("", "")
    parts = cleaned.split(",", 1)
    if len(parts) != 2:
        return ("", "")
    return (parts[0].strip(), parts[1].strip())


def _detect_table_number(filename):
    m = re.search(r"Table\s+15\s*\(\d+\)\.([\w]+)", filename)
    if m:
        return m.group(1)
    m = re.search(r"\.([\d]+[ab])\b", filename)
    if m:
        return m.group(1)
    return None


def _detect_soc_version(filename):
    if "SOC20 (4)" in filename or "SOC20(4)" in filename:
        return 4
    if "SOC20 (3)" in filename or "SOC20(3)" in filename:
        return 3
    return 0


def _detect_year(filename):
    m = re.search(r"(20\d{2})", filename)
    return int(m.group(1)) if m else None


def _open_workbook(filepath):
    suffix = filepath.suffix.lower()
    if suffix == ".xls":
        import xlrd
        return xlrd.open_workbook(str(filepath)), "xlrd"
    elif suffix in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(str(filepath), read_only=True, data_only=True)
        return wb, "openpyxl"
    raise ValueError(f"Unsupported file type: {suffix}")


def _read_sheet_rows(workbook, sheet_name, backend):
    if backend == "xlrd":
        sh = workbook.sheet_by_name(sheet_name)
        return [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
    ws = workbook[sheet_name]
    return [list(row) for row in ws.iter_rows(values_only=True)]


def parse_xls_file(filepath):
    filepath = Path(filepath)
    filename = filepath.name

    year = _detect_year(filename)
    if not year:
        return []

    table_num = _detect_table_number(filename)
    metric_name = TABLE_METRICS.get(table_num, f"table_{table_num}")

    try:
        workbook, backend = _open_workbook(filepath)
    except Exception as e:
        print(f"  Warning: cannot open {filepath.name}: {e}")
        return []

    try:
        if backend == "xlrd":
            sheet_names = workbook.sheet_names()
        else:
            sheet_names = workbook.sheetnames
        if "All" not in sheet_names:
            print(f"  Warning: no 'All' sheet in {filepath.name}")
            return []
        rows = _read_sheet_rows(workbook, "All", backend)
    finally:
        if backend == "openpyxl":
            workbook.close()

    if len(rows) < 6:
        return []

    records = []
    for row_idx in range(5, len(rows)):
        row = rows[row_idx]
        if len(row) < 6:
            continue

        desc = str(row[0] or "").strip()
        code = str(row[1] or "").strip()

        if not code or not code[0].isdigit():
            continue

        region, occupation_name = _parse_description(desc)
        if not region or not occupation_name:
            continue

        median = _safe_float(row[3]) if len(row) > 3 else None
        mean = _safe_float(row[5]) if len(row) > 5 else None
        num_jobs = _safe_float(row[2]) if len(row) > 2 else None

        records.append({
            "region": region,
            "soc_code": code,
            "occupation_name": occupation_name,
            "metric": metric_name,
            "median": median,
            "mean": mean,
            "num_jobs": num_jobs,
            "sheet": "All",
            "year": year,
        })

    return records


def normalize_ashe(raw, year):
    soc_code = raw["soc_code"]
    region = raw["region"]
    metric = raw["metric"]
    effective_at = f"{year}-04-01"
    source_id = "ashe_earnings"
    observation_id = _hash_observation(source_id, soc_code, metric, effective_at, region)

    return {
        "observation_id": observation_id,
        "garden": "ukgraph",
        "source_id": source_id,
        "source_url": ASHE_SOURCE_URL,
        "observed_at": OBSERVED_AT,
        "effective_at": effective_at,
        "metric": metric,
        "entity_type": "occupation",
        "entity_ref": soc_code,
        "value": {
            "occupation_code": soc_code,
            "occupation_name": raw["occupation_name"],
            "region": region,
            "median_annual_pay": raw.get("median"),
            "mean_annual_pay": raw.get("mean"),
            "year": year,
            "num_jobs_thousands": raw.get("num_jobs"),
        },
        "truth_class": "KNOWN",
    }


def _find_xls_for_year(year, metric_pattern="7a", prefer_soc4=True):
    year_dir = ASHE_ROOT / str(year)
    if not year_dir.exists():
        return []

    candidates = []
    for xls_path in year_dir.rglob("*.*"):
        if xls_path.suffix.lower() not in (".xls", ".xlsx"):
            continue
        fname = xls_path.name
        if metric_pattern not in fname:
            continue
        if " CV" in fname or "cv" in fname.lower():
            continue

        soc_ver = _detect_soc_version(fname)
        candidates.append((soc_ver, xls_path))

    if not candidates:
        return []

    candidates.sort(key=lambda x: (-x[0], x[1]))
    best_soc = candidates[0][0]
    return [p for v, p in candidates if v == best_soc]


def parse_all_years(metric_pattern="7a", prefer_soc4=True):
    all_records = []
    for year in YEARS:
        files = _find_xls_for_year(year, metric_pattern, prefer_soc4)
        if not files:
            print(f"  No files for {year} matching '{metric_pattern}'")
            continue

        for filepath in files:
            print(f"  Parsing {filepath.name}...")
            raw = parse_xls_file(filepath)
            print(f"    -> {len(raw)} raw records")
            all_records.extend(raw)

    return all_records


def seed_canonical(observations, output_dir=None):
    output_dir = Path(output_dir) if output_dir else CANONICAL_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    outpath = output_dir / "ashe_earnings.jsonl"
    count = 0
    with open(outpath, "w") as f:
        for obs in observations:
            f.write(json.dumps(obs, default=str) + "\n")
            count += 1

    print(f"Wrote {count} observations to {outpath}")
    return count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ASHE Earnings Data Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python collectors/ashe_parser.py --parse
  python collectors/ashe_parser.py --seed
  python collectors/ashe_parser.py --parse --metric 5a
  python collectors/ashe_parser.py --parse --year 2022
  python collectors/ashe_parser.py --parse --file path/to/file.xls
        """,
    )
    parser.add_argument("--parse", action="store_true", help="Parse ASHE XLS files and print summary")
    parser.add_argument("--seed", action="store_true", help="Parse and store to canonical JSONL")
    parser.add_argument("--metric", default="7a", help="Table number to parse (default: 7a = annual pay gross)")
    parser.add_argument("--year", type=int, choices=YEARS, help="Parse only this year")
    parser.add_argument("--file", type=str, help="Parse a single file instead of scanning directories")
    parser.add_argument("--output", type=str, help="Output directory for canonical JSONL")

    args = parser.parse_args()

    if not args.parse and not args.seed:
        parser.print_help()
        return

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"File not found: {filepath}")
            sys.exit(1)
        print(f"Parsing single file: {filepath.name}")
        raw = parse_xls_file(filepath)
        print(f"Raw records: {len(raw)}")
        observations = [normalize_ashe(r, r["year"]) for r in raw]
        print(f"Canonical observations: {len(observations)}")

        if observations:
            print(f"\nSample observation:")
            print(json.dumps(observations[0], indent=2, default=str))

        if args.seed:
            seed_canonical(observations, args.output)
        return

    if args.year:
        years_to_parse = [args.year]
    else:
        years_to_parse = YEARS

    print(f"ASHE Parser — years: {years_to_parse}, metric: {args.metric}")
    print("=" * 50)

    all_raw = []
    for year in years_to_parse:
        print(f"\n[{year}]")
        files = _find_xls_for_year(year, args.metric)
        if not files:
            print(f"  No files found")
            continue
        for filepath in files:
            print(f"  Parsing {filepath.name}...")
            raw = parse_xls_file(filepath)
            print(f"    -> {len(raw)} records")
            all_raw.extend(raw)

    observations = [normalize_ashe(r, r["year"]) for r in all_raw]

    print(f"\n{'=' * 50}")
    print(f"Total raw records: {len(all_raw)}")
    print(f"Total observations: {len(observations)}")

    if observations:
        regions = set(o["value"]["region"] for o in observations)
        soc_codes = set(o["entity_ref"] for o in observations)
        years = set(o["value"]["year"] for o in observations)
        print(f"Regions: {len(regions)} — {sorted(regions)}")
        print(f"SOC codes: {len(soc_codes)}")
        print(f"Years: {sorted(years)}")
        print(f"\nSample:")
        print(json.dumps(observations[0], indent=2, default=str))

    if args.seed:
        saved = seed_canonical(observations, args.output)
        print(f"\nSeeded {saved} observations to canonical store")


if __name__ == "__main__":
    main()
