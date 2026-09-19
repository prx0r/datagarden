#!/usr/bin/env python3
"""
Breadup MCP Server — Physical Goods Value Engine

Tools:
- value_listing: "Is this actually a bargain?"
- find_flips: "What could I flip this weekend?"
- max_offer: "What should I offer?"
- cheapest_source: "Where's the cheapest place to buy this?"
- liquidity_score: "How fast does this sell?"
- depreciation_forecast: "What's this worth in 6 months?"
- price_history: "How have prices changed?"
- repair_vs_sell: "Should I fix it or sell as-is?"
- part_out_economics: "Should I part this out?"
- best_categories: "Which categories have the best margins?"

Usage:
    python breadup_mcp.py                     # List tools
    python breadup_mcp.py <tool> '<json>'     # Call tool
    python breadup_mcp.py --serve             # MCP stdio server
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, date
import requests

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'breadup' / 'data' / 'ebay_sold'
sys.path.insert(0, str(ROOT))

# ============================================================
# TOOLS
# ============================================================

TOOLS = [
    {
        "name": "value_listing",
        "description": "Is this listing actually a bargain? Cross-references asking price against market data. Returns verdict: BARGAIN / FAIR / OVERPRICED with suggested offer.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name (e.g. 'Roland SP-404', 'technics turntable')"},
                "asking_price": {"type": "number", "description": "Asking price in GBP"},
                "platform": {"type": "string", "description": "Platform (facebook, ebay, gumtree, vinted)"}
            },
            "required": ["item", "asking_price"]
        }
    },
    {
        "name": "find_flips",
        "description": "What stuff could I flip this weekend? Returns items with the largest price gaps between asking and market value.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Category (electronics, audio, cameras, bikes)"},
                "budget": {"type": "number", "description": "Max spend in GBP"},
                "limit": {"type": "integer", "description": "Max results (default 10)"}
            }
        }
    },
    {
        "name": "max_offer",
        "description": "What should I offer this seller? Calculates the max offer that leaves a target profit margin.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"},
                "target_margin": {"type": "number", "description": "Target profit margin (default 0.25 = 25%)"}
            },
            "required": ["item"]
        }
    },
    {
        "name": "cheapest_source",
        "description": "Where's the cheapest place to buy this item? Compares prices across platforms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"}
            },
            "required": ["item"]
        }
    },
    {
        "name": "liquidity_score",
        "description": "How fast does this item sell? Returns sell-through rate and average days to sell.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"}
            },
            "required": ["item"]
        }
    },
    {
        "name": "price_history",
        "description": "How have prices for this item changed over time? Returns trend data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"},
                "days": {"type": "integer", "description": "Days of history (default 90)"}
            },
            "required": ["item"]
        }
    },
    {
        "name": "repair_vs_sell",
        "description": "Should I repair this item or sell it as-is? Compares repair cost to value uplift.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"},
                "fault": {"type": "string", "description": "What's wrong with it"},
                "repair_cost": {"type": "number", "description": "Estimated repair cost in GBP"}
            },
            "required": ["item", "fault"]
        }
    },
    {
        "name": "part_out_economics",
        "description": "Should I part this out or sell whole? Compares sum of parts to whole value.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"}
            },
            "required": ["item"]
        }
    },
    {
        "name": "best_categories",
        "description": "Which eBay categories have the best margins right now?",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_margin": {"type": "number", "description": "Minimum margin percentage (default 20)"}
            }
        }
    },
    {
        "name": "ebay_search",
        "description": "Search eBay UK sold listings via SoldComps API (free tier: 40 results per request).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
                "limit": {"type": "integer", "description": "Max results (default 40)"}
            },
            "required": ["query"]
        }
    },
]

# ============================================================
# IMPLEMENTATIONS
# ============================================================

def _load_sold_data(query: str = None, limit: int = 100) -> list:
    """Load sold data from local JSONL files."""
    if not DATA_DIR.exists():
        return []
    
    results = []
    for f in sorted(DATA_DIR.glob('*.jsonl'), reverse=True)[:7]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    if query:
                        title = item.get('title', '').lower()
                        if not any(w in title for w in query.lower().split()):
                            continue
                    results.append(item)
                    if len(results) >= limit:
                        return results
                except json.JSONDecodeError:
                    continue
    return results


def value_listing(item: str, asking_price: float, platform: str = 'facebook') -> dict:
    """Is this listing actually a bargain?"""
    sold = _load_sold_data(item)
    if not sold:
        return {
            'status': 'no_data',
            'item': item,
            'asking_price': asking_price,
            'message': f'No sold data for "{item}". Run: python -m collectors.ebay_free --query "{item}"'
        }
    
    prices = []
    for s in sold:
        p = s.get('soldPrice', s.get('sold_price', 0))
        if p and p > 0:
            prices.append(p)
    
    if not prices:
        return {'status': 'no_prices', 'item': item}
    
    prices.sort()
    n = len(prices)
    median = prices[n // 2]
    p25 = prices[n // 4]
    p75 = prices[3 * n // 4]
    
    below = asking_price < median
    gap_pct = ((median - asking_price) / median * 100) if below else ((asking_price - median) / median * 100)
    
    if below and gap_pct > 20:
        verdict = 'BARGAIN'
    elif below:
        verdict = 'SLIGHT_DEAL'
    elif gap_pct < 10:
        verdict = 'FAIR'
    else:
        verdict = 'OVERPRICED'
    
    suggested_offer = round(median * 0.85) if below else round(p25 * 0.90)
    
    return {
        'status': 'ok',
        'item': item,
        'asking_price': asking_price,
        'platform': platform,
        'market_median': median,
        'market_p25': p25,
        'market_p75': p75,
        'comparable_sales': n,
        'verdict': verdict,
        'savings_vs_median': f'{round(gap_pct, 1)}%' if below else f'-{round(gap_pct, 1)}%',
        'suggested_offer': suggested_offer,
        'why': f'Item sells for £{median} median (n={n}). You are being asked £{asking_price}.',
    }


def find_flips(category: str = None, budget: float = None, limit: int = 10) -> dict:
    """What stuff could I flip this weekend?"""
    sold = _load_sold_data(category, limit=500)
    
    items = {}
    for s in sold:
        title = s.get('title', '')
        price = s.get('soldPrice', s.get('sold_price', 0))
        if not price or price <= 0:
            continue
        
        key = title[:50].lower()
        if key not in items:
            items[key] = {'title': title, 'prices': [], 'count': 0}
        items[key]['prices'].append(price)
        items[key]['count'] += 1
    
    flips = []
    for key, data in items.items():
        if data['count'] < 2:
            continue
        prices = sorted(data['prices'])
        median = prices[len(prices) // 2]
        spread = prices[-1] - prices[0]
        margin_pct = (spread / median * 100) if median > 0 else 0
        
        if margin_pct > 15:
            flips.append({
                'title': data['title'],
                'median_price': median,
                'price_range': f'£{prices[0]} - £{prices[-1]}',
                'potential_margin_pct': round(margin_pct, 1),
                'sample_size': data['count'],
            })
    
    flips.sort(key=lambda x: x['potential_margin_pct'], reverse=True)
    return {
        'status': 'ok',
        'category': category,
        'flips': flips[:limit],
        'total_items_analyzed': len(items),
    }


def max_offer(item: str, target_margin: float = 0.25) -> dict:
    """What should I offer this seller?"""
    sold = _load_sold_data(item)
    prices = [s.get('soldPrice', s.get('sold_price', 0)) for s in sold if s.get('soldPrice') or s.get('sold_price')]
    prices = [p for p in prices if p > 0]
    
    if not prices:
        return {'status': 'no_data', 'item': item}
    
    median = sorted(prices)[len(prices) // 2]
    max_offer = round(median * (1 - target_margin))
    fast_sale = round(median * 0.80)
    
    return {
        'status': 'ok',
        'item': item,
        'market_median': median,
        'target_margin': f'{round(target_margin * 100)}%',
        'max_offer': max_offer,
        'fast_sale_offer': fast_sale,
        'buy_now_price': round(median * 1.1),
        'strategy': f'Offer £{max_offer} ({round(target_margin * 100)}% margin). For fast sale, offer £{fast_sale}.',
    }


def cheapest_source(item: str) -> dict:
    """Where's the cheapest place to buy this?"""
    return {
        'status': 'conceptual',
        'item': item,
        'message': 'Cross-platform comparison requires eBay + Vinted + Facebook collectors. Currently only eBay data available.',
        'available_platforms': ['ebay_uk'],
    }


def liquidity_score(item: str) -> dict:
    """How fast does this sell?"""
    sold = _load_sold_data(item)
    if not sold:
        return {'status': 'no_data', 'item': item}
    
    dates = []
    for s in sold:
        d = s.get('soldDate', s.get('collected_at', ''))
        if d:
            dates.append(d)
    
    return {
        'status': 'ok',
        'item': item,
        'total_sales': len(dates),
        'recent_sales_7d': len([d for d in dates if '2026-09' in d]),
        'liquidity': 'HIGH' if len(dates) > 10 else 'MEDIUM' if len(dates) > 3 else 'LOW',
        'note': 'Exact days-to-sell requires individual listing date tracking.',
    }


def price_history(item: str, days: int = 90) -> dict:
    """How have prices changed?"""
    if not DATA_DIR.exists():
        return {'status': 'no_data', 'item': item}
    
    history = []
    for f in sorted(DATA_DIR.glob('*.jsonl')):
        date_str = f.stem
        prices = []
        with open(f) as fh:
            for line in fh:
                try:
                    data = json.loads(line)
                    title = data.get('title', '').lower()
                    if any(w in title for w in item.lower().split()):
                        p = data.get('soldPrice', data.get('sold_price', 0))
                        if p and p > 0:
                            prices.append(p)
                except json.JSONDecodeError:
                    continue
        if prices:
            prices.sort()
            history.append({
                'date': date_str,
                'median': prices[len(prices) // 2],
                'min': min(prices),
                'max': max(prices),
                'count': len(prices),
            })
    
    trend = 'stable'
    if len(history) >= 2:
        first = history[0]['median']
        last = history[-1]['median']
        change_pct = ((last - first) / first * 100) if first > 0 else 0
        trend = 'rising' if change_pct > 5 else 'falling' if change_pct < -5 else 'stable'
    
    return {
        'status': 'ok',
        'item': item,
        'history': history,
        'trend': trend,
    }


def repair_vs_sell(item: str, fault: str, repair_cost: float = None) -> dict:
    """Should I repair it or sell as-is?"""
    sold = _load_sold_data(item)
    prices = [s.get('soldPrice', s.get('sold_price', 0)) for s in sold if s.get('soldPrice') or s.get('sold_price')]
    prices = [p for p in prices if p > 0]
    
    if not prices:
        return {'status': 'no_data', 'item': item}
    
    median = sorted(prices)[len(prices) // 2]
    
    # Estimated broken price = ~40-60% of working price depending on fault
    broken_multiplier = 0.4 if 'not working' in fault.lower() else 0.6
    broken_price = round(median * broken_multiplier)
    
    if repair_cost is None:
        # Estimate based on common faults
        fault_estimates = {
            'screen': 80, 'battery': 30, 'button': 20,
            'cosmetic': 0, 'software': 0, 'power': 50,
        }
        repair_cost = fault_estimates.get(fault.lower().split()[0], 40)
    
    repair_profit = median - repair_cost - broken_price
    
    return {
        'status': 'ok',
        'item': item,
        'fault': fault,
        'working_value': median,
        'broken_value': broken_price,
        'repair_cost': repair_cost,
        'repair_profit_uplift': repair_profit,
        'verdict': 'REPAIR' if repair_profit > 0 else 'SELL_AS_IS',
        'recommendation': f'Sell as-is for ~£{broken_price}' if repair_profit <= 0 else f'Repair for £{repair_cost}, sell for £{median}, net gain £{repair_profit}',
    }


def part_out_economics(item: str) -> dict:
    """Should I part this out or sell whole?"""
    sold = _load_sold_data(item)
    prices = [s.get('soldPrice', s.get('sold_price', 0)) for s in sold if s.get('soldPrice') or s.get('sold_price')]
    prices = [p for p in prices if p > 0]
    
    if not prices:
        return {'status': 'no_data', 'item': item}
    
    whole_value = sorted(prices)[len(prices) // 2]
    
    return {
        'status': 'ok',
        'item': item,
        'whole_value': whole_value,
        'message': 'Part-out economics requires per-part price data. General rule: if parts value > 1.5x whole value, part out.',
        'rule_of_thumb': 'Part out if: sum(parts_value) > whole_value * 1.3 (30% premium for hassle)',
    }


def best_categories(min_margin: float = 20) -> dict:
    """Which categories have the best margins?"""
    if not DATA_DIR.exists():
        return {'status': 'no_data'}
    
    categories = {}
    for f in sorted(DATA_DIR.glob('*.jsonl'), reverse=True)[:7]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    cat = item.get('category', item.get('keyword', 'unknown'))
                    price = item.get('soldPrice', item.get('sold_price', 0))
                    if cat and price and price > 0:
                        if cat not in categories:
                            categories[cat] = []
                        categories[cat].append(price)
                except json.JSONDecodeError:
                    continue
    
    results = []
    for cat, prices in categories.items():
        if len(prices) < 3:
            continue
        prices.sort()
        median = prices[len(prices) // 2]
        spread = prices[-1] - prices[0]
        margin = (spread / median * 100) if median > 0 else 0
        if margin >= min_margin:
            results.append({
                'category': cat,
                'median_price': round(median),
                'price_range': f'£{prices[0]} - £{prices[-1]}',
                'margin_pct': round(margin, 1),
                'sample_size': len(prices),
            })
    
    results.sort(key=lambda x: x['margin_pct'], reverse=True)
    return {
        'status': 'ok',
        'categories': results,
        'min_margin': min_margin,
    }


def ebay_search(query: str, limit: int = 40) -> dict:
    """Search eBay UK sold via SoldComps API."""
    # Try the free SoldComps API
    try:
        resp = requests.get(
            'https://api.sold-comps.com/v1/sold',
            params={
                'query': query,
                'site': 'EBAY_GB',
                'limit': min(limit, 40),
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                'status': 'ok',
                'query': query,
                'source': 'sold_comps_api',
                'results': data.get('results', [])[:limit],
                'count': data.get('count', 0),
            }
    except Exception:
        pass
    
    # Fallback to local data
    sold = _load_sold_data(query, limit)
    return {
        'status': 'local_only',
        'query': query,
        'results': sold[:limit],
        'message': 'SoldComps API unavailable. Using local data.',
    }


DISPATCH = {t['name']: globals()[t['name']] for t in TOOLS}

def handle_tool_call(name: str, args: dict) -> dict:
    func = DISPATCH.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except TypeError as e:
        return {"error": f"Invalid args: {e}"}


# ============================================================
# MCP STDIO SERVER
# ============================================================

def run_mcp_stdio():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        method = msg.get("method", "")
        msg_id = msg.get("id")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "breadup", "version": "1.0.0",
                                   "description": "Breadup — Physical goods value engine. Find deals, price items, detect mispricings."},
                },
            }
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = msg.get("params", {})
            result = handle_tool_call(params.get("name", ""), params.get("arguments", {}))
            response = {"jsonrpc": "2.0", "id": msg_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}}
        else:
            response = {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}}
        
        print(json.dumps(response), flush=True)


if __name__ == '__main__':
    if '--serve' in sys.argv:
        run_mcp_stdio()
    elif len(sys.argv) > 2:
        result = handle_tool_call(sys.argv[1], json.loads(sys.argv[2]))
        print(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps({"name": "breadup", "tools": [t["name"] for t in TOOLS]}, indent=2))
