#!/usr/bin/env python3
"""
Breadup Historical Data Collectors

Seeds the Breadup garden with historical data before our own observations begin.

Sources:
1. CoinGecko API (free: 10-30 calls/min) - reference prices
2. Kaggle eBay datasets (download required) - 2.8M listings
3. NBER bargaining data (download required) - 98M Best Offer records
"""

import argparse
import json
import os
import random
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

FOREST_DIR = Path(__file__).resolve().parent.parent / "forests" / "breadup" / "data" / "historical"

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINGECKO_DELAY = 3.0  # seconds between calls to stay within rate limit

KAGGLE_DATASETS = [
    {
        "name": "promptcloud/ebay-product-listing-dataset",
        "description": "eBay product listing dataset (~980k records from 2020, 1.8M from 2021)",
        "url": "https://www.kaggle.com/datasets/promptcloud/ebay-product-listing-dataset",
    },
]

NBER_URL = "https://www.nber.org/research/data/best-offer-sequential-bargaining"

CATALOG = {
    "coin_reference": {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "litecoin": "litecoin",
        "cardano": "cardano",
        "solana": "solana",
    },
    "ebay_categories": [
        "cameras",
        "phones",
        "laptops",
        "gaming_consoles",
        "headphones",
        "watches",
        "shoes",
    ],
}


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def _write_jsonl(records: list, filepath: Path) -> int:
    """Write records to a JSONL file. Returns count written."""
    _ensure_dir(filepath.parent)
    with open(filepath, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return len(records)


def _read_jsonl(filepath: Path) -> list:
    """Read records from a JSONL file."""
    records = []
    if filepath.exists():
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def _gbp_usd_approx() -> float:
    """Rough GBP to USD conversion (updated periodically in production)."""
    return 1.27


# ---------------------------------------------------------------------------
# CoinGecko collectors
# ---------------------------------------------------------------------------

def fetch_coingecko_history(coin_id: str, days: int = 365) -> list:
    """
    Fetch historical price data from CoinGecko for a single coin.
    Returns list of {timestamp, price_usd}.
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    print(f"  CoinGecko: fetching {coin_id} ({days} days)...")
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            print(f"  Rate limited on {coin_id}, waiting 60s...")
            time.sleep(60)
            resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        prices = data.get("prices", [])
        result = []
        for ts_ms, price in prices:
            dt = datetime.utcfromtimestamp(ts_ms / 1000)
            result.append({
                "coin_id": coin_id,
                "date": dt.strftime("%Y-%m-%d"),
                "price_usd": round(price, 4),
            })
        print(f"  Got {len(result)} daily prices for {coin_id}")
        return result
    except Exception as e:
        print(f"  Error fetching {coin_id}: {e}")
        return []


def seed_coingecko_reference(coins: Optional[list] = None, days: int = 365) -> dict:
    """
    Seed historical reference prices from CoinGecko.
    Saves one JSONL per coin under historical/coingecko/.
    """
    if coins is None:
        coins = list(CATALOG["coin_reference"].values())

    _ensure_dir(FOREST_DIR / "coingecko")
    results = {"coins_fetched": 0, "total_records": 0, "files": []}

    for i, coin_id in enumerate(coins):
        prices = fetch_coingecko_history(coin_id, days=days)
        if prices:
            fp = FOREST_DIR / "coingecko" / f"{coin_id}_usd_daily.jsonl"
            n = _write_jsonl(prices, fp)
            results["coins_fetched"] += 1
            results["total_records"] += n
            results["files"].append(str(fp))
        if i < len(coins) - 1:
            time.sleep(COINGECKO_DELAY)

    return results


# ---------------------------------------------------------------------------
# SoldComps free tier collector
# ---------------------------------------------------------------------------

def seed_from_soldcomps(queries: list, limit_per_query: int = 40) -> dict:
    """
    Seed Breadup with real sold prices from SoldComps API (free, no key).

    SoldComps provides 40 results per free request. For each query we hit
    the public endpoint and normalise into Breadup canonical form.
    """
    _ensure_dir(FOREST_DIR / "soldcomps")
    results = {"queries_run": 0, "total_records": 0, "files": []}

    for query in queries:
        print(f"  SoldComps: searching '{query}' (limit={limit_per_query})...")
        try:
            url = "https://api.soldcomps.com/search"
            params = {"q": query, "limit": limit_per_query}
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                print("  Rate limited, waiting 30s...")
                time.sleep(30)
                resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("results", data.get("items", []))

            canonical = []
            for item in items:
                canonical.append(_normalize_soldcomps_item(item, query))

            safe_name = query.replace(" ", "_").lower()[:40]
            fp = FOREST_DIR / "soldcomps" / f"{safe_name}.jsonl"
            n = _write_jsonl(canonical, fp)
            results["queries_run"] += 1
            results["total_records"] += n
            results["files"].append(str(fp))
            print(f"  Got {n} sold items for '{query}'")

        except Exception as e:
            print(f"  Error for '{query}': {e}")

        time.sleep(2)

    return results


def _normalize_soldcomps_item(raw: dict, query: str) -> dict:
    """Normalize a SoldComps result into Breadup canonical form."""
    title = raw.get("title", raw.get("name", query))
    price_usd = raw.get("price", raw.get("sold_price", 0))
    sold_date = raw.get("sold_date", raw.get("date", _timestamp()[:10]))

    brand, model = _extract_brand_model(title)

    return {
        "object_id": f"soldcomps_{_safe_id(title, sold_date)}",
        "canonical_name": title.strip(),
        "category": _guess_category(title),
        "subcategory": _guess_subcategory(title),
        "brand": brand,
        "model": model,
        "condition": raw.get("condition", "used_unknown"),
        "sold_price_gbp": round(float(price_usd) / _gbp_usd_approx(), 2) if price_usd else 0,
        "original_price_gbp": None,
        "platform": "ebay_uk",
        "sold_date": sold_date[:10] if isinstance(sold_date, str) else sold_date,
        "source": "sold_comps_api",
        "observed_at": _timestamp(),
    }


# ---------------------------------------------------------------------------
# Kaggle dataset collectors
# ---------------------------------------------------------------------------

def download_kaggle_datasets() -> dict:
    """
    Download Kaggle eBay datasets (requires kaggle CLI + API credentials).

    Setup:
      pip install kaggle
      mkdir -p ~/.kaggle
      echo '{"username":"YOUR_USER","key":"YOUR_KEY"}' > ~/.kaggle/kaggle.json
      chmod 600 ~/.kaggle/kaggle.json

    Datasets:
      promptcloud/ebay-product-listing-dataset (~2.8M records)
      URL: https://www.kaggle.com/datasets/promptcloud/ebay-product-listing-dataset
    """
    _ensure_dir(FOREST_DIR / "kaggle_raw")
    results = {"datasets_downloaded": 0, "files": [], "errors": []}

    for ds in KAGGLE_DATASETS:
        name = ds["name"].split("/")[-1]
        dest = FOREST_DIR / "kaggle_raw" / name
        print(f"  Kaggle: downloading {ds['name']} -> {dest}")

        try:
            cmd = ["kaggle", "datasets", "download", "-d", ds["name"], "-p", str(dest), "--unzip"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if proc.returncode != 0:
                results["errors"].append({"dataset": ds["name"], "error": proc.stderr.strip()})
                print(f"  Kaggle download failed: {proc.stderr.strip()[:200]}")
            else:
                results["datasets_downloaded"] += 1
                downloaded_files = list(dest.glob("*"))
                results["files"].extend([str(f) for f in downloaded_files])
                print(f"  Downloaded {len(downloaded_files)} files to {dest}")

        except FileNotFoundError:
            msg = "kaggle CLI not found. Install with: pip install kaggle"
            results["errors"].append({"dataset": ds["name"], "error": msg})
            print(f"  {msg}")
        except subprocess.TimeoutExpired:
            results["errors"].append({"dataset": ds["name"], "error": "Download timed out"})
            print(f"  Download timed out for {ds['name']}")

    return results


def load_kaggle_data(kaggle_dir: str, sample_size: int = 10000) -> list:
    """
    Load and normalize Kaggle eBay data from downloaded CSV/JSON files.
    Samples from large datasets to keep processing tractable.
    """
    kaggle_path = Path(kaggle_dir)
    if not kaggle_path.exists():
        print(f"  Kaggle directory not found: {kaggle_dir}")
        return []

    csv_files = list(kaggle_path.glob("*.csv")) + list(kaggle_path.glob("*/**/*.csv"))
    json_files = list(kaggle_path.glob("*.json")) + list(kaggle_path.glob("*/**/*.json"))
    all_files = csv_files + json_files

    if not all_files:
        print(f"  No data files found in {kaggle_dir}")
        return []

    print(f"  Found {len(all_files)} data files, loading sample of {sample_size}...")
    canonical_items = []
    loaded = 0

    for fp in all_files:
        if loaded >= sample_size:
            break
        try:
            if fp.suffix == ".csv":
                items = _load_csv_sample(fp, sample_size - loaded)
            else:
                items = _load_json_sample(fp, sample_size - loaded)
            for item in items:
                canonical_items.append(normalize_kaggle_item(item))
                loaded += 1
        except Exception as e:
            print(f"  Error reading {fp.name}: {e}")

    print(f"  Loaded and normalized {len(canonical_items)} Kaggle items")
    return canonical_items


def _load_csv_sample(fp: Path, max_rows: int) -> list:
    """Load a sample of rows from a CSV file."""
    import csv
    rows = []
    with open(fp, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(dict(row))
    return rows


def _load_json_sample(fp: Path, max_items: int) -> list:
    """Load a sample of items from a JSON/JSONL file."""
    items = []
    with open(fp, encoding="utf-8", errors="replace") as f:
        content = f.read(50_000_000)  # read up to 50MB
    try:
        data = json.loads(content)
        if isinstance(data, list):
            items = data[:max_items]
        elif isinstance(data, dict):
            # could be {"results": [...]} or {"items": [...]}
            for key in ("results", "items", "data", "records"):
                if key in data and isinstance(data[key], list):
                    items = data[key][:max_items]
                    break
    except json.JSONDecodeError:
        # try JSONL
        for line in content.split("\n"):
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                    if len(items) >= max_items:
                        break
                except json.JSONDecodeError:
                    continue
    return items


def normalize_kaggle_item(raw: dict) -> dict:
    """
    Normalize a Kaggle eBay listing into Breadup canonical form.

    Handles various column naming conventions from different Kaggle datasets:
    - promptcloud: product_name, selling_price, brand, etc.
    - others may use: title, price, item_condition, etc.
    """
    title = (
        raw.get("product_name")
        or raw.get("title")
        or raw.get("item_title")
        or raw.get("name")
        or ""
    )
    price_raw = (
        raw.get("selling_price")
        or raw.get("price")
        or raw.get("current_price")
        or raw.get("listed_price")
        or 0
    )
    brand = raw.get("brand", "") or ""
    condition = raw.get("item_condition", raw.get("condition", "")) or ""
    date_sold = (
        raw.get("sold_date")
        or raw.get("date_sold")
        or raw.get("listing_date")
        or raw.get("scraped_at")
        or _timestamp()[:10]
    )

    price_gbp = _parse_price(price_raw)

    extracted_brand, model = _extract_brand_model(title)
    final_brand = brand if brand else extracted_brand

    return {
        "object_id": f"kaggle_{_safe_id(title, str(date_sold))}",
        "canonical_name": title.strip(),
        "category": _guess_category(title),
        "subcategory": _guess_subcategory(title),
        "brand": final_brand,
        "model": model,
        "condition": _normalize_condition(condition),
        "sold_price_gbp": price_gbp,
        "original_price_gbp": None,
        "platform": "ebay_uk",
        "sold_date": str(date_sold)[:10],
        "source": "kaggle_ebay_dataset",
        "observed_at": _timestamp(),
    }


# ---------------------------------------------------------------------------
# NBER bargaining data collectors
# ---------------------------------------------------------------------------

def download_nber_data() -> dict:
    """
    Download NBER Best Offer bargaining dataset.

    Contains 98 million Best Offer listings with offer/counteroffer sequences.
    Reference: https://arxiv.org/abs/2607.03124

    Direct download page:
      https://www.nber.org/research/data/best-offer-sequential-bargaining

    The NBER data is typically distributed as .zip or .tar.gz archives.
    This function attempts to download from the published URL.
    """
    _ensure_dir(FOREST_DIR / "nber_raw")
    results = {"downloaded": False, "files": [], "errors": []}

    archive_name = "nber_best_offer_data.zip"
    dest = FOREST_DIR / "nber_raw" / archive_name

    print(f"  NBER: attempting download from {NBER_URL}...")
    try:
        resp = requests.get(NBER_URL, timeout=30, allow_redirects=True)
        resp.raise_for_status()

        # Try to find download links on the page
        links = _extract_download_links(resp.text, NBER_URL)
        if not links:
            results["errors"].append({
                "message": "No download links found on NBER page",
                "note": "Manual download may be required. Visit: " + NBER_URL,
            })
            print("  No direct download links found. Manual download required.")
            print(f"  Visit: {NBER_URL}")
            return results

        for link in links[:3]:  # download up to 3 files
            fname = link.split("/")[-1].split("?")[0]
            fpath = FOREST_DIR / "nber_raw" / fname
            print(f"  Downloading {fname}...")
            dl_resp = requests.get(link, timeout=300, stream=True)
            dl_resp.raise_for_status()
            with open(fpath, "wb") as f:
                for chunk in dl_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            results["files"].append(str(fpath))
            results["downloaded"] = True
            print(f"  Saved {fname} ({fpath.stat().st_size / 1e6:.1f} MB)")

    except Exception as e:
        results["errors"].append({"error": str(e)})
        print(f"  NBER download error: {e}")

    return results


def _extract_download_links(html: str, base_url: str) -> list:
    """Extract potential download links from NBER page HTML."""
    import re
    patterns = [
        r'href="([^"]*\.(?:zip|tar\.gz|csv|tsv|gz|rar))"',
        r'href="([^"]*download[^"]*)"',
        r'href="([^"]*data[^"]*\.(?:zip|csv))"',
    ]
    links = []
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for m in matches:
            if m.startswith("/"):
                from urllib.parse import urljoin
                m = urljoin(base_url, m)
            if m.startswith("http"):
                links.append(m)
    return list(dict.fromkeys(links))  # dedupe, preserve order


def normalize_nber_item(raw: dict) -> dict:
    """
    Normalize an NBER Best Offer listing into Breadup canonical form.

    NBER data fields (typical):
      - listing_id, title, price, offer_price, counteroffer_price
      - category, condition, seller_id, date_listed, date_sold
      - offer_count, final_price
    """
    title = (
        raw.get("title")
        or raw.get("product_name")
        or raw.get("item_title")
        or ""
    )
    final_price = (
        raw.get("final_price")
        or raw.get("sold_price")
        or raw.get("price")
        or raw.get("closing_price")
        or 0
    )
    original_price = (
        raw.get("price")
        or raw.get("listing_price")
        or raw.get("original_price")
        or 0
    )
    condition = raw.get("condition", "") or ""
    date_sold = (
        raw.get("date_sold")
        or raw.get("sold_date")
        or raw.get("end_date")
        or _timestamp()[:10]
    )
    listing_id = raw.get("listing_id", raw.get("item_id", ""))

    price_gbp = _parse_price(final_price)
    orig_gbp = _parse_price(original_price)

    brand, model = _extract_brand_model(title)

    return {
        "object_id": f"nber_{listing_id or _safe_id(title, str(date_sold))}",
        "canonical_name": title.strip(),
        "category": _guess_category(title),
        "subcategory": _guess_subcategory(title),
        "brand": brand,
        "model": model,
        "condition": _normalize_condition(condition),
        "sold_price_gbp": price_gbp,
        "original_price_gbp": orig_gbp if orig_gbp else None,
        "platform": "ebay_us",
        "sold_date": str(date_sold)[:10],
        "source": "nber_bargaining_data",
        "observed_at": _timestamp(),
        "_nber_meta": {
            "offer_count": raw.get("offer_count"),
            "had_counteroffer": raw.get("had_counteroffer", raw.get("counteroffer_count", 0)),
            "bargaining_sequence": raw.get("bargaining_sequence"),
        },
    }


# ---------------------------------------------------------------------------
# Seed all
# ---------------------------------------------------------------------------

def seed_all(coingecko_days: int = 365, kaggle_sample: int = 10000) -> dict:
    """
    Run all seed collectors and report results.
    """
    print("=" * 60)
    print("Breadup Historical Seed - Starting all collectors")
    print("=" * 60)

    all_results = {"started_at": _timestamp(), "collectors": {}}

    # 1. CoinGecko reference prices
    print("\n[1/3] CoinGecko reference prices...")
    try:
        all_results["collectors"]["coingecko"] = seed_coingecko_reference(days=coingecko_days)
    except Exception as e:
        all_results["collectors"]["coingecko"] = {"error": str(e)}
        print(f"  CoinGecko error: {e}")

    # 2. Kaggle datasets (if already downloaded)
    print("\n[2/3] Kaggle eBay data...")
    kaggle_dir = str(FOREST_DIR / "kaggle_raw" / "ebay-product-listing-dataset")
    try:
        kaggle_items = load_kaggle_data(kaggle_dir, sample_size=kaggle_sample)
        if kaggle_items:
            fp = FOREST_DIR / "kaggle_ebay_canonical.jsonl"
            n = _write_jsonl(kaggle_items, fp)
            all_results["collectors"]["kaggle"] = {
                "items_loaded": n,
                "file": str(fp),
            }
        else:
            all_results["collectors"]["kaggle"] = {
                "items_loaded": 0,
                "note": "No data found. Run --download-kaggle first.",
            }
    except Exception as e:
        all_results["collectors"]["kaggle"] = {"error": str(e)}
        print(f"  Kaggle error: {e}")

    # 3. NBER data (if already downloaded)
    print("\n[3/3] NBER bargaining data...")
    nber_dir = FOREST_DIR / "nber_raw"
    nber_files = list(nber_dir.glob("*.csv")) + list(nber_dir.glob("*.tsv")) + list(nber_dir.glob("*.json"))
    try:
        if nber_files:
            nber_items = []
            for nfp in nber_files[:3]:
                if nfp.suffix == ".csv":
                    nber_items.extend(_load_csv_sample(nfp, 5000))
                elif nfp.suffix == ".json":
                    nber_items.extend(_load_json_sample(nfp, 5000))
            canonical_nber = [normalize_nber_item(item) for item in nber_items]
            fp = FOREST_DIR / "nber_bargaining_canonical.jsonl"
            n = _write_jsonl(canonical_nber, fp)
            all_results["collectors"]["nber"] = {
                "items_loaded": n,
                "file": str(fp),
            }
        else:
            all_results["collectors"]["nber"] = {
                "items_loaded": 0,
                "note": "No data found. Run --download-nber first.",
            }
    except Exception as e:
        all_results["collectors"]["nber"] = {"error": str(e)}
        print(f"  NBER error: {e}")

    # Summary
    all_results["finished_at"] = _timestamp()
    total = sum(
        c.get("items_loaded", c.get("total_records", 0))
        for c in all_results["collectors"].values()
        if isinstance(c, dict)
    )
    print(f"\n{'=' * 60}")
    print(f"Seed complete. Total canonical records: {total}")
    print(f"Saved to: {FOREST_DIR}")
    print(f"{'=' * 60}")

    # Write manifest
    manifest_path = FOREST_DIR / "_manifest.json"
    _ensure_dir(manifest_path.parent)
    with open(manifest_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Manifest written to {manifest_path}")

    return all_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_id(title: str, date: str) -> str:
    """Generate a short deterministic ID from title + date."""
    import hashlib
    combo = f"{title}_{date}"
    return hashlib.sha256(combo.encode()).hexdigest()[:16]


def _parse_price(val) -> float:
    """Parse a price value that might be string with currency symbols."""
    if isinstance(val, (int, float)):
        return float(val)
    if not val:
        return 0.0
    s = str(val).strip()
    s = s.replace("£", "").replace("$", "").replace("€", "").replace(",", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return 0.0


def _normalize_condition(raw: str) -> str:
    """Map raw condition strings to Breadup canonical condition."""
    s = raw.lower().strip() if raw else ""
    if any(w in s for w in ("new", "sealed", "bnib", "bnip")):
        return "new"
    if any(w in s for w in ("like new", "mint", "excellent")):
        return "used_like_new"
    if any(w in s for w in ("good", "very good")):
        return "used_good"
    if any(w in s for w in ("fair", "acceptable")):
        return "used_fair"
    if any(w in s for w in ("poor", "broken", "for parts")):
        return "used_poor"
    if any(w in s for w in ("refurbished", "renewed")):
        return "refurbished"
    return "used_unknown"


# Known brand patterns for extraction
_BRAND_PATTERNS = [
    "Apple", "Samsung", "Sony", "Canon", "Nikon", "Dell", "HP", "Lenovo",
    "Asus", "MSI", "LG", "Panasonic", "Bose", "Sennheiser", "JBL",
    "Nintendo", "Microsoft", "Xbox", "PlayStation", "Intel", "AMD",
    "NVIDIA", "GoPro", "DJI", "Garmin", "Fitbit", "Apple Watch",
    "Rolex", "Omega", "Casio", "Seiko", "Timex", "Fossil",
    "Nike", "Adidas", "Jordan", "New Balance", "Puma",
    "Dyson", "iRobot", "Shark",
]


def _extract_brand_model(title: str) -> tuple:
    """Try to extract brand and model from a product title."""
    brand = ""
    model = ""
    for b in _BRAND_PATTERNS:
        if b.lower() in title.lower():
            brand = b
            break
    if brand:
        # Try to get model: text after brand up to next delimiter
        idx = title.lower().find(brand.lower())
        after = title[idx + len(brand):].strip(" -–—|/,")
        parts = after.split()
        if parts:
            model = parts[0]
    return brand, model


def _guess_category(title: str) -> str:
    """Heuristic category from title keywords."""
    s = title.lower()
    if any(w in s for w in ("camera", "lens", "dslr", "mirrorless", "gopro")):
        return "cameras"
    if any(w in s for w in ("phone", "iphone", "galaxy", "pixel", "smartphone")):
        return "phones"
    if any(w in s for w in ("laptop", "macbook", "chromebook", "notebook", "thinkpad")):
        return "laptops"
    if any(w in s for w in ("ps5", "ps4", "xbox", "switch", "console", "gaming")):
        return "gaming_consoles"
    if any(w in s for w in ("headphone", "earphone", "earbuds", "airpods", "headset")):
        return "headphones"
    if any(w in s for w in ("watch", "smartwatch", "band")):
        return "watches"
    if any(w in s for w in ("shoe", "sneaker", "trainer", "boot")):
        return "shoes"
    return "general"


def _guess_subcategory(title: str) -> str:
    """Heuristic subcategory from title keywords."""
    s = title.lower()
    if "mirrorless" in s:
        return "mirrorless"
    if "dslr" in s:
        return "dslr"
    if "action cam" in s or "gopro" in s:
        return "action_cam"
    if "point and shoot" in s or "compact" in s:
        return "compact"
    if any(w in s for w in ("pro max", "pro ", "ultra")):
        return "flagship"
    if any(w in s for w in ("mini", "se ", "lite")):
        return "budget"
    return "standard"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Breadup Historical Data Collectors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m collectors.breadup_historical --seed-coingecko
  python -m collectors.breadup_historical --seed-soldcomps --queries "canon eos r6" "sony a7iii"
  python -m collectors.breadup_historical --download-kaggle
  python -m collectors.breadup_historical --download-nber
  python -m collectors.breadup_historical --seed-all
        """,
    )
    parser.add_argument(
        "--seed-coingecko",
        action="store_true",
        help="Fetch historical prices from CoinGecko",
    )
    parser.add_argument(
        "--seed-soldcomps",
        action="store_true",
        help="Seed from SoldComps free API",
    )
    parser.add_argument(
        "--queries",
        nargs="+",
        default=["canon eos r6", "sony a7iii", "iphone 14", "macbook pro", "nintendo switch"],
        help="Search queries for SoldComps",
    )
    parser.add_argument(
        "--download-kaggle",
        action="store_true",
        help="Download Kaggle eBay datasets",
    )
    parser.add_argument(
        "--load-kaggle",
        action="store_true",
        help="Load already-downloaded Kaggle data",
    )
    parser.add_argument(
        "--kaggle-dir",
        default=str(FOREST_DIR / "kaggle_raw" / "ebay-product-listing-dataset"),
        help="Path to downloaded Kaggle data",
    )
    parser.add_argument(
        "--download-nber",
        action="store_true",
        help="Download NBER bargaining dataset",
    )
    parser.add_argument(
        "--seed-all",
        action="store_true",
        help="Run all collectors",
    )
    parser.add_argument(
        "--coingecko-days",
        type=int,
        default=365,
        help="Days of CoinGecko history (default: 365)",
    )
    parser.add_argument(
        "--kaggle-sample",
        type=int,
        default=10000,
        help="Number of Kaggle items to sample (default: 10000)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(FOREST_DIR),
        help="Output directory",
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    _ensure_dir(output_dir)
    # Update module-level directory for all collectors
    globals()["FOREST_DIR"] = output_dir

    any_action = any([
        args.seed_coingecko,
        args.seed_soldcomps,
        args.download_kaggle,
        args.load_kaggle,
        args.download_nber,
        args.seed_all,
    ])

    if not any_action:
        parser.print_help()
        return

    if args.seed_all:
        results = seed_all(
            coingecko_days=args.coingecko_days,
            kaggle_sample=args.kaggle_sample,
        )
        print(json.dumps(results, indent=2))
        return

    if args.seed_coingecko:
        print("--- CoinGecko Reference Prices ---")
        r = seed_coingecko_reference(days=args.coingecko_days)
        print(json.dumps(r, indent=2))

    if args.seed_soldcomps:
        print("--- SoldComps API Seed ---")
        r = seed_from_soldcomps(args.queries)
        print(json.dumps(r, indent=2))

    if args.download_kaggle:
        print("--- Kaggle Dataset Download ---")
        r = download_kaggle_datasets()
        print(json.dumps(r, indent=2))

    if args.load_kaggle:
        print("--- Kaggle Data Load ---")
        items = load_kaggle_data(args.kaggle_dir, sample_size=args.kaggle_sample)
        if items:
            fp = FOREST_DIR / "kaggle_ebay_canonical.jsonl"
            n = _write_jsonl(items, fp)
            print(f"Wrote {n} items to {fp}")

    if args.download_nber:
        print("--- NBER Bargaining Data Download ---")
        r = download_nber_data()
        print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
