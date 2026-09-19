"""Contracts Finder collector.

Pulls government procurement data from Contracts Finder API.
Free, no key required.
"""

import requests
import json
import time
from datetime import datetime, date, timedelta
from pathlib import Path

API_BASE = "https://www.contractsfinder.service.gov.uk/api"
DATA_DIR = Path(__file__).parent.parent / 'forests' / 'ukgraph' / 'data' / 'contracts'


def collect_recent_contracts(days: int = 30, limit: int = 100) -> list:
    """Collect recent contract awards."""
    results = []
    try:
        start = (date.today() - timedelta(days=days)).isoformat()
        
        payload = {
            "searchCriteria": {
                "types": ["Contract"],
                "statuses": ["Awarded"],
                "publishedFrom": f"{start}T00:00:00+01:00",
            },
            "size": min(limit, 100),
        }
        
        resp = requests.post(
            f"{API_BASE}/rest/2/search_notices/JSON",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            records = data.get('records', data.get('searchResults', []))
            if isinstance(records, list):
                for record in records[:limit]:
                    results.append(normalize_contract(record))
        else:
            print(f"  HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    return results


def collect_contracts_by_area(area: str, limit: int = 50) -> list:
    """Collect contracts for a specific area."""
    results = []
    try:
        payload = {
            "searchCriteria": {
                "types": ["Contract"],
                "statuses": ["Awarded"],
                "keyword": area,
            },
            "size": min(limit, 100),
        }
        
        resp = requests.post(
            f"{API_BASE}/rest/2/search_notices/JSON",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            records = data.get('records', data.get('searchResults', []))
            if isinstance(records, list):
                for record in records[:limit]:
                    results.append(normalize_contract(record))
    except Exception as e:
        print(f"  Error: {e}")
    return results


def normalize_contract(raw: dict) -> dict:
    """Normalize contract to canonical form."""
    return {
        'contract_id': raw.get('id', '') or raw.get('noticeIdentifier', ''),
        'title': raw.get('title', ''),
        'description': raw.get('description', '')[:500],
        'buyer': raw.get('organisationName', ''),
        'buyer_location': raw.get('postcode', ''),
        'cpv_codes': raw.get('cpvCodes', []),
        'value_gbp': raw.get('awardedValue', 0) or raw.get('valueHigh', 0) or 0,
        'status': raw.get('noticeStatus', ''),
        'award_date': raw.get('awardedDate', '') or raw.get('publishedDate', ''),
        'supplier': raw.get('awardedSupplier', ''),
        'source': 'contracts_finder',
        'observed_at': datetime.now().isoformat(),
    }


def save_results(data_type: str, results: list) -> int:
    """Save to daily JSONL."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filepath = DATA_DIR / f"{today}.jsonl"
    
    count = 0
    with open(filepath, 'a') as f:
        for item in results:
            record = {
                'data_type': data_type,
                'collected_at': datetime.now().isoformat(),
                'data': item,
            }
            f.write(json.dumps(record, default=str) + '\n')
            count += 1
    return count


def seed_all() -> dict:
    """Run all collectors."""
    print("Collecting contracts data...")
    
    print("  Recent contracts...", end=' ')
    contracts = collect_recent_contracts(days=30, limit=100)
    saved = save_results('contracts', contracts)
    print(f"{saved} items")
    
    print(f"\nData saved to: {DATA_DIR}")
    return {'contracts': len(contracts)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Contracts Finder Collector')
    parser.add_argument('--seed-all', action='store_true', help='Run all collectors')
    parser.add_argument('--recent', action='store_true', help='Collect recent contracts')
    parser.add_argument('--area', type=str, help='Collect contracts for an area')
    args = parser.parse_args()
    
    if args.seed_all:
        seed_all()
    elif args.recent:
        contracts = collect_recent_contracts()
        save_results('contracts', contracts)
        print(f"Saved {len(contracts)} contracts")
    elif args.area:
        contracts = collect_contracts_by_area(args.area)
        save_results('contracts', contracts)
        print(f"Saved {len(contracts)} contracts for {args.area}")
    else:
        parser.print_help()
