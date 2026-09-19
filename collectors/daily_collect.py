"""Daily collection pipeline.

Runs all collectors, normalizes data, detects signals.
Output: daily manifest of new observations and signals.
"""

import json
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_collectors() -> dict:
    """Run each collector, return counts of raw records collected."""
    print("\n=== Collectors ===")
    counts = {}

    print("\n--- Planning Collector ---")
    try:
        from collectors.planning_collector import collect_recent_applications, save_results
        apps = collect_recent_applications(days=30, limit=100)
        saved = save_results("planning_applications", apps)
        counts["planning"] = saved
        print(f"  Collected {saved} planning applications")
    except Exception as e:
        print(f"  Error: {e}")
        counts["planning"] = 0

    print("\n--- Contracts Collector ---")
    try:
        from collectors.contracts_collector import collect_recent_contracts, save_results
        contracts = collect_recent_contracts(days=30, limit=100)
        saved = save_results("contracts", contracts)
        counts["contracts"] = saved
        print(f"  Collected {saved} contracts")
    except Exception as e:
        print(f"  Error: {e}")
        counts["contracts"] = 0

    print("\n--- ASHE Parser ---")
    try:
        from collectors.ashe_parser import parse_all_years, seed_canonical, normalize_ashe
        raw_records = parse_all_years()
        observations = [normalize_ashe(r, r["year"]) for r in raw_records]
        saved = seed_canonical(observations)
        counts["ashe"] = saved
        print(f"  Parsed {saved} ASHE observations")
    except Exception as e:
        print(f"  Error: {e}")
        counts["ashe"] = 0

    return counts


def normalize_all() -> dict:
    """Normalize raw JSONL → canonical store for each source.

    Reads raw records from forests/, normalizes via core.normalize, writes
    to canonical/{garden}/.  Returns per-source counts.
    """
    print("\n=== Normalize ===")
    from core.normalize import normalize, store_observation_batch, SOURCE_TO_GARDEN
    from core.normalize import _read_jsonl
    from pathlib import Path

    root = Path(__file__).parent.parent
    counts = {}

    source_dirs = {
        "planning_data": root / "forests" / "ukgraph" / "data" / "planning",
        "contracts_finder": root / "forests" / "ukgraph" / "data" / "contracts",
    }

    for source_key, raw_dir in source_dirs.items():
        if not raw_dir.exists():
            print(f"  {source_key}: no raw directory")
            counts[source_key] = 0
            continue

        today_str = date.today().isoformat()
        today_file = raw_dir / f"{today_str}.jsonl"

        if not today_file.exists():
            print(f"  {source_key}: no data for {today_str}")
            counts[source_key] = 0
            continue

        raw_records = _read_jsonl(today_file)
        garden = SOURCE_TO_GARDEN[source_key]

        canonical = []
        for rec in raw_records:
            data = rec.get("data", rec)
            try:
                obs = normalize(source_key, data)
                canonical.append(obs)
            except Exception as e:
                print(f"  {source_key}: normalize error: {e}")

        if canonical:
            saved = store_observation_batch(garden, canonical)
            counts[source_key] = saved
            print(f"  {source_key}: normalized {saved} → {garden}")
        else:
            counts[source_key] = 0
            print(f"  {source_key}: nothing to normalize")

    return counts


def detect_daily_signals() -> list:
    """Find signals in today's new observations.

    Looks for: new planning applications with construction keywords,
    high-value contract awards, and ONS shifts.
    """
    print("\n=== Signal Detection ===")
    from core.normalize import load_observations
    from core.signal import Signal
    from datetime import timezone

    today_str = date.today().isoformat()
    signals = []

    planning = load_observations("ukopportunity", source="planning_data_api", limit=500)
    today_planning = [o for o in planning if o.get("effective_at", "") >= today_str]
    construction_kw = ["extension", "conversion", "new build", "commercial", "demolition"]
    for obs in today_planning:
        desc = obs.get("value", {}).get("description", "").lower()
        if any(kw in desc for kw in construction_kw):
            signals.append(Signal(
                signal_id=f"sig_plan_{obs.get('observation_id', '')[:8]}",
                entity=obs.get("value", {}).get("description", "")[:60],
                place=obs.get("value", {}).get("name", "UK"),
                metric="new_construction_application",
                change=1.0,
                window="1d",
                evidence=[obs.get("observation_id", "")],
                confidence=0.5,
                content_frames=["opportunity"],
                content_worthy=True,
                source_garden="ukopportunity",
                detected_at=datetime.now(timezone.utc).isoformat(),
            ))

    contracts = load_observations("ukopportunity", source="contracts_finder", limit=500)
    today_contracts = [o for o in contracts if o.get("effective_at", "") >= today_str]
    for obs in today_contracts:
        value_gbp = obs.get("value", {}).get("value_gbp", 0)
        if value_gbp >= 100_000:
            signals.append(Signal(
                signal_id=f"sig_con_{obs.get('observation_id', '')[:8]}",
                entity=obs.get("value", {}).get("title", "")[:60],
                place=obs.get("value", {}).get("buyer_location", "UK"),
                metric="high_value_contract",
                change=value_gbp,
                window="1d",
                evidence=[obs.get("observation_id", "")],
                confidence=0.7,
                content_frames=["opportunity"],
                content_worthy=True,
                source_garden="ukopportunity",
                detected_at=datetime.now(timezone.utc).isoformat(),
            ))

    print(f"  Detected {len(signals)} signals")
    return [s.to_dict() for s in signals]


def generate_manifest() -> dict:
    """Output daily summary manifest."""
    print("\n=== Daily Manifest ===")
    from shared.manifest import generate_manifest as _gen
    manifest = _gen()
    print(f"  Merkle root: {manifest['merkle_root'][:16]}...")
    return manifest


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Daily collection pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--collect", action="store_true", help="Run all collectors")
    parser.add_argument("--normalize", action="store_true", help="Normalize raw → canonical")
    parser.add_argument("--signals", action="store_true", help="Detect signals from new data")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    args = parser.parse_args()

    if not any([args.collect, args.normalize, args.signals, args.all]):
        parser.print_help()
        return

    print(f"Datagarden Daily Pipeline — {datetime.now()}")
    print("=" * 50)

    if args.all or args.collect:
        counts = run_all_collectors()
        print(f"\n  Raw totals: {counts}")

    if args.all or args.normalize:
        counts = normalize_all()
        print(f"\n  Normalized totals: {counts}")

    if args.all or args.signals:
        signals = detect_daily_signals()
        if signals:
            out_dir = Path(__file__).parent.parent / "canonical" / "signals"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{date.today().isoformat()}.jsonl"
            with open(out_path, "a") as f:
                for s in signals:
                    f.write(json.dumps(s, default=str) + "\n")
            print(f"  Wrote {len(signals)} signals to {out_path.name}")

    if args.all:
        generate_manifest()

    print(f"\n{'=' * 50}")
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
