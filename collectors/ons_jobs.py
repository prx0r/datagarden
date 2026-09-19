"""
UKGraph — UK Economic Data Collector

Collects from multiple free sources:
1. ONS API — labour market statistics
2. Companies House — business births/deaths (needs free API key)
3. GOV.UK — regulation and policy data
"""

import json
import requests
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'forests' / 'room' / 'data' / 'ons'

ONS_API = 'https://api.beta.ons.gov.uk/v1'


def collect_ons_topics():
    """Collect ONS topic listings to find available labour market datasets."""
    results = []
    try:
        resp = requests.get(f"{ONS_API}/topics", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('items', []):
                title = item.get('title', '').lower()
                if any(kw in title for kw in ['labour', 'employment', 'work', 'economy', 'business']):
                    results.append({
                        'source': 'ons_topic',
                        'topic_id': item.get('id', ''),
                        'title': item.get('title', ''),
                        'subtopics': len(item.get('subtopics', [])),
                    })
    except Exception as e:
        print(f"  ONS topics error: {e}")
    return results


def collect_ons_bulletins():
    """Collect latest ONS bulletins related to labour market."""
    results = []
    queries = ['labour market', 'employment', 'vacancies', 'earnings', 'business population']
    
    for q in queries:
        try:
            resp = requests.get(f"{ONS_API}/search", params={'q': q}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('items', [])[:5]:
                    results.append({
                        'source': 'ons_bulletin',
                        'query': q,
                        'title': item.get('title', ''),
                        'summary': item.get('summary', '')[:200],
                        'type': item.get('type', ''),
                        'release_date': item.get('release_date', ''),
                        'uri': item.get('uri', ''),
                    })
        except Exception as e:
            print(f"  ONS bulletin error ({q}): {e}")
    
    return results


def collect_ons_dataset_data(dataset_id: str):
    """Try to get actual data from an ONS dataset."""
    try:
        # Get latest edition
        resp = requests.get(f"{ONS_API}/datasets/{dataset_id}/editions", timeout=15)
        if resp.status_code != 200:
            return []
        
        editions = resp.json().get('items', [])
        if not editions:
            return []
        
        latest = editions[-1].get('id', '')
        
        # Get latest version
        resp2 = requests.get(f"{ONS_API}/datasets/{dataset_id}/editions/{latest}/versions", timeout=15)
        if resp2.status_code != 200:
            return []
        
        versions = resp2.json().get('items', [])
        if not versions:
            return []
        
        version_url = versions[0].get('downloads', {}).get('csv', {}).get('href', '')
        if version_url:
            return [{'dataset_id': dataset_id, 'edition': latest, 'csv_url': version_url}]
    except Exception:
        pass
    return []


def collect_govuk_regulations():
    """Collect recent UK government regulations and policy changes."""
    results = []
    try:
        # GOV.UK announcements API
        resp = requests.get(
            'https://www.gov.uk/announcements.json',
            params={'filter[topics][]': 'business-and-economy', 'per_page': 10},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('results', []):
                results.append({
                    'source': 'govuk',
                    'title': item.get('title', ''),
                    'summary': item.get('summary', '')[:200],
                    'date': item.get('public_timestamp', ''),
                    'url': item.get('web_url', ''),
                })
    except Exception as e:
        print(f"  GOV.UK error: {e}")
    return results


def save_results(data_type: str, results: list) -> int:
    """Save results to daily JSONL file."""
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


def main():
    """Collect UK economic data."""
    print("Collecting UK economic data...")

    print("  ONS topics...", end=' ')
    results = collect_ons_topics()
    saved = save_results('ons_topics', results)
    print(f"{saved} items")

    print("  ONS bulletins...", end=' ')
    results = collect_ons_bulletins()
    saved = save_results('ons_bulletins', results)
    print(f"{saved} items")

    print("  GOV.UK regulations...", end=' ')
    results = collect_govuk_regulations()
    saved = save_results('govuk_regulations', results)
    print(f"{saved} items")

    print(f"\nData saved to: {DATA_DIR}")


if __name__ == '__main__':
    main()
