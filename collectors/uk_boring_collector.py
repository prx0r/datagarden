#!/usr/bin/env python3
"""UK Boring — Persistent data collector.

Runs continuously, collecting data from free sources.
Stores everything in the canonical garden.

Usage:
    python -m collectors.uk_boring_collector --run-once
    python -m collectors.uk_boring_collector --daemon
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.normalize import store_observation, compute_observation_id

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'uk_products' / 'data'


def collect_soldcomps(query: str, site: str = "EBAY_GB") -> list:
    """Collect sold listings from SoldComps API (free tier: 100/month)."""
    results = []
    try:
        resp = requests.get(
            'https://api.sold-comps.com/v1/sold',
            params={'query': query, 'site': site, 'limit': 40},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'sold_price': float(item.get('soldPrice', 0)),
                    'sold_date': item.get('endedAt', ''),
                    'condition': item.get('condition', ''),
                    'shipping': item.get('shippingPrice', ''),
                    'currency': item.get('soldCurrency', 'GBP'),
                    'url': item.get('url', ''),
                    'source': 'sold_comps',
                })
    except Exception as e:
        print(f"  SoldComps error: {e}")
    return results


def collect_planning(limit: int = 50) -> list:
    """Collect recent planning applications from Planning Data API."""
    results = []
    try:
        resp = requests.get(
            'https://www.planning.data.gov.uk/entity.json',
            params={'dataset': 'planning-application', 'limit': limit},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('entities', [])[:limit]:
                results.append({
                    'reference': item.get('reference', ''),
                    'description': (item.get('description', '') or '')[:500],
                    'status': 'decided' if item.get('decision-date') else 'pending',
                    'entry_date': item.get('entry-date', ''),
                    'source': 'planning_data_api',
                })
    except Exception as e:
        print(f"  Planning error: {e}")
    return results


def normalize_and_store(data_type: str, items: list, garden: str = 'ukproducts') -> int:
    """Normalize items and store as canonical observations."""
    count = 0
    for item in items:
        obs = {
            'observation_id': '',
            'garden': garden,
            'source_id': data_type,
            'source_url': item.get('source', ''),
            'observed_at': datetime.now(timezone.utc).isoformat(),
            'metric': data_type,
            'entity_type': data_type,
            'entity_ref': item.get('title', item.get('reference', ''))[:50].lower().replace(' ', '_'),
            'value': item,
            'truth_class': 'KNOWN',
        }
        obs['observation_id'] = compute_observation_id(obs)
        store_observation(garden, obs)
        count += 1
    return count


def run_once():
    """Run all collectors once."""
    print(f"\n{'='*50}")
    print(f"UK Boring Collection — {datetime.now()}")
    print(f"{'='*50}")

    # Planning data
    print("\n--- Planning Data ---")
    planning = collect_planning(limit=50)
    saved = normalize_and_store('planning_application', planning, 'ukgraph')
    print(f"  Saved {saved} planning applications")

    # Sold comps (if API key available)
    queries = ['technics turntable', 'fender stratocaster', 'nikon camera', 'makita drill']
    print("\n--- Sold Comps ---")
    for q in queries:
        items = collect_soldcomps(q)
        saved = normalize_and_store(f'sold_comps_{q.replace(" ", "_")}', items, 'ukproducts')
        print(f"  {q}: {saved} sold listings")
        time.sleep(1)  # Rate limit

    # Check totals
    print(f"\n--- Totals ---")
    for garden in ['ukproducts', 'ukgraph', 'ukadmin', 'ukopportunity']:
        path = Path(f'canonical/{garden}')
        if path.exists():
            total = sum(1 for f in path.glob('*.jsonl') for _ in open(f))
            print(f"  {garden}: {total}")


def daemon(interval: int = 3600):
    """Run collectors periodically."""
    while True:
        run_once()
        print(f"\nSleeping {interval}s...")
        time.sleep(interval)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-once', action='store_true')
    parser.add_argument('--daemon', action='store_true')
    parser.add_argument('--interval', type=int, default=3600)
    args = parser.parse_args()

    if args.daemon:
        daemon(args.interval)
    else:
        run_once()
