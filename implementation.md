# DataGarden Implementation

## Architecture

```text
QUESTION (human sentence)
    ↓
VIDEO TITLE (clickable)
    ↓
EXPERIMENT (publish)
    ↓
ATTENTION SIGNAL (YouTube analytics)
    ↓
CAPABILITY (MCP tool / Muse connector)
    ↓
AGENT USAGE (real requests)
    ↓
OUTCOME DATA (resolved answers)
    ↓
NEW QUESTIONS
```

Historical datasets give the plant roots. YouTube tells us where the sunlight is. Agent usage tells us where to grow branches. Verified outcomes become the new wood.

---

## Garden Status

| Garden | Historical Data | Live Collectors | MCP Server | Status |
|--------|----------------|-----------------|------------|--------|
| Breadup | CoinGecko ✅ SoldComps needs local | eBay blocked from VPS | 10 tools ✅ | Seed phase |
| UKGraph | ONS bulletins ✅ (68 records) | Nomis needs API key | 10 tools ✅ | Seed phase |
| PowPowPow | 17 chains live ✅ | 24 collectors ✅ | 12 tools ✅ | Operational |
| UK Admin | 36 curated tasks ✅ | GOV.UK API ✅ | 12 tools ✅ | Seeded |

---

## Historical Datasets

### Breadup — Physical Goods

| Source | Records | Access | What It Unlocks |
|--------|---------|--------|-----------------|
| **SoldComps API** | 40/request, free tier | REST API, no key needed for basic | Real eBay sold prices, dates, conditions |
| **CoinGecko API** | 365 days × 18 coins | Free, 10-30 calls/min | Reference prices for crypto-related items |
| **Kaggle eBay datasets** | ~980K (2020) + 1.8M (2021) | Download, no API key | Product normalization, title → entity mapping |
| **NBER bargaining data** | 98M Best Offer records (2012-13) | Download from NBER | Negotiation models, seller acceptance behavior |
| **eBay Product Research** | 3 years of sales | Free for eBay sellers | Sell-through, seasonality, trends |
| **Terapeak** | ~3 years | Built into eBay Seller Hub | Historical pricing context |

**How to seed Breadup:**

```bash
# 1. SoldComps (works from any machine)
python -m collectors.breadup_historical --seed-soldcomps

# 2. CoinGecko reference prices
python -m collectors.breadup_historical --seed-coingecko

# 3. Kaggle datasets (requires kaggle CLI)
pip install kaggle
kaggle datasets download -d promptcloud/ebay-product-listing-dataset -p /tmp/kaggle
python -m collectors.breadup_historical --load-kaggle /tmp/kaggle

# 4. NBER bargaining data
python -m collectors.breadup_historical --download-nber
```

**Data directory:** `forests/breadup/data/historical/`

**Canonical form:**
```python
{
    "object_id": "ebay_2026_abc123",
    "canonical_name": "Canon EOS R6",
    "category": "cameras",
    "subcategory": "mirrorless",
    "brand": "Canon",
    "model": "EOS R6",
    "condition": "used_good",
    "sold_price_gbp": 1250.00,
    "original_price_gbp": 1499.00,
    "platform": "ebay_uk",
    "sold_date": "2026-09-15",
    "source": "sold_comps_api",
    "observed_at": "2026-09-19T14:00:00"
}
```

**What NBER data gives us:**
```text
98 million Best Offer listings with:
- asking price
- offer #1
- counter #1
- offer #2
- ...
- accepted / rejected / expired
- category, condition, seller history

→ Train Jev: P(seller accepts offer at 0.72 × ask)?
→ Muse capability: "What should I offer this seller?"
```

---

### UKGraph — UK Markets

| Source | Records | Access | What It Unlocks |
|--------|---------|--------|-----------------|
| **Nomis API** | Employment/unemployment by occupation × region | Free REST API | Labour market intelligence |
| **ASHE** | Earnings by occupation × region (annual) | Free CSV download | Wage scarcity/change |
| **ONS Job Ads** | Adzuna index Feb 2018 – Oct 2024 | Free CSV | Historical labour demand |
| **Companies House bulk** | ~469MB monthly snapshot | Free download | All UK registered companies |
| **Land Registry** | Every sale since 1995 | Free CSV | Property transaction economics |
| **Business Demography** | Enterprise births/deaths | Free CSV | Business lifecycle |
| **Contracts Finder** | Government procurement OCDS | Free API | What government buys |
| **Business Counts** | Enterprise counts by SIC/region | Free CSV | Market structure |
| **DfT Traffic** | Road traffic 1993–2025 | Free CSV | Physical activity proxy |
| **DESNZ Electricity** | Consumption 2005–2024 | Free CSV | Economic activity proxy |
| **EPC Data** | Building certificates from 2012 | Free download | Property characteristics |

**How to seed UKGraph:**

```bash
# 1. Nomis employment data
python -m collectors.ukgraph_historical --seed-nomis

# 2. ASHE earnings
python -m collectors.ukgraph_historical --seed-ashe

# 3. Companies House bulk (large download, ~469MB)
python -m collectors.ukgraph_historical --seed-companies-house

# 4. Land Registry Price Paid
python -m collectors.ukgraph_historical --seed-land-registry

# 5. All at once
python -m collectors.ukgraph_historical --seed-all
```

**Data directory:** `forests/room/data/historical/`

**Canonical form (employment):**
```python
{
    "series_id": "nomis_emp_2024_q1",
    "metric": "employment_rate",
    "occupation": "6135",
    "occupation_name": "Software developers",
    "region": "E12000001",
    "region_name": "North East",
    "period": "2024-Q1",
    "value": 92.3,
    "unit": "rate_per_1000",
    "source": "nomis",
    "observed_at": "2026-09-19T14:00:00"
}
```

**Canonical form (company):**
```python
{
    "company_number": "SC123456",
    "company_name": "Example Ltd",
    "sic_code": "62011",
    "sic_description": "Software programming activities",
    "region": "Scotland",
    "postcode": "EH1 1BB",
    "status": "active",
    "incorporation_date": "2020-01-15",
    "source": "companies_house",
    "observed_at": "2026-09-19T14:00:00"
}
```

**Canonical form (property):**
```python
{
    "transaction_id": "12345678",
    "price": 285000,
    "date": "2026-08-15",
    "postcode": "M1 1AA",
    "property_type": "D",
    "new_build": false,
    "tenure": "F",
    "source": "land_registry",
    "observed_at": "2026-09-19T14:00:00"
}
```

**Cross-source joins that create value:**
```text
employment (Nomis)
+ wages (ASHE)
+ job adverts (ONS/Adzuna)
+ business formations (Business Demography)
+ business closures (Business Demography)
+ companies (Companies House)
+ public contracts (Contracts Finder)
+ property (Land Registry)
+ energy (DESNZ)
+ traffic (DfT)

→ CONSTRAINT SURFACE
→ "What is Britain running out of?"
→ "Where are wages rising fastest?"
→ "Which businesses are dying vs being born?"
```

---

### UK Admin — Get Boring British Things Done

```text
UKGRAPH = understand Britain
UK ADMIN = get boring British things done
```

| Source | Records | Access | What It Unlocks |
|--------|---------|--------|-----------------|
| **GOV.UK API** | All services + transactions | Free REST API | Complete government service map |
| **GOV.UK One Login** | Auth status | Public tracking | Agent authentication boundaries |
| **Curated tasks** | 36 tasks across 9 categories | Built-in | Immediate capability |
| **DVLA/DVSA** | Driving + vehicle services | GOV.UK API | Licence, MOT, tax |
| **HMRC** | Tax obligations | GOV.UK API | Self assessment, VAT, PAYE |
| **Companies House** | Company setup/management | Free API | Business administration |

**How to seed UK Admin:**

```bash
# 1. Curated tasks (works immediately)
python -m collectors.uk_admin_collectors --seed-curated

# 2. Full GOV.UK service map
python -m collectors.uk_admin_collectors --seed-govuk

# 3. Build action graph
python -m collectors.uk_admin_collectors --build-graph
```

**Data directory:** `forests/uk_admin/data/`

**Canonical form (task):**
```python
{
    "task_id": "renew_driving_licence",
    "task_name": "Renew your driving licence",
    "category": "driving",
    "authority": "DVLA",
    "jurisdiction": "GB",
    "url": "https://www.gov.uk/renew-driving-licence",
    "cost_gbp": 14.00,
    "takes_time": "3 weeks",
    "requires": ["identity", "licence_details", "address", "photo"],
    "agent_permissions": {
        "explain": True,
        "gather_requirements": True,
        "prefill": True,
        "submit": False,
        "payment": "explicit_approval",
        "retain_credentials": False
    },
    "failure_modes": ["identity_mismatch", "address_mismatch"],
    "last_verified": "2026-09-19",
    "is_recurring": True,
    "recurrence": "every 10 years"
}
```

**The garden knows where the boundary is:**

Since May 2026, DVSA says a car candidate **must book their own test**. Our garden returns:

```text
ACTION CLASS: USER_ONLY

Muse may:
✓ identify test centres
✓ explain release/cancellation mechanics
✓ collect information needed
✓ remind you

Muse must hand control to user for:
✗ booking
✗ changing
✗ cancelling
```

**Connection to UKGraph:**

UKGraph discovers: "Manchester driving instructors constrained, prices rising."

UK Admin knows: "Here's exactly what becoming one entails — requirements, qualification sequence, fees, registration."

Muse: "Given your situation, here's the process and the parts I can handle."

**The proposition:** "Muse, keep my UK life admin sorted."

---

### PowPowPow — Compute Economics

| Source | Records | Access | What It Unlocks |
|--------|---------|--------|-----------------|
| **Existing collectors** | 17 chains, 24 collectors | Live API calls | Real-time chain state |
| **CoinGecko history** | Price/market for 18 mineable coins | Free, 10-30 calls/min | Historical price reconstruction |
| **Minerstat benchmarks** | 10,730 hardware/algorithm pairs | Free API | Hardware capability database |
| **WhatToMine** | Network difficulty/hashrate | Free (scraping) | Network economics history |
| **Open Bitcoin Metrics** | Full-node verified daily metrics | Open source | Bitcoin gold standard |
| **Hashrate.no** | GPU/CPU benchmarks | Free basic | Hardware efficiency data |
| **NiceHash** | Profitability calculator | Free | Rental vs mining comparison |

**How to seed PowPowPow:**

```bash
# 1. CoinGecko price history
python -m collectors.powpowpow_historical --seed-coingecko

# 2. Minerstat hardware benchmarks
python -m collectors.powpowpow_historical --seed-minerstat

# 3. WhatToMine network data
python -m collectors.powpowpow_historical --seed-what-to-mine

# 4. All at once
python -m collectors.powpowpow_historical --seed-all
```

**Data directory:** `forests/powpowpow/data/historical/` + `/home/box/powpowpow/chains/`

**Canonical form (price):**
```python
{
    "symbol": "XMR",
    "timestamp": "2026-09-19T00:00:00",
    "price_usd": 564.55,
    "market_cap": 10400000000,
    "volume_24h": 85000000,
    "source": "coingecko",
    "observed_at": "2026-09-19T14:00:00"
}
```

**Canonical form (hardware):**
```python
{
    "device": "RTX_4090",
    "algorithm": "RandomX",
    "hashrate": 26000,
    "hashrate_unit": "H/s",
    "power_watts": 450,
    "cost_usd": 1599,
    "efficiency": 57.8,
    "source": "minerstat",
    "observed_at": "2026-09-19T14:00:00"
}
```

**Historical reconstruction formula:**
```text
given:
  historical price (CoinGecko)
  historical difficulty (WhatToMine)
  hardware benchmark (Minerstat)

calculate:
  expected_coins/day = hashrate / difficulty × block_reward × 86400
  revenue/day = expected_coins/day × price
  electricity/day = power_watts × 24 / 1000 × cost_per_kwh
  profit/day = revenue - electricity

→ reconstruct any historical timestamp
→ before today = reconstructed evidence
→ after today = verified evidence
```

---

## MCP Servers

### Individual servers (recommended for Muse/agents)

| Server | File | Tools | Status |
|--------|------|-------|--------|
| Breadup | `mcp/breadup_mcp.py` | 10 | ✅ |
| UKGraph | `mcp/ukgraph_mcp.py` | 10 | ✅ |
| PowPowPow | `mcp/powpowpow_mcp.py` | 12 | ✅ |

### Unified server (all gardens combined)

| Server | File | Tools | Status |
|--------|------|-------|--------|
| DataGarden | `mcp_server.py` | 23 | ✅ |

**Running:**
```bash
# CLI mode
python mcp/breadup_mcp.py value_listing '{"item": "technics turntable", "asking_price": 180}'

# MCP stdio mode (for agents)
python mcp/powpowpow_mcp.py --serve
```

---

## Capability-First Tools (what people actually ask)

| Question | Garden | Tool | Video Title |
|----------|--------|------|-------------|
| "Can this gaming PC make money?" | PowPowPow | `can_my_pc_make_money` | "Can Your Gaming PC Make Money While You Sleep?" |
| "What should I mine?" | PowPowPow | `what_should_i_mine` | "We Tracked RTX 4090 Profitability Every Hour" |
| "Mine or rent?" | PowPowPow | `mine_or_rent` | "Mine or Rent? The Math Will Surprise You" |
| "Is this a bargain?" | Breadup | `value_listing` | "Can AI Spot Undervalued Listings?" |
| "What should I offer?" | Breadup | `max_offer` | "I Tracked 10,000 eBay Sales to Find What Flips" |
| "What could I flip?" | Breadup | `find_flips` | "What Stuff Around You Could You Flip?" |
| "What is Britain running out of?" | UKGraph | `find_shortages` | "What Is Britain Running Out Of?" |
| "Should I switch careers?" | UKGraph | `career_crowding` | "The UK Jobs Getting Crowded Fastest" |
| "Is there room for a business?" | UKGraph | `market_gap` | "What Businesses Are Undersupplied?" |
| "Where are wages rising?" | UKGraph | `wage_growth_map` | "Where Wages Are Rising Fastest" |

---

## Jev Integration

**Installed:** `typesafe-sdk>=0.7` ✅

**Question templates:** `experiments/jev_questions.json` ✅

**Functions in `shared/jev.py`:**
- `classify_observation(state, forest)` — classify raw data
- `score_hypothesis(state)` — gate content before creation
- `classify_response(state)` — post-publish audience analysis
- `batch_classify(texts, forest)` — bulk classification

**Activation:** Add `TYPESAFE_API_KEY=your_key` to `.env`
**Cost:** $0.042 per million input tokens, output free

---

## Muse Connector

**Submission doc:** `docs/muse_connector_submission.md` ✅

**Submit at:** https://muse.ai/platform

**What Muse users would ask:**
- "Is this Marketplace camera a bargain?"
- "Should I mine Qubic or rent my GPUs?"
- "What businesses are undersupplied near me?"
- "What should I learn to get a higher-paying job?"

---

## File Structure

```
datagarden/
├── CANONICAL.md              # The architecture reference
├── capabilities.md           # Fake Muse requests → video titles → capabilities
├── mcp_server.py             # Unified MCP server (23 tools)
├── mcp/
│   ├── breadup_mcp.py        # Breadup standalone MCP (10 tools)
│   ├── ukgraph_mcp.py        # UKGraph standalone MCP (10 tools)
│   └── powpowpow_mcp.py      # PowPowPow standalone MCP (12 tools)
├── shared/
│   ├── jev.py                # TypeSafe Jev integration
│   ├── normalize.py          # Canonical schemas + normalization
│   ├── schema.py             # Existing dataclasses
│   ├── warehouse.py          # Storage layer
│   ├── entities.py           # Entity registry
│   ├── manifest.py           # Daily manifests
│   └── experiment.py         # PublicationExperiment
├── collectors/
│   ├── ebay_free.py          # eBay public search (VPS-blocked)
│   ├── ons_jobs.py           # ONS + GOV.UK data
│   ├── companies_house.py    # Companies House streaming
│   ├── breadup_historical.py # Breadup seed collectors
│   ├── ukgraph_historical.py # UKGraph seed collectors
│   └── powpowpow_historical.py # PowPowPow seed collectors
├── capabilities/
│   └── evaluate_hardware.py  # First probe capability
├── content/
│   └── pipeline.py           # Video generation (with Jev gate)
├── experiments/
│   ├── jev_questions.json    # Question templates
│   └── jev_log.jsonl         # Jev call log
├── forests/
│   ├── breadup/data/         # Breadup JSONL data
│   ├── room/data/            # UKGraph JSONL data
│   └── powpowpow/            # PowPowPow chain data
├── docs/
│   └── muse_connector_submission.md
├── requirements.txt
├── .env.example
└── SETUP.md
```

---

## Setup Checklist

```bash
# 1. Install
cd /home/box/datagarden
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Environment
cp .env.example .env
# Add: TYPESAFE_API_KEY=your_key (optional, for Jev)
# Add: COMPANIES_HOUSE_API_KEY=your_key (free, for live company data)

# 3. Seed PowPowPow (works immediately)
python -m collectors.powpowpow_historical --seed-coingecko

# 4. Test MCP server
python mcp/powpowpow_mcp.py all_networks '{}'
python mcp_server.py can_my_pc_make_money '{"gpu": "RTX_4090"}'

# 5. Seed UKGraph (needs local machine for full data)
python -m collectors.ukgraph_historical --seed-nomis

# 6. Seed Breadup (needs local machine)
python -m collectors.breadup_historical --seed-soldcomps

# 7. Run daily collection
python -m collectors.run_daily
```

---

## The Loop

```text
QUESTION
   ↓
CONTENT
   ↓
ATTENTION SIGNAL
   ↓
RESEARCH
   ↓
DATA
   ↓
JEV
   ↓
CAPABILITY
   ↓
AGENT USAGE
   ↓
OUTCOME DATA
   └────────────→ QUESTION
```

Historical datasets give the plant roots. YouTube tells us where the sunlight is. Agent usage tells us where to grow branches. Verified outcomes become the new wood.

The gardens become demand-shaped. Don't build a capability until you can write ten compelling natural-language requests for it.
