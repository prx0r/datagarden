# Human Tasks — Unlock the Full Data Garden

Every action a human must take before the garden runs on its own.

---

## Table of Contents

1. [System Setup](#system-setup)
2. [API Keys & Accounts](#api-keys--accounts)
3. [Manual Downloads](#manual-downloads)
4. [YouTube Channel Setup](#youtube-channel-setup)
5. [Platform Submissions](#platform-submissions)
6. [Daily/Ongoing Human Actions](#dailyongoing-human-actions)

---

## System Setup

| # | Task | Command | What It Unlocks | Priority |
|---|------|---------|-----------------|----------|
| 1 | Install Python 3.10+ | `python3 --version` | Everything | CRITICAL |
| 2 | Install FFmpeg | `sudo apt install ffmpeg` | Video assembly (all Shorts) | CRITICAL |
| 3 | Create virtualenv + install deps | `cd /home/box/datagarden && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` | All Python collectors & MCP servers | CRITICAL |
| 4 | Install openpyxl | `pip install openpyxl` | ASHE earnings + Business Demography XLSX parsing (UKGraph) | NICE-TO-HAVE |

---

## API Keys & Accounts

### CRITICAL — Required for Core Gardens

| # | Service | What You Get | Where | Cost | Unlocks | Priority |
|---|---------|-------------|-------|------|---------|----------|
| 1 | **Companies House API Key** | Real-time company births/deaths stream | https://developer.company-information.service.gov.uk/ | FREE | UKGraph live collector (`companies_house.py`), company formation tasks (UKAdmin) | CRITICAL |
| 2 | **YouTube Data API Key** | Upload videos + read analytics | https://console.cloud.google.com → Create project → Enable YouTube Data API v3 → Create API key | FREE (10k units/day) | YouTube Shorts publishing loop, analytics feedback, content experiments | CRITICAL |
| 3 | **TypeSafe API Key** (Jev) | Typed observation classification, hypothesis scoring, audience response analysis | https://console.typesafe.ai/keys | FREE ($0.042/Mtok input, output free) | Jev classification of observations, content quality gating, batch processing (`shared/jev.py`) | CRITICAL |

### NICE-TO-HAVE — Improves Data Quality

| # | Service | What You Get | Where | Cost | Unlocks | Priority |
|---|---------|-------------|-------|------|---------|----------|
| 4 | **Apify Token** | Better eBay scraping (structured data, no HTML parsing) | https://apify.com → Sign up → Settings → API & Integrations → Create token | FREE ($5/mo credit, no card needed) | `collectors/ebay_sold.py`, ~2,500 listings/month across 50 categories | NICE-TO-HAVE |
| 5 | **Kaggle Account + API Key** | 2.8M eBay product listings dataset | https://www.kaggle.com → Sign up → Settings → API → Create New Token → Save to `~/.kaggle/kaggle.json` | FREE | `collectors/breadup_historical.py --download-kaggle`, product normalization, title→entity mapping | NICE-TO-HAVE |
| 6 | **MOT History API Credentials** | Vehicle MOT history lookup | https://register-mot-history.api.gov.uk/ | FREE | `collectors/mot_history.py`, vehicle admin tasks | NICE-TO-HAVE |

**MOT API setup** requires 4 env vars:
```
MOT_CLIENT_ID=...
MOT_CLIENT_SECRET=...
MOT_TENANT_ID=...
MOT_API_KEY=...
```

---

## Manual Downloads

These datasets must be downloaded manually — the collectors try but may fail from a VPS.

| # | Dataset | Records | Where | Size | What It Unlocks | Priority |
|---|---------|---------|-------|------|-----------------|----------|
| 1 | **NBER Best Offer Bargaining Data** | 98M Best Offer records (2012-13) | https://www.nber.org/research/data/best-offer-sequential-bargaining | Large (download page, may require manual link following) | Negotiation models, seller acceptance behavior, "What should I offer?" capability | NICE-TO-HAVE |
| 2 | **Kaggle eBay Product Listings** | ~980K (2020) + 1.8M (2021) | https://www.kaggle.com/datasets/promptcloud/ebay-product-listing-dataset | ~200MB compressed | Product normalization, title→entity mapping, historical Breadup seed | NICE-TO-HAVE |
| 3 | **Companies House Bulk Snapshot** | ~5M companies | https://download.companieshouse.gov.uk/ (auto-detected by `ukgraph_historical.py`) | ~469MB compressed | Full UK company database for UKGraph joins | NICE-TO-HAVE |

**How to download NBER data:**
1. Visit https://www.nber.org/research/data/best-offer-sequential-bargaining
2. Find the download link (may be a zip/tar.gz)
3. Download to `/home/box/datagarden/forests/breadup/data/historical/nber_raw/`
4. Run: `python -m collectors.breadup_historical --load-kaggle` (after placing files)

**How to download Kaggle data:**
```bash
pip install kaggle
mkdir -p ~/.kaggle
echo '{"username":"YOUR_USER","key":"YOUR_KEY"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
python -m collectors.breadup_historical --download-kaggle
```

---

## YouTube Channel Setup

| # | Task | URL | What It Unlocks | Priority |
|---|------|-----|-----------------|----------|
| 1 | Create YouTube channel | https://studio.youtube.com | All Shorts publishing | CRITICAL |
| 2 | Upload first 3 probe Shorts | https://studio.youtube.com → Upload → Set as Short (vertical, <60s) | First attention signals, experiment data | CRITICAL |
| 3 | Add thumbnails from `content/shorts/thumb_*.png` | YouTube Studio upload flow | Click-through rate measurement | CRITICAL |
| 4 | Record analytics after 24-48 hours | YouTube Studio → Analytics | Update experiment JSONs with impressions, CTR, views, likes, comments | CRITICAL |
| 5 | Set channel description + links | YouTube Studio → Customization | Brand presence, MCP connector discoverability | NICE-TO-HAVE |

---

## Platform Submissions

| # | Platform | URL | What It Unlocks | Priority |
|---|----------|-----|-----------------|----------|
| 1 | **Submit Muse Connector** | https://muse.ai/platform | DataGarden as a Muse capability (agents can ask "Is this a bargain?", "What should I mine?", etc.) | NICE-TO-HAVE |

---

## Seed Data Commands (Run After Keys Are Set)

These commands populate the gardens with historical data. Some work immediately, others need the keys above.

### PowPowPow — Works Immediately (No Keys Needed)

```bash
# CoinGecko price history (10-30 calls/min free)
python -m collectors.powpowpow_historical --seed-coingecko

# Minerstat hardware benchmarks
python -m collectors.powpowpow_historical --seed-minerstat

# WhatToMine network stats
python -m collectors.powpowpow_historical --seed-what-to-mine

# Bitcoin metrics from Blockchair
python -m collectors.powpowpow_historical --seed-bitcoin

# Reconstruct historical profitability
python -m collectors.powpowpow_historical --seed-profitability

# All at once
python -m collectors.powpowpow_historical --seed-all
```

### UKGraph — Mostly Works (Some Need Keys)

```bash
# Nomis employment data (free, no key)
python -m collectors.ukgraph_historical --seed-nomis

# ASHE earnings (free XLSX download, needs openpyxl)
python -m collectors.ukgraph_historical --seed-ashe

# Companies House bulk (free, large download ~469MB)
python -m collectors.ukgraph_historical --seed-companies-house

# Land Registry Price Paid (free CSV)
python -m collectors.ukgraph_historical --seed-land-registry

# Business Demography (free XLSX, needs openpyxl)
python -m collectors.ukgraph_historical --seed-business-demography

# Contracts Finder (free API, no key)
python -m collectors.ukgraph_historical --seed-contracts

# All at once
python -m collectors.ukgraph_historical --seed-all
```

### Breadup — Needs Keys for Full Power

```bash
# CoinGecko reference prices (free, no key)
python -m collectors.breadup_historical --seed-coingecko

# SoldComps API (free, no key)
python -m collectors.breadup_historical --seed-soldcomps

# Kaggle datasets (needs kaggle CLI + API key)
python -m collectors.breadup_historical --download-kaggle

# NBER data (needs manual download first)
python -m collectors.breadup_historical --download-nber

# Free eBay scraping (works but may be blocked from VPS IPs)
python -m collectors.ebay_free

# Apify eBay scraping (needs APIFY_TOKEN)
python -m collectors.ebay_sold
```

### UK Admin — Works Immediately

```bash
# Curated tasks (built-in, no keys)
python -m collectors.uk_admin_collectors --seed-curated

# Full GOV.UK service map (free API)
python -m collectors.uk_admin_collectors --seed-govuk

# Build action graph
python -m collectors.uk_admin_collectors --build-graph
```

### Live Collectors (Daily)

```bash
# ONS job adverts (free, no key)
python -m collectors.ons_jobs

# Companies House streaming (needs COMPANIES_HOUSE_API_KEY)
python -m collectors.companies_house

# MOT History (needs MOT credentials)
python -m collectors.mot_history --lookup AB12CDE

# Run all daily collectors
python -m collectors.run_daily
```

---

## Daily/Ongoing Human Actions

| # | Action | Frequency | What It Unlocks | Priority |
|---|--------|-----------|-----------------|----------|
| 1 | Run `python -m collectors.run_daily` | Daily | Fresh data collection + Jev classification + manifest | CRITICAL |
| 2 | Upload generated Shorts to YouTube | After each generation | Attention signals for the feedback loop | CRITICAL |
| 3 | Record YouTube analytics (24-48h after upload) | After each upload | Experiment decisions (deepen/prune/pivot) | CRITICAL |
| 4 | Update experiment JSONs with metrics | After analytics review | Jev hypothesis scoring, content strategy | CRITICAL |
| 5 | Review Jev classification logs | Weekly | Identify high-severity, high-actionability signals | NICE-TO-HAVE |
| 6 | Check Apify credit usage | Monthly | Stay within $5/mo free tier | NICE-TO-HAVE |

---

## Environment Variables Summary

Copy `.env.example` to `.env` and fill in:

```bash
# CRITICAL
COMPANIES_HOUSE_API_KEY=        # Free from https://developer.company-information.service.gov.uk/
YOUTUBE_API_KEY=                # Free from https://console.cloud.google.com
TYPESAFE_API_KEY=               # Free from https://console.typesafe.ai/keys

# NICE-TO-HAVE
APIFY_TOKEN=                    # Free $5/mo from https://apify.com

# MOT History (if using vehicle features)
MOT_CLIENT_ID=
MOT_CLIENT_SECRET=
MOT_TENANT_ID=
MOT_API_KEY=
```

---

## Priority Summary

### CRITICAL (garden won't function without these)
1. Python 3.10+ + FFmpeg + pip install
2. Companies House API key
3. YouTube Data API key
4. TypeSafe API key (Jev)
5. YouTube channel + first 3 Shorts uploaded
6. Analytics recording after 48h

### NICE-TO-HAVE (garden works but with less data)
1. Apify token (better eBay data)
2. Kaggle account (2.8M historical eBay listings)
3. NBER data download (98M negotiation records)
4. MOT History API credentials
5. Muse connector submission
6. openpyxl for XLSX parsing

---

## Quick Start Checklist

```
[ ] sudo apt install ffmpeg
[ ] cd /home/box/datagarden && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
[ ] cp .env.example .env
[ ] Get Companies House key → add to .env
[ ] Get YouTube API key → add to .env
[ ] Get TypeSafe key → add to .env
[ ] python -m collectors.uk_admin_collectors --seed-curated
[ ] python -m collectors.powpowpow_historical --seed-all
[ ] python -m collectors.ukgraph_historical --seed-nomis
[ ] python -m collectors.breadup_historical --seed-soldcomps
[ ] python -m collectors.breadup_historical --seed-coingecko
[ ] python content/generate_first_three.py
[ ] Upload shorts to YouTube Studio
[ ] Record analytics after 48h
[ ] Update experiment JSONs
[ ] Set up daily cron: python -m collectors.run_daily
```
