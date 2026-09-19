#!/usr/bin/env python3
"""
Breadup MCP Server — Physical Goods Value Engine (PR5 Truth Contract)

Every tool returns:
{
    "capability": "breadup.<tool>",
    "as_of": "<ISO UTC>",
    "result": {...},
    "truth_class": "VERIFIED|DERIVED|ESTIMATED|HEURISTIC|UNAVAILABLE",
    "confidence": <0.0-1.0>,
    "evidence": [<observation_ids>],
    "method": {"id": "...", "version": "0.2.0"},
    "limitations": [...],
    "action": {"class": "ADVISORY|AUTO|APPROVAL_REQUIRED"}
}
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone, date
from statistics import median, quantiles

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'breadup' / 'data' / 'ebay_sold'
sys.path.insert(0, str(ROOT))

AS_OF = "2026-09-19T08:00:00Z"
METHOD_VERSION = "0.2.0"

# ============================================================
# PLATFORM FEE CONSTANTS
# ============================================================

PLATFORM_FEES = {
    'ebay': 0.128,
    'ebay_uk': 0.128,
    'vinted': 0.10,
    'facebook': 0.0,
    'gumtree': 0.0,
}

# ============================================================
# COMMON RESPONSE CONTRACT
# ============================================================

def _contract(capability: str, result: dict, truth_class: str,
              confidence: float, evidence: list, limitations: list,
              action_class: str = "ADVISORY") -> dict:
    return {
        "capability": capability,
        "as_of": AS_OF,
        "result": result,
        "truth_class": truth_class,
        "confidence": confidence,
        "evidence": evidence,
        "method": {"id": capability.split(".")[-1] if "." in capability else capability, "version": METHOD_VERSION},
        "limitations": limitations,
        "action": {"class": action_class},
    }


def _obs_id(item: str, metric: str, source: str = "ebay_sold") -> str:
    content = json.dumps({"item": item, "metric": metric, "source": source}, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# ============================================================
# TOOLS
# ============================================================

TOOLS = [
    {
        "name": "value_listing",
        "description": "Is this listing actually a bargain? Cross-references asking price against sold comps. Returns verdict with sample size, percentiles, and evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name (e.g. 'Roland SP-404', 'technics turntable')"},
                "asking_price": {"type": "number", "description": "Asking price in GBP"},
                "platform": {"type": "string", "description": "Platform (facebook, ebay, gumtree, vinted)"},
                "condition": {"type": "string", "description": "Item condition (new, like_new, good, acceptable, broken)"},
            },
            "required": ["item", "asking_price"]
        }
    },
    {
        "name": "find_flips",
        "description": "What items have high price variance across conditions/platforms? Acquisition cost is unknown — margin cannot be computed.",
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
        "description": "What should I offer this seller? Estimates max offer after platform fees, postage, and condition risk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"},
                "target_margin": {"type": "number", "description": "Target profit margin (default 0.25 = 25%)"},
                "platform": {"type": "string", "description": "Selling platform (default ebay)"},
                "condition": {"type": "string", "description": "Item condition"},
                "postage_cost": {"type": "number", "description": "Estimated postage in GBP (default 5.00)"},
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
        "description": "How fast does this item sell? Computes from actual dates when available.",
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
        "description": "Should I repair this item or sell it as-is? Repair cost estimates are generic heuristics.",
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
    {
        "name": "valuation_detail",
        "description": "Full evidence object for a valuation. Shows every comparable sale, computation details, percentiles, and confidence interval. The 'show your work' tool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name"},
                "asking_price": {"type": "number", "description": "Asking price in GBP (optional, for comparison)"},
            },
            "required": ["item"]
        }
    },
]

# ============================================================
# DATA LOADING
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


def _extract_prices(sold: list) -> list:
    prices = []
    for s in sold:
        p = s.get('soldPrice', s.get('sold_price', 0))
        if p and p > 0:
            prices.append(p)
    return prices


def _parse_date(date_str: str):
    """Try to parse a date string into a date object. Returns None on failure."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"):
        try:
            return datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str.split(' ')[0], fmt.split('T')[0].split(' ')[0]).date()
        except (ValueError, IndexError):
            continue
    return None


def _compute_comp_age_days(sold: list) -> dict:
    """Compute how old the comparable sales are."""
    today = date(2026, 9, 19)
    ages = []
    for s in sold:
        d = _parse_date(s.get('soldDate', s.get('collected_at', '')))
        if d:
            ages.append((today - d).days)
    if not ages:
        return {"median_days": None, "max_days": None, "count_with_dates": 0}
    return {
        "median_days": int(median(ages)),
        "max_days": max(ages),
        "count_with_dates": len(ages),
    }


def _compute_condition_match_rate(sold: list, target_condition: str) -> float:
    """What % of comps match the target condition?"""
    if not target_condition or not sold:
        return 0.0
    target = target_condition.lower().replace('_', ' ').replace('-', ' ')
    matched = 0
    for s in sold:
        cond = s.get('condition', s.get('itemCondition', '')).lower().replace('_', ' ').replace('-', ' ')
        if cond and (target in cond or cond in target):
            matched += 1
    return round(matched / len(sold), 2) if sold else 0.0


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def value_listing(item: str, asking_price: float, platform: str = 'facebook', condition: str = None) -> dict:
    """Is this listing actually a bargain?"""
    sold = _load_sold_data(item)

    if not sold:
        return _contract(
            "breadup.value_listing",
            {
                "item": item,
                "asking_price": asking_price,
                "platform": platform,
                "verdict": "NO_DATA",
                "message": f'No sold data for "{item}". Collect data first.',
            },
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=[f'No sold comps found for "{item}"'],
        )

    prices = _extract_prices(sold)
    if not prices:
        return _contract(
            "breadup.value_listing",
            {
                "item": item,
                "asking_price": asking_price,
                "verdict": "NO_DATA",
                "message": "Found records but no valid sold prices.",
            },
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["Sold records exist but contain no valid prices"],
        )

    prices.sort()
    n = len(prices)
    med = median(prices)
    p25, p75 = quantiles(prices, n=4)[0], quantiles(prices, n=4)[2] if n >= 4 else (prices[0], prices[-1])

    comp_age = _compute_comp_age_days(sold)
    condition_rate = _compute_condition_match_rate(sold, condition) if condition else None

    below = asking_price < med
    gap_pct = ((med - asking_price) / med * 100) if below else ((asking_price - med) / med * 100)

    if below and gap_pct > 20:
        verdict = 'BARGAIN'
    elif below:
        verdict = 'SLIGHT_DEAL'
    elif gap_pct < 10:
        verdict = 'FAIR'
    else:
        verdict = 'OVERPRICED'

    suggested_offer = round(med * 0.85) if below else round(p25 * 0.90)

    # Evidence IDs
    evidence_ids = [_obs_id(item, f"sold_price_{i}") for i in range(min(n, 10))]

    # Truth class and confidence based on sample size
    if n >= 10:
        truth_class = "VERIFIED"
        confidence = min(0.95, 0.5 + (n * 0.02))
    elif n >= 5:
        truth_class = "DERIVED"
        confidence = 0.65
    else:
        truth_class = "ESTIMATED"
        confidence = 0.4

    limitations = []
    if n < 5:
        limitations.append(f"Small sample size (n={n}). Results may not be representative.")
    if comp_age["median_days"] and comp_age["median_days"] > 60:
        limitations.append(f"Comps are {comp_age['median_days']} days old on median. Market may have shifted.")
    if condition and condition_rate is not None and condition_rate < 0.5:
        limitations.append(f"Only {round(condition_rate*100)}% of comps match target condition '{condition}'.")

    return _contract(
        "breadup.value_listing",
        {
            "item": item,
            "asking_price": asking_price,
            "platform": platform,
            "n": n,
            "median": med,
            "p25": p25,
            "p75": p75,
            "comp_age_days": comp_age,
            "condition_match_rate": condition_rate,
            "verdict": verdict,
            "savings_vs_median": f'{round(gap_pct, 1)}%' if below else f'-{round(gap_pct, 1)}%',
            "suggested_offer": suggested_offer,
            "why": f"Item sells for GBP{med} median (n={n}). Asking price is GBP{asking_price}.",
        },
        truth_class=truth_class,
        confidence=confidence,
        evidence=evidence_ids,
        limitations=limitations,
    )


def find_flips(category: str = None, budget: float = None, limit: int = 10) -> dict:
    """What items have high price variance across conditions/platforms?"""
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
        med = median(prices)
        spread = prices[-1] - prices[0]
        variance_pct = (spread / med * 100) if med > 0 else 0

        if variance_pct > 15:
            flips.append({
                'title': data['title'],
                'median_price': med,
                'price_range': f'GBP{prices[0]} - GBP{prices[-1]}',
                'price_variance_pct': round(variance_pct, 1),
                'sample_size': data['count'],
            })

    flips.sort(key=lambda x: x['price_variance_pct'], reverse=True)

    evidence_ids = [_obs_id(category or "all", f"flip_{i}") for i in range(min(len(flips), 10))]

    return _contract(
        "breadup.find_flips",
        {
            "category": category,
            "flips": flips[:limit],
            "total_items_analyzed": len(items),
            "note": "Price variance indicates potential arbitrage opportunities. Acquisition cost is unknown — margin cannot be computed.",
        },
        truth_class="HEURISTIC",
        confidence=0.45,
        evidence=evidence_ids,
        limitations=[
            "Acquisition cost unknown — margin cannot be computed from sold data alone",
            "Price variance may reflect condition differences, not arbitrage opportunity",
            "Requires cross-platform sourcing data to compute actual margins",
        ],
    )


def max_offer(item: str, target_margin: float = 0.25, platform: str = 'ebay',
              condition: str = None, postage_cost: float = 5.00) -> dict:
    """What should I offer this seller? Includes platform fees, postage, condition risk."""
    sold = _load_sold_data(item)
    prices = _extract_prices(sold)

    if not prices:
        return _contract(
            "breadup.max_offer",
            {"item": item, "message": "No sold data available."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["No sold data to compute offer from"],
        )

    med = median(prices)
    platform_fee_pct = PLATFORM_FEES.get(platform, 0.128)
    platform_fee = med * platform_fee_pct

    # Condition risk adjustment: worse condition = higher risk of return/complaint
    condition_risk = 0.0
    if condition:
        risk_map = {"new": 0.0, "like_new": 0.02, "good": 0.05, "acceptable": 0.10, "broken": 0.20}
        condition_risk = risk_map.get(condition.lower().replace(' ', '_').replace('-', '_'), 0.05)
    risk_adjustment = med * condition_risk

    # All-in cost at market price
    total_fees = platform_fee + postage_cost + risk_adjustment

    # Max offer = sell price minus fees, minus target margin on sell price
    max_offer_val = round(med - total_fees - (med * target_margin))
    fast_sale = round(med * 0.80 - total_fees)

    assumptions = [
        f"Platform: {platform} ({round(platform_fee_pct*100, 1)}% fees)",
        f"Postage estimate: GBP{postage_cost}",
        f"Condition risk adjustment: {round(condition_risk*100, 1)}%",
        f"Target margin: {round(target_margin*100)}% on selling price",
        "Sell price based on median of sold comps",
    ]

    evidence_ids = [_obs_id(item, f"sold_price_{i}") for i in range(min(len(prices), 10))]

    return _contract(
        "breadup.max_offer",
        {
            "item": item,
            "market_median": med,
            "platform": platform,
            "platform_fee": round(platform_fee, 2),
            "postage_cost": postage_cost,
            "condition_risk_pct": round(condition_risk * 100, 1),
            "target_margin": f'{round(target_margin * 100)}%',
            "max_offer": max_offer_val,
            "fast_sale_offer": fast_sale,
            "strategy": f"Offer GBP{max_offer_val} ({round(target_margin*100)}% margin after fees). For fast sale, offer GBP{fast_sale}.",
            "assumptions": assumptions,
        },
        truth_class="ESTIMATED",
        confidence=0.55,
        evidence=evidence_ids,
        limitations=[
            "Median sold price used as expected sell price — actual price may vary",
            "Postage is an estimate — actual cost depends on weight/size/speed",
            "Condition risk is a rough adjustment — actual return rate unknown",
            "Does not account for time-to-sell or capital cost",
        ],
    )


def cheapest_source(item: str) -> dict:
    """Where's the cheapest place to buy this?"""
    return _contract(
        "breadup.cheapest_source",
        {
            "item": item,
            "available_platforms": ["ebay_uk"],
            "message": "Cross-platform comparison requires eBay + Vinted + Facebook collectors. Currently only eBay data available.",
        },
        truth_class="UNAVAILABLE",
        confidence=0.0,
        evidence=[],
        limitations=[
            "Only eBay UK data available",
            "Vinted and Facebook Marketplace collectors not yet built",
            "Cannot compare prices across platforms",
        ],
    )


def liquidity_score(item: str) -> dict:
    """How fast does this sell? Computes from actual dates when possible."""
    sold = _load_sold_data(item)
    if not sold:
        return _contract(
            "breadup.liquidity_score",
            {"item": item, "message": "No sold data available."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["No sold data to compute liquidity from"],
        )

    # Parse actual dates
    parsed_dates = []
    for s in sold:
        d = _parse_date(s.get('soldDate', s.get('collected_at', '')))
        if d:
            parsed_dates.append(d)

    total_sales = len(sold)

    if len(parsed_dates) >= 3:
        # We have enough date data to compute actual days-to-sale
        parsed_dates.sort()
        # Approximate days-to-sale: time between earliest listing and sale
        # For now, use spread of dates as proxy for activity
        date_range_days = (parsed_dates[-1] - parsed_dates[0]).days
        sales_per_day = total_sales / max(date_range_days, 1)
        median_days_to_sale = round(date_range_days / total_sales) if total_sales > 0 else None

        # Recent sales: within last 14 days of our reference date
        ref_date = date(2026, 9, 19)
        recent = sum(1 for d in parsed_dates if (ref_date - d).days <= 14)

        truth_class = "DERIVED"
        confidence = 0.70
        limitations = [
            "Days-to-sale is estimated from date spread, not individual listing durations",
            "collected_at may not reflect actual sale date",
        ]

        result = {
            "item": item,
            "total_sales": total_sales,
            "recent_sales_14d": recent,
            "median_days_to_sale": median_days_to_sale,
            "date_range_days": date_range_days,
            "sales_per_day": round(sales_per_day, 2),
            "liquidity": "HIGH" if sales_per_day > 1 else "MEDIUM" if sales_per_day > 0.2 else "LOW",
        }
    else:
        # No date data — fall back to heuristic based on volume
        recent = 0
        for s in sold:
            d_str = s.get('soldDate', s.get('collected_at', ''))
            if d_str and '2026-09' in d_str:
                recent += 1

        truth_class = "HEURISTIC"
        confidence = 0.35
        limitations = [
            "Insufficient date data for computation — using volume-based heuristic",
            "liquidity estimate is a rough guess based on number of sold records",
            "Exact days-to-sell requires individual listing date tracking",
        ]

        result = {
            "item": item,
            "total_sales": total_sales,
            "recent_sales_14d": recent,
            "median_days_to_sale": None,
            "liquidity": "HIGH" if total_sales > 10 else "MEDIUM" if total_sales > 3 else "LOW",
        }

    evidence_ids = [_obs_id(item, f"sold_date_{i}") for i in range(min(len(parsed_dates), 10))]

    return _contract(
        "breadup.liquidity_score",
        result,
        truth_class=truth_class,
        confidence=confidence,
        evidence=evidence_ids,
        limitations=limitations,
    )


def price_history(item: str, days: int = 90) -> dict:
    """How have prices changed?"""
    if not DATA_DIR.exists():
        return _contract(
            "breadup.price_history",
            {"item": item, "message": "No data directory found."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["Data directory does not exist"],
        )

    history = []
    evidence_ids = []
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
                'median': median(prices),
                'min': min(prices),
                'max': max(prices),
                'count': len(prices),
            })
            evidence_ids.append(_obs_id(item, f"price_history_{date_str}"))

    trend = 'stable'
    if len(history) >= 2:
        first = history[0]['median']
        last = history[-1]['median']
        change_pct = ((last - first) / first * 100) if first > 0 else 0
        trend = 'rising' if change_pct > 5 else 'falling' if change_pct < -5 else 'stable'

    has_data = len(history) > 0

    return _contract(
        "breadup.price_history",
        {
            "item": item,
            "history": history,
            "trend": trend,
            "data_points": len(history),
        },
        truth_class="DERIVED" if has_data else "UNAVAILABLE",
        confidence=0.70 if has_data else 0.0,
        evidence=evidence_ids,
        limitations=[
            "Trend computed from daily median snapshots, not continuous price tracking",
            "Price changes may reflect composition changes (different items sold) not true market movement",
        ] if has_data else ["No price history data available"],
    )


def repair_vs_sell(item: str, fault: str, repair_cost: float = None) -> dict:
    """Should I repair it or sell as-is?"""
    sold = _load_sold_data(item)
    prices = _extract_prices(sold)

    if not prices:
        return _contract(
            "breadup.repair_vs_sell",
            {"item": item, "message": "No sold data available."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["No sold data to estimate working value"],
        )

    med = median(prices)

    # Broken value multiplier — these are ASSUMPTIONS, not calibrated
    broken_multiplier = 0.4 if 'not working' in fault.lower() else 0.6
    broken_price = round(med * broken_multiplier)

    if repair_cost is None:
        # Generic heuristic estimates — not item-specific
        fault_estimates = {
            'screen': 80, 'battery': 30, 'button': 20,
            'cosmetic': 0, 'software': 0, 'power': 50,
        }
        repair_cost = fault_estimates.get(fault.lower().split()[0], 40)

    repair_profit = med - repair_cost - broken_price

    evidence_ids = [_obs_id(item, f"repair_{fault}")]

    return _contract(
        "breadup.repair_vs_sell",
        {
            "item": item,
            "fault": fault,
            "working_value": med,
            "broken_value": broken_price,
            "broken_multiplier_used": broken_multiplier,
            "repair_cost": repair_cost,
            "repair_profit_uplift": repair_profit,
            "verdict": "REPAIR" if repair_profit > 0 else "SELL_AS_IS",
            "recommendation": (
                f"Sell as-is for ~GBP{broken_price}" if repair_profit <= 0
                else f"Repair for GBP{repair_cost}, sell for GBP{med}, net gain GBP{repair_profit}"
            ),
        },
        truth_class="HEURISTIC",
        confidence=0.35,
        evidence=evidence_ids,
        limitations=[
            f"Broken value multiplier ({broken_multiplier}) is an assumption — actual broken price varies by market",
            "Repair cost estimates are generic heuristics, not quotes from actual repair services",
            "Repair cost should be obtained from a qualified repairer for decision-making",
            "Does not account for risk of failed repair or time spent repairing",
        ],
    )


def part_out_economics(item: str) -> dict:
    """Should I part this out or sell whole?"""
    sold = _load_sold_data(item)
    prices = _extract_prices(sold)

    if not prices:
        return _contract(
            "breadup.part_out_economics",
            {"item": item, "message": "No sold data available."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["No sold data to estimate whole value"],
        )

    whole_value = median(prices)

    return _contract(
        "breadup.part_out_economics",
        {
            "item": item,
            "whole_value": whole_value,
            "message": "Part-out economics requires per-part price data. General rule: if parts value > 1.5x whole value, part out.",
            "rule_of_thumb": "Part out if: sum(parts_value) > whole_value * 1.3 (30% premium for hassle)",
        },
        truth_class="HEURISTIC",
        confidence=0.30,
        evidence=[_obs_id(item, "whole_value")],
        limitations=[
            "No per-part price data available — using rule of thumb only",
            "Actual part-out economics depend on individual part demand and shipping costs",
            "Requires manual research of individual part prices",
        ],
    )


def best_categories(min_margin: float = 20) -> dict:
    """Which categories have the best margins?"""
    if not DATA_DIR.exists():
        return _contract(
            "breadup.best_categories",
            {"message": "No data directory found."},
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["Data directory does not exist"],
        )

    categories = {}
    evidence_ids = []
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
        med = median(prices)
        spread = prices[-1] - prices[0]
        margin = (spread / med * 100) if med > 0 else 0
        if margin >= min_margin:
            results.append({
                'category': cat,
                'median_price': round(med),
                'price_range': f'GBP{prices[0]} - GBP{prices[-1]}',
                'margin_pct': round(margin, 1),
                'sample_size': len(prices),
            })
            evidence_ids.append(_obs_id(cat, "category_margin"))

    results.sort(key=lambda x: x['margin_pct'], reverse=True)

    return _contract(
        "breadup.best_categories",
        {
            "categories": results,
            "min_margin": min_margin,
        },
        truth_class="DERIVED",
        confidence=0.60,
        evidence=evidence_ids,
        limitations=[
            "Margin computed from price spread within category, not actual buy/sell pairs",
            "High spread may reflect item diversity, not true arbitrage opportunity",
            "Category labels are from eBay data — may not be precise",
        ],
    )


def ebay_search(query: str, limit: int = 40) -> dict:
    """Search eBay UK sold via SoldComps API."""
    import requests

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
            results = data.get('results', [])[:limit]
            return _contract(
                "breadup.ebay_search",
                {
                    "query": query,
                    "results": results,
                    "count": data.get('count', 0),
                },
                truth_class="VERIFIED",
                confidence=0.90,
                evidence=[],
                limitations=[],
                action_class="ADVISORY",
            )
    except Exception:
        pass

    # Fallback to local data
    sold = _load_sold_data(query, limit)
    return _contract(
        "breadup.ebay_search",
        {
            "query": query,
            "results": sold[:limit],
        },
        truth_class="DERIVED",
        confidence=0.70,
        evidence=[],
        limitations=["SoldComps API unavailable — using local cached data"],
    )


def valuation_detail(item: str, asking_price: float = None) -> dict:
    """Full evidence object for a valuation. Shows every comparable sale with details."""
    sold = _load_sold_data(item)

    if not sold:
        return _contract(
            "breadup.valuation_detail",
            {
                "item": item,
                "comps": [],
                "message": f'No sold data for "{item}".',
            },
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=[f'No sold comps found for "{item}"'],
        )

    # Build detailed comp list
    comps = []
    all_prices = []
    for s in sold:
        p = s.get('soldPrice', s.get('sold_price', 0))
        if not p or p <= 0:
            continue
        all_prices.append(p)
        comps.append({
            "title": s.get('title', ''),
            "price": p,
            "condition": s.get('condition', s.get('itemCondition', 'unknown')),
            "date": s.get('soldDate', s.get('collected_at', '')),
            "platform": s.get('platform', 'ebay'),
            "url": s.get('url', s.get('link', '')),
        })

    if not all_prices:
        return _contract(
            "breadup.valuation_detail",
            {
                "item": item,
                "comps": [],
                "message": "Found records but no valid prices.",
            },
            truth_class="UNAVAILABLE",
            confidence=0.0,
            evidence=[],
            limitations=["Sold records exist but contain no valid prices"],
        )

    all_prices.sort()
    n = len(all_prices)
    med = median(all_prices)
    p25, p75 = quantiles(all_prices, n=4)[0], quantiles(all_prices, n=4)[2] if n >= 4 else (all_prices[0], all_prices[-1])

    # Confidence interval (approximate)
    ci_lower = round(p25 * 0.95, 2)
    ci_upper = round(p75 * 1.05, 2)

    # Comp age
    comp_age = _compute_comp_age_days(sold)

    # Evidence IDs for each comp
    evidence_ids = [_obs_id(item, f"comp_{i}") for i in range(min(n, 20))]

    # Truth class based on sample
    if n >= 10:
        truth_class = "VERIFIED"
        confidence = min(0.95, 0.5 + (n * 0.02))
    elif n >= 5:
        truth_class = "DERIVED"
        confidence = 0.65
    else:
        truth_class = "ESTIMATED"
        confidence = 0.4

    result = {
        "item": item,
        "comps": comps,
        "computation": {
            "n": n,
            "median": med,
            "p25": p25,
            "p75": p75,
            "min": all_prices[0],
            "max": all_prices[-1],
            "confidence_interval": {"lower": ci_lower, "upper": ci_upper},
        },
        "comp_age_days": comp_age,
    }

    if asking_price is not None:
        gap = asking_price - med
        result["asking_price_analysis"] = {
            "asking_price": asking_price,
            "diff_from_median": round(gap, 2),
            "diff_pct": round((gap / med * 100), 1) if med > 0 else 0,
            "verdict": "BARGAIN" if gap < -med * 0.2 else "FAIR" if abs(gap) < med * 0.1 else "OVERPRICED",
        }

    limitations = []
    if n < 5:
        limitations.append(f"Small sample size (n={n}). Statistics may not be reliable.")
    if comp_age["median_days"] and comp_age["median_days"] > 60:
        limitations.append(f"Comps are {comp_age['median_days']} days old on median.")

    return _contract(
        "breadup.valuation_detail",
        result,
        truth_class=truth_class,
        confidence=confidence,
        evidence=evidence_ids,
        limitations=limitations,
    )


# ============================================================
# DISPATCH & MCP SERVER
# ============================================================

DISPATCH = {t['name']: globals()[t['name']] for t in TOOLS}


def handle_tool_call(name: str, args: dict) -> dict:
    func = DISPATCH.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except TypeError as e:
        return {"error": f"Invalid args: {e}"}


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
                    "serverInfo": {"name": "breadup", "version": "2.0.0",
                                   "description": "Breadup — Physical goods value engine. PR5 truth contract."},
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
