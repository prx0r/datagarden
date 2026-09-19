"""Planning Data collector.

Pulls planning applications and constraints from planning.data.gov.uk.
Free API, no key required.
"""

import requests
import json
import time
from datetime import datetime, date
from pathlib import Path

API_BASE = "https://www.planning.data.gov.uk"
DATA_DIR = Path(__file__).parent.parent / 'forests' / 'ukgraph' / 'data' / 'planning'


def collect_recent_applications(days: int = 30, limit: int = 100) -> list:
    """Collect recent planning applications."""
    results = []
    try:
        from datetime import timedelta
        start = (date.today() - timedelta(days=days)).isoformat()
        parts = start.split('-')
        
        resp = requests.get(
            f"{API_BASE}/entity.json",
            params={
                'dataset': 'planning-application',
                'start_date_year': parts[0],
                'start_date_month': int(parts[1]),
                'limit': min(limit, 500),
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('entities', data.get('items', data if isinstance(data, list) else []))
            if isinstance(items, list):
                for item in items[:limit]:
                    results.append(normalize_application(item))
    except Exception as e:
        print(f"  Error collecting applications: {e}")
    return results


def collect_constraints_by_uprn(uprn: str) -> dict:
    """Get all planning constraints for a UPRN."""
    datasets = [
        'conservation-area', 'listed-building', 'scheduled-monument',
        'site-of-special-scientific-interest', 'ancient-woodland',
        'flood-risk-zone', 'heritage-at-risk', 'area-of-outstanding-natural-beauty',
    ]
    
    results = []
    try:
        resp = requests.get(
            f"{API_BASE}/entity.json",
            params={
                'q': uprn,
                'dataset': ','.join(datasets),
                'limit': 100,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data if isinstance(data, list) else data.get('items', data.get('data', []))
            if isinstance(items, list):
                for item in items:
                    results.append(normalize_constraint(item))
    except Exception as e:
        print(f"  Error: {e}")
    
    return {'uprn': uprn, 'constraints': results, 'count': len(results)}


def collect_lpas() -> list:
    """List all local planning authorities."""
    results = []
    try:
        resp = requests.get(
            f"{API_BASE}/entity.json",
            params={
                'dataset': 'local-planning-authority',
                'limit': 500,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('entities', data.get('items', data if isinstance(data, list) else []))
            if isinstance(items, list):
                for item in items:
                    results.append({
                        'entity': item.get('entity', ''),
                        'name': item.get('name', ''),
                        'reference': item.get('reference', ''),
                    })
    except Exception as e:
        print(f"  Error: {e}")
    return results


def normalize_application(raw: dict) -> dict:
    """Normalize planning application to canonical form."""
    return {
        'reference': raw.get('reference', ''),
        'address': raw.get('name', ''),
        'description': raw.get('description', ''),
        'status': raw.get('decision', '') or raw.get('status', ''),
        'application_type': raw.get('application-type', ''),
        'decision_date': raw.get('decision-date', ''),
        'start_date': raw.get('start-date', ''),
        'lpa': raw.get('organisation-entity', ''),
        'source': 'planning_data_api',
        'observed_at': datetime.now().isoformat(),
    }


def normalize_constraint(raw: dict) -> dict:
    """Normalize constraint to canonical form."""
    return {
        'name': raw.get('name', ''),
        'dataset': raw.get('dataset', ''),
        'start_date': raw.get('start-date', ''),
        'end_date': raw.get('end-date', ''),
        'entity': raw.get('entity', ''),
        'source': 'planning_data_api',
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
    print("Collecting planning data...")
    
    print("  Recent applications...", end=' ')
    apps = collect_recent_applications(days=30, limit=100)
    saved = save_results('planning_applications', apps)
    print(f"{saved} items")
    
    print("  LPAs...", end=' ')
    lpas = collect_lpas()
    saved = save_results('lpas', lpas)
    print(f"{saved} items")
    
    print(f"\nData saved to: {DATA_DIR}")
    return {'applications': len(apps), 'lpas': len(lpas)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Planning Data Collector')
    parser.add_argument('--seed-all', action='store_true', help='Run all collectors')
    parser.add_argument('--applications', action='store_true', help='Collect applications')
    parser.add_argument('--lpas', action='store_true', help='List LPAs')
    parser.add_argument('--constraints', type=str, help='Get constraints for UPRN')
    args = parser.parse_args()
    
    if args.seed_all:
        seed_all()
    elif args.applications:
        apps = collect_recent_applications()
        save_results('planning_applications', apps)
        print(f"Saved {len(apps)} applications")
    elif args.lpas:
        lpas = collect_lpas()
        print(f"Found {len(lpas)} LPAs")
    elif args.constraints:
        result = collect_constraints_by_uprn(args.constraints)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
