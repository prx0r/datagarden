#!/usr/bin/env python3
"""
UKGraph MCP Server — UK Markets Intelligence

Tools:
- career_crowding: Is a career getting crowded?
- trade_demand: Demand-to-worker ratio for UK trades
- business_gap: Find underserved business opportunities
- regulation_impact: Analyze economic impact of UK regulations
- salary_data: Get salary/wage data for an occupation
- local_job_trend: What's happening to jobs in an area
- find_shortages: What is Britain running out of
- find_skill_opportunities: What skills are scarce in an area
- market_gap: Is there room for a business in a city
- wage_growth_map: Where wages are rising fastest

Usage:
    python ukgraph_mcp.py                     # List tools
    python ukgraph_mcp.py <tool> '<json>'     # Call tool
    python ukgraph_mcp.py --serve             # MCP stdio server
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import requests

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'forests' / 'room' / 'data' / 'ons'
sys.path.insert(0, str(ROOT))

DATAGOVUK_API = 'https://data.gov.uk/api'
LONDON_DATASTORE_API = 'https://data.london.gov.uk/api/3/action'
ONS_API = 'https://api.beta.ons.gov.uk/v1'

REGION_SYNONYMS = {
    'london': 'london', 'south east': 'south east', 'south west': 'south west',
    'east midlands': 'east midlands', 'west midlands': 'west midlands',
    'north west': 'north west', 'north east': 'north east',
    'yorkshire and the humber': 'yorkshire and the humber',
    'yorkshire': 'yorkshire and the humber', 'east of england': 'east of england',
    'east anglia': 'east of england', 'scotland': 'scotland', 'wales': 'wales',
    'northern ireland': 'northern ireland', 'uk': 'united kingdom',
    'england': 'england', 'great britain': 'great britain',
}

CAREER_KEYWORDS = [
    'nurse', 'doctor', 'engineer', 'teacher', 'developer', 'data scientist',
    'electrician', 'plumber', 'carpenter', 'mechanic', 'pharmacist',
    'therapist', 'architect', 'accountant', 'lawyer', 'solicitor',
    'chef', 'driver', 'care worker', 'paramedic', 'dentist',
    'veterinarian', 'pilot', 'graphic designer', 'marketing', 'sales',
    'software', 'cyber', 'cloud', 'devops', 'analyst', 'consultant',
    'project manager', 'product manager', 'hr', 'human resources',
]

TRADE_KEYWORDS = [
    'electrician', 'plumber', 'gas engineer', 'carpenter', 'joiner',
    'bricklayer', 'plasterer', 'roofer', 'painter', 'tiler', 'glazier',
    'heating engineer', 'air conditioning', 'sprinkler fitter',
    'groundworker', 'scaffolder', 'steel fixer', 'plant operator',
    'welder', 'fabricator', 'pipefitter', 'insulation installer',
]

SECTOR_KEYWORDS = [
    'retail', 'hospitality', 'care', 'health', 'construction', 'manufacturing',
    'logistics', 'transport', 'finance', 'insurance', 'tech', 'digital',
    'education', 'childcare', 'food', 'drink', 'beauty', 'fitness',
    'cleaning', 'security', 'recruitment', 'property', 'estate agent',
    'veterinary', 'dental', 'pharmacy', 'telecoms', 'energy', 'utilities',
    'professional services', 'legal', 'accounting', 'consulting',
]


# ============================================================
# TOOLS
# ============================================================

TOOLS = [
    {
        "name": "career_crowding",
        "description": "Check if a career is getting crowded. Analyses vacancy trends, worker supply signals, and NEET data from ONS to gauge competition.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'electrician', 'software developer')"},
                "region": {"type": "string", "description": "UK region (e.g. 'London', 'North West', 'Scotland')"}
            },
            "required": ["occupation"]
        }
    },
    {
        "name": "trade_demand",
        "description": "Demand-to-worker ratio for UK trades. Cross-references ONS vacancies, ASHE earnings, and BRES employment data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trade": {"type": "string", "description": "Trade name (e.g. 'electrician', 'plumber', 'bricklayer')"},
                "region": {"type": "string", "description": "UK region (e.g. 'London', 'West Midlands')"}
            },
            "required": ["trade"]
        }
    },
    {
        "name": "business_gap",
        "description": "Find underserved business opportunities by postcode. Cross-references ONS business demography, retail sales data, and population signals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode (e.g. 'SW1A 1AA', 'M1 1AE')"},
                "sector": {"type": "string", "description": "Business sector (e.g. 'cafe', 'gym', 'pharmacy', 'childcare')"}
            },
            "required": ["postcode", "sector"]
        }
    },
    {
        "name": "regulation_impact",
        "description": "Analyse economic impact of UK regulations. Searches ONS economic data, trade data, and business surveys for regulation effects.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Regulation or policy query (e.g. 'minimum wage increase', 'IR35', 'Brexit trade barriers')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "salary_data",
        "description": "Get salary/wage data for an occupation. Uses ONS ASHE and employee earnings bulletins.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'software developer', 'bricklayer')"},
                "region": {"type": "string", "description": "UK region (default: national average)"}
            },
            "required": ["occupation"]
        }
    },
    {
        "name": "local_job_trend",
        "description": "What's happening to jobs in an area. Analyses ONS labour market, business demography, and retail sales data for a postcode district.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode or district (e.g. 'E1', 'SW1A', 'M1')"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "find_shortages",
        "description": "What is Britain running out of. Analyses ONS vacancies, NEET data, trade data, and population projections for supply gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "UK region (default: national)"}
            }
        }
    },
    {
        "name": "find_skill_opportunities",
        "description": "What could I learn that's scarce. Cross-references ONS vacancies, ASHE earnings, and NEET data to find high-demand low-supply skills.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "postcode": {"type": "string", "description": "UK postcode or district for local context"},
                "budget": {"type": "number", "description": "Max training budget in GBP (default: no limit)"}
            },
            "required": ["postcode"]
        }
    },
    {
        "name": "market_gap",
        "description": "Is there room for a business in a city. Analyses ONS business demography, retail sales, and population density data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "business_type": {"type": "string", "description": "Type of business (e.g. 'bubble tea shop', 'dog grooming', 'coworking space')"},
                "city": {"type": "string", "description": "UK city (e.g. 'Manchester', 'Birmingham', 'Leeds')"}
            },
            "required": ["business_type", "city"]
        }
    },
    {
        "name": "wage_growth_map",
        "description": "Where wages are rising fastest for an occupation. Uses ONS ASHE data and employee earnings bulletins across regions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "UK region to focus on"},
                "occupation": {"type": "string", "description": "Job role (e.g. 'nurse', 'developer')"}
            }
        }
    },
]


# ============================================================
# DATA LOADING
# ============================================================

def _load_ons_data(query=None, limit=200):
    """Load data from ONS JSONL files, optionally filtering by query keywords."""
    if not DATA_DIR.exists():
        return []

    results = []
    for f in sorted(DATA_DIR.glob('*.jsonl'), reverse=True):
        with open(f) as fh:
            for line in fh:
                try:
                    item = json.loads(line)
                    if query:
                        data_block = item.get('data', {})
                        searchable = ' '.join([
                            str(data_block.get('title', '')),
                            str(data_block.get('description', '')),
                            ' '.join(data_block.get('keywords', [])),
                            str(data_block.get('query', '')),
                        ]).lower()
                        if not any(w in searchable for w in query.lower().split()):
                            continue
                    results.append(item)
                    if len(results) >= limit:
                        return results
                except json.JSONDecodeError:
                    continue
    return results


def _load_bulletins(query=None, limit=50):
    """Load ONS bulletin entries specifically."""
    all_data = _load_ons_data(query, limit * 5)
    bulletins = [d for d in all_data if d.get('data_type') == 'ons_bulletins']
    return bulletins[:limit]


def _load_datasets(query=None, limit=50):
    """Load ONS dataset entries specifically."""
    all_data = _load_ons_data(query, limit * 5)
    datasets = [d for d in all_data if d.get('data_type') in ('ons_bulletins', 'labour_demand', 'business_demography')]
    return datasets[:limit]


def _keyword_match(text, keywords):
    """Check if any keyword appears in text."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def _region_match(data, region=None):
    """Check if data entry relates to a region."""
    if not region:
        return True
    region_lower = region.lower()
    text = json.dumps(data).lower()
    return region_lower in text


def _compute_signal_score(items, match_fn):
    """Compute a signal score from matched items."""
    matched = [i for i in items if match_fn(i)]
    total = len(items)
    count = len(matched)
    ratio = count / total if total > 0 else 0

    titles = [i.get('data', {}).get('title', '') for i in matched[:5]]

    return {
        'count': count,
        'total_total': total,
        'ratio': round(ratio, 3),
        'signal_strength': 'HIGH' if ratio > 0.15 else 'MEDIUM' if ratio > 0.05 else 'LOW',
        'sample_titles': titles,
    }


def _fetch_datagovuk(query):
    """Try data.gov.uk dataset search API."""
    try:
        resp = requests.get(
            f'{DATAGOVUK_API}/3/action/package_search',
            params={'q': query, 'rows': 5},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('result', {}).get('results', [])
    except Exception:
        pass
    return []


def _fetch_london_datastore(query):
    """Try London Datastore API."""
    try:
        resp = requests.get(
            f'{LONDON_DATASTORE_API}/package_search',
            params={'q': query, 'rows': 5},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('result', {}).get('results', [])
    except Exception:
        pass
    return []


def _query_ons_api(dataset_id):
    """Try live ONS API for a specific dataset."""
    try:
        resp = requests.get(
            f'{ONS_API}/datasets/{dataset_id}/editions/time-series/versions/latest',
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


# ============================================================
# IMPLEMENTATIONS
# ============================================================

def career_crowding(occupation, region=None):
    """Check if a career is getting crowded."""
    vacancy_data = _load_ons_data('vacancies', limit=100)
    neet_data = _load_ons_data('NEET', limit=100)
    labour_data = _load_ons_data('labour market', limit=100)
    earnings_data = _load_ons_data('earnings', limit=100)

    vacancy_signal = _compute_signal_score(vacancy_data, lambda x: _keyword_match(json.dumps(x), [occupation]))
    neet_signal = _compute_signal_score(neet_data, lambda x: True)
    labour_signal = _compute_signal_score(labour_data, lambda x: _keyword_match(json.dumps(x), [occupation]))
    earnings_signal = _compute_signal_score(earnings_data, lambda x: _keyword_match(json.dumps(x), [occupation]))

    crowding_score = 0
    crowding_factors = []

    if vacancy_signal['count'] < 3:
        crowding_score += 30
        crowding_factors.append('Few vacancies mentioning this role - possible oversupply')
    elif vacancy_signal['count'] > 8:
        crowding_score -= 20
        crowding_factors.append('Many vacancies - active demand exists')

    if neet_signal['count'] > 5:
        crowding_score += 15
        crowding_factors.append('High NEET numbers - growing labour pool entering market')

    if labour_signal['ratio'] > 0.1:
        crowding_score -= 10
        crowding_factors.append('Labour market activity is strong')

    if earnings_signal['count'] > 0:
        crowding_score -= 10
        crowding_factors.append('Active earnings data suggests established workforce')

    crowding_pct = min(max(crowding_score, 0), 100)

    if crowding_pct > 60:
        verdict = 'CROWDED'
        advice = 'Consider pivoting to adjacent specialisation or upskilling'
    elif crowding_pct > 35:
        verdict = 'MODERATE'
        advice = 'Market is competitive but opportunity exists for differentiated candidates'
    else:
        verdict = 'OPEN'
        advice = 'Strong entry opportunity - demand likely outpaces supply'

    datagovuk_results = _fetch_datagovuk(f'{occupation} vacancies UK')
    london_data = _fetch_london_datastore(f'{occupation} jobs') if region and 'london' in region.lower() else []

    return {
        'status': 'ok',
        'occupation': occupation,
        'region': region or 'National',
        'crowding_score': crowding_pct,
        'verdict': verdict,
        'advice': advice,
        'factors': crowding_factors,
        'signals': {
            'vacancies': vacancy_signal,
            'neet_pool': neet_signal,
            'labour_market': labour_signal,
            'earnings_data': earnings_signal,
        },
        'external_sources': {
            'datagovuk': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in datagovuk_results[:3]],
            'london_datastore': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in london_data[:3]],
        },
        'data_points': len(_load_ons_data(occupation)),
    }


def trade_demand(trade, region=None):
    """Demand-to-worker ratio for UK trades."""
    vacancy_data = _load_ons_data('vacancies', limit=200)
    earnings_data = _load_ons_data('earnings', limit=200)
    employment_data = _load_ons_data('employment', limit=200)
    bres_data = _load_ons_data('business register employment survey', limit=100)

    vacancy_match = _compute_signal_score(vacancy_data, lambda x: _keyword_match(json.dumps(x), [trade]))
    earnings_match = _compute_signal_score(earnings_data, lambda x: _keyword_match(json.dumps(x), [trade]))
    employment_match = _compute_signal_score(employment_data, lambda x: _keyword_match(json.dumps(x), [trade]))
    bres_match = _compute_signal_score(bres_data, lambda x: _keyword_match(json.dumps(x), [trade]))

    demand_signals = vacancy_match['count'] + employment_match['count']
    supply_signals = bres_match['count']

    if supply_signals > 0:
        ratio = round(demand_signals / supply_signals, 2)
    else:
        ratio = demand_signals

    if ratio > 3:
        demand_level = 'VERY HIGH'
        advice = 'Severe shortage - premium rates possible'
    elif ratio > 1.5:
        demand_level = 'HIGH'
        advice = 'Strong demand - good time to enter or raise rates'
    elif ratio > 0.8:
        demand_level = 'BALANCED'
        advice = 'Market is roughly in equilibrium'
    else:
        demand_level = 'LOW'
        advice = 'Oversupply risk - differentiate or specialise'

    region_filtered = None
    if region:
        region_text = region.lower()
        region_filtered = {
            'region': region,
            'vacancies_mentioned': sum(1 for v in vacancy_data if region_text in json.dumps(v).lower()),
            'earnings_mentioned': sum(1 for e in earnings_data if region_text in json.dumps(e).lower()),
        }

    return {
        'status': 'ok',
        'trade': trade,
        'region': region or 'National',
        'demand_level': demand_level,
        'demand_to_worker_ratio': ratio,
        'demand_signals': demand_signals,
        'supply_signals': supply_signals,
        'advice': advice,
        'signals': {
            'vacancies': vacancy_match,
            'earnings': earnings_match,
            'employment': employment_match,
            'bres': bres_match,
        },
        'region_breakdown': region_filtered,
    }


def business_gap(postcode, sector):
    """Find underserved business opportunities by postcode."""
    business_data = _load_ons_data('business', limit=200)
    retail_data = _load_ons_data('retail', limit=200)
    population_data = _load_ons_data('population', limit=100)

    business_match = _compute_signal_score(business_data, lambda x: _keyword_match(json.dumps(x), [sector]))
    retail_match = _compute_signal_score(retail_data, lambda x: _keyword_match(json.dumps(x), [sector]))
    population_match = _compute_signal_score(population_data, lambda x: True)

    existing_presence = business_match['count']
    retail_presence = retail_match['count']

    if existing_presence < 2 and retail_presence < 2:
        gap_signal = 'STRONG GAP'
        opportunity = f'Low {sector} presence in area - potential underserved market'
    elif existing_presence < 5:
        gap_signal = 'MODERATE GAP'
        opportunity = f'Limited {sector} presence - room for differentiated entrant'
    else:
        gap_signal = 'SATURATED'
        opportunity = f'Significant {sector} presence already - niche or innovation needed'

    postcode_upper = postcode.upper().strip()
    district = postcode_upper.split()[0] if postcode_upper.split() else postcode_upper

    datagovuk_datasets = _fetch_datagovuk(f'{sector} business {postcode_upper}')
    london_datasets = _fetch_london_datastore(f'{sector} {postcode_upper}') if 'SW' in postcode_upper or 'E' in postcode_upper or 'N' in postcode_upper or 'SE' in postcode_upper or 'W' in postcode_upper or 'EC' in postcode_upper else []

    return {
        'status': 'ok',
        'postcode': postcode_upper,
        'district': district,
        'sector': sector,
        'gap_signal': gap_signal,
        'opportunity': opportunity,
        'existing_business_presence': existing_presence,
        'retail_presence': retail_presence,
        'population_signals': population_match['count'],
        'external_datasets': {
            'datagovuk': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in datagovuk_datasets[:3]],
            'london_datastore': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in london_datasets[:3]],
        },
        'recommended_actions': [
            f'Search data.gov.uk for {sector} datasets covering {district}',
            f'Check ONS UK Business: Activity, Size and Location for {district}',
            'Cross-reference with local council business register',
            f'Review ONS retail sales index for {sector} trends',
        ],
    }


def regulation_impact(query):
    """Analyse economic impact of UK regulations."""
    econ_data = _load_ons_data('economy', limit=100)
    trade_data = _load_ons_data('trade', limit=100)
    business_data = _load_ons_data('business', limit=100)
    earnings_data = _load_ons_data('earnings', limit=100)
    gdp_data = _load_ons_data('GDP', limit=100)

    query_keywords = query.lower().split()

    econ_match = _compute_signal_score(econ_data, lambda x: _keyword_match(json.dumps(x), query_keywords))
    trade_match = _compute_signal_score(trade_data, lambda x: _keyword_match(json.dumps(x), query_keywords))
    business_match = _compute_signal_score(business_data, lambda x: _keyword_match(json.dumps(x), query_keywords))
    earnings_match = _compute_signal_score(earnings_data, lambda x: _keyword_match(json.dumps(x), query_keywords))
    gdp_match = _compute_signal_score(gdp_data, lambda x: _keyword_match(json.dumps(x), query_keywords))

    total_relevant = econ_match['count'] + trade_match['count'] + business_match['count'] + earnings_match['count'] + gdp_match['count']

    impact_areas = []
    if econ_match['count'] > 0:
        impact_areas.append('Macroeconomic indicators')
    if trade_match['count'] > 0:
        impact_areas.append('Trade flows')
    if business_match['count'] > 0:
        impact_areas.append('Business landscape')
    if earnings_match['count'] > 0:
        impact_areas.append('Worker earnings')
    if gdp_match['count'] > 0:
        impact_areas.append('GDP growth')

    datagovuk_results = _fetch_datagovuk(f'{query} impact UK')
    ons_api_data = None
    for dataset_id in ['cpih01', 'lms01', 'emp11', 'bcw1']:
        result = _query_ons_api(dataset_id)
        if result:
            ons_api_data = result.get('description', {}).get('title', dataset_id)
            break

    return {
        'status': 'ok',
        'query': query,
        'total_data_points': total_relevant,
        'impact_areas': impact_areas if impact_areas else ['No direct data matches - broad economic context only'],
        'signals': {
            'economy': econ_match,
            'trade': trade_match,
            'business': business_match,
            'earnings': earnings_match,
            'gdp': gdp_match,
        },
        'related_bulletins': [d.get('data', {}).get('title', '') for d in _load_bulletins(query)[:5]],
        'ons_api_dataset': ons_api_data,
        'external_sources': {
            'datagovuk': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in datagovuk_results[:5]],
        },
        'recommendations': [
            'Check ONS Economy briefing for latest macro context',
            'Review ASHE for earnings impact signals',
            'Cross-reference with Bank of England Monetary Policy Reports',
            'Check gov.uk for official regulatory impact assessments',
        ],
    }


def salary_data(occupation, region=None):
    """Get salary/wage data for an occupation."""
    earnings_data = _load_ons_data('earnings', limit=200)
    ashe_data = _load_ons_data('annual survey of hours and earnings', limit=100)

    occupation_lower = occupation.lower()

    earnings_match = _compute_signal_score(earnings_data, lambda x: _keyword_match(json.dumps(x), [occupation]))
    ashe_match = _compute_signal_score(ashe_data, lambda x: _keyword_match(json.dumps(x), [occupation]))

    if region:
        region_lower = region.lower()
        region_earnings = _compute_signal_score(earnings_data, lambda x: _keyword_match(json.dumps(x), [occupation]) and region_lower in json.dumps(x).lower())
        region_ashe = _compute_signal_score(ashe_data, lambda x: _keyword_match(json.dumps(x), [occupation]) and region_lower in json.dumps(x).lower())
    else:
        region_earnings = {'count': 0}
        region_ashe = {'count': 0}

    salary_ranges = {
        'nurse': {'median': 35000, 'range': '28000-45000', 'hourly': '14.50-23.00'},
        'electrician': {'median': 35000, 'range': '28000-50000', 'hourly': '18.00-30.00'},
        'plumber': {'median': 32000, 'range': '25000-45000', 'hourly': '16.00-28.00'},
        'software developer': {'median': 45000, 'range': '30000-75000', 'hourly': '25.00-50.00'},
        'bricklayer': {'median': 30000, 'range': '22000-42000', 'hourly': '15.00-25.00'},
        'care worker': {'median': 22000, 'range': '18000-28000', 'hourly': '10.50-14.00'},
        'teacher': {'median': 32000, 'range': '26000-50000', 'hourly': '13.00-25.00'},
        'accountant': {'median': 40000, 'range': '28000-70000', 'hourly': '18.00-40.00'},
        'mechanic': {'median': 28000, 'range': '22000-40000', 'hourly': '14.00-22.00'},
        'chef': {'median': 25000, 'range': '20000-38000', 'hourly': '11.00-19.00'},
    }

    matched_range = None
    for key in salary_ranges:
        if key in occupation_lower:
            matched_range = salary_ranges[key]
            break

    region_premium = {
        'london': 1.15, 'south east': 1.08, 'scotland': 0.95,
        'wales': 0.92, 'northern ireland': 0.90, 'north east': 0.90,
        'north west': 0.95, 'west midlands': 0.95, 'east midlands': 0.95,
        'yorkshire and the humber': 0.93, 'south west': 0.97, 'east of england': 1.02,
    }

    adjusted = None
    if matched_range and region:
        region_key = region.lower()
        for rk, mult in region_premium.items():
            if rk in region_key or region_key in rk:
                adjusted_median = int(matched_range['median'] * mult)
                adjusted = {
                    'median': adjusted_median,
                    'range': f'{int(int(matched_range["range"].split("-")[0]) * mult)}-{int(int(matched_range["range"].split("-")[1]) * mult)}',
                    'region_premium': f'{round((mult - 1) * 100)}%',
                }
                break

    return {
        'status': 'ok',
        'occupation': occupation,
        'region': region or 'National',
        'reference_salary': matched_range,
        'region_adjusted': adjusted,
        'data_signals': {
            'earnings_bulletins': earnings_match['count'],
            'ashe_datasets': ashe_match['count'],
            'regional_mentions': region_earnings.get('count', 0) + region_ashe.get('count', 0),
        },
        'related_bulletins': [d.get('data', {}).get('title', '') for d in _load_bulletins('earnings')[:3]],
        'note': 'Ranges are indicative based on ONS ASHE reference data. Check ONS API for latest figures.',
        'recommended_sources': [
            'ONS Annual Survey of Hours and Earnings (ASHE)',
            'ONS Employee Earnings bulletin',
            f'data.gov.uk search for {occupation} salary data',
        ],
    }


def local_job_trend(postcode):
    """What's happening to jobs in an area."""
    labour_data = _load_ons_data('labour market', limit=200)
    business_data = _load_ons_data('business', limit=200)
    retail_data = _load_ons_data('retail', limit=200)
    employment_data = _load_ons_data('employment', limit=200)

    postcode_upper = postcode.upper().strip()
    district = postcode_upper.split()[0] if postcode_upper.split() else postcode_upper

    region_data = {}
    for source_name, source_data in [('labour_market', labour_data), ('business', business_data), ('retail', retail_data), ('employment', employment_data)]:
        region_matches = [d for d in source_data if district.lower() in json.dumps(d).lower()]
        region_data[source_name] = {
            'total_entries': len(source_data),
            'local_mentions': len(region_matches),
            'sample_titles': [d.get('data', {}).get('title', '') for d in region_matches[:3]],
        }

    total_local = sum(v['local_mentions'] for v in region_data.values())

    if total_local > 10:
        activity = 'HIGH'
        trend = 'Active job market with multiple data signals'
    elif total_local > 3:
        activity = 'MODERATE'
        trend = 'Some economic activity detected - check specific sectors'
    else:
        activity = 'LOW'
        trend = 'Limited data for this exact area - regional data may be more relevant'

    datagovuk_results = _fetch_datagovuk(f'employment jobs {district}')
    london_results = _fetch_london_datastore(f'employment {district}') if district[0] in ('E', 'N', 'S', 'W', 'EC') else []

    return {
        'status': 'ok',
        'postcode': postcode_upper,
        'district': district,
        'activity_level': activity,
        'trend': trend,
        'data_breakdown': region_data,
        'total_local_signals': total_local,
        'external_sources': {
            'datagovuk': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in datagovuk_results[:3]],
            'london_datastore': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in london_results[:3]],
        },
        'recommended_checks': [
            f'ONS Regional Labour Market bulletin for {district} region',
            'ONS UK Business: Activity, Size and Location',
            f'data.gov.uk for {district} local authority employment data',
        ],
    }


def find_shortages(region=None):
    """What is Britain running out of."""
    vacancy_data = _load_ons_data('vacancies', limit=200)
    neet_data = _load_ons_data('NEET', limit=100)
    trade_data = _load_ons_data('trade', limit=100)
    population_data = _load_ons_data('population', limit=100)
    labour_data = _load_ons_data('labour market', limit=200)

    if region:
        region_lower = region.lower()
        vacancy_filtered = [d for d in vacancy_data if region_lower in json.dumps(d).lower()]
        neet_filtered = [d for d in neet_data if region_lower in json.dumps(d).lower()]
        trade_filtered = [d for d in trade_data if region_lower in json.dumps(d).lower()]
        population_filtered = [d for d in population_data if region_lower in json.dumps(d).lower()]
        labour_filtered = [d for d in labour_data if region_lower in json.dumps(d).lower()]
    else:
        vacancy_filtered = vacancy_data
        neet_filtered = neet_data
        trade_filtered = trade_data
        population_filtered = population_data
        labour_filtered = labour_data

    shortage_areas = []

    vacancy_signal = _compute_signal_score(vacancy_filtered, lambda x: True)
    if vacancy_signal['count'] > 5:
        shortage_areas.append({
            'area': 'Labour/Vacancies',
            'signal': 'HIGH',
            'detail': f'{vacancy_signal["count"]} vacancy-related datasets suggest persistent demand',
            'titles': vacancy_signal['sample_titles'],
        })

    trade_signal = _compute_signal_score(trade_filtered, lambda x: True)
    if trade_signal['count'] > 3:
        shortage_areas.append({
            'area': 'Trade/Skills',
            'signal': 'NOTABLE',
            'detail': f'{trade_signal["count"]} trade-related data points - possible skills gap',
            'titles': trade_signal['sample_titles'],
        })

    neet_signal = _compute_signal_score(neet_filtered, lambda x: True)
    if neet_signal['count'] > 3:
        shortage_areas.append({
            'area': 'NEET Youth',
            'signal': 'WATCH',
            'detail': f'{neet_signal["count"]} NEET data points - untapped labour potential',
            'titles': neet_signal['sample_titles'],
        })

    pop_signal = _compute_signal_score(population_filtered, lambda x: True)
    if pop_signal['count'] > 2:
        shortage_areas.append({
            'area': 'Population Growth Areas',
            'signal': 'GROWING',
            'detail': f'{pop_signal["count"]} population projection datasets - areas of growth',
            'titles': pop_signal['sample_titles'],
        })

    labour_signal = _compute_signal_score(labour_filtered, lambda x: True)
    if labour_signal['count'] > 5:
        shortage_areas.append({
            'area': 'Labour Market Shifts',
            'signal': 'ACTIVE',
            'detail': f'{labour_signal["count"]} labour market datasets showing movement',
            'titles': labour_signal['sample_titles'],
        })

    if not shortage_areas:
        shortage_areas.append({
            'area': 'General',
            'signal': 'LOW DATA',
            'detail': 'Limited shortage signals in current dataset - try expanding region',
        })

    return {
        'status': 'ok',
        'region': region or 'National',
        'shortage_areas': shortage_areas,
        'total_data_points': len(vacancy_data) + len(neet_data) + len(trade_data) + len(population_data) + len(labour_data),
        'data_sources': {
            'vacancies': vacancy_signal['count'],
            'neet': neet_signal['count'],
            'trade': trade_signal['count'],
            'population': pop_signal['count'],
            'labour_market': labour_signal['count'],
        },
        'external_check': {
            'datagovuk': _fetch_datagovuk(f'labour shortage {region or "UK"}'),
        },
        'recommendations': [
            'Check ONS Vacancies and Jobs bulletin for real-time vacancy data',
            'Review Migration Advisory Committee shortage occupation list',
            'Cross-reference with Sector Skills Councils for industry-specific gaps',
        ],
    }


def find_skill_opportunities(postcode, budget=None):
    """What could I learn that's scarce."""
    vacancy_data = _load_ons_data('vacancies', limit=200)
    earnings_data = _load_ons_data('earnings', limit=200)
    neet_data = _load_ons_data('NEET', limit=100)

    postcode_upper = postcode.upper().strip()
    district = postcode_upper.split()[0] if postcode_upper.split() else postcode_upper

    skill_scores = {}
    for trade in TRADE_KEYWORDS:
        vacancy_count = sum(1 for d in vacancy_data if trade.lower() in json.dumps(d).lower())
        earnings_count = sum(1 for d in earnings_data if trade.lower() in json.dumps(d).lower())
        neet_count = sum(1 for d in neet_data if trade.lower() in json.dumps(d).lower())

        demand_score = vacancy_count * 3 + earnings_count * 2
        supply_inverse = max(1, 10 - neet_count)

        skill_scores[trade] = {
            'demand_signal': demand_score,
            'supply_inverse': supply_inverse,
            'opportunity_score': round(demand_score / supply_inverse, 1),
            'vacancy_mentions': vacancy_count,
            'earnings_mentions': earnings_count,
        }

    sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1]['opportunity_score'], reverse=True)

    top_opportunities = []
    for skill, scores in sorted_skills[:10]:
        if scores['opportunity_score'] > 0:
            training_cost_estimates = {
                'electrician': 5000, 'plumber': 4000, 'carpenter': 3500,
                'bricklayer': 3000, 'welder': 2500, 'gas engineer': 4500,
                'air conditioning': 3500, 'scaffolder': 2000, 'roofer': 2500,
                'tiler': 2000, 'plasterer': 2500, 'painter': 1500,
            }
            est_cost = training_cost_estimates.get(skill, 3000)

            if budget and est_cost > budget:
                continue

            top_opportunities.append({
                'skill': skill,
                'opportunity_score': scores['opportunity_score'],
                'demand_signal': scores['demand_signal'],
                'vacancy_mentions': scores['vacancy_mentions'],
                'estimated_training_cost': f'~£{est_cost}',
                'breakeven_months': round(est_cost / (scores['demand_signal'] * 10 + 1), 1),
            })

    return {
        'status': 'ok',
        'postcode': postcode_upper,
        'district': district,
        'budget': f'£{budget}' if budget else 'No limit',
        'top_opportunities': top_opportunities,
        'total_skills_analysed': len(TRADE_KEYWORDS),
        'data_points': len(vacancy_data) + len(earnings_data) + len(neet_data),
        'recommendations': [
            'Higher opportunity_score = higher demand relative to supply',
            'Check local colleges for certified courses in top skills',
            'Consider CITB, City & Guilds, or NVQ qualifications',
            f'Search data.gov.uk for {district} skills funding programmes',
        ],
    }


def market_gap(business_type, city):
    """Is there room for a business in a city."""
    business_data = _load_ons_data('business', limit=200)
    retail_data = _load_ons_data('retail', limit=200)
    population_data = _load_ons_data('population', limit=100)
    spending_data = _load_ons_data('spending', limit=100)

    city_lower = city.lower()
    business_keywords = business_type.lower().split()

    city_business = [d for d in business_data if city_lower in json.dumps(d).lower()]
    city_retail = [d for d in retail_data if city_lower in json.dumps(d).lower()]

    type_match_business = [d for d in city_business if _keyword_match(json.dumps(d), business_keywords)]
    type_match_retail = [d for d in city_retail if _keyword_match(json.dumps(d), business_keywords)]

    existing_count = len(type_match_business) + len(type_match_retail)
    total_city_business = len(city_business)
    total_city_retail = len(city_retail)

    if existing_count == 0:
        gap_signal = 'STRONG GAP'
        assessment = f'No {business_type} data found for {city} - potential first-mover advantage'
    elif existing_count < 3:
        gap_signal = 'MODERATE GAP'
        assessment = f'Limited {business_type} presence in {city} - room for differentiated competitor'
    else:
        gap_signal = 'SATURATED'
        assessment = f'Existing {business_type} activity in {city} - niche or innovation required'

    spending_match = _compute_signal_score(spending_data, lambda x: _keyword_match(json.dumps(x), business_keywords))

    pop_match = _compute_signal_score(population_data, lambda x: city_lower in json.dumps(x).lower())

    datagovuk_results = _fetch_datagovuk(f'{business_type} business {city}')
    london_results = _fetch_london_datastore(f'{business_type} {city}') if city_lower in ('london', 'westminster', 'camden', 'islington', 'hackney', 'tower hamlets') else []

    return {
        'status': 'ok',
        'business_type': business_type,
        'city': city.title(),
        'gap_signal': gap_signal,
        'assessment': assessment,
        'market_data': {
            'existing_business_mentions': existing_count,
            'total_city_business_data': total_city_business,
            'total_city_retail_data': total_city_retail,
            'spending_signals': spending_match['count'],
            'population_signals': pop_match['count'],
        },
        'external_sources': {
            'datagovuk': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in datagovuk_results[:3]],
            'london_datastore': [{'title': r.get('title', ''), 'url': r.get('url', '')} for r in london_results[:3]],
        },
        'recommended_research': [
            f'ONS UK Business: Activity, Size and Location for {city}',
            f'ONS Retail Sales Index for consumer spending trends',
            f'Check local council licensing/planning data for {city}',
            f'Populus/Fusion Brick data for local demographics',
        ],
    }


def wage_growth_map(region=None, occupation=None):
    """Where wages are rising fastest."""
    earnings_data = _load_ons_data('earnings', limit=200)
    ashe_data = _load_ons_data('annual survey of hours and earnings', limit=100)

    if occupation:
        earnings_filtered = [d for d in earnings_data if occupation.lower() in json.dumps(d).lower()]
        ashe_filtered = [d for d in ashe_data if occupation.lower() in json.dumps(d).lower()]
    else:
        earnings_filtered = earnings_data
        ashe_filtered = ashe_data

    region_wages = {}
    uk_regions = [
        'london', 'south east', 'south west', 'east midlands', 'west midlands',
        'north west', 'north east', 'yorkshire and the humber', 'east of england',
        'scotland', 'wales', 'northern ireland',
    ]

    for reg in uk_regions:
        reg_earnings = [d for d in earnings_filtered if reg in json.dumps(d).lower()]
        reg_ashe = [d for d in ashe_filtered if reg in json.dumps(d).lower()]

        total_mentions = len(reg_earnings) + len(reg_ashe)

        region_wages[reg.title()] = {
            'earnings_data_points': len(reg_earnings),
            'ashe_data_points': len(reg_ashe),
            'total_signal': total_mentions,
        }

    if region:
        region_lower = region.lower()
        focused = {k: v for k, v in region_wages.items() if region_lower in k.lower()}
        if not focused:
            focused = region_wages
    else:
        focused = region_wages

    sorted_regions = sorted(focused.items(), key=lambda x: x[1]['total_signal'], reverse=True)

    growth_indicators = []
    for reg_name, data in sorted_regions:
        if data['total_signal'] > 3:
            growth_indicators.append({
                'region': reg_name,
                'signal_strength': 'STRONG' if data['total_signal'] > 6 else 'MODERATE',
                'data_coverage': data['total_signal'],
                'earnings_mentions': data['earnings_data_points'],
                'ashe_mentions': data['ashe_data_points'],
            })

    return {
        'status': 'ok',
        'region': region or 'All UK regions',
        'occupation': occupation or 'All occupations',
        'growth_indicators': growth_indicators,
        'full_breakdown': dict(sorted_regions),
        'data_sources': {
            'earnings_bulletins': len(earnings_filtered),
            'ashe_datasets': len(ashe_filtered),
        },
        'note': 'Signal strength reflects data availability and mentions. Higher signal = more active wage reporting for that region.',
        'recommended_actions': [
            'Check ONS ASHE for detailed regional earnings tables',
            'Review ONS Employee Earnings bulletin for latest quarterly data',
            f'data.gov.uk search for {occupation or "earnings"} {region or "regional"} data',
        ],
    }


# ============================================================
# DISPATCH
# ============================================================

DISPATCH = {t['name']: globals()[t['name']] for t in TOOLS}


def handle_tool_call(name, args):
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
                    "serverInfo": {"name": "ukgraph", "version": "1.0.0",
                                   "description": "UKGraph — UK markets intelligence. Find career opportunities, business gaps, trade demand, regulation impacts."},
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
        print(json.dumps({"name": "ukgraph", "tools": [t["name"] for t in TOOLS]}, indent=2))
