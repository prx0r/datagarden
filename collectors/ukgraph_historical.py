#!/usr/bin/env python3
"""
UKGraph Historical Data Collectors

Seeds the UKGraph garden with decades of UK economic data.

Sources:
1. Nomis API - ONS labour market (employment, unemployment, wages, jobs)
2. ASHE - Earnings by occupation x region (annual)
3. Companies House bulk - All registered companies (monthly)
4. Land Registry - Every property sale since 1995
5. Business Demography - Enterprise births/deaths
6. Contracts Finder - Government procurement
7. ONS Business Counts - Enterprise counts by SIC/region
"""

import csv
import gzip
import io
import json
import os
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from urllib.parse import urlencode

import requests

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'room' / 'data' / 'historical'

NOMIS_BASE = 'https://www.nomisweb.co.uk/api/v01'
CONTRACTS_FINDER_BASE = 'https://www.contractsfinder.service.gov.uk/api/1'

NOMIS_DATASETS = {
    'employment': 'A01',
    'business_counts': 'KAB9',
    'earnings': 'NM_1',
}

HEADERS = {
    'User-Agent': 'UKGraph-DataGarden/1.0 (research)',
}

RATE_LIMIT_DELAY = 1.0


def ensure_dir(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def rate_limit(seconds: float = RATE_LIMIT_DELAY):
    """Sleep to respect rate limits."""
    time.sleep(seconds)


def save_jsonl(filepath: Path, records: list) -> int:
    """Save records to a JSONL file. Returns count saved."""
    ensure_dir(filepath.parent)
    count = 0
    with open(filepath, 'a') as f:
        for record in records:
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def now_iso() -> str:
    """Current UTC time as ISO string."""
    return datetime.utcnow().isoformat() + 'Z'


# ---------------------------------------------------------------------------
# 1. Nomis API Collectors
# ---------------------------------------------------------------------------

def _nomis_get(dataset_id: str, geography: str, params: dict = None) -> dict:
    """Generic Nomis API GET request."""
    url = f"{NOMIS_BASE}/dataset/{dataset_id}/geography/{geography}.json"
    query = params or {}
    query['pageSize'] = query.get('pageSize', 500)
    try:
        resp = requests.get(url, params=query, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"  Nomis API error ({dataset_id}): {e}")
        return {}


def _nomis_get_csv(dataset_id: str, geography: str, params: dict = None) -> str:
    """Download Nomis data as CSV string."""
    url = f"{NOMIS_BASE}/dataset/{dataset_id}/geography/{geography}.csv"
    query = params or {}
    try:
        resp = requests.get(url, params=query, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  Nomis CSV error ({dataset_id}): {e}")
        return ''


def collect_nomis_employment(geography: str = 'K04000001') -> dict:
    """Collect employment/unemployment data from Nomis API.

    Dataset A01: Employment, unemployment and economic activity.
    geography=K04000001 is UK overall.
    Returns records in canonical UKGraph form.
    """
    print(f"  Collecting Nomis employment ({geography})...")
    dataset_id = NOMIS_DATASETS['employment']
    records = []

    csv_text = _nomis_get_csv(dataset_id, geography)
    if not csv_text:
        return {'source': 'nomis', 'dataset': 'employment', 'count': 0, 'records': []}

    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        normalized = normalize_employment({
            'series_id': f"nomis_emp_{row.get('DATE', '')}",
            'metric': 'employment_rate',
            'occupation': row.get('OBS_VALUE', ''),
            'occupation_name': row.get('OBS_STATUS', ''),
            'region': geography,
            'region_name': row.get('GEOGRAPHY_NAME', geography),
            'period': row.get('DATE', ''),
            'value': row.get('OBS_VALUE', ''),
            'unit': 'rate_per_1000',
            'source': 'nomis',
        })
        if normalized:
            records.append(normalized)
        rate_limit(0.1)

    print(f"    Got {len(records)} employment records")
    return {'source': 'nomis', 'dataset': 'employment', 'count': len(records), 'records': records}


def collect_nomis_business(geography: str = 'K04000001') -> dict:
    """Collect business counts from Nomis.

    Dataset KAB9: Business demography.
    """
    print(f"  Collecting Nomis business counts ({geography})...")
    dataset_id = NOMIS_DATASETS['business_counts']
    records = []

    csv_text = _nomis_get_csv(dataset_id, geography)
    if not csv_text:
        return {'source': 'nomis', 'dataset': 'business_counts', 'count': 0, 'records': []}

    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        record = {
            'series_id': f"nomis_biz_{row.get('DATE', '')}",
            'metric': 'enterprise_count',
            'sic_code': row.get('INDUSTRY', ''),
            'region': geography,
            'region_name': row.get('GEOGRAPHY_NAME', geography),
            'period': row.get('DATE', ''),
            'value': row.get('OBS_VALUE', ''),
            'unit': 'count',
            'source': 'nomis',
            'observed_at': now_iso(),
        }
        records.append(record)
        rate_limit(0.1)

    print(f"    Got {len(records)} business count records")
    return {'source': 'nomis', 'dataset': 'business_counts', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# 2. ASHE Earnings Collector
# ---------------------------------------------------------------------------

ASHE_URL = (
    'https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/'
    'peopleinwork/earningsandworkinghours/datasets/'
    'regionbyoccupation4digitsoc2010ashetable15/'
    'ashe-table-15.xlsx'
)


def collect_ashe_earnings() -> dict:
    """Download ASHE earnings by occupation x region.

    Annual Survey of Hours and Earnings - Table 15.
    Downloads XLSX (or CSV if available) and parses earnings data.
    """
    print("  Collecting ASHE earnings data...")
    records = []

    try:
        resp = requests.get(ASHE_URL, headers=HEADERS, timeout=120, stream=True)
        resp.raise_for_status()
        content = resp.content

        if len(content) < 100:
            print("    ASHE download too small, skipping")
            return {'source': 'ashe', 'dataset': 'earnings', 'count': 0, 'records': []}

        # Try to parse as XLSX
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            wb.close()

            if rows:
                header = [str(c).strip() if c else '' for c in rows[0]]
                for row in rows[1:]:
                    values = [str(c).strip() if c else '' for c in row]
                    if not any(values):
                        continue
                    row_dict = dict(zip(header, values))
                    normalized = normalize_earnings(row_dict)
                    if normalized:
                        records.append(normalized)
        except ImportError:
            print("    openpyxl not installed, attempting CSV fallback")
            # Save raw for manual processing
            csv_path = DATA_DIR / 'ashe_raw.xlsx'
            ensure_dir(DATA_DIR)
            with open(csv_path, 'wb') as f:
                f.write(content)
            print(f"    Saved raw ASHE file to {csv_path}")

    except requests.RequestException as e:
        print(f"    ASHE download error: {e}")

    print(f"    Got {len(records)} ASHE earnings records")
    return {'source': 'ashe', 'dataset': 'earnings', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# 3. Companies House Bulk Collector
# ---------------------------------------------------------------------------

def _latest_companies_house_url() -> str:
    """Construct URL for latest Companies House bulk snapshot."""
    today = date.today()
    for days_back in range(0, 31):
        d = today - timedelta(days=days_back)
        date_str = d.strftime('%Y-%m-%d')
        url = f"https://download.companieshouse.gov.uk/BasicCompanyData-{date_str}.csv.gz"
        try:
            resp = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if resp.status_code == 200:
                return url
        except requests.RequestException:
            continue
    return ''


def collect_companies_house_bulk() -> dict:
    """Download latest Companies House bulk snapshot.

    Downloads the gzipped CSV of all UK registered companies.
    Processes in streaming mode to handle ~469MB compressed files.
    """
    print("  Collecting Companies House bulk data...")
    url = _latest_companies_house_url()
    if not url:
        print("    Could not find latest Companies House snapshot")
        return {'source': 'companies_house', 'dataset': 'bulk', 'count': 0, 'records': []}

    print(f"    Downloading from {url}")
    records = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=600, stream=True)
        resp.raise_for_status()

        # Stream and decompress
        gz_stream = gzip.GzipFile(fileobj=resp.raw)
        text_stream = io.TextIOWrapper(gz_stream, encoding='utf-8', errors='replace')
        reader = csv.DictReader(text_stream)

        count = 0
        batch = []
        for row in reader:
            normalized = normalize_company(row)
            if normalized:
                batch.append(normalized)
                count += 1

            if len(batch) >= 10000:
                records.extend(batch)
                print(f"    Processed {count} companies...")
                batch = []

            # Only collect first 50k for initial seed (full set is ~5M)
            if count >= 50000:
                print(f"    Reached 50k limit, stopping (full set has ~5M companies)")
                break

        records.extend(batch)

    except requests.RequestException as e:
        print(f"    Companies House download error: {e}")

    print(f"    Got {len(records)} company records")
    return {'source': 'companies_house', 'dataset': 'bulk', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# 4. Land Registry Price Paid Collector
# ---------------------------------------------------------------------------

LAND_REGISTRY_URL = (
    'https://landregistry.data.gov.uk/app/ppd'
    '?limit=10000'
    '&header=true'
    '&binary=true'
)


def collect_land_registry() -> dict:
    """Download Land Registry Price Paid Data.

    Every property sale in England and Wales since 1995.
    Downloads CSV in chunks using pagination.
    """
    print("  Collecting Land Registry Price Paid Data...")
    records = []
    page = 1
    max_pages = 5  # Limit for initial seed

    while page <= max_pages:
        url = f"{LAND_REGISTRY_URL}&page={page}"
        print(f"    Downloading page {page}...")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=120)
            resp.raise_for_status()

            reader = csv.DictReader(io.StringIO(resp.text))
            page_count = 0
            for row in reader:
                normalized = normalize_property_sale(row)
                if normalized:
                    records.append(normalized)
                    page_count += 1

            if page_count == 0:
                break

            print(f"    Page {page}: {page_count} records")
            page += 1
            rate_limit(2.0)

        except requests.RequestException as e:
            print(f"    Land Registry download error (page {page}): {e}")
            break

    print(f"    Got {len(records)} property sale records")
    return {'source': 'land_registry', 'dataset': 'price_paid', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# 5. Business Demography Collector
# ---------------------------------------------------------------------------

BUSINESS_DEMOGRAPHY_URL = (
    'https://www.ons.gov.uk/file?uri=/businessindustryandtrade/'
    'business/activitysizeandlocation/datasets/'
    'businessdemographyreferencetable/'
    'referencetable2022.xlsx'
)


def collect_business_demography() -> dict:
    """Download ONS Business Demography.

    Enterprise births, deaths, and survival rates by industry.
    """
    print("  Collecting ONS Business Demography...")
    records = []

    try:
        resp = requests.get(BUSINESS_DEMOGRAPHY_URL, headers=HEADERS, timeout=120)
        resp.raise_for_status()

        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(resp.content), read_only=True, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            wb.close()

            if rows:
                header = [str(c).strip() if c else '' for c in rows[0]]
                for row in rows[1:]:
                    values = [str(c).strip() if c else '' for c in row]
                    if not any(values):
                        continue
                    row_dict = dict(zip(header, values))
                    record = {
                        'series_id': f"biz_demo_{row_dict.get('Year', '')}",
                        'metric': 'enterprise_births',
                        'sic_code': row_dict.get('SIC 2007', row_dict.get('Industry', '')),
                        'period': row_dict.get('Year', ''),
                        'value': row_dict.get('Births', row_dict.get('Value', '')),
                        'unit': 'count',
                        'source': 'ons_business_demography',
                        'observed_at': now_iso(),
                    }
                    records.append(record)
        except ImportError:
            print("    openpyxl not installed, saving raw file")
            xlsx_path = DATA_DIR / 'business_demography_raw.xlsx'
            ensure_dir(DATA_DIR)
            with open(xlsx_path, 'wb') as f:
                f.write(resp.content)
            print(f"    Saved raw file to {xlsx_path}")

    except requests.RequestException as e:
        print(f"    Business Demography download error: {e}")

    print(f"    Got {len(records)} business demography records")
    return {'source': 'ons', 'dataset': 'business_demography', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# 6. Contracts Finder Collector
# ---------------------------------------------------------------------------

def collect_contracts_finder(limit: int = 100) -> dict:
    """Collect recent government contracts from Contracts Finder.

    Free API, no key needed. Returns OCDS-formatted procurement data.
    """
    print(f"  Collecting Contracts Finder (limit={limit})...")
    records = []
    offset = 0
    page_size = min(limit, 100)

    while offset < limit:
        url = f"{CONTRACTS_FINDER_BASE}/searchrecords"
        params = {
            'searchTerm': '',
            'offset': offset,
            'resultTypes': 'contract',
        }
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            results = data.get('results', [])
            if not results:
                break

            for item in results:
                record = {
                    'series_id': f"contract_{item.get('id', '')}",
                    'contract_id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'description': item.get('description', '')[:500],
                    'organisation': item.get('organization', [{}])[0].get('name', '') if item.get('organization') else '',
                    'status': item.get('status', ''),
                    'value': item.get('value', {}).get('amount', ''),
                    'currency': item.get('value', {}).get('currency', 'GBP'),
                    'award_date': item.get('awardDate', ''),
                    'source': 'contracts_finder',
                    'observed_at': now_iso(),
                }
                records.append(record)

            offset += page_size
            rate_limit(1.0)

        except requests.RequestException as e:
            print(f"    Contracts Finder error: {e}")
            break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"    Contracts Finder parse error: {e}")
            break

    print(f"    Got {len(records)} contract records")
    return {'source': 'contracts_finder', 'dataset': 'contracts', 'count': len(records), 'records': records}


# ---------------------------------------------------------------------------
# Normalization Functions
# ---------------------------------------------------------------------------

def normalize_company(raw: dict) -> dict:
    """Normalize a Companies House company record."""
    company_number = raw.get('CompanyNumber', raw.get('company_number', '')).strip()
    if not company_number:
        return {}

    return {
        'company_number': company_number,
        'company_name': raw.get('CompanyName', raw.get('company_name', '')).strip(),
        'sic_code': raw.get('SICCode_SicText_1', raw.get('sic_code', '')).strip(),
        'sic_description': raw.get('SICCode_SicText_1', raw.get('sic_description', '')).strip(),
        'region': raw.get('RegAddress_Region', raw.get('region', '')).strip(),
        'postcode': raw.get('RegAddress_PostCode', raw.get('postcode', '')).strip(),
        'status': raw.get('CompanyStatus', raw.get('status', '')).strip(),
        'incorporation_date': raw.get('IncorporationDate', raw.get('incorporation_date', '')).strip(),
        'source': 'companies_house',
        'observed_at': now_iso(),
    }


def normalize_property_sale(raw: dict) -> dict:
    """Normalize a Land Registry price paid record."""
    transaction_id = raw.get('Transaction unique identifier', raw.get('transaction_id', '')).strip()
    if not transaction_id:
        return {}

    price_str = raw.get('Price', raw.get('price', '0')).strip().replace(',', '')
    try:
        price = float(price_str)
    except (ValueError, TypeError):
        price = 0

    return {
        'transaction_id': transaction_id,
        'price': price,
        'date': raw.get('Date of Transfer', raw.get('date', '')).strip(),
        'postcode': raw.get('Postcode', raw.get('postcode', '')).strip(),
        'property_type': raw.get('Property Type', raw.get('property_type', '')).strip(),
        'new_build': raw.get('New Build', raw.get('new_build', '')).strip().upper() == 'Y',
        'tenure': raw.get('Tenure', raw.get('tenure', '')).strip(),
        'paon': raw.get('PAON', raw.get('paon', '')).strip(),
        'street': raw.get('Street', raw.get('street', '')).strip(),
        'town': raw.get('Town/City', raw.get('town', '')).strip(),
        'district': raw.get('District', raw.get('district', '')).strip(),
        'county': raw.get('County', raw.get('county', '')).strip(),
        'source': 'land_registry',
        'observed_at': now_iso(),
    }


def normalize_employment(raw: dict) -> dict:
    """Normalize a Nomis employment record."""
    value_str = str(raw.get('value', '')).strip()
    try:
        value = float(value_str)
    except (ValueError, TypeError):
        value = 0

    return {
        'series_id': raw.get('series_id', ''),
        'metric': raw.get('metric', 'employment_rate'),
        'occupation': raw.get('occupation', ''),
        'occupation_name': raw.get('occupation_name', ''),
        'region': raw.get('region', ''),
        'region_name': raw.get('region_name', ''),
        'period': raw.get('period', ''),
        'value': value,
        'unit': raw.get('unit', 'rate_per_1000'),
        'source': 'nomis',
        'observed_at': now_iso(),
    }


def normalize_earnings(raw: dict) -> dict:
    """Normalize an ASHE earnings record."""
    # Try common ASHE column names
    occupation = raw.get('SOC 2010', raw.get('Occupation', raw.get('4 Digit SOC', ''))).strip()
    region = raw.get('Region', raw.get('Area', '')).strip()
    year = raw.get('Year', raw.get('Survey Year', '')).strip()

    # Find pay value column
    pay_value = ''
    for key in ['Median', 'Annual Pay', 'Median Annual Pay', 'Gross Weekly']:
        if key in raw and raw[key]:
            pay_value = str(raw[key]).strip().replace(',', '').replace('£', '')
            break

    try:
        value = float(pay_value)
    except (ValueError, TypeError):
        value = 0

    if not occupation and not region:
        return {}

    return {
        'series_id': f"ashe_{year}_{occupation}",
        'metric': 'median_annual_pay',
        'occupation': occupation,
        'occupation_name': raw.get('Occupation Label', ''),
        'region': region,
        'region_name': raw.get('Region Name', region),
        'period': year,
        'value': value,
        'currency': 'GBP',
        'source': 'ashe',
        'observed_at': now_iso(),
    }


# ---------------------------------------------------------------------------
# Seed All
# ---------------------------------------------------------------------------

def seed_all() -> dict:
    """Run all seed collectors and save to historical directory."""
    ensure_dir(DATA_DIR)
    today = date.today().isoformat()
    summary = {}

    print(f"UKGraph Historical Seed — {today}")
    print("=" * 50)

    # 1. Nomis Employment
    print("\n[1/7] Nomis Employment")
    result = collect_nomis_employment()
    if result['count'] > 0:
        filepath = DATA_DIR / f"nomis_employment_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['nomis_employment'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 2. Nomis Business
    print("\n[2/7] Nomis Business Counts")
    result = collect_nomis_business()
    if result['count'] > 0:
        filepath = DATA_DIR / f"nomis_business_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['nomis_business'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 3. ASHE Earnings
    print("\n[3/7] ASHE Earnings")
    result = collect_ashe_earnings()
    if result['count'] > 0:
        filepath = DATA_DIR / f"ashe_earnings_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['ashe_earnings'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 4. Companies House Bulk
    print("\n[4/7] Companies House Bulk")
    result = collect_companies_house_bulk()
    if result['count'] > 0:
        filepath = DATA_DIR / f"companies_house_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['companies_house'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 5. Land Registry
    print("\n[5/7] Land Registry Price Paid")
    result = collect_land_registry()
    if result['count'] > 0:
        filepath = DATA_DIR / f"land_registry_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['land_registry'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 6. Business Demography
    print("\n[6/7] Business Demography")
    result = collect_business_demography()
    if result['count'] > 0:
        filepath = DATA_DIR / f"business_demography_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['business_demography'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    # 7. Contracts Finder
    print("\n[7/7] Contracts Finder")
    result = collect_contracts_finder(limit=100)
    if result['count'] > 0:
        filepath = DATA_DIR / f"contracts_finder_{today}.jsonl"
        saved = save_jsonl(filepath, result['records'])
        summary['contracts_finder'] = saved
        print(f"  Saved {saved} records → {filepath.name}")

    print(f"\n{'=' * 50}")
    total = sum(summary.values())
    print(f"Total records saved: {total}")
    for source, count in summary.items():
        print(f"  {source}: {count}")
    print(f"\nData directory: {DATA_DIR}")

    return summary


# ---------------------------------------------------------------------------
# CLI Argument Parsing
# ---------------------------------------------------------------------------

def main():
    """Parse CLI arguments and run collectors."""
    import argparse

    parser = argparse.ArgumentParser(
        description='UKGraph Historical Data Collectors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m collectors.ukgraph_historical --seed-all
  python -m collectors.ukgraph_historical --seed-nomis
  python -m collectors.ukgraph_historical --seed-companies-house
  python -m collectors.ukgraph_historical --seed-land-registry
        """,
    )
    parser.add_argument('--seed-all', action='store_true', help='Run all seed collectors')
    parser.add_argument('--seed-nomis', action='store_true', help='Seed Nomis employment + business data')
    parser.add_argument('--seed-ashe', action='store_true', help='Seed ASHE earnings data')
    parser.add_argument('--seed-companies-house', action='store_true', help='Seed Companies House bulk data')
    parser.add_argument('--seed-land-registry', action='store_true', help='Seed Land Registry price paid data')
    parser.add_argument('--seed-business-demography', action='store_true', help='Seed Business Demography data')
    parser.add_argument('--seed-contracts', action='store_true', help='Seed Contracts Finder data')
    parser.add_argument('--geography', default='K04000001', help='Nomis geography code (default: K04000001 = UK)')
    parser.add_argument('--contracts-limit', type=int, default=100, help='Number of contracts to fetch')

    args = parser.parse_args()

    if not any([
        args.seed_all, args.seed_nomis, args.seed_ashe,
        args.seed_companies_house, args.seed_land_registry,
        args.seed_business_demography, args.seed_contracts,
    ]):
        parser.print_help()
        return

    ensure_dir(DATA_DIR)
    today = date.today().isoformat()

    if args.seed_all:
        seed_all()
        return

    if args.seed_nomis:
        print("Collecting Nomis data...")
        for dataset in ['employment', 'business_counts']:
            if dataset == 'employment':
                result = collect_nomis_employment(args.geography)
            else:
                result = collect_nomis_business(args.geography)
            if result['count'] > 0:
                filepath = DATA_DIR / f"nomis_{dataset}_{today}.jsonl"
                saved = save_jsonl(filepath, result['records'])
                print(f"  Saved {saved} records → {filepath.name}")

    if args.seed_ashe:
        print("Collecting ASHE earnings...")
        result = collect_ashe_earnings()
        if result['count'] > 0:
            filepath = DATA_DIR / f"ashe_earnings_{today}.jsonl"
            saved = save_jsonl(filepath, result['records'])
            print(f"  Saved {saved} records → {filepath.name}")

    if args.seed_companies_house:
        print("Collecting Companies House bulk data...")
        result = collect_companies_house_bulk()
        if result['count'] > 0:
            filepath = DATA_DIR / f"companies_house_{today}.jsonl"
            saved = save_jsonl(filepath, result['records'])
            print(f"  Saved {saved} records → {filepath.name}")

    if args.seed_land_registry:
        print("Collecting Land Registry price paid data...")
        result = collect_land_registry()
        if result['count'] > 0:
            filepath = DATA_DIR / f"land_registry_{today}.jsonl"
            saved = save_jsonl(filepath, result['records'])
            print(f"  Saved {saved} records → {filepath.name}")

    if args.seed_business_demography:
        print("Collecting Business Demography...")
        result = collect_business_demography()
        if result['count'] > 0:
            filepath = DATA_DIR / f"business_demography_{today}.jsonl"
            saved = save_jsonl(filepath, result['records'])
            print(f"  Saved {saved} records → {filepath.name}")

    if args.seed_contracts:
        print("Collecting Contracts Finder...")
        result = collect_contracts_finder(args.contracts_limit)
        if result['count'] > 0:
            filepath = DATA_DIR / f"contracts_finder_{today}.jsonl"
            saved = save_jsonl(filepath, result['records'])
            print(f"  Saved {saved} records → {filepath.name}")


if __name__ == '__main__':
    main()
