#!/usr/bin/env python3
"""
DataGarden MCP Server
Unified Model Context Protocol server for all three data gardens.

Usage:
    python mcp_server.py                    # Print server info
    python mcp_server.py <tool> <args_json> # Call a tool
    python mcp_server.py --serve            # Run as MCP stdio server
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================
# TOOL DEFINITIONS (MCP format)
# ============================================================

TOOLS = [
    # --- BREADUP TOOLS ---
    {
        "name": "breadup_valuation",
        "description": "Get the current market valuation for a used physical item. Returns median sold price, price trend, listing count, and liquidity score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Item to search for (e.g. 'Roland SP-404', 'technics turntable', 'fender stratocaster')"},
                "category": {"type": "string", "description": "Optional category filter (e.g. 'synthesizer', 'pedal', 'turntable', 'amplifier')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "breadup_mispricing",
        "description": "Find items currently priced below their estimated fair market value. Returns items with the largest price gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Category to search (e.g. 'electronics', 'synthesizer', 'audio')"},
                "limit": {"type": "integer", "description": "Max results (default 10)"}
            }
        }
    },
    {
        "name": "breadup_price_history",
        "description": "Get historical price data for an item. Shows how its value has changed over time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Item to look up"},
                "days": {"type": "integer", "description": "Days of history (default 90)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "breadup_cross_market_spread",
        "description": "Compare prices for the same item across different platforms (eBay, Vinted, Facebook, etc).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Item to compare"}
            },
            "required": ["query"]
        }
    },

    # --- UKGRAPH TOOLS ---
    {
        "name": "ukgraph_career_crowding",
        "description": "Check how crowded a UK career/occupation is. Returns entrant rate vs demand growth, salary trend, and room score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job title or occupation (e.g. 'cybersecurity', 'electrician', 'data scientist')"},
                "region": {"type": "string", "description": "Optional UK region filter (e.g. 'London', 'Manchester', 'West Midlands')"}
            },
            "required": ["occupation"]
        }
    },
    {
        "name": "ukgraph_trade_demand",
        "description": "Check demand-to-worker ratio for UK trades by region. Shows where tradespeople are most needed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trade": {"type": "string", "description": "Trade (e.g. 'electrician', 'plumber', 'hvac', 'builder')"},
                "region": {"type": "string", "description": "Optional UK region"}
            }
        }
    },
    {
        "name": "ukgraph_business_gap",
        "description": "Find underserved business opportunities in a UK postcode area. Shows demand vs supply gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode area (e.g. 'M1', 'B1', 'LS1')"},
                "sector": {"type": "string", "description": "Optional business sector filter"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "ukgraph_regulation_impact",
        "description": "Analyze the economic impact of a UK regulation or policy change. Shows affected sectors and new market opportunities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Regulation or policy to analyze (e.g. 'building regulations 2027', 'UK AI regulation', 'net zero targets')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "ukgraph_salary_data",
        "description": "Get salary and wage data for UK occupations by region.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job title or SOC code"},
                "region": {"type": "string", "description": "Optional UK region"}
            },
            "required": ["occupation"]
        }
    },

    # --- POWPOWPOW TOOLS ---
    {
        "name": "pow_network_status",
        "description": "Get current status of a proof-of-work network (hashrate, difficulty, price, block reward).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol (e.g. 'QUBIC', 'XMR', 'KAS', 'BTC')"}
            },
            "required": ["network"]
        }
    },
    {
        "name": "pow_mining_profitability",
        "description": "Calculate mining profitability for specific hardware on a given network.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol"},
                "hardware": {"type": "string", "description": "Hardware model (e.g. 'RTX_4090', 'RTX_3080', 'H100', 'ASIC_X19')"},
                "electricity_cost": {"type": "number", "description": "Electricity cost in $/kWh (default 0.10)"}
            },
            "required": ["network", "hardware"]
        }
    },
    {
        "name": "pow_best_mining",
        "description": "Find the most profitable network to mine for a given hardware model.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hardware": {"type": "string", "description": "Hardware model (e.g. 'RTX_4090', 'H100')"},
                "electricity_cost": {"type": "number", "description": "Electricity cost in $/kWh (default 0.10)"}
            },
            "required": ["hardware"]
        }
    },
    {
        "name": "pow_compare_networks",
        "description": "Compare mining economics across multiple proof-of-work networks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "networks": {"type": "array", "items": {"type": "string"}, "description": "List of network symbols to compare"},
                "hardware": {"type": "string", "description": "Optional hardware model for profitability comparison"}
            },
            "required": ["networks"]
        }
    },
    {
        "name": "pow_all_networks",
        "description": "Get profitability cards for all tracked proof-of-work networks.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "pow_hashrate_migration",
        "description": "Show where hashrate is moving between networks (7-day trend).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Trend period in days (default 7)"}
            }
        }
    },

    # --- UK ADMIN TOOLS ---
    {
        "name": "uk_admin_explain_task",
        "description": "How do I do X? Full walkthrough for a UK government task with step-by-step instructions, cost, and time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to explain (e.g. 'renew_driving_licence', 'book_mot', 'self_assessment_submit')"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "uk_admin_check_requirements",
        "description": "What do I need for X? Prerequisites checklist for a UK government task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to check requirements for"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "uk_admin_can_agent_do_it",
        "description": "Can Muse handle this? Check if an AI agent can help with a UK admin task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task to check agent permissions for"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "uk_admin_moving_house",
        "description": "I've moved house, what do I update? Complete checklist of government notifications.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "new_address": {"type": "string", "description": "Your new address"},
                "move_date": {"type": "string", "description": "Date you moved (YYYY-MM-DD)"},
                "old_address": {"type": "string", "description": "Your previous address"}
            },
            "required": ["new_address", "move_date"]
        }
    },
    {
        "name": "uk_admin_lost_passport",
        "description": "I lost my passport, what do I do? Step-by-step guide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "was_stolen": {"type": "boolean", "description": "Was it stolen? Default false"}
            }
        }
    },
    {
        "name": "uk_admin_tax_obligations",
        "description": "What do I need to file this year? Tax obligation summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {"type": "string", "description": "Your situation ('employed', 'sole_trader', 'limited_company')"}
            },
            "required": ["situation"]
        }
    },
    {
        "name": "uk_admin_benefits_check",
        "description": "What benefits might I qualify for? Eligibility check.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "situation": {"type": "string", "description": "Your situation (e.g. 'family with kids', 'disabled')"}
            },
            "required": ["situation"]
        }
    },
    {
        "name": "uk_admin_company_setup",
        "description": "Set up a company for this side project. Step-by-step guide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Proposed company name"},
                "sector": {"type": "string", "description": "Business sector"}
            }
        }
    },

    # --- CROSS-GARDEN TOOLS ---
    {
        "name": "garden_health",
        "description": "Check the health status of all data gardens — last collection time, data freshness, and any errors.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "garden_cross_analysis",
        "description": "Analyze connections between physical goods markets, UK labor markets, and compute economics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to analyze (e.g. 'how does AI demand affect GPU mining vs UK tech jobs?')"}
            },
            "required": ["query"]
        }
    },

    # --- CAPABILITY-FIRST TOOLS (what people actually ask) ---
    {
        "name": "can_my_pc_make_money",
        "description": "Answer: 'Can this gaming PC make me money?' Shows profitability of mining with a specific GPU across all tracked networks, accounting for electricity costs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model (e.g. 'RTX_4060', 'RTX_4090', 'RX_7900_XTX')"},
                "electricity_rate": {"type": "number", "description": "Electricity cost in $/kWh (default 0.15)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "what_should_i_mine",
        "description": "Answer: 'What should I mine with this GPU today?' Returns the most profitable network for a given GPU.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model"},
                "electricity_rate": {"type": "number", "description": "Electricity cost in $/kWh (default 0.15)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "mine_or_rent",
        "description": "Answer: 'Is it better to mine or rent out my GPUs?' Compares mining revenue vs AI inference rental revenue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model"},
                "count": {"type": "integer", "description": "Number of GPUs (default 1)"},
                "electricity_rate": {"type": "number", "description": "Electricity cost in $/kWh (default 0.15)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "my_mining_portfolio",
        "description": "Answer: 'How much would I make with [X] GPUs?' Calculates total revenue for a custom GPU portfolio.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpus": {"type": "array", "items": {"type": "string"}, "description": "List of GPU models (e.g. ['RTX_4060', 'RTX_4090'])"},
                "electricity_rate": {"type": "number", "description": "Electricity cost in $/kWh (default 0.15)"}
            },
            "required": ["gpus"]
        }
    },
    {
        "name": "british_shortages",
        "description": "Answer: 'What is Britain running out of?' Shows UK sectors where demand outpaces supply based on ONS data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Optional UK region filter"}
            }
        }
    },
    {
        "name": "is_this_a_bargain",
        "description": "Answer: 'Is this listing actually a bargain?' Cross-references an item's asking price against market data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Item name or description"},
                "asking_price": {"type": "number", "description": "Asking price in GBP"},
                "platform": {"type": "string", "description": "Platform (e.g. 'facebook', 'ebay', 'gumtree')"}
            },
            "required": ["item", "asking_price"]
        }
    },
]


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def breadup_valuation(query: str, category: str = None) -> dict:
    """Get valuation for a used physical item."""
    data_dir = Path(__file__).parent / 'forests' / 'breadup' / 'data'
    ebay_dir = data_dir / 'ebay_sold'

    if not ebay_dir.exists():
        return {
            "status": "no_data",
            "message": "No Breadup data collected yet. Run: python -m collectors.ebay_sold --query '{}' --count 50".format(query),
            "query": query
        }

    # Search across all date files
    results = []
    for f in sorted(ebay_dir.glob('*.jsonl'), reverse=True)[:7]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    title = item.get('title', '').lower()
                    if query.lower() in title:
                        results.append(item)
                except json.JSONDecodeError:
                    continue

    if not results:
        return {"status": "not_found", "query": query, "message": f"No results for '{query}' in collected data"}

    prices = [r.get('sold_price', 0) for r in results if r.get('sold_price')]
    if not prices:
        return {"status": "no_prices", "query": query}

    prices_sorted = sorted(prices)
    n = len(prices_sorted)
    median = prices_sorted[n // 2]
    p25 = prices_sorted[n // 4]
    p75 = prices_sorted[3 * n // 4]

    return {
        "status": "ok",
        "query": query,
        "median_price": median,
        "p25": p25,
        "p75": p75,
        "sample_size": n,
        "min": min(prices),
        "max": max(prices),
        "source": "ebay_uk_sold",
        "last_updated": f.stem if f.exists() else None,
    }


def breadup_mispricing(category: str = None, limit: int = 10) -> dict:
    """Find mispriced items."""
    data_dir = Path(__file__).parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'

    if not data_dir.exists():
        return {"status": "no_data", "message": "No Breadup data collected yet"}

    all_items = []
    for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:7]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    if category and category.lower() not in item.get('category', '').lower():
                        continue
                    all_items.append(item)
                except json.JSONDecodeError:
                    continue

    # Calculate mispricing = original_price - sold_price (positive = sold below original)
    mispriced = []
    for item in all_items:
        sold = item.get('sold_price', 0)
        original = item.get('original_price', 0)
        if sold and original and original > sold:
            gap = original - sold
            pct = gap / original
            mispriced.append({
                "title": item.get('title', 'unknown'),
                "sold_price": sold,
                "original_price": original,
                "savings": gap,
                "savings_pct": round(pct * 100, 1),
                "condition": item.get('condition', 'unknown'),
            })

    mispriced.sort(key=lambda x: x['savings_pct'], reverse=True)
    return {"status": "ok", "count": len(mispriced), "items": mispriced[:limit]}


def breadup_price_history(query: str, days: int = 90) -> dict:
    """Get price history for an item."""
    data_dir = Path(__file__).parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'

    if not data_dir.exists():
        return {"status": "no_data", "message": "No Breadup data collected yet"}

    history = []
    for f in sorted(data_dir.glob('*.jsonl')):
        date_str = f.stem
        prices = []
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    if query.lower() in item.get('title', '').lower():
                        price = item.get('sold_price', 0)
                        if price:
                            prices.append(price)
                except json.JSONDecodeError:
                    continue
        if prices:
            history.append({
                "date": date_str,
                "median": sorted(prices)[len(prices) // 2],
                "count": len(prices),
                "min": min(prices),
                "max": max(prices),
            })

    return {"status": "ok", "query": query, "history": history}


def breadup_cross_market_spread(query: str) -> dict:
    """Compare prices across platforms."""
    return {
        "status": "partial",
        "message": "Cross-platform comparison requires Vinted + eBay collectors running. Currently only eBay data available.",
        "query": query,
        "available_platforms": ["ebay_uk"],
    }


def ukgraph_career_crowding(occupation: str, region: str = None) -> dict:
    """Check career crowding for a UK occupation."""
    data_dir = Path(__file__).parent / 'forests' / 'room' / 'data' / 'ons'

    if not data_dir.exists() or not any(data_dir.glob('*.jsonl')):
        return {
            "status": "no_data",
            "message": "No UKGraph data collected yet. Run: python -m collectors.ons_jobs",
            "occupation": occupation
        }

    # Search across all data types for relevant mentions
    results = []
    for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:30]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    data = item.get('data', {})
                    title = data.get('title', '').lower()
                    summary = data.get('summary', '').lower()
                    query = data.get('query', '').lower()
                    if occupation.lower() in title or occupation.lower() in summary or occupation.lower() in query:
                        results.append({
                            'title': data.get('title', ''),
                            'summary': data.get('summary', '')[:200],
                            'type': data.get('type', item.get('data_type', '')),
                            'release_date': data.get('release_date', ''),
                            'source': data.get('source', item.get('data_type', '')),
                        })
                except json.JSONDecodeError:
                    continue

    if not results:
        # Fall back to general labour market data
        all_items = []
        for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:10]:
            with open(f) as fh:
                for line in fh:
                    try:
                        item = json.loads(line)
                        if item.get('data_type') == 'ons_bulletins':
                            all_items.append(item.get('data', {}))
                    except json.JSONDecodeError:
                        continue
        return {
            "status": "general",
            "occupation": occupation,
            "message": f"No specific data for '{occupation}'. Showing general labour market context.",
            "latest_bulletins": [
                {"title": b.get('title', ''), "summary": b.get('summary', '')[:150]}
                for b in all_items[:5]
            ],
        }

    return {
        "status": "ok",
        "occupation": occupation,
        "region": region,
        "data_points": len(results),
        "results": results[:5],
        "source": "ons_labour_market",
    }


def ukgraph_trade_demand(trade: str, region: str = None) -> dict:
    """Check trade demand."""
    return ukgraph_career_crowding(trade, region)


def ukgraph_business_gap(postcode: str, sector: str = None) -> dict:
    """Find business gaps."""
    data_dir = Path(__file__).parent / 'forests' / 'room' / 'data' / 'companies_house'

    if not data_dir.exists() or not any(data_dir.glob('*.jsonl')):
        return {
            "status": "no_data",
            "message": "No Companies House data collected yet. Run the Companies House collector.",
            "postcode": postcode
        }

    births = []
    deaths = []
    for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:30]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    addr = item.get('address', {})
                    if postcode.upper() in str(addr):
                        if item.get('status') == 'active':
                            births.append(item)
                        else:
                            deaths.append(item)
                except json.JSONDecodeError:
                    continue

    return {
        "status": "ok",
        "postcode": postcode,
        "sector": sector,
        "recent_births": len(births),
        "recent_deaths": len(deaths),
        "net_change": len(births) - len(deaths),
        "sample_births": [b.get('name', '') for b in births[:5]],
        "sample_deaths": [d.get('name', '') for d in deaths[:5]],
    }


def ukgraph_regulation_impact(query: str) -> dict:
    """Analyze regulation impact."""
    return {
        "status": "not_implemented",
        "message": "Regulation analysis requires GOV.UK + planning data collectors. Design complete, not yet built.",
        "query": query,
        "planned_data_sources": ["legislation.gov.uk", "planning_data", "statutory_instruments"],
    }


def ukgraph_salary_data(occupation: str, region: str = None) -> dict:
    """Get salary data."""
    return {
        "status": "not_implemented",
        "message": "Salary data requires ONS ASHE dataset integration. Career crowding data is available.",
        "occupation": occupation,
    }


def pow_network_status(network: str) -> dict:
    """Get network status from powpowpow data."""
    chain_dir = Path(os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')) / 'chains' / network.lower()
    data_file = chain_dir / f'{network.lower()}_data.json'

    if not data_file.exists():
        return {"status": "not_found", "network": network, "message": f"No data file for {network}"}

    with open(data_file) as f:
        data = json.load(f)

    price = data.get('price', {})
    price_usd = price.get('usd', 0) if isinstance(price, dict) else price

    registry_file = Path(os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')) / 'v1_registry.py'
    coin_info = {}
    if registry_file.exists():
        sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
        try:
            from v1_registry import get_v1_coin
            coin_info = get_v1_coin(network.upper()) or {}
        except Exception:
            pass

    return {
        "status": "ok",
        "network": network.upper(),
        "name": coin_info.get('name', network),
        "physical_resource": coin_info.get('physical_resource', 'unknown'),
        "price_usd": price_usd,
        "raw_data": data,
    }


def pow_mining_profitability(network: str, hardware: str, electricity_cost: float = 0.10) -> dict:
    """Calculate mining profitability."""
    sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"status": "error", "message": "Cannot import v1_live_cards from powpowpow"}

    data_file = Path(f"{os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')}/chains/{network.lower()}/{network.lower()}_data.json')
    if not data_file.exists():
        return {"status": "not_found", "network": network}

    with open(data_file) as f:
        data = json.load(f)

    price = data.get('price', {})
    price_usd = price.get('usd', 0) if isinstance(price, dict) else price

    if not price_usd:
        return {"status": "no_price", "network": network}

    card = generate_card(network, price_usd)

    if hardware.upper() in card.get('hardware', {}):
        return {"status": "ok", "network": network, "hardware": hardware, **card['hardware'][hardware.upper()]}

    return {"status": "hardware_not_found", "network": network, "hardware": hardware, "available_hardware": list(card.get('hardware', {}).keys())}


def pow_best_mining(hardware: str, electricity_cost: float = 0.10) -> dict:
    """Find best mining option for hardware."""
    sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"status": "error", "message": "Cannot import v1_live_cards"}

    best = None
    best_profit = float('-inf')
    chains = ['PRL', 'QUBIC', 'XMR', 'KAS', 'QUAN']

    for chain in chains:
        data_file = Path(f"{os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')}/chains/{chain.lower()}/{chain.lower()}_data.json')
        if not data_file.exists():
            continue

        with open(data_file) as f:
            data = json.load(f)

        price = data.get('price', {})
        price_usd = price.get('usd', 0) if isinstance(price, dict) else price

        if price_usd:
            card = generate_card(chain, price_usd)
            if hardware.upper() in card.get('hardware', {}):
                hw = card['hardware'][hardware.upper()]
                profit = hw.get('net_profit_usd_day', 0)
                if profit > best_profit:
                    best_profit = profit
                    best = {"network": chain, "hardware": hardware, **hw}

    return best or {"status": "no_data", "hardware": hardware, "message": "No profitability data found"}


def pow_compare_networks(networks: list, hardware: str = None) -> dict:
    """Compare networks."""
    sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"status": "error", "message": "Cannot import v1_live_cards"}

    results = []
    for network in networks:
        data_file = Path(f"{os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')}/chains/{network.lower()}/{network.lower()}_data.json')
        if not data_file.exists():
            results.append({"network": network, "status": "no_data"})
            continue

        with open(data_file) as f:
            data = json.load(f)

        price = data.get('price', {})
        price_usd = price.get('usd', 0) if isinstance(price, dict) else price

        if price_usd:
            card = generate_card(network, price_usd)
            entry = {"network": network, "price_usd": price_usd}
            if hardware and hardware.upper() in card.get('hardware', {}):
                entry["hardware"] = card['hardware'][hardware.upper()]
            results.append(entry)
        else:
            results.append({"network": network, "status": "no_price"})

    return {"status": "ok", "networks": results}


def pow_all_networks() -> dict:
    """Get all network cards."""
    sys.path.insert(0, os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"status": "error", "message": "Cannot import v1_live_cards"}

    cards = {}
    for chain in ['PRL', 'QUBIC', 'QUAN', 'XMR', 'KAS']:
        data_file = Path(f"{os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')}/chains/{chain.lower()}/{chain.lower()}_data.json')
        if data_file.exists():
            with open(data_file) as f:
                data = json.load(f)
            price = data.get('price', {})
            price_usd = price.get('usd', 0) if isinstance(price, dict) else price
            if price_usd:
                cards[chain] = generate_card(chain, price_usd)

    return {"status": "ok", "cards": cards}


def pow_hashrate_migration(days: int = 7) -> dict:
    """Show hashrate migration trends."""
    return {
        "status": "not_implemented",
        "message": "Hashrate migration requires historical time-series data. Design complete, needs data collection.",
        "days": days,
    }


def garden_health() -> dict:
    """Check health of all gardens."""
    gardens = {}

    # Breadup
    ebay_dir = Path(__file__).parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'
    ebay_files = list(ebay_dir.glob('*.jsonl')) if ebay_dir.exists() else []
    gardens['breadup'] = {
        "data_files": len(ebay_files),
        "latest": ebay_files[-1].stem if ebay_files else None,
        "status": "ok" if ebay_files else "no_data",
    }

    # UKGraph
    ons_dir = Path(__file__).parent / 'forests' / 'room' / 'data' / 'ons'
    ons_files = list(ons_dir.glob('*.jsonl')) if ons_dir.exists() else []
    ch_dir = Path(__file__).parent / 'forests' / 'room' / 'data' / 'companies_house'
    ch_files = list(ch_dir.glob('*.jsonl')) if ch_dir.exists() else []
    gardens['ukgraph'] = {
        "ons_files": len(ons_files),
        "companies_house_files": len(ch_files),
        "latest_ons": ons_files[-1].stem if ons_files else None,
        "latest_ch": ch_files[-1].stem if ch_files else None,
        "status": "ok" if (ons_files or ch_files) else "no_data",
    }

    # PowPowPow
    chains_dir = Path(os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow')) / 'chains'
    chain_data_files = list(chains_dir.glob('*/*_data.json')) if chains_dir.exists() else []
    gardens['powpowpow'] = {
        "chain_files": len(chain_data_files),
        "chains_with_data": [f.parent.name for f in chain_data_files],
        "status": "ok" if chain_data_files else "no_data",
    }

    # UK Admin
    uk_admin_dir = Path(__file__).parent / 'forests' / 'uk_admin' / 'data'
    uk_admin_files = list(uk_admin_dir.glob('**/*.jsonl')) if uk_admin_dir.exists() else []
    uk_admin_json = list(uk_admin_dir.glob('**/*.json')) if uk_admin_dir.exists() else []
    gardens['ukadmin'] = {
        "data_files": len(uk_admin_files) + len(uk_admin_json),
        "status": "ok" if uk_admin_files or uk_admin_json else "no_data",
    }

    return {"status": "ok", "gardens": gardens, "timestamp": datetime.now().isoformat()}


def garden_cross_analysis(query: str) -> dict:
    """Cross-garden analysis."""
    return {
        "status": "conceptual",
        "query": query,
        "message": "Cross-garden analysis is the highest-level function. Requires all three gardens populated. The connection pattern: AI capability improves -> compute demand changes (PowPowPow) -> GPU demand -> UK tech job demand (UKGraph) -> physical goods pricing changes (Breadup).",
    }


# ============================================================
# DISPATCHER
# ============================================================

# ============================================================
# CAPABILITY-FIRST IMPLEMENTATIONS (what people actually ask)
# ============================================================

def can_my_pc_make_money(gpu: str, electricity_rate: float = 0.15) -> dict:
    """Can this gaming PC make me money?"""
    sys.path.insert(0, str(Path(__file__).parent / 'capabilities'))
    try:
        from evaluate_hardware import evaluate_hardware
        return evaluate_hardware(gpu, electricity_rate)
    except ImportError:
        return {"error": "evaluate_hardware module not found"}


def what_should_i_mine(gpu: str, electricity_rate: float = 0.15) -> dict:
    """What should I mine with this GPU today?"""
    sys.path.insert(0, str(Path(__file__).parent / 'capabilities'))
    try:
        from evaluate_hardware import find_compute_opportunity
        return find_compute_opportunity(electricity_rate)
    except ImportError:
        return {"error": "evaluate_hardware module not found"}


def mine_or_rent(gpu: str, count: int = 1, electricity_rate: float = 0.15) -> dict:
    """Is it better to mine or rent out my GPUs?"""
    sys.path.insert(0, str(Path(__file__).parent / 'capabilities'))
    try:
        from evaluate_hardware import evaluate_hardware
    except ImportError:
        return {"error": "evaluate_hardware module not found"}
    
    mining = evaluate_hardware(gpu, electricity_rate)
    
    # Rough AI inference rental estimates (Vast.ai / RunPod ranges)
    RENTAL_RATES = {
        'RTX_4060': 0.12,
        'RTX_4060_TI': 0.16,
        'RTX_4070': 0.22,
        'RTX_4070_TI': 0.30,
        'RTX_4080': 0.40,
        'RTX_4090': 0.70,
        'RX_7900_XTX': 0.35,
        'RX_7800_XT': 0.20,
    }
    
    rental_per_hour = RENTAL_RATES.get(gpu, 0.20)
    rental_per_day = rental_per_hour * 24 * count
    mining_per_day = mining.get('daily_if_best', 0) * count
    
    return {
        'gpu': gpu,
        'count': count,
        'mining': {
            'daily_gbp': round(mining_per_day, 2),
            'monthly_gbp': round(mining_per_day * 30, 2),
            'best_network': mining.get('best_option', {}).get('network', 'none'),
        },
        'renting': {
            'daily_gbp': round(rental_per_day, 2),
            'monthly_gbp': round(rental_per_day * 30, 2),
            'rate_per_hour': rental_per_hour,
        },
        'winner': 'renting' if rental_per_day > mining_per_day else 'mining',
        'difference_per_day': round(abs(rental_per_day - mining_per_day), 2),
    }


def my_mining_portfolio(gpus: list, electricity_rate: float = 0.15) -> dict:
    """How much would I make with multiple GPUs?"""
    sys.path.insert(0, str(Path(__file__).parent / 'capabilities'))
    try:
        from evaluate_hardware import portfolio_revenue
        return portfolio_revenue(gpus, electricity_rate)
    except ImportError:
        return {"error": "evaluate_hardware module not found"}


def british_shortages(region: str = None) -> dict:
    """What is Britain running out of?"""
    data_dir = Path(__file__).parent / 'forests' / 'room' / 'data' / 'ons'
    
    if not data_dir.exists() or not any(data_dir.glob('*.jsonl')):
        return {"status": "no_data", "message": "No UKGraph data collected yet"}
    
    # Search for vacancy and shortage-related bulletins
    results = []
    for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:30]:
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    data = item.get('data', {})
                    title = data.get('title', '').lower()
                    summary = data.get('summary', '').lower()
                    if any(kw in title or kw in summary for kw in ['vacanc', 'shortage', 'skill', 'labour', 'employment', 'earnings']):
                        results.append({
                            'title': data.get('title', ''),
                            'summary': data.get('summary', '')[:200],
                            'type': data.get('type', item.get('data_type', '')),
                            'release_date': data.get('release_date', ''),
                        })
                except json.JSONDecodeError:
                    continue
    
    return {
        'status': 'ok',
        'region': region,
        'data_points': len(results),
        'bulletins': results[:5],
        'message': 'Based on ONS labour market data. For specific regional analysis, run the full UKGraph collector.',
    }


def is_this_a_bargain(item: str, asking_price: float, platform: str = 'facebook') -> dict:
    """Is this listing actually a bargain?"""
    # Try Breadup valuation
    data_dir = Path(__file__).parent / 'forests' / 'breadup' / 'data' / 'ebay_sold'
    
    if not data_dir.exists() or not any(data_dir.glob('*.jsonl')):
        return {
            'status': 'no_data',
            'item': item,
            'asking_price': asking_price,
            'message': 'No Breadup data available. Need eBay sold data to compare.',
        }
    
    # Search for comparable items
    results = []
    for f in sorted(data_dir.glob('*.jsonl'), reverse=True)[:7]:
        with open(f) as fh:
            for line in fh:
                try:
                    data = json.loads(line)
                    title = data.get('title', '').lower()
                    if any(word in title for word in item.lower().split()):
                        results.append(data)
                except json.JSONDecodeError:
                    continue
    
    if not results:
        return {
            'status': 'not_found',
            'item': item,
            'asking_price': asking_price,
            'message': f"No comparable sales found for '{item}'",
        }
    
    prices = [r.get('soldPrice', r.get('sold_price', 0)) for r in results if r.get('soldPrice') or r.get('sold_price')]
    if not prices:
        return {'status': 'no_prices', 'item': item}
    
    median = sorted(prices)[len(prices) // 2]
    below_market = asking_price < median
    savings_pct = ((median - asking_price) / median * 100) if below_market else ((asking_price - median) / median * 100)
    
    return {
        'status': 'ok',
        'item': item,
        'asking_price': asking_price,
        'platform': platform,
        'market_median': median,
        'comparable_sales': len(prices),
        'verdict': 'BARGAIN' if below_market else 'OVERPRICED',
        'savings_pct': round(savings_pct, 1),
        'suggestion': f"Offer £{round(median * 0.85)}" if below_market else f"Market median is £{median} — offer less",
    }


# ============================================================
# UK ADMIN IMPLEMENTATIONS
# ============================================================

UK_ADMIN_TASKS = {
    'renew_driving_licence': {
        'task_name': 'Renew your driving licence', 'category': 'driving',
        'authority': 'DVLA', 'url': 'https://www.gov.uk/renew-driving-licence',
        'cost_gbp': 14.00, 'takes_time': '3 weeks',
        'requires': ['identity', 'licence_details', 'address', 'photo'],
        'how_to': ['1. Go to https://www.gov.uk/renew-driving-licence', '2. Enter licence number, addresses for 3 years, photo', '3. Pay £14', '4. Licence arrives in ~3 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
        'related_tasks': ['update_address', 'replace_lost_licence'],
    },
    'replace_lost_licence': {
        'task_name': 'Replace a lost or stolen driving licence', 'category': 'driving',
        'authority': 'DVLA', 'url': 'https://www.gov.uk/replace-driving-licence',
        'cost_gbp': 20.00, 'takes_time': '3 weeks',
        'requires': ['identity', 'address', 'photo'],
        'how_to': ['1. Report to police if stolen', '2. Go to https://www.gov.uk/replace-driving-licence', '3. Pay £20', '4. Licence arrives in ~3 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
        'related_tasks': ['renew_driving_licence'],
    },
    'update_address': {
        'task_name': 'Change address on driving licence', 'category': 'driving',
        'authority': 'DVLA', 'url': 'https://www.gov.uk/change-address-driving-licence',
        'cost_gbp': 0.0, 'takes_time': '3 weeks',
        'requires': ['identity', 'new_address'],
        'how_to': ['1. Go to https://www.gov.uk/change-address-driving-licence', '2. Enter licence number and new address', '3. Free', '4. Updated licence in ~3 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
        'related_tasks': ['renew_driving_licence', 'update_vehicle_tax'],
    },
    'check_mot': {
        'task_name': 'Check MOT history', 'category': 'vehicle',
        'authority': 'DVSA', 'url': 'https://www.gov.uk/check-mot-history',
        'cost_gbp': 0.0, 'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'how_to': ['1. Go to https://www.gov.uk/check-mot-history', '2. Enter registration', '3. See history, advisories, expiry'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
        'related_tasks': ['book_mot', 'check_vehicle_tax'],
    },
    'book_mot': {
        'task_name': 'Book an MOT', 'category': 'vehicle',
        'authority': 'DVSA', 'url': 'https://www.gov.uk/get-mot',
        'cost_gbp': 54.85, 'takes_time': '1 hour',
        'requires': ['vehicle_registration'],
        'how_to': ['1. Go to https://www.gov.uk/get-mot', '2. Enter registration', '3. Find a garage (max £54.85)', '4. Book and attend'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': False, 'submit': False, 'payment': 'explicit_approval'},
        'is_recurring': True, 'recurrence': 'every 12 months',
        'related_tasks': ['check_mot'],
    },
    'check_vehicle_tax': {
        'task_name': 'Check vehicle tax', 'category': 'vehicle',
        'authority': 'DVLA', 'url': 'https://www.gov.uk/check-vehicle-tax',
        'cost_gbp': 0.0, 'takes_time': 'instant',
        'requires': ['vehicle_registration'],
        'how_to': ['1. Go to https://www.gov.uk/check-vehicle-tax', '2. Enter registration', '3. See tax status and expiry'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
        'related_tasks': ['update_vehicle_tax'],
    },
    'self_assessment_register': {
        'task_name': 'Register for Self Assessment', 'category': 'tax',
        'authority': 'HMRC', 'url': 'https://www.gov.uk/register-for-self-assessment',
        'cost_gbp': 0.0, 'takes_time': '10 working days',
        'requires': ['identity', 'national_insurance_number'],
        'how_to': ['1. Go to https://www.gov.uk/register-for-self-assessment', '2. Need Government Gateway account', '3. Enter NI number', '4. HMRC sends UTR'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
        'related_tasks': ['self_assessment_submit'],
    },
    'self_assessment_submit': {
        'task_name': 'Complete Self Assessment tax return', 'category': 'tax',
        'authority': 'HMRC', 'url': 'https://www.gov.uk/self-assessment-tax-returns',
        'cost_gbp': 0.0, 'takes_time': '1-3 hours',
        'requires': ['identity', 'national_insurance_number', 'income_details'],
        'how_to': ['1. Log in to Government Gateway', '2. Fill in return', '3. Need P60, bank statements', '4. File by 31 January', '5. Pay tax owed'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
        'is_recurring': True, 'recurrence': 'annually by 31 January',
    },
    'apply_passport': {
        'task_name': 'Apply for a UK passport', 'category': 'passport',
        'authority': 'HM Passport Office', 'url': 'https://www.gov.uk/apply-renew-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'birth_certificate'],
        'how_to': ['1. Go to https://www.gov.uk/apply-renew-passport', '2. Need digital photo and countersignatory', '3. Fill online form', '4. Pay £82.50', '5. Passport in ~10 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
    },
    'renew_passport': {
        'task_name': 'Renew your passport', 'category': 'passport',
        'authority': 'HM Passport Office', 'url': 'https://www.gov.uk/renew-adult-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos', 'existing_passport'],
        'how_to': ['1. Go to https://www.gov.uk/renew-adult-passport', '2. Need current passport and new photo', '3. Pay £82.50', '4. Post old passport', '5. New passport in ~10 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
        'is_recurring': True, 'recurrence': 'every 10 years',
    },
    'replace_lost_passport': {
        'task_name': 'Replace lost or stolen passport', 'category': 'passport',
        'authority': 'HM Passport Office', 'url': 'https://www.gov.uk/replace-lost-stolen-passport',
        'cost_gbp': 82.50, 'takes_time': '10 weeks',
        'requires': ['identity', 'photos'],
        'how_to': ['1. Report lost/stolen: https://www.gov.uk/report-a-lost-or-stolen-passport', '2. Apply for replacement', '3. Pay £82.50', '4. Old passport cancelled immediately'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
    },
    'setup_sole_trader': {
        'task_name': 'Set up as a sole trader', 'category': 'business',
        'authority': 'HMRC', 'url': 'https://www.gov.uk/working-for-yourself',
        'cost_gbp': 0.0, 'takes_time': '10 working days',
        'requires': ['identity', 'national_insurance_number', 'business_details'],
        'how_to': ['1. Register as self-employed with HMRC', '2. Need Government Gateway account', '3. HMRC sends UTR', '4. Keep income/expense records', '5. File Self Assessment yearly'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
        'related_tasks': ['self_assessment_register'],
    },
    'register_limited_company': {
        'task_name': 'Register a limited company', 'category': 'business',
        'authority': 'Companies House', 'url': 'https://www.gov.uk/limited-company-formation',
        'cost_gbp': 12.0, 'takes_time': '24 hours',
        'requires': ['identity', 'registered_address', 'directors'],
        'how_to': ['1. Go to https://www.gov.uk/limited-company-formation', '2. Choose name (check availability)', '3. Provide address and directors', '4. Pay £12 online', '5. Registered in ~24 hours'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'explicit_approval'},
        'related_tasks': ['register_corporation_tax'],
    },
    'update_council_tax': {
        'task_name': 'Update council tax details', 'category': 'home',
        'authority': 'Local Council', 'url': 'https://www.gov.uk/council-tax',
        'cost_gbp': 0.0, 'takes_time': 'varies',
        'requires': ['identity', 'address', 'move_date'],
        'how_to': ['1. Find your council: https://www.gov.uk/find-local-council', '2. Contact to update address', '3. Notify both old and new councils if moving'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
    },
    'register_to_vote': {
        'task_name': 'Register to vote', 'category': 'home',
        'authority': 'Electoral Commission', 'url': 'https://www.gov.uk/register-to-vote',
        'cost_gbp': 0.0, 'takes_time': '2 weeks',
        'requires': ['identity', 'address', 'national_insurance_number'],
        'how_to': ['1. Go to https://www.gov.uk/register-to-vote', '2. Enter name, address, NI number', '3. Registration takes ~2 weeks', '4. Re-register when you move'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
    },
    'check_benefits': {
        'task_name': 'Check what benefits you can get', 'category': 'benefits',
        'authority': 'DWP', 'url': 'https://www.gov.uk/browse/child-disability-family/benefits',
        'cost_gbp': 0.0, 'takes_time': '5 minutes',
        'requires': ['identity', 'income_details'],
        'how_to': ['1. Use calculator: https://www.gov.uk/benefits-calculators', '2. Enter income and household details', '3. See eligibility'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': False, 'submit': False, 'payment': 'not_possible'},
    },
    'apply_universal_credit': {
        'task_name': 'Apply for Universal Credit', 'category': 'benefits',
        'authority': 'DWP', 'url': 'https://www.gov.uk/universal-credit/how-to-apply',
        'cost_gbp': 0.0, 'takes_time': '5-8 weeks',
        'requires': ['identity', 'income_details', 'housing_costs', 'bank_details'],
        'how_to': ['1. Go to https://www.gov.uk/universal-credit/how-to-apply', '2. Need Government Gateway and bank account', '3. Attend Jobcentre appointment', '4. First payment in ~5 weeks'],
        'agent_permissions': {'explain': True, 'gather_requirements': True, 'prefill': True, 'submit': False, 'payment': 'not_possible'},
    },
}


def _uk_admin_find_task(query):
    """Find a UK admin task by ID or fuzzy search."""
    q = query.lower().strip()
    if q in UK_ADMIN_TASKS:
        return UK_ADMIN_TASKS[q]
    for tid, task in UK_ADMIN_TASKS.items():
        if q.replace(' ', '_') == tid:
            return task
    for tid, task in UK_ADMIN_TASKS.items():
        if q in task['task_name'].lower():
            return task
    return None


def uk_admin_explain_task(task: str) -> dict:
    """How do I do X? Full walkthrough."""
    td = _uk_admin_find_task(task)
    if not td:
        available = {}
        for tid, t in UK_ADMIN_TASKS.items():
            available.setdefault(t['category'], []).append(tid)
        return {'status': 'not_found', 'query': task, 'available_tasks': available}
    return {
        'status': 'ok', 'task': td['task_name'], 'category': td['category'],
        'authority': td['authority'], 'url': td['url'],
        'cost': f"£{td['cost_gbp']:.2f}" if td['cost_gbp'] else 'Free',
        'time': td.get('takes_time', 'Unknown'), 'steps': td.get('how_to', []),
        'related_tasks': td.get('related_tasks', []),
        'recurring': td.get('is_recurring', False), 'recurrence': td.get('recurrence', ''),
    }


def uk_admin_check_requirements(task: str) -> dict:
    """What do I need for X?"""
    td = _uk_admin_find_task(task)
    if not td:
        return {'status': 'not_found', 'query': task}
    return {
        'status': 'ok', 'task': td['task_name'], 'url': td['url'],
        'requirements': td.get('requires', []), 'count': len(td.get('requires', [])),
    }


def uk_admin_can_agent_do_it(task: str) -> dict:
    """Can Muse handle this?"""
    td = _uk_admin_find_task(task)
    if not td:
        return {'status': 'not_found', 'query': task}
    perms = td.get('agent_permissions', {})
    agent_can = [k for k, v in perms.items() if v is True]
    user_must = [k for k, v in perms.items() if v is False]
    return {
        'status': 'ok', 'task': td['task_name'],
        'agent_can_do': agent_can, 'user_must_do': user_must, 'permissions': perms,
    }


def uk_admin_moving_house(new_address: str, move_date: str, old_address: str = '') -> dict:
    """I've moved house, what do I update?"""
    return {
        'status': 'ok', 'new_address': new_address, 'move_date': move_date,
        'checklist': [
            {'what': 'Update driving licence', 'authority': 'DVLA', 'cost': 'Free', 'url': 'https://www.gov.uk/change-address-driving-licence'},
            {'what': 'Update vehicle tax', 'authority': 'DVLA', 'cost': 'Free', 'url': 'https://www.gov.uk/vehicle-tax'},
            {'what': 'Update council tax', 'authority': 'Council', 'cost': 'Free', 'url': 'https://www.gov.uk/council-tax'},
            {'what': 'Register to vote', 'authority': 'Electoral Commission', 'cost': 'Free', 'url': 'https://www.gov.uk/register-to-vote'},
            {'what': 'Redirect post', 'authority': 'Royal Mail', 'cost': 'From £82.99', 'url': 'https://www.royalmail.com/redirection'},
        ],
        'tip': 'Start with DVLA and council tax - they have legal deadlines.',
    }


def uk_admin_lost_passport(was_stolen: bool = False) -> dict:
    """I lost my passport, what do I do?"""
    return {
        'status': 'ok', 'situation': 'stolen' if was_stolen else 'lost',
        'steps': [
            '1. Report: https://www.gov.uk/report-a-lost-or-stolen-passport',
            '2. Passport cancelled immediately',
            '3. Apply for replacement: https://www.gov.uk/replace-lost-stolen-passport',
            '4. Pay £82.50, new passport in ~10 weeks',
        ],
        'cost': '£82.50', 'time': '10 weeks',
    }


def uk_admin_tax_obligations(situation: str) -> dict:
    """What do I need to file this year?"""
    sit = situation.lower()
    obligations = []
    if 'sole_trader' in sit or 'self_employed' in sit:
        obligations = [
            {'form': 'Self Assessment', 'deadline': '31 January'},
            {'form': 'Payment on account', 'deadline': '31 July'},
        ]
    elif 'company' in sit or 'limited' in sit:
        obligations = [
            {'form': 'Company Tax Return', 'deadline': '12 months after period end'},
            {'form': 'Corporation Tax payment', 'deadline': '9 months + 1 day'},
            {'form': 'Annual Confirmation Statement', 'deadline': 'Yearly'},
        ]
    else:
        obligations = [{'form': 'Check your tax account', 'deadline': 'Now'}]
    return {'status': 'ok', 'situation': situation, 'obligations': obligations}


def uk_admin_benefits_check(situation: str) -> dict:
    """What benefits might I qualify for?"""
    sit = situation.lower()
    benefits = []
    if any(w in sit for w in ['kid', 'child', 'family']):
        benefits.append({'benefit': 'Child Benefit', 'amount': '£25.60/week'})
    if any(w in sit for w in ['disabled', 'mobility']):
        benefits.append({'benefit': 'PIP', 'amount': '£72.65-£184.25/week'})
    if any(w in sit for w in ['unemploy', 'jobseek']):
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Up to £393.45/month'})
    if not benefits:
        benefits.append({'benefit': 'Universal Credit', 'amount': 'Varies'})
    return {'status': 'ok', 'situation': situation, 'possible_benefits': benefits,
            'calculator': 'https://www.gov.uk/benefits-calculators'}


def uk_admin_company_setup(company_name: str = '', sector: str = '') -> dict:
    """Set up a company for this side project."""
    return {
        'status': 'ok', 'company_name': company_name,
        'steps': [
            '1. Choose name (check at Companies House)', '2. Register: https://www.gov.uk/limited-company-formation',
            '3. Pay £12 online', '4. Registered in ~24 hours', '5. Register for Corporation Tax',
        ],
        'cost': '£12', 'time': '24 hours',
    }


DISPATCH = {
    "breadup_valuation": breadup_valuation,
    "breadup_mispricing": breadup_mispricing,
    "breadup_price_history": breadup_price_history,
    "breadup_cross_market_spread": breadup_cross_market_spread,
    "ukgraph_career_crowding": ukgraph_career_crowding,
    "ukgraph_trade_demand": ukgraph_trade_demand,
    "ukgraph_business_gap": ukgraph_business_gap,
    "ukgraph_regulation_impact": ukgraph_regulation_impact,
    "ukgraph_salary_data": ukgraph_salary_data,
    "pow_network_status": pow_network_status,
    "pow_mining_profitability": pow_mining_profitability,
    "pow_best_mining": pow_best_mining,
    "pow_compare_networks": pow_compare_networks,
    "pow_all_networks": pow_all_networks,
    "pow_hashrate_migration": pow_hashrate_migration,
    "garden_health": garden_health,
    "garden_cross_analysis": garden_cross_analysis,
    "can_my_pc_make_money": can_my_pc_make_money,
    "what_should_i_mine": what_should_i_mine,
    "mine_or_rent": mine_or_rent,
    "my_mining_portfolio": my_mining_portfolio,
    "british_shortages": british_shortages,
    "is_this_a_bargain": is_this_a_bargain,
    "uk_admin_explain_task": uk_admin_explain_task,
    "uk_admin_check_requirements": uk_admin_check_requirements,
    "uk_admin_can_agent_do_it": uk_admin_can_agent_do_it,
    "uk_admin_moving_house": uk_admin_moving_house,
    "uk_admin_lost_passport": uk_admin_lost_passport,
    "uk_admin_tax_obligations": uk_admin_tax_obligations,
    "uk_admin_benefits_check": uk_admin_benefits_check,
    "uk_admin_company_setup": uk_admin_company_setup,
}


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Dispatch a tool call."""
    func = DISPATCH.get(tool_name)
    if not func:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return func(**arguments)
    except TypeError as e:
        return {"error": f"Invalid arguments for {tool_name}: {e}"}
    except Exception as e:
        return {"error": f"Tool {tool_name} failed: {e}"}


# ============================================================
# MCP STDIO SERVER (for AI agents)
# ============================================================

def run_mcp_stdio():
    """Run as an MCP server over stdin/stdout."""
    server_info = {
        "name": "datagarden",
        "version": "1.0.0",
        "description": "DataGarden — economic reality engine. Four data forests: Breadup (physical goods), UKGraph (UK markets), PowPowPow (compute economics), UKAdmin (government tasks).",
        "tools": TOOLS,
    }

    # Respond to MCP protocol messages
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
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": server_info,
                },
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS},
            }
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = handle_tool_call(tool_name, arguments)
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]
                },
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        print(json.dumps(response), flush=True)


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--serve':
        run_mcp_stdio()
    elif len(sys.argv) > 2:
        tool = sys.argv[1]
        args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        result = handle_tool_call(tool, args)
        print(json.dumps(result, indent=2, default=str))
    else:
        info = {
            "name": "DataGarden MCP Server",
            "version": "1.0.0",
            "tools": [t["name"] for t in TOOLS],
            "usage": {
                "cli": "python mcp_server.py <tool_name> '<json_args>'",
                "mcp": "python mcp_server.py --serve  (stdio transport)",
                "example": "python mcp_server.py breadup_valuation '{\"query\": \"Roland SP-404\"}'"
            }
        }
        print(json.dumps(info, indent=2))
