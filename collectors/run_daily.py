"""
Datagarden — Daily collection runner.

Runs all collectors, classifies observations with Jev, generates daily manifest.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_ebay():
    """Run eBay sold collector."""
    print("\n=== eBay UK Sold ===")
    try:
        from collectors.ebay_sold import main as ebay_main
        ebay_main()
    except Exception as e:
        print(f"  Error: {e}")


def run_companies_house():
    """Run Companies House collector (short burst)."""
    print("\n=== Companies House ===")
    api_key = os.environ.get('COMPANIES_HOUSE_API_KEY')
    if not api_key:
        print("  Skipping: COMPANIES_HOUSE_API_KEY not set")
        return

    try:
        from collectors.companies_house import collect
        import websocket
        import threading

        # Run for 60 seconds then stop
        def timeout():
            import time
            time.sleep(60)
            print("  Timeout reached, stopping")

        timer = threading.Thread(target=timeout, daemon=True)
        timer.start()

        collect(api_key)
    except Exception as e:
        print(f"  Error: {e}")


def run_ons():
    """Run ONS jobs collector."""
    print("\n=== ONS Job Adverts ===")
    try:
        from collectors.ons_jobs import main as ons_main
        ons_main()
    except Exception as e:
        print(f"  Error: {e}")


def classify_observations():
    """Classify today's raw observations with Jev."""
    print("\n=== Jev Classification ===")

    if not os.environ.get('TYPESAFE_API_KEY'):
        print("  Skipping: TYPESAFE_API_KEY not set")
        return

    try:
        from shared.jev import classify_observation
    except ImportError:
        print("  Skipping: typesafe-sdk not installed")
        return

    data_dir = Path(__file__).parent.parent / 'forests'
    results = []

    # Classify eBay observations (breadup)
    ebay_dir = data_dir / 'breadup' / 'data' / 'ebay_sold'
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = ebay_dir / f'{today}.jsonl'

    if today_file.exists():
        print(f"  Classifying breadup observations from {today_file.name}")
        with open(today_file) as f:
            for line in f:
                try:
                    item = json.loads(line)
                    state = (
                        f"Item: {item.get('title', 'unknown')}. "
                        f"Sold price: £{item.get('sold_price', 0)}. "
                        f"Original price: £{item.get('original_price', 0)}. "
                        f"Condition: {item.get('condition', 'unknown')}."
                    )
                    answers = classify_observation(state, forest='breadup')
                    if answers:
                        results.append({
                            'forest': 'breadup',
                            'item': item.get('title', ''),
                            'category': answers['category'].choice,
                            'severity': answers['severity'].score,
                            'actionable': answers['actionable'].noul,
                            'audience': answers['audience'].choice,
                        })
                except (json.JSONDecodeError, KeyError):
                    continue

    # Classify ONS observations (ukgraph)
    ons_dir = data_dir / 'room' / 'data' / 'ons'
    ons_file = ons_dir / f'{today}.jsonl'

    if ons_file.exists():
        print(f"  Classifying ukgraph observations from {ons_file.name}")
        with open(ons_file) as f:
            for line in f:
                try:
                    item = json.loads(line)
                    state = (
                        f"{item.get('title', 'unknown')}. "
                        f"Sector: {item.get('sector', 'unknown')}. "
                        f"Region: {item.get('region', 'unknown')}. "
                        f"Change: {item.get('change', 'unknown')}."
                    )
                    answers = classify_observation(state, forest='ukgraph')
                    if answers:
                        results.append({
                            'forest': 'ukgraph',
                            'item': item.get('title', ''),
                            'category': answers['category'].choice,
                            'urgency': answers['urgency'].score,
                            'content_value': answers['content_value'].noul,
                            'audience': answers['audience'].choice,
                        })
                except (json.JSONDecodeError, KeyError):
                    continue

    # Save classified results
    if results:
        out_dir = data_dir / 'classified'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{today}.jsonl'
        with open(out_path, 'a') as f:
            for r in results:
                f.write(json.dumps(r, default=str) + '\n')
        print(f"  Classified {len(results)} observations → {out_path.name}")
    else:
        print("  No observations to classify today")


def generate_manifest():
    """Generate daily manifest."""
    print("\n=== Generating Manifest ===")
    try:
        from shared.manifest import generate_manifest
        manifest = generate_manifest()
        print(f"  Root hash: {manifest['merkle_root'][:16]}...")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    print(f"Datagarden Daily Collection — {datetime.now()}")
    print("=" * 50)

    run_ebay()
    run_companies_house()
    run_ons()
    classify_observations()
    generate_manifest()

    print(f"\n{'=' * 50}")
    print("Collection complete.")


if __name__ == '__main__':
    main()
