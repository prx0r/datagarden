#!/usr/bin/env python3
"""
Probe Capability #1: Can Your Gaming PC Make Money?

Answer: "Can this gaming PC make me money overnight?"

Capability: evaluate_hardware(hardware, electricity_cost)
Data source: PowPowPow chains (17 networks, live)
Output: profitability ranking across all networks

This is the probe video capability.
When someone asks Muse this, we give them a real answer.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/box/powpowpow')))
sys.path.insert(0, str(Path(__file__).parent.parent))


COMMON_HARDWARE = {
    'RTX_4060': {'name': 'RTX 4060', 'cost_gbp': 299, 'power_watts': 115},
    'RTX_4060_TI': {'name': 'RTX 4060 Ti', 'cost_gbp': 399, 'power_watts': 160},
    'RTX_4070': {'name': 'RTX 4070', 'cost_gbp': 499, 'power_watts': 200},
    'RTX_4070_TI': {'name': 'RTX 4070 Ti', 'cost_gbp': 599, 'power_watts': 285},
    'RTX_4080': {'name': 'RTX 4080', 'cost_gbp': 899, 'power_watts': 320},
    'RTX_4090': {'name': 'RTX 4090', 'cost_gbp': 1599, 'power_watts': 450},
    'RX_7900_XTX': {'name': 'RX 7900 XTX', 'cost_gbp': 899, 'power_watts': 355},
    'RX_7800_XT': {'name': 'RX 7800 XT', 'cost_gbp': 449, 'power_watts': 263},
}

ELECTRICITY_TIERS = {
    'cheap': {'rate': 0.08, 'label': 'UK off-peak / cheap tariff'},
    'average': {'rate': 0.15, 'label': 'UK average'},
    'expensive': {'rate': 0.25, 'label': 'UK expensive / day rate'},
    'extreme': {'rate': 0.35, 'label': 'Very expensive / no deal'},
}


def evaluate_hardware(hardware_key: str = 'RTX_4060', electricity_rate: float = 0.15) -> dict:
    """
    Can this gaming PC make money?
    
    Returns profitability across all 17 tracked networks for a given GPU.
    """
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"error": "Cannot import powpowpow modules"}
    
    hardware = COMMON_HARDWARE.get(hardware_key)
    if not hardware:
        return {"error": f"Unknown hardware: {hardware_key}", "available": list(COMMON_HARDWARE.keys())}
    
    # Load all chain data
    chains_dir = Path('/home/box/powpowpow/chains')
    results = []
    
    for chain_dir in sorted(chains_dir.iterdir()):
        if not chain_dir.is_dir():
            continue
        
        data_file = chain_dir / f'{chain_dir.name}_data.json'
        if not data_file.exists():
            continue
        
        try:
            with open(data_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        
        price = data.get('price', {})
        price_usd = price.get('usd', 0) if isinstance(price, dict) else price
        
        if not price_usd or price_usd <= 0:
            continue
        
        symbol = chain_dir.name.upper()
        try:
            card = generate_card(symbol, price_usd)
        except Exception:
            continue
        
        hw_data = card.get('hardware', {}).get(hardware_key, {})
        if not hw_data:
            # Try common names
            for alt in ['RTX_4090', 'RTX_4060', 'RX_7900_XTX']:
                hw_data = card.get('hardware', {}).get(alt, {})
                if hw_data:
                    break
        
        if not hw_data:
            continue
        
        # Calculate with actual electricity cost
        revenue_day = hw_data.get('revenue_usd_day', 0)
        power_watts = hw_data.get('power_watts', hardware['power_watts'])
        electricity_day = (power_watts * 24 / 1000) * electricity_rate
        net_profit_day = revenue_day - electricity_day
        
        hw_cost = hw_data.get('cost_usd', hardware['cost_gbp'] * 1.25)
        payback_days = hw_cost / net_profit_day if net_profit_day > 0 else None
        
        results.append({
            'network': symbol,
            'price_usd': price_usd,
            'revenue_usd_day': round(revenue_day, 4),
            'electricity_usd_day': round(electricity_day, 4),
            'net_profit_usd_day': round(net_profit_day, 4),
            'net_profit_gbp_day': round(net_profit_day * 0.79, 4),
            'payback_days': round(payback_days) if payback_days else None,
            'algo': hw_data.get('algo', 'unknown'),
        })
    
    # Sort by profitability
    results.sort(key=lambda x: x['net_profit_usd_day'], reverse=True)
    
    profitable = [r for r in results if r['net_profit_usd_day'] > 0]
    unprofitable = [r for r in results if r['net_profit_usd_day'] <= 0]
    
    return {
        'hardware': hardware['name'],
        'hardware_cost_gbp': hardware['cost_gbp'],
        'electricity_rate': electricity_rate,
        'total_networks': len(results),
        'profitable_count': len(profitable),
        'profitable': profitable[:5],
        'unprofitable': unprofitable[:3],
        'best_option': profitable[0] if profitable else None,
        'daily_if_best': round(profitable[0]['net_profit_gbp_day'], 2) if profitable else 0,
        'monthly_if_best': round(profitable[0]['net_profit_gbp_day'] * 30, 2) if profitable else 0,
    }


def find_compute_opportunity(electricity_rate: float = 0.15, risk: str = 'medium') -> dict:
    """
    What should I mine with this GPU today?
    
    Returns the best mining option for any common GPU.
    """
    try:
        from v1_live_cards import generate_card
    except ImportError:
        return {"error": "Cannot import powpowpow modules"}
    
    chains_dir = Path('/home/box/powpowpow/chains')
    best_by_hardware = {}
    
    for hw_key, hw_info in COMMON_HARDWARE.items():
        best_profit = float('-inf')
        best_chain = None
        
        for chain_dir in chains_dir.iterdir():
            if not chain_dir.is_dir():
                continue
            data_file = chain_dir / f'{chain_dir.name}_data.json'
            if not data_file.exists():
                continue
            
            try:
                with open(data_file) as f:
                    data = json.load(f)
                price = data.get('price', {})
                price_usd = price.get('usd', 0) if isinstance(price, dict) else price
                if not price_usd or price_usd <= 0:
                    continue
                
                symbol = chain_dir.name.upper()
                card = generate_card(symbol, price_usd)
                hw_data = card.get('hardware', {}).get(hw_key, {})
                if not hw_data:
                    continue
                
                revenue = hw_data.get('revenue_usd_day', 0)
                power = hw_data.get('power_watts', hw_info['power_watts'])
                elec = (power * 24 / 1000) * electricity_rate
                net = revenue - elec
                
                if net > best_profit:
                    best_profit = net
                    best_chain = symbol
            except Exception:
                continue
        
        if best_chain:
            best_by_hardware[hw_key] = {
                'hardware': hw_info['name'],
                'best_network': best_chain,
                'net_profit_usd_day': round(best_profit, 4),
                'net_profit_gbp_day': round(best_profit * 0.79, 4),
            }
    
    return {
        'electricity_rate': electricity_rate,
        'recommendations': best_by_hardware,
        'top_pick': max(best_by_hardware.values(), key=lambda x: x['net_profit_usd_day']) if best_by_hardware else None,
    }


def portfolio_revenue(hardware_list: list, electricity_rate: float = 0.15) -> dict:
    """
    How much would I make with multiple GPUs?
    """
    results = []
    total_daily = 0
    
    for hw_key in hardware_list:
        result = evaluate_hardware(hw_key, electricity_rate)
        if result.get('best_option'):
            daily_gbp = result['daily_if_best']
            total_daily += daily_gbp
            results.append({
                'hardware': COMMON_HARDWARE.get(hw_key, {}).get('name', hw_key),
                'best_network': result['best_option']['network'],
                'daily_gbp': daily_gbp,
            })
    
    return {
        'hardware_count': len(hardware_list),
        'electricity_rate': electricity_rate,
        'per_hardware': results,
        'total_daily_gbp': round(total_daily, 2),
        'total_monthly_gbp': round(total_daily * 30, 2),
        'total_yearly_gbp': round(total_daily * 365, 2),
    }


# ============================================================
# CLI
# ============================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'evaluate':
            hw = sys.argv[2] if len(sys.argv) > 2 else 'RTX_4060'
            elec = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
            result = evaluate_hardware(hw, elec)
        elif cmd == 'find':
            elec = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
            result = find_compute_opportunity(elec)
        elif cmd == 'portfolio':
            hws = sys.argv[2].split(',') if len(sys.argv) > 2 else ['RTX_4060', 'RTX_4090']
            elec = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
            result = portfolio_revenue(hws, elec)
        else:
            result = {"error": f"Unknown command: {cmd}", "usage": "python evaluate_hardware.py evaluate|find|portfolio"}
        
        print(json.dumps(result, indent=2))
    else:
        # Default: evaluate RTX 4060 at UK average electricity
        result = evaluate_hardware('RTX_4060', 0.15)
        print(json.dumps(result, indent=2))
