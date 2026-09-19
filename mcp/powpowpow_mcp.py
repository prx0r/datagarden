#!/usr/bin/env python3
"""
PowPowPow MCP Server — Compute Economics Engine

Tools:
- network_status: Current hashrate, difficulty, price for a chain
- mining_profitability: Profitability calc for hardware on a network
- best_mining: Find most profitable network for given hardware
- compare_networks: Compare mining across multiple networks
- all_networks: Get all tracked networks
- hashrate_migration: Where hashrate is moving over time
- can_my_pc_make_money: Answer the question for a specific GPU
- what_should_i_mine: Find compute opportunity for hardware
- mine_or_rent: Compare mining vs renting GPU
- portfolio_revenue: Total revenue for a GPU portfolio
- emission_forecast: Token emission forecast for a network
- pool_risk_assessment: Pool safety analysis for a network

Usage:
    python powpowpow_mcp.py                     # List tools
    python powpowpow_mcp.py <tool> '<json>'     # Call tool
    python powpowpow_mcp.py --serve             # MCP stdio server
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

ROOT = Path(os.environ.get('POWPOWPOW_DIR', '/home/box/powpowpow'))
CHAINS_DIR = ROOT / 'chains'
sys.path.insert(0, str(ROOT))

# ============================================================
# HARDWARE DEFINITIONS
# ============================================================

COMMON_HARDWARE = {
    'RTX_4060': {'name': 'RTX 4060', 'cost_gbp': 299, 'power_watts': 115},
    'RTX_4070': {'name': 'RTX 4070', 'cost_gbp': 499, 'power_watts': 200},
    'RTX_4080': {'name': 'RTX 4080', 'cost_gbp': 899, 'power_watts': 320},
    'RTX_4090': {'name': 'RTX 4090', 'cost_gbp': 1599, 'power_watts': 450},
    'RX_7900_XTX': {'name': 'RX 7900 XTX', 'cost_gbp': 899, 'power_watts': 355},
}

# ============================================================
# TOOLS
# ============================================================

TOOLS = [
    {
        "name": "network_status",
        "description": "Get current hashrate, difficulty, and price for a mining network.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol (XMR, KAS, PRL, QUBIC, etc)"}
            },
            "required": ["network"]
        }
    },
    {
        "name": "mining_profitability",
        "description": "Calculate mining profitability for specific hardware on a network. Returns revenue, electricity cost, and net profit per day.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol (XMR, KAS, PRL, etc)"},
                "hardware": {"type": "string", "description": "Hardware model (RTX_4090, Ryzen_9_7950X, KS5_Pro, etc)"},
                "electricity_cost": {"type": "number", "description": "Electricity cost in $/kWh (default 0.10)"}
            },
            "required": ["network", "hardware"]
        }
    },
    {
        "name": "best_mining",
        "description": "Find the most profitable network to mine with given hardware right now.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hardware": {"type": "string", "description": "Hardware model (RTX_4090, Ryzen_9_7950X, etc)"},
                "electricity_cost": {"type": "number", "description": "Electricity cost in $/kWh (default 0.10)"}
            },
            "required": ["hardware"]
        }
    },
    {
        "name": "compare_networks",
        "description": "Compare mining economics across multiple networks side by side.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "networks": {"type": "array", "items": {"type": "string"}, "description": "List of network symbols to compare"},
                "hardware": {"type": "string", "description": "Hardware model to compare across networks"}
            },
            "required": ["networks"]
        }
    },
    {
        "name": "all_networks",
        "description": "Get all tracked networks with their current status and category.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "hashrate_migration",
        "description": "Show where hashrate is moving — which networks are gaining or losing compute power.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Days of history to analyze (default 7)"}
            }
        }
    },
    {
        "name": "can_my_pc_make_money",
        "description": "Answer: can my PC actually make money mining? Takes a GPU name and electricity rate, returns a clear yes/no with daily profit breakdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model (RTX_4060, RTX_4070, RTX_4090, RX_7900_XTX)"},
                "electricity_rate": {"type": "number", "description": "Electricity rate in $/kWh (default 0.10)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "what_should_i_mine",
        "description": "Given your hardware, find the best compute opportunity — mining, AI inference, or rental income.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model"},
                "electricity_rate": {"type": "number", "description": "Electricity rate in $/kWh (default 0.10)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "mine_or_rent",
        "description": "Compare mining profitability vs renting out your GPU on compute marketplaces.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpu": {"type": "string", "description": "GPU model"},
                "count": {"type": "integer", "description": "Number of GPUs (default 1)"},
                "electricity_rate": {"type": "number", "description": "Electricity rate in $/kWh (default 0.10)"}
            },
            "required": ["gpu"]
        }
    },
    {
        "name": "portfolio_revenue",
        "description": "Calculate total daily revenue for a portfolio of GPUs across all profitable networks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "gpus": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "GPU model"},
                            "count": {"type": "integer", "description": "Number of this GPU"}
                        }
                    },
                    "description": "List of GPU models and quantities"
                },
                "electricity_rate": {"type": "number", "description": "Electricity rate in $/kWh (default 0.10)"}
            },
            "required": ["gpus"]
        }
    },
    {
        "name": "emission_forecast",
        "description": "Forecast token emissions for a network — daily, monthly, and annual emission rates with USD value.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol (XMR, PRL, QUBIC, etc)"}
            },
            "required": ["network"]
        }
    },
    {
        "name": "pool_risk_assessment",
        "description": "Assess pool centralization risk and mining safety for a network.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network": {"type": "string", "description": "Network symbol"}
            },
            "required": ["network"]
        }
    },
]

# ============================================================
# DATA LOADING HELPERS
# ============================================================

def _load_chain_data(symbol):
    """Load chain data from JSON file."""
    s = symbol.lower()
    data_file = CHAINS_DIR / s / f'{s}_data.json'
    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)
    return {}

def _load_fundamentals():
    """Load chain fundamentals registry."""
    f = CHAINS_DIR / 'chain_fundamentals.json'
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {}

def _load_economics():
    """Load miner economics data."""
    f = CHAINS_DIR / 'economics' / 'miner_economics.json'
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {}

def _load_real_stats():
    """Load real chain stats."""
    f = CHAINS_DIR / 'real_chain_stats.json'
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {}

def _load_registry():
    """Load V1 registry."""
    try:
        from v1_registry import get_v1, get_v1_coin
        return get_v1()
    except ImportError:
        return {}

def _get_price(data):
    """Extract USD price from chain data."""
    price = data.get('price')
    if isinstance(price, dict):
        return price.get('usd', 0) or 0
    if isinstance(price, (int, float)):
        return price
    return 0

def _generate_card(symbol, price_usd):
    """Generate profitability card using v1_live_cards."""
    try:
        from v1_live_cards import generate_card
        return generate_card(symbol, price_usd)
    except ImportError:
        return {'coin': symbol, 'price_usd': price_usd, 'hardware': {}}

def _all_chain_symbols():
    """Get all chain symbols that have data files."""
    symbols = []
    for d in sorted(CHAINS_DIR.iterdir()):
        if d.is_dir() and (d / f'{d.name}_data.json').exists():
            symbols.append(d.name.upper())
    return symbols

def _get_network_data(symbol):
    """Get full network data: fundamentals, data, real_stats, economics."""
    s = symbol.upper()
    return {
        'fundamentals': _load_fundamentals().get(s, {}),
        'data': _load_chain_data(s),
        'real_stats': _load_real_stats().get(s, {}),
        'economics': _load_economics().get(s, {}),
        'registry': _load_registry().get(s, {}),
    }

# ============================================================
# IMPLEMENTATIONS
# ============================================================

def network_status(network: str) -> dict:
    """Get current hashrate, difficulty, and price for a network."""
    net = network.upper()
    data = _load_chain_data(net)
    fundamentals = _load_fundamentals().get(net, {})
    real_stats = _load_real_stats().get(net, {})
    registry = _load_registry().get(net, {})

    price_usd = _get_price(data)

    hashrate = None
    difficulty = None
    block_reward = None
    block_time = None

    # Try real_stats first
    stats = real_stats.get('stats', {})
    if stats:
        hashrate = stats.get('hashrate')
        difficulty = stats.get('difficulty')
        block_reward = stats.get('block_reward')
        block_time = stats.get('block_time')

    # Try localmonero for XMR
    lm = data.get('localmonero', {})
    if lm:
        hashrate = lm.get('hashrate', hashrate)
        difficulty = lm.get('difficulty', difficulty)
        block_reward = lm.get('last_reward', block_reward)
        if block_reward and isinstance(block_reward, (int, float)):
            block_reward = block_reward / 1e12

    # Try network data
    net_data = data.get('network', {})
    if isinstance(net_data, dict):
        hashrate = net_data.get('hashrate', hashrate)

    return {
        'network': net,
        'name': fundamentals.get('name', registry.get('name', net)),
        'category': fundamentals.get('type', registry.get('category', 'unknown')),
        'mining_algo': fundamentals.get('mining_algo', 'unknown'),
        'hardware_type': fundamentals.get('hardware', registry.get('physical_resource', 'unknown')),
        'price_usd': price_usd,
        'hashrate': hashrate,
        'difficulty': difficulty,
        'block_reward': block_reward,
        'block_time': block_time,
        'daily_emission': fundamentals.get('daily_emission'),
        'daily_emission_usd': fundamentals.get('daily_emission_usd'),
        'circulating_supply': fundamentals.get('circulating_supply'),
        'max_supply': fundamentals.get('max_supply'),
        'volume_24h': fundamentals.get('safe_trade_volume_24h'),
        'github': fundamentals.get('github'),
        'github_stars': fundamentals.get('github_stars'),
        'timestamp': data.get('timestamp'),
    }


def mining_profitability(network: str, hardware: str, electricity_cost: float = 0.10) -> dict:
    """Calculate mining profitability for specific hardware on a network."""
    net = network.upper()
    hw = hardware
    data = _load_chain_data(net)
    price_usd = _get_price(data)

    if not price_usd:
        return {'error': f'No price data for {net}', 'network': net}

    card = _generate_card(net, price_usd)
    hw_data = card.get('hardware', {})

    # Direct match
    if hw in hw_data:
        result = dict(hw_data[hw])
        result['network'] = net
        result['hardware'] = hw
        result['electricity_rate'] = electricity_cost
        result['status'] = 'profitable' if result.get('net_profit_usd_day', 0) > 0 else 'unprofitable'
        return result

    # Try case-insensitive match
    hw_lower = hw.lower()
    for k, v in hw_data.items():
        if k.lower() == hw_lower:
            result = dict(v)
            result['network'] = net
            result['hardware'] = hw
            result['electricity_rate'] = electricity_cost
            result['status'] = 'profitable' if result.get('net_profit_usd_day', 0) > 0 else 'unprofitable'
            return result

    # Fallback: calculate from COMMON_HARDWARE if we know the power
    hw_info = COMMON_HARDWARE.get(hw.upper()) or COMMON_HARDWARE.get(hw)
    if hw_info:
        power_w = hw_info['power_watts']
        daily_electricity = (power_w / 1000) * 24 * electricity_cost
        daily_hw_cost = (hw_info.get('cost_gbp', 0) * 1.25) / (3 * 365)  # assume 3yr amort, GBP->USD ~1.25

        # Estimate from fundamentals
        fundamentals = _load_fundamentals().get(net, {})
        daily_emission_usd = fundamentals.get('daily_emission_usd', 0) or 0

        return {
            'network': net,
            'hardware': hw,
            'hashrate': None,
            'power_watts': power_w,
            'revenue_usd_day': None,
            'electricity_usd_day': round(daily_electricity, 4),
            'hw_amort_usd_day': round(daily_hw_cost, 4),
            'net_profit_usd_day': None,
            'status': 'no_hashrate_data',
            'note': f'No hashrate data for {hw} on {net}. Daily electricity: ${daily_electricity:.2f}',
            'daily_emission_usd': daily_emission_usd,
        }

    return {'error': f'Hardware {hw} not found for {net}', 'available': list(hw_data.keys())}


def best_mining(hardware: str, electricity_cost: float = 0.10) -> dict:
    """Find the most profitable network for given hardware."""
    hw = hardware
    results = []
    errors = []

    for symbol in _all_chain_symbols():
        try:
            result = mining_profitability(symbol, hw, electricity_cost)
            if 'error' not in result:
                results.append(result)
            else:
                errors.append({'network': symbol, 'reason': result.get('error', 'unknown')})
        except Exception as e:
            errors.append({'network': symbol, 'reason': str(e)})

    # Also check compute rental networks
    rental_chains = ['CLORE', 'AKT', 'NOS']
    for symbol in rental_chains:
        if symbol not in [r['network'] for r in results]:
            data = _load_chain_data(symbol)
            price_usd = _get_price(data)
            if price_usd:
                card = _generate_card(symbol, price_usd)
                for k, v in card.get('hardware', {}).items():
                    rev = v.get('revenue_usd_day', 0) or 0
                    if rev > 0:
                        hw_info = COMMON_HARDWARE.get(hw.upper()) or COMMON_HARDWARE.get(hw)
                        power_w = hw_info['power_watts'] if hw_info else 200
                        elec = (power_w / 1000) * 24 * electricity_cost
                        net = rev - elec
                        results.append({
                            'network': symbol,
                            'hardware': hw,
                            'revenue_usd_day': rev,
                            'electricity_usd_day': round(elec, 4),
                            'net_profit_usd_day': round(net, 4),
                            'status': 'rental_income',
                            'algo': v.get('algo', 'rental'),
                        })

    # Sort by net profit
    results.sort(key=lambda x: x.get('net_profit_usd_day') or -999, reverse=True)

    best = results[0] if results else None
    return {
        'hardware': hw,
        'electricity_cost': electricity_cost,
        'best_option': best,
        'all_options': results,
        'analyzed_networks': len(results),
        'errors': errors[:5],
    }


def compare_networks(networks: list, hardware: str = None) -> dict:
    """Compare mining economics across multiple networks."""
    results = []
    for net in networks:
        net_upper = net.upper()
        data = _load_chain_data(net_upper)
        fundamentals = _load_fundamentals().get(net_upper, {})
        price_usd = _get_price(data)
        registry = _load_registry().get(net_upper, {})

        entry = {
            'network': net_upper,
            'name': fundamentals.get('name', registry.get('name', net_upper)),
            'price_usd': price_usd,
            'category': fundamentals.get('type', 'unknown'),
            'mining_algo': fundamentals.get('mining_algo', 'unknown'),
            'daily_emission': fundamentals.get('daily_emission'),
            'daily_emission_usd': fundamentals.get('daily_emission_usd'),
            'volume_24h': fundamentals.get('safe_trade_volume_24h'),
            'hardware': {},
        }

        if hardware and price_usd:
            card = _generate_card(net_upper, price_usd)
            hw_data = card.get('hardware', {})
            # Match hardware
            for k, v in hw_data.items():
                if k.lower() == hardware.lower():
                    entry['hardware'] = v
                    break
            # If no match, try any hardware with revenue
            if not entry['hardware'] and hw_data:
                for k, v in hw_data.items():
                    if v.get('revenue_usd_day', 0) > 0:
                        entry['hardware'] = v
                        entry['hardware']['_actual_model'] = k
                        break

        results.append(entry)

    # Rank by emission USD if available
    results.sort(key=lambda x: x.get('daily_emission_usd') or 0, reverse=True)

    return {
        'networks': results,
        'hardware_filter': hardware,
        'count': len(results),
    }


def all_networks() -> dict:
    """Get all tracked networks with status and category."""
    fundamentals = _load_fundamentals()
    registry = _load_registry()
    networks = []

    for symbol in _all_chain_symbols():
        data = _load_chain_data(symbol)
        fund = fundamentals.get(symbol, {})
        reg = registry.get(symbol, {})
        price_usd = _get_price(data)

        networks.append({
            'symbol': symbol,
            'name': fund.get('name', reg.get('name', symbol)),
            'category': fund.get('type', reg.get('category', 'unknown')),
            'mining_algo': fund.get('mining_algo', 'unknown'),
            'hardware_type': fund.get('hardware', reg.get('physical_resource', 'unknown')),
            'price_usd': price_usd,
            'daily_emission': fund.get('daily_emission'),
            'daily_emission_usd': fund.get('daily_emission_usd'),
            'volume_24h': fund.get('safe_trade_volume_24h'),
            'github_stars': fund.get('github_stars'),
            'pools': reg.get('pools', []),
        })

    # Categorize
    categories = defaultdict(list)
    for n in networks:
        categories[n['category']].append(n['symbol'])

    return {
        'total_networks': len(networks),
        'networks': networks,
        'categories': dict(categories),
    }


def hashrate_migration(days: int = 7) -> dict:
    """Show where hashrate is moving — gaining or losing compute power."""
    # Load current stats
    real_stats = _load_real_stats()
    fundamentals = _load_fundamentals()
    economics = _load_economics()

    migrations = []

    for symbol in _all_chain_symbols():
        stats = real_stats.get(symbol, {}).get('stats', {})
        fund = fundamentals.get(symbol, {})
        econ = economics.get(symbol, {})
        data = _load_chain_data(symbol)

        current_hashrate = stats.get('hashrate')
        if current_hashrate is None:
            lm = data.get('localmonero', {})
            current_hashrate = lm.get('hashrate')

        # Calculate implied trends from sell pressure and absorption
        sell_pressure = fund.get('sell_pressure_daily', 0) or 0
        daily_emission_usd = fund.get('daily_emission_usd', 0) or 0
        volume_24h = fund.get('safe_trade_volume_24h', 0) or 0
        absorption = fund.get('absorption_ratio')
        dilution = fund.get('dilution_pressure')

        # Signal: if sell pressure < emission, network is being absorbed = hashrate attractive
        if daily_emission_usd > 0:
            absorption_score = volume_24h / daily_emission_usd if daily_emission_usd else None
        else:
            absorption_score = None

        # Direction heuristic
        if absorption_score is not None:
            if absorption_score > 10:
                direction = 'attracting'
                signal = 'strong_absorption'
            elif absorption_score > 2:
                direction = 'stable'
                signal = 'moderate_absorption'
            else:
                direction = 'leaking'
                signal = 'weak_absorption'
        else:
            direction = 'unknown'
            signal = 'no_data'

        migrations.append({
            'symbol': symbol,
            'name': fund.get('name', symbol),
            'current_hashrate': current_hashrate,
            'daily_emission_usd': daily_emission_usd,
            'volume_24h': volume_24h,
            'sell_pressure_daily': sell_pressure,
            'absorption_ratio': absorption,
            'dilution_pressure': dilution,
            'absorption_score': round(absorption_score, 1) if absorption_score else None,
            'direction': direction,
            'signal': signal,
        })

    # Sort by direction
    dir_order = {'attracting': 0, 'stable': 1, 'unknown': 2, 'leaking': 3}
    migrations.sort(key=lambda x: dir_order.get(x['direction'], 99))

    attracting = [m['symbol'] for m in migrations if m['direction'] == 'attracting']
    leaking = [m['symbol'] for m in migrations if m['direction'] == 'leaking']

    return {
        'period_days': days,
        'attracting_hashrate': attracting,
        'losing_hashrate': leaking,
        'networks': migrations,
        'summary': f'{len(attracting)} networks attracting hashrate, {len(leaking)} losing hashrate',
    }


def can_my_pc_make_money(gpu: str, electricity_rate: float = 0.10) -> dict:
    """Answer: can my PC actually make money mining?"""
    gpu_upper = gpu.upper().replace(' ', '_')

    # Get best option
    best = best_mining(gpu_upper, electricity_rate)
    best_option = best.get('best_option')

    hw_info = COMMON_HARDWARE.get(gpu_upper) or COMMON_HARDWARE.get(gpu)

    if not best_option:
        return {
            'gpu': gpu,
            'electricity_rate': electricity_rate,
            'answer': 'NO',
            'reason': f'No profitable mining found for {gpu} at ${electricity_rate}/kWh',
            'hardware_cost_gbp': hw_info['cost_gbp'] if hw_info else None,
            'power_watts': hw_info['power_watts'] if hw_info else None,
            'best_option': None,
        }

    net_profit = best_option.get('net_profit_usd_day', 0)
    revenue = best_option.get('revenue_usd_day', 0)
    electricity = best_option.get('electricity_usd_day', 0)
    power_w = best_option.get('power_watts', hw_info['power_watts'] if hw_info else 0)

    if net_profit > 0:
        answer = 'YES'
        monthly = net_profit * 30
        annual = net_profit * 365
        hw_cost = hw_info['cost_gbp'] * 1.25 if hw_info else 0  # GBP to USD
        payback_days = hw_cost / net_profit if net_profit > 0 else None

        reason = (f'Mine {best_option["network"]} for ${net_profit:.2f}/day. '
                  f'${monthly:.0f}/month, ${annual:.0f}/year.')
        if payback_days and payback_days < 365:
            reason += f' Hardware payback in {payback_days:.0f} days.'
    else:
        answer = 'BARELY'
        reason = (f'Best option is {best_option["network"]} but only ${net_profit:.4f}/day net. '
                  f'Electricity costs ${electricity:.2f}/day vs ${revenue:.2f}/day revenue.')

    return {
        'gpu': gpu,
        'electricity_rate': electricity_rate,
        'answer': answer,
        'daily_profit_usd': net_profit,
        'monthly_profit_usd': round(net_profit * 30, 2) if net_profit else 0,
        'annual_profit_usd': round(net_profit * 365, 2) if net_profit else 0,
        'best_network': best_option.get('network'),
        'daily_revenue': revenue,
        'daily_electricity': electricity,
        'power_watts': power_w,
        'hardware_cost_gbp': hw_info['cost_gbp'] if hw_info else None,
        'payback_days': round(hw_info['cost_gbp'] * 1.25 / net_profit) if hw_info and net_profit > 0 else None,
        'reason': reason,
    }


def what_should_i_mine(gpu: str, electricity_rate: float = 0.10) -> dict:
    """Find the best compute opportunity for hardware — mining, AI inference, or rental."""
    gpu_upper = gpu.upper().replace(' ', '_')
    hw_info = COMMON_HARDWARE.get(gpu_upper) or COMMON_HARDWARE.get(gpu)
    power_w = hw_info['power_watts'] if hw_info else 200

    opportunities = []

    # Check mining networks
    for symbol in _all_chain_symbols():
        try:
            result = mining_profitability(symbol, gpu_upper, electricity_rate)
            if 'error' not in result and result.get('revenue_usd_day') is not None:
                opportunities.append({
                    'type': 'mining',
                    'network': symbol,
                    'revenue_usd_day': result.get('revenue_usd_day', 0),
                    'electricity_usd_day': result.get('electricity_usd_day', 0),
                    'net_profit_usd_day': result.get('net_profit_usd_day', 0),
                    'algo': result.get('algo', 'unknown'),
                    'hashrate': result.get('hashrate'),
                })
        except Exception:
            continue

    # Check compute rental
    rental_networks = ['CLORE', 'AKT', 'NOS']
    for symbol in rental_networks:
        data = _load_chain_data(symbol)
        price_usd = _get_price(data)
        if price_usd:
            card = _generate_card(symbol, price_usd)
            for k, v in card.get('hardware', {}).items():
                rental_rev = v.get('revenue_usd_day', 0)
                if rental_rev > 0:
                    electricity_cost = (power_w / 1000) * 24 * electricity_rate
                    net = rental_rev - electricity_cost
                    opportunities.append({
                        'type': 'rental',
                        'network': symbol,
                        'revenue_usd_day': rental_rev,
                        'electricity_usd_day': round(electricity_cost, 4),
                        'net_profit_usd_day': round(net, 4),
                        'algo': v.get('algo', 'rental'),
                    })

    opportunities.sort(key=lambda x: x.get('net_profit_usd_day', -999), reverse=True)

    best = opportunities[0] if opportunities else None

    return {
        'gpu': gpu,
        'power_watts': power_w,
        'electricity_rate': electricity_rate,
        'best_opportunity': best,
        'all_opportunities': opportunities[:10],
        'recommendation': (
            f"Best: {best['type'].upper()} on {best['network']} for ${best['net_profit_usd_day']:.2f}/day"
            if best else "No profitable opportunity found"
        ),
    }


def mine_or_rent(gpu: str, count: int = 1, electricity_rate: float = 0.10) -> dict:
    """Compare mining profitability vs renting out GPU on compute marketplaces."""
    gpu_upper = gpu.upper().replace(' ', '_')
    hw_info = COMMON_HARDWARE.get(gpu_upper) or COMMON_HARDWARE.get(gpu)
    power_w = hw_info['power_watts'] if hw_info else 200
    hw_cost_gbp = hw_info['cost_gbp'] if hw_info else 0
    hw_cost_usd = hw_cost_gbp * 1.25

    electricity_daily_single = (power_w / 1000) * 24 * electricity_rate

    # Mining option
    mining_best = best_mining(gpu_upper, electricity_rate)
    mining_opt = mining_best.get('best_option')
    mining_revenue = mining_opt.get('revenue_usd_day', 0) if mining_opt else 0
    mining_profit = mining_opt.get('net_profit_usd_day', 0) if mining_opt else 0

    # Rental option
    rental_data = {}
    rental_networks = ['CLORE', 'AKT', 'NOS']
    for symbol in rental_networks:
        data = _load_chain_data(symbol)
        price_usd = _get_price(data)
        if price_usd:
            card = _generate_card(symbol, price_usd)
            for k, v in card.get('hardware', {}).items():
                rev = v.get('revenue_usd_day', 0)
                if rev > 0:
                    net = rev - electricity_daily_single
                    rental_data[symbol] = {
                        'revenue_usd_day': rev,
                        'net_profit_usd_day': round(net, 4),
                        'algo': v.get('algo', 'rental'),
                    }

    best_rental = max(rental_data.values(), key=lambda x: x['net_profit_usd_day']) if rental_data else None
    best_rental_network = max(rental_data, key=lambda k: rental_data[k]['net_profit_usd_day']) if rental_data else None

    # Portfolio scale
    mining_monthly = mining_profit * 30 * count
    mining_annual = mining_profit * 365 * count
    rental_monthly = (best_rental['net_profit_usd_day'] * 30 * count) if best_rental else 0
    rental_annual = (best_rental['net_profit_usd_day'] * 365 * count) if best_rental else 0

    total_investment = hw_cost_usd * count
    mining_roi = (mining_annual / total_investment * 100) if total_investment > 0 else 0
    rental_roi = (rental_annual / total_investment * 100) if total_investment > 0 else 0

    winner = 'mining' if mining_profit > (best_rental['net_profit_usd_day'] if best_rental else 0) else 'rental'

    return {
        'gpu': gpu,
        'count': count,
        'electricity_rate': electricity_rate,
        'total_investment_usd': total_investment,
        'mining': {
            'best_network': mining_opt.get('network') if mining_opt else None,
            'daily_revenue': mining_revenue * count,
            'daily_electricity': electricity_daily_single * count,
            'daily_profit': mining_profit * count,
            'monthly_profit': round(mining_monthly, 2),
            'annual_profit': round(mining_annual, 2),
            'annual_roi_pct': round(mining_roi, 1),
        },
        'rental': {
            'best_network': best_rental_network,
            'options': rental_data,
            'daily_profit': (best_rental['net_profit_usd_day'] * count) if best_rental else 0,
            'monthly_profit': round(rental_monthly, 2),
            'annual_profit': round(rental_annual, 2),
            'annual_roi_pct': round(rental_roi, 1),
        },
        'winner': winner,
        'recommendation': (
            f"{'Mine' if winner == 'mining' else 'Rent'}: "
            f"${(mining_profit if winner == 'mining' else (best_rental['net_profit_usd_day'] if best_rental else 0)) * count:.2f}/day "
            f"({round(mining_roi if winner == 'mining' else rental_roi, 1)}% annual ROI)"
        ),
    }


def portfolio_revenue(gpus: list, electricity_rate: float = 0.10) -> dict:
    """Calculate total daily revenue for a GPU portfolio across all profitable networks."""
    portfolio_results = []
    total_daily_revenue = 0
    total_daily_electricity = 0
    total_daily_profit = 0
    total_power_watts = 0
    total_hardware_cost = 0

    for gpu_entry in gpus:
        model = gpu_entry.get('model', '')
        count = gpu_entry.get('count', 1)
        gpu_upper = model.upper().replace(' ', '_')
        hw_info = COMMON_HARDWARE.get(gpu_upper) or COMMON_HARDWARE.get(model)
        power_w = hw_info['power_watts'] if hw_info else 200

        best = best_mining(gpu_upper, electricity_rate)
        best_opt = best.get('best_option')

        net_profit = best_opt.get('net_profit_usd_day') or 0 if best_opt else 0
        if best_opt and net_profit > 0:
            rev = (best_opt.get('revenue_usd_day') or 0) * count
            elec = (best_opt.get('electricity_usd_day') or 0) * count
            prof = net_profit * count

            portfolio_results.append({
                'gpu': model,
                'count': count,
                'network': best_opt.get('network'),
                'daily_revenue': round(rev, 4),
                'daily_electricity': round(elec, 4),
                'daily_profit': round(prof, 4),
                'power_watts': power_w * count,
            })
        else:
            elec = (power_w / 1000) * 24 * electricity_rate * count
            portfolio_results.append({
                'gpu': model,
                'count': count,
                'network': None,
                'daily_revenue': 0,
                'daily_electricity': round(elec, 4),
                'daily_profit': -round(elec, 4),
                'power_watts': power_w * count,
                'note': 'No profitable network found',
            })

        total_daily_revenue += portfolio_results[-1]['daily_revenue']
        total_daily_electricity += portfolio_results[-1]['daily_electricity']
        total_daily_profit += portfolio_results[-1]['daily_profit']
        total_power_watts += portfolio_results[-1]['power_watts']
        total_hardware_cost += (hw_info.get('cost_gbp', 0) * 1.25 * count) if hw_info else 0

    return {
        'portfolio': portfolio_results,
        'summary': {
            'total_gpus': sum(g.get('count', 1) for g in gpus),
            'total_daily_revenue': round(total_daily_revenue, 4),
            'total_daily_electricity': round(total_daily_electricity, 4),
            'total_daily_profit': round(total_daily_profit, 4),
            'total_monthly_profit': round(total_daily_profit * 30, 2),
            'total_annual_profit': round(total_daily_profit * 365, 2),
            'total_power_watts': total_power_watts,
            'total_hardware_cost_usd': round(total_hardware_cost, 2),
            'electricity_rate': electricity_rate,
        },
    }


def emission_forecast(network: str) -> dict:
    """Forecast token emissions for a network."""
    net = network.upper()
    fundamentals = _load_fundamentals().get(net, {})
    real_stats = _load_real_stats().get(net, {})
    data = _load_chain_data(net)
    price_usd = _get_price(data)

    daily_emission = fundamentals.get('daily_emission')
    block_reward = real_stats.get('stats', {}).get('block_reward')
    block_time = real_stats.get('stats', {}).get('block_time') or fundamentals.get('block_time')
    blocks_per_day = fundamentals.get('blocks_per_day')
    tail_emission = real_stats.get('stats', {}).get('tail_emission', False)

    # Calculate if we have block info
    if block_reward and block_time:
        if not blocks_per_day:
            blocks_per_day = 86400 / block_time if block_time else None
        if blocks_per_day and not daily_emission:
            daily_emission = block_reward * blocks_per_day

    monthly_emission = daily_emission * 30 if daily_emission else None
    annual_emission = daily_emission * 365 if daily_emission else None

    daily_usd = fundamentals.get('daily_emission_usd')
    if not daily_usd and daily_emission and price_usd:
        daily_usd = daily_emission * price_usd

    monthly_usd = daily_usd * 30 if daily_usd else None
    annual_usd = daily_usd * 365 if daily_usd else None

    max_supply = fundamentals.get('max_supply')
    circulating = fundamentals.get('circulating_supply')

    forecast_years = None
    if annual_emission and max_supply and circulating:
        remaining = max_supply - circulating
        forecast_years = remaining / annual_emission

    return {
        'network': net,
        'name': fundamentals.get('name', net),
        'mining_algo': fundamentals.get('mining_algo', 'unknown'),
        'daily_emission': daily_emission,
        'monthly_emission': monthly_emission,
        'annual_emission': annual_emission,
        'daily_emission_usd': round(daily_usd, 2) if daily_usd else None,
        'monthly_emission_usd': round(monthly_usd, 2) if monthly_usd else None,
        'annual_emission_usd': round(annual_usd, 2) if annual_usd else None,
        'price_usd': price_usd,
        'block_reward': block_reward,
        'block_time': block_time,
        'blocks_per_day': blocks_per_day,
        'tail_emission': tail_emission,
        'max_supply': max_supply,
        'circulating_supply': circulating,
        'years_to_max': round(forecast_years, 1) if forecast_years else None,
        'inflation_rate': round(annual_emission / circulating * 100, 2) if annual_emission and circulating else None,
    }


def pool_risk_assessment(network: str) -> dict:
    """Assess pool centralization risk and mining safety for a network."""
    net = network.upper()
    fundamentals = _load_fundamentals().get(net, {})
    registry = _load_registry().get(net, {})
    data = _load_chain_data(net)

    pools = registry.get('pools', [])
    hardware = fundamentals.get('hardware', registry.get('physical_resource', 'unknown'))
    mining_algo = fundamentals.get('mining_algo', 'unknown')

    # Risk factors
    risks = []
    score = 100  # Start at 100, deduct for risks

    # Pool count risk
    if len(pools) == 0:
        risks.append({'factor': 'no_known_pools', 'severity': 'info', 'impact': 0})
    elif len(pools) <= 2:
        risks.append({'factor': 'few_pools', 'severity': 'medium', 'impact': -15,
                      'detail': f'Only {len(pools)} known pools: {", ".join(pools)}'})
        score -= 15
    else:
        risks.append({'factor': 'pool_diversity', 'severity': 'low', 'impact': 5,
                      'detail': f'{len(pools)} pools: {", ".join(pools)}'})
        score += 5

    # ASIC risk
    if 'ASIC' in str(hardware).upper():
        risks.append({'factor': 'asic_dominated', 'severity': 'high', 'impact': -25,
                      'detail': 'ASIC mining = high barrier to entry, centralization risk'})
        score -= 25
    elif 'GPU' in str(hardware).upper():
        risks.append({'factor': 'gpu_mineable', 'severity': 'low', 'impact': 10,
                      'detail': 'GPU mineable = accessible to home miners'})
        score += 10
    elif 'CPU' in str(hardware).upper():
        risks.append({'factor': 'cpu_mineable', 'severity': 'low', 'impact': 15,
                      'detail': 'CPU mineable = most accessible to home miners'})
        score += 15

    # Algo complexity
    if 'RandomX' in mining_algo:
        risks.append({'factor': 'randomx_asic_resistant', 'severity': 'low', 'impact': 10,
                      'detail': 'RandomX is ASIC-resistant, keeps mining decentralized'})
        score += 10

    # Useful work networks
    category = fundamentals.get('type', '')
    if 'compute' in category.lower() or 'ai' in category.lower():
        risks.append({'factor': 'useful_work', 'severity': 'low', 'impact': 5,
                      'detail': 'Useful work = hashrate has external value'})
        score += 5

    # Supply/dilution risk
    dilution = fundamentals.get('dilution_pressure')
    if dilution and dilution > 0.05:
        risks.append({'factor': 'high_dilution', 'severity': 'medium', 'impact': -10,
                      'detail': f'Dilution pressure: {dilution:.1%}'})
        score -= 10

    score = max(0, min(100, score))

    if score >= 80:
        safety = 'SAFE'
    elif score >= 60:
        safety = 'MODERATE'
    elif score >= 40:
        safety = 'RISKY'
    else:
        safety = 'DANGEROUS'

    return {
        'network': net,
        'name': fundamentals.get('name', net),
        'safety_score': score,
        'safety_rating': safety,
        'mining_algo': mining_algo,
        'hardware_type': hardware,
        'known_pools': pools,
        'pool_count': len(pools),
        'risk_factors': risks,
        'summary': f'{safety} ({score}/100): {mining_algo} on {hardware}',
    }


# ============================================================
# DISPATCH
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
                    "serverInfo": {
                        "name": "powpowpow",
                        "version": "1.0.0",
                        "description": "PowPowPow — Compute economics. Mining profitability, hardware ROI, network comparisons, hashrate migration.",
                    },
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
        print(json.dumps({"name": "powpowpow", "tools": [t["name"] for t in TOOLS]}, indent=2))
