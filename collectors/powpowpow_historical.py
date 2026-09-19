#!/usr/bin/env python3
"""
PowPowPow Historical Data Collectors

Seeds the PowPowPow garden with historical mining economics data.

Sources:
1. CoinGecko - Price/market history for all mineable coins
2. Minerstat - GPU/ASIC hardware benchmarks (10,730+ entries)
3. WhatToMine - Network difficulty/hashrate/profitability
4. Open Bitcoin Metrics - Full-node verified Bitcoin history
5. Existing powpowpow chain data - 17 chains already tracked
"""

import json
import os
import sys
import time
import argparse
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = '/home/box/datagarden'
FOREST_DIR = os.path.join(BASE_DIR, 'forests', 'powpowpow', 'data', 'historical')
POWPOWPOW_CHAINS = os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow') + '/chains'

# ---------------------------------------------------------------------------
# Imports from existing powpowpow modules (best-effort)
# ---------------------------------------------------------------------------
try:
    sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
    from coins import COINS, get_all_symbols
    from v1_registry import V1, get_v1_symbols
except ImportError:
    COINS = {}
    V1 = {}

# All mineable symbols tracked by PowPowPow
ALL_SYMBOLS = list(COINS.keys()) if COINS else [
    'XMR', 'KAS', 'PRL', 'QUBIC', 'QUAN', 'XEL', 'XTM', 'NOCK',
    'GNK', 'TSC', 'NPT', 'QTC', 'TAO', 'QRL', 'ZEPH', 'ALPH',
    'ERG', 'AKT', 'PHA', 'LA', 'TIG', 'MCM',
]

# Coins available on CoinGecko (CoinGecko id -> symbol mapping)
COINGECKO_IDS = {
    'monero': 'XMR', 'kaspa': 'KAS', 'bittensor': 'TAO',
    'ergo': 'ERG', 'alephium': 'ALPH', 'qrl': 'QRL',
    'akash-network': 'AKT', 'phala': 'PHA', 'theta-token': 'THETA',
    'flux-zcash': 'FLUX', 'zephyr-protocol': 'ZEPH',
    'mochimo': 'MCM',
    # SafeTrade coins may not be on CoinGecko; kept for completeness
    'pearl': 'PRL', 'qubic': 'QUBIC', 'nockchain': 'NOCK',
    'xelis': 'XEL', 'tari': 'XTM', 'gonka': 'GNK',
}

# Hardware benchmark device list (for Minerstat / WhatToMine)
BENCHMARK_DEVICES = [
    'RTX_4090', 'RTX_4080', 'RTX_4070_Ti', 'RTX_4070',
    'RTX_3090', 'RTX_3080', 'RTX_3070', 'RTX_3060',
    'RX_7900_XTX', 'RX_7900_XT', 'RX_7800_XT', 'RX_6800_XT',
    'H100', 'H200', 'A100', 'A6000',
    'KS5_Pro', 'KS5_L', 'KS3_L',
    'Ryzen_9_7950X', 'Ryzen_7_7800X3D', 'EPYC_7763',
]

# Rate-limit sleeps (seconds)
COINGECKO_SLEEP = 4    # free tier ~10-30 calls/min
MINERSTAT_SLEEP = 2
WHATTO_SLEEP = 3

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def _ts_from_ms(ms: float) -> str:
    """Convert millisecond epoch to ISO string."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _fetch_json(url: str, params: dict = None, headers: dict = None,
                timeout: int = 30) -> Optional[dict]:
    """GET JSON with error handling. Returns None on failure."""
    hdrs = {'User-Agent': 'PowPowPow-DataGarden/1.0', 'Accept': 'application/json'}
    if headers:
        hdrs.update(headers)
    try:
        r = requests.get(url, params=params, headers=hdrs, timeout=timeout)
        if r.status_code == 429:
            retry = int(r.headers.get('Retry-After', 60))
            print(f"  [429] Rate limited. Sleeping {retry}s...")
            time.sleep(retry)
            r = requests.get(url, params=params, headers=hdrs, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"  [ERR] {url}: {e}")
        return None


def _fetch_text(url: str, timeout: int = 30) -> Optional[str]:
    """GET text (for HTML scraping). Returns None on failure."""
    try:
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; PowPowPowBot/1.0)',
        }, timeout=timeout)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"  [ERR] {url}: {e}")
        return None


def _write_jsonl(path: str, records: list):
    """Append a list of dicts as JSONL."""
    _ensure_dir(os.path.dirname(path))
    with open(path, 'a') as f:
        for rec in records:
            f.write(json.dumps(rec, default=str) + '\n')


def _load_jsonl(path: str) -> list:
    """Load a JSONL file into a list of dicts."""
    if not os.path.exists(path):
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _copy_to_chains(symbol: str, filename: str, records: list):
    """Copy records into the existing powpowpow/chains/<SYM>/ directory."""
    chain_dir = os.path.join(POWPOWPOW_CHAINS, symbol.upper())
    if not os.path.isdir(chain_dir):
        return
    events_dir = os.path.join(chain_dir, 'events')
    _ensure_dir(events_dir)
    dest = os.path.join(events_dir, filename)
    _write_jsonl(dest, records)


# ===================================================================
# 1. CoinGecko Collectors
# ===================================================================

def collect_coingecko_history(coin_id: str, days: int = 365) -> dict:
    """Fetch price/market history from CoinGecko.

    Returns raw API response with keys: prices, market_caps, total_volumes.
    Each entry is [timestamp_ms, value].
    """
    print(f"  [CoinGecko] Fetching {coin_id} ({days}d)...")
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
    data = _fetch_json(url, params={'vs_currency': 'usd', 'days': str(days)})
    if data:
        print(f"    prices={len(data.get('prices', []))}, "
              f"volumes={len(data.get('total_volumes', []))}")
    time.sleep(COINGECKO_SLEEP)
    return data or {}


def collect_coingecko_all_mineable() -> dict:
    """Fetch history for all tracked mineable coins on CoinGecko."""
    print("\n[CoinGecko] All mineable coins")
    results = {}
    for cg_id, symbol in COINGECKO_IDS.items():
        raw = collect_coingecko_history(cg_id, days=365)
        if raw:
            results[symbol] = {'coin_id': cg_id, 'raw': raw}
    return results


def normalize_coingecko_history(coin_id: str, raw: dict) -> list:
    """Normalize CoinGecko history into canonical PowPowPow price records.

    Returns a list of dicts matching the price history schema.
    """
    symbol = COINGECKO_IDS.get(coin_id, coin_id.upper())
    now = _now_iso()
    records = []

    prices = raw.get('prices', [])
    vols = raw.get('total_volumes', [])
    caps = raw.get('market_caps', [])

    vol_map = {}
    for ts_ms, val in vols:
        day = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
        vol_map[day] = val

    cap_map = {}
    for ts_ms, val in caps:
        day = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
        cap_map[day] = val

    for ts_ms, price in prices:
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        day = dt.strftime('%Y-%m-%d')
        records.append({
            'symbol': symbol,
            'timestamp': dt.isoformat(),
            'price_usd': price,
            'market_cap': cap_map.get(day),
            'volume_24h': vol_map.get(day),
            'source': 'coingecko',
            'observed_at': now,
        })

    return records


# ===================================================================
# 2. Minerstat Collectors
# ===================================================================

def collect_minerstat_benchmarks() -> dict:
    """Fetch GPU/ASIC benchmarks from Minerstat (all hardware).

    Returns raw response keyed by device name.
    """
    print("\n[Minerstat] Hardware benchmarks")
    results = {}

    # Try the public hardware listing endpoint
    url = 'https://api.minerstat.com/v2/hardware'
    data = _fetch_json(url)
    if data:
        print(f"    Got {len(data) if isinstance(data, (dict, list)) else '?'} entries")
        results['all'] = data
    time.sleep(MINERSTAT_SLEEP)

    # Also try the coins/algorithm listing
    url2 = 'https://api.minerstat.com/v2/coins'
    data2 = _fetch_json(url2)
    if data2:
        results['coins'] = data2
    time.sleep(MINERSTAT_SLEEP)

    return results


def collect_minerstat_device(device_name: str) -> dict:
    """Fetch specific device benchmarks from Minerstat.

    device_name should match the Minerstat naming (e.g. 'RTX-4090', 'H100').
    """
    print(f"  [Minerstat] Device: {device_name}")
    # Normalize name for API (replace underscores with dashes)
    api_name = device_name.replace('_', '-')
    url = f'https://api.minerstat.com/v2/hardware/{api_name}'
    data = _fetch_json(url)
    if data:
        print(f"    Got benchmark data for {device_name}")
    time.sleep(MINERSTAT_SLEEP)
    return data or {}


def normalize_minerstat_device(raw: dict) -> dict:
    """Normalize a Minerstat device benchmark into canonical form.

    The raw response contains algorithm -> {hashrate, power, ...} mappings.
    Returns a dict keyed by algorithm name with normalized records.
    """
    now = _now_iso()
    normalized = {}

    if not isinstance(raw, dict):
        return normalized

    device_name = raw.get('name', raw.get('device', 'unknown'))
    # Clean device name
    device_name = device_name.replace('-', '_').replace(' ', '_')

    for algo, specs in raw.items():
        if isinstance(specs, dict) and 'hashrate' in specs:
            hashrate = specs.get('hashrate', 0)
            power = specs.get('power', specs.get('power_draw', 0))
            cost = specs.get('price', specs.get('cost', 0))

            efficiency = 0
            if power and power > 0:
                efficiency = round(hashrate / power, 2)

            normalized[algo] = {
                'device': device_name,
                'algorithm': algo,
                'hashrate': hashrate,
                'hashrate_unit': specs.get('hashrate_unit', 'H/s'),
                'power_watts': power,
                'cost_usd': cost,
                'efficiency': efficiency,
                'source': 'minerstat',
                'observed_at': now,
            }

    return normalized


# ===================================================================
# 3. WhatToMine Collectors
# ===================================================================

def collect_what_to_mine_networks() -> dict:
    """Scrape WhatToMine for network stats across all mineable coins.

    Uses the whattomine.com main page which embeds JSON data.
    """
    print("\n[WhatToMine] Network stats")
    text = _fetch_text('https://whattomine.com')
    if not text:
        return {}

    # WhatToMine embeds coin data in JavaScript; try to extract JSON blocks
    results = {}
    import re

    # Look for coin data in script tags
    pattern = r'var\s+(\w+)\s*=\s*(\{[^}]+\})'
    matches = re.findall(pattern, text)
    for name, blob in matches:
        try:
            # Clean up JS object syntax
            cleaned = blob.replace("'", '"')
            data = json.loads(cleaned)
            results[name.upper()] = data
        except (json.JSONDecodeError, ValueError):
            pass

    # Also look for the coins JSON data structure
    json_pattern = r'"coins"\s*:\s*(\[.*?\])'
    json_matches = re.findall(json_pattern, text, re.DOTALL)
    for match in json_matches[:1]:
        try:
            coins_list = json.loads(match.replace("'", '"'))
            for coin in coins_list:
                if isinstance(coin, dict):
                    tag = coin.get('tag', '').upper()
                    if tag:
                        results[tag] = coin
        except (json.JSONDecodeError, ValueError):
            pass

    print(f"    Found {len(results)} coin entries")
    return results


def collect_what_to_mine_coin(tag: str) -> dict:
    """Scrape WhatToMine for a specific coin's detailed data.

    tag should be the WhatToMine coin ticker (e.g. 'XMR', 'KAS').
    """
    print(f"  [WhatToMine] Coin: {tag}")
    url = f'https://whattomine.com/coins/{tag.lower()}'
    text = _fetch_text(url)
    if not text:
        return {}

    import re
    result = {}

    # Extract key metrics from the page
    patterns = {
        'difficulty': r'difficulty["\s:]+([\d.]+[eE]?[\d]*)',
        'hashrate': r'hashrate["\s:]+([\d.]+[eE]?[\d]*)',
        'block_reward': r'block.?reward["\s:]+([\d.]+)',
        'block_time': r'block.?time["\s:]+([\d.]+)',
        'daily_revenue': r'daily.?revenue["\s:]+([\d.]+)',
        'profitability': r'profitability["\s:]+([\d.]+)',
    }

    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                result[key] = float(m.group(1))
            except ValueError:
                pass

    time.sleep(WHATTO_SLEEP)
    return result


def normalize_what_to_mine_coin(tag: str, raw: dict) -> dict:
    """Normalize WhatToMine data into canonical network stats form."""
    now = _now_iso()

    record = {
        'symbol': tag.upper(),
        'timestamp': _today_str() + 'T00:00:00+00:00',
        'hashrate': raw.get('hashrate'),
        'difficulty': raw.get('difficulty'),
        'block_reward': raw.get('block_reward'),
        'block_time': raw.get('block_time'),
        'daily_revenue_usd': raw.get('daily_revenue'),
        'profitability': raw.get('profitability'),
        'source': 'what_to_mine',
        'observed_at': now,
    }

    return record


# ===================================================================
# 4. Open Bitcoin Metrics
# ===================================================================

def collect_open_bitcoin_metrics() -> dict:
    """Fetch Bitcoin full-node derived metrics.

    Tries the open-bitcoin-metrics GitHub repository and mirrors.
    Falls back to blockchair.com free API for Bitcoin-specific data.
    """
    print("\n[Open Bitcoin Metrics]")

    results = {}

    # Try blockchair free API for Bitcoin stats
    url = 'https://api.blockchair.com/bitcoin/stats'
    data = _fetch_json(url)
    if data and 'data' in data:
        stats = data['data']
        results['bitcoin_stats'] = {
            'blocks': stats.get('blocks'),
            'transactions': stats.get('transactions'),
            'outputs': stats.get('outputs'),
            'circulation': stats.get('circulation'),
            'blockchain_size': stats.get('blockchain_size'),
            'nodes': stats.get('nodes'),
            'difficulty': stats.get('difficulty'),
            'hashrate_24h': stats.get('hashrate_24h'),
            'next_retarget_time_estimate': stats.get('next_retarget_time_estimate'),
            'next_difficulty_estimate': stats.get('next_difficulty_estimate'),
            'mempool_transactions': stats.get('mempool_transactions'),
            'mempool_size': stats.get('mempool_size'),
            'mempool_tps': stats.get('mempool_tps'),
            'average_transaction_fee_24h': stats.get('average_transaction_fee_24h'),
            'median_transaction_fee_24h': stats.get('median_transaction_fee_24h'),
            'market_price_usd': stats.get('market_price_usd'),
            'market_cap_usd': stats.get('market_cap_usd'),
            'market_dominance_percentage': stats.get('market_dominance_percentage'),
        }
        print(f"    Got Bitcoin stats from Blockchair")

    time.sleep(2)

    # Also try to get recent difficulty adjustments
    url2 = 'https://api.blockchair.com/bitcoin/blocks?s=id(desc)&limit=10'
    data2 = _fetch_json(url2)
    if data2 and 'data' in data2:
        blocks = data2['data']
        if isinstance(blocks, list):
            results['recent_blocks'] = []
            for b in blocks:
                results['recent_blocks'].append({
                    'height': b.get('id'),
                    'timestamp': b.get('time'),
                    'difficulty': b.get('difficulty'),
                    'size': b.get('size'),
                    'transaction_count': b.get('transaction_count'),
                    'output_total': b.get('output_total'),
                    'fee_total': b.get('fee_total'),
                })
            print(f"    Got {len(blocks)} recent Bitcoin blocks")

    time.sleep(2)

    return results


# ===================================================================
# 5. Reconstruct Historical Profitability
# ===================================================================

def reconstruct_historical_profitability(coin: str, hardware: str,
                                         start_date: str, end_date: str) -> dict:
    """Reconstruct historical mining profitability by combining:

    - CoinGecko price history
    - WhatToMine / existing difficulty/hashrate data
    - Minerstat / v1_live_cards hardware benchmarks

    Parameters:
        coin: e.g. 'XMR', 'KAS'
        hardware: e.g. 'RTX_4090', 'H100', 'KS5_Pro'
        start_date: 'YYYY-MM-DD'
        end_date: 'YYYY-MM-DD'

    Returns dict with 'daily' list of reconstructed profitability records.
    """
    print(f"\n[Reconstruct] {coin} / {hardware} / {start_date} -> {end_date}")
    now = _now_iso()

    # 1. Load price history
    price_records = _load_coin_prices(coin)
    price_by_date = {}
    for rec in price_records:
        day = rec['timestamp'][:10]
        price_by_date[day] = rec.get('price_usd', 0)

    # 2. Load hardware benchmark
    hw_specs = _load_hardware_benchmark(hardware)

    # 3. Load network difficulty history
    network_records = _load_network_history(coin)
    diff_by_date = {}
    hr_by_date = {}
    reward_by_date = {}
    for rec in network_records:
        day = rec['timestamp'][:10]
        if rec.get('difficulty'):
            diff_by_date[day] = rec['difficulty']
        if rec.get('hashrate'):
            hr_by_date[day] = rec['hashrate']
        if rec.get('block_reward'):
            reward_by_date[day] = rec['block_reward']

    # 4. Build daily profitability
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    daily = []

    current = start
    while current <= end:
        day = current.strftime('%Y-%m-%d')

        price = price_by_date.get(day, 0)
        difficulty = diff_by_date.get(day)
        hashrate_net = hr_by_date.get(day)
        block_reward = reward_by_date.get(day)

        hw_hashrate = hw_specs.get('hashrate', 0)
        hw_power = hw_specs.get('power_watts', 0)
        electricity_rate = 0.10  # $/kWh default

        # Calculate daily electricity cost
        electricity_usd_day = (hw_power / 1000) * 24 * electricity_rate

        # Estimate revenue
        revenue_usd_day = 0
        if hw_hashrate and hashrate_net and hashrate_net > 0 and price:
            # Share of network
            share = hw_hashrate / hashrate_net
            # Daily block rewards
            blocks_per_day = 86400 / (hw_specs.get('block_time', 120) or 120)
            daily_emission = (block_reward or 0) * blocks_per_day
            revenue_usd_day = share * daily_emission * price

        # HW depreciation (3-year)
        hw_cost = hw_specs.get('cost_usd', 0)
        hw_amort_day = hw_cost / (3 * 365) if hw_cost else 0

        net = revenue_usd_day - electricity_usd_day - hw_amort_day

        daily.append({
            'symbol': coin.upper(),
            'device': hardware,
            'date': day,
            'price_usd': round(price, 6) if price else None,
            'difficulty': difficulty,
            'hashrate_network': hashrate_net,
            'block_reward': block_reward,
            'hashrate_hw': hw_hashrate,
            'power_watts': hw_power,
            'revenue_usd_day': round(revenue_usd_day, 6),
            'electricity_usd_day': round(electricity_usd_day, 4),
            'hw_amort_usd_day': round(hw_amort_day, 4),
            'net_profit_usd_day': round(net, 6),
            'source': 'reconstructed',
            'observed_at': now,
        })

        current += timedelta(days=1)

    return {'coin': coin, 'hardware': hardware, 'daily': daily}


def _load_coin_prices(symbol: str) -> list:
    """Load previously collected CoinGecko prices for a symbol."""
    path = os.path.join(FOREST_DIR, 'coingecko', f'{symbol.upper()}_price_history.jsonl')
    return _load_jsonl(path)


def _load_hardware_benchmark(device: str) -> dict:
    """Load hardware benchmark data for a device."""
    # Check v1_live_cards first
    if V1:
        for chain_bench in V1.values():
            if device in chain_bench:
                return chain_bench[device]

    # Check collected benchmark files
    path = os.path.join(FOREST_DIR, 'minerstat', f'{device}_benchmarks.jsonl')
    records = _load_jsonl(path)
    if records:
        return records[0]

    # Fallback defaults
    return {
        'hashrate': 0, 'power_watts': 0, 'cost_usd': 0,
        'algo': 'unknown', 'block_time': 120,
    }


def _load_network_history(symbol: str) -> list:
    """Load previously collected network stats for a symbol."""
    path = os.path.join(FOREST_DIR, 'what_to_mine', f'{symbol.upper()}_network.jsonl')
    records = _load_jsonl(path)
    if records:
        return records

    # Fallback: check powpowpow chains
    chain_path = os.path.join(POWPOWPOW_CHAINS, symbol.upper(), 'events')
    if os.path.isdir(chain_path):
        for fname in sorted(os.listdir(chain_path)):
            if fname.endswith('.jsonl'):
                records.extend(_load_jsonl(os.path.join(chain_path, fname)))

    return records


# ===================================================================
# Seed Orchestrator
# ===================================================================

def seed_coingecko() -> dict:
    """Seed all CoinGecko data."""
    print(f"\n{'='*60}")
    print("Seeding CoinGecko Historical Data")
    print(f"{'='*60}")

    all_results = collect_coingecko_all_mineable()
    out_dir = os.path.join(FOREST_DIR, 'coingecko')
    _ensure_dir(out_dir)

    saved = 0
    for symbol, payload in all_results.items():
        cg_id = payload.get('coin_id', '')
        raw = payload.get('raw', {})
        records = normalize_coingecko_history(cg_id, raw)
        if records:
            path = os.path.join(out_dir, f'{symbol}_price_history.jsonl')
            _write_jsonl(path, records)
            _copy_to_chains(symbol, f'price_history_coingecko.jsonl', records)
            saved += len(records)
            print(f"  [OK] {symbol}: {len(records)} records")

    print(f"\n  Total: {saved} price records")
    return {'source': 'coingecko', 'records': saved}


def seed_minerstat() -> dict:
    """Seed all Minerstat benchmark data."""
    print(f"\n{'='*60}")
    print("Seeding Minerstat Hardware Benchmarks")
    print(f"{'='*60}")

    all_benchmarks = collect_minerstat_benchmarks()
    out_dir = os.path.join(FOREST_DIR, 'minerstat')
    _ensure_dir(out_dir)

    saved = 0

    # Process all hardware data
    raw_all = all_benchmarks.get('all', {})
    if isinstance(raw_all, dict):
        for device_name, device_data in raw_all.items():
            if isinstance(device_data, dict):
                normalized = normalize_minerstat_device(device_data)
                if normalized:
                    path = os.path.join(out_dir, f'{device_name}_benchmarks.jsonl')
                    records = list(normalized.values())
                    _write_jsonl(path, records)
                    saved += len(records)

    # Also fetch individual devices we care about
    for device in BENCHMARK_DEVICES:
        data = collect_minerstat_device(device)
        if data:
            normalized = normalize_minerstat_device(data)
            if normalized:
                path = os.path.join(out_dir, f'{device}_benchmarks.jsonl')
                records = list(normalized.values())
                _write_jsonl(path, records)
                saved += len(records)
                print(f"  [OK] {device}: {len(records)} algo benchmarks")

    print(f"\n  Total: {saved} benchmark records")
    return {'source': 'minerstat', 'records': saved}


def seed_what_to_mine() -> dict:
    """Seed WhatToMine network data."""
    print(f"\n{'='*60}")
    print("Seeding WhatToMine Network Data")
    print(f"{'='*60}")

    networks = collect_what_to_mine_networks()
    out_dir = os.path.join(FOREST_DIR, 'what_to_mine')
    _ensure_dir(out_dir)

    saved = 0

    # Normalize coins we found
    mineable_tags = ['XMR', 'KAS', 'ERG', 'ALPH', 'QRL', 'FLUX',
                     'ZEPH', 'RVN', 'ETC', 'CFX', 'BCH', 'LTC',
                     'DOGE', 'DASH', 'SC', 'DCR']

    for tag in mineable_tags:
        # Try from scraped data
        raw = networks.get(tag, {})
        if raw:
            record = normalize_what_to_mine_coin(tag, raw)
            path = os.path.join(out_dir, f'{tag}_network.jsonl')
            _write_jsonl(path, [record])
            _copy_to_chains(tag, 'network_what_to_mine.jsonl', [record])
            saved += 1
            print(f"  [OK] {tag}")

        # Also try the dedicated endpoint
        detail = collect_what_to_mine_coin(tag)
        if detail:
            record = normalize_what_to_mine_coin(tag, detail)
            path = os.path.join(out_dir, f'{tag}_network.jsonl')
            _write_jsonl(path, [record])
            _copy_to_chains(tag, 'network_what_to_mine.jsonl', [record])
            saved += 1

    print(f"\n  Total: {saved} network records")
    return {'source': 'what_to_mine', 'records': saved}


def seed_bitcoin_metrics() -> dict:
    """Seed Bitcoin metrics from Open Bitcoin Metrics / Blockchair."""
    print(f"\n{'='*60}")
    print("Seeding Bitcoin Metrics")
    print(f"{'='*60}")

    data = collect_open_bitcoin_metrics()
    out_dir = os.path.join(FOREST_DIR, 'bitcoin_metrics')
    _ensure_dir(out_dir)

    saved = 0

    if data.get('bitcoin_stats'):
        path = os.path.join(out_dir, 'bitcoin_stats.json')
        with open(path, 'w') as f:
            json.dump(data['bitcoin_stats'], f, indent=2)
        saved += 1
        print(f"  [OK] Bitcoin stats saved")

        # Also create a BTC price history record if available
        stats = data['bitcoin_stats']
        if stats.get('market_price_usd'):
            btc_record = {
                'symbol': 'BTC',
                'timestamp': _now_iso(),
                'price_usd': stats['market_price_usd'],
                'market_cap': stats.get('market_cap_usd'),
                'difficulty': stats.get('difficulty'),
                'hashrate': stats.get('hashrate_24h'),
                'source': 'blockchair',
                'observed_at': _now_iso(),
            }
            btc_dir = os.path.join(FOREST_DIR, 'coingecko')
            _ensure_dir(btc_dir)
            _write_jsonl(os.path.join(btc_dir, 'BTC_price_history.jsonl'), [btc_record])
            saved += 1

    if data.get('recent_blocks'):
        path = os.path.join(out_dir, 'recent_blocks.jsonl')
        _write_jsonl(path, data['recent_blocks'])
        saved += len(data['recent_blocks'])
        print(f"  [OK] {len(data['recent_blocks'])} recent blocks")

    print(f"\n  Total: {saved} records")
    return {'source': 'bitcoin_metrics', 'records': saved}


def seed_profitability_reconstruction() -> dict:
    """Reconstruct historical profitability for key coin/hardware combos."""
    print(f"\n{'='*60}")
    print("Reconstructing Historical Profitability")
    print(f"{'='*60}")

    combos = [
        ('XMR', 'Ryzen_9_7950X'),
        ('XMR', 'Ryzen_7_7800X3D'),
        ('KAS', 'KS5_Pro'),
        ('KAS', 'KS3_L'),
        ('PRL', 'RTX_4090'),
        ('PRL', 'H100'),
        ('QUAN', 'RTX_4090'),
        ('ERG', 'RTX_4090'),
        ('ALPH', 'RTX_4090'),
        ('FLUX', 'RTX_4090'),
    ]

    out_dir = os.path.join(FOREST_DIR, 'profitability')
    _ensure_dir(out_dir)

    end = _today_str()
    start = (datetime.now(timezone.utc) - timedelta(days=365)).strftime('%Y-%m-%d')

    saved = 0
    for coin, hw in combos:
        result = reconstruct_historical_profitability(coin, hw, start, end)
        daily = result.get('daily', [])
        if daily:
            path = os.path.join(out_dir, f'{coin}_{hw}_profitability.jsonl')
            _write_jsonl(path, daily)
            _copy_to_chains(coin, f'profitability_{hw}.jsonl', daily)
            saved += len(daily)
            print(f"  [OK] {coin}/{hw}: {len(daily)} days")

    print(f"\n  Total: {saved} profitability records")
    return {'source': 'reconstructed', 'records': saved}


def seed_all() -> dict:
    """Run all seed collectors."""
    print(f"\n{'#'*60}")
    print(f"  PowPowPow Historical Data Seeding")
    print(f"  Started: {_now_iso()}")
    print(f"{'#'*60}")

    _ensure_dir(FOREST_DIR)

    results = {}
    results['coingecko'] = seed_coingecko()
    results['minerstat'] = seed_minerstat()
    results['what_to_mine'] = seed_what_to_mine()
    results['bitcoin_metrics'] = seed_bitcoin_metrics()
    results['profitability'] = seed_profitability_reconstruction()

    # Summary
    total = sum(r.get('records', 0) for r in results.values())
    print(f"\n{'#'*60}")
    print(f"  Seeding Complete")
    print(f"  Total records: {total}")
    print(f"  Finished: {_now_iso()}")
    print(f"{'#'*60}")

    # Save manifest
    manifest = {
        'seeded_at': _now_iso(),
        'total_records': total,
        'sources': results,
    }
    manifest_path = os.path.join(FOREST_DIR, 'seed_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"  Manifest: {manifest_path}")

    return results


# ===================================================================
# CLI
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description='PowPowPow Historical Data Collectors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m collectors.powpowpow_historical --seed-coingecko
  python -m collectors.powpowpow_historical --seed-minerstat
  python -m collectors.powpowpow_historical --seed-what-to-mine
  python -m collectors.powpowpow_historical --seed-bitcoin
  python -m collectors.powpowpow_historical --seed-profitability
  python -m collectors.powpowpow_historical --seed-all
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--seed-coingecko', action='store_true',
                       help='Seed CoinGecko price/market history')
    group.add_argument('--seed-minerstat', action='store_true',
                       help='Seed Minerstat hardware benchmarks')
    group.add_argument('--seed-what-to-mine', action='store_true',
                       help='Seed WhatToMine network stats')
    group.add_argument('--seed-bitcoin', action='store_true',
                       help='Seed Bitcoin metrics')
    group.add_argument('--seed-profitability', action='store_true',
                       help='Reconstruct historical profitability')
    group.add_argument('--seed-all', action='store_true',
                       help='Run all seed collectors')

    args = parser.parse_args()

    if args.seed_all:
        seed_all()
    elif args.seed_coingecko:
        seed_coingecko()
    elif args.seed_minerstat:
        seed_minerstat()
    elif args.seed_what_to_mine:
        seed_what_to_mine()
    elif args.seed_bitcoin:
        seed_bitcoin_metrics()
    elif args.seed_profitability:
        seed_profitability_reconstruction()


if __name__ == '__main__':
    main()
