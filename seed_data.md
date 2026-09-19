# Breadup & UKGraph — Seed Data Sources

## BREADUP — Physical Goods Value Graph

### Live/Daily APIs

| Source | What | Access | Cost | Notes |
|--------|------|--------|------|-------|
| **eBay UK Sold** | Completed/sold prices, condition, date, shipping | Apify actors, Trawl API, Parse API, SoldComps API | $1-3/1K listings | eBay shut down Finding API Feb 2025. Apify actors are the main route. 8 marketplaces. |
| **eBay UK Active** | Live listings, prices, categories | Parse API (MCP-ready), Real Data API | Free tier + paid | 7 endpoints, health-checked |
| **Vinted** | Secondhand fashion listings across 19 countries | Scrappa API (500 free credits/mo), Apify actors ($2/1K) | $2-3/1K | No official API. Scrappa/Apify use internal catalog endpoints |
| **Facebook Marketplace** | Local listings, prices, condition | Apify actors ($0.70-2.60/1K), ChocoData scraper | $0.70-2.60/1K | No official API. Scrapers work but Meta enforcement increasing 2025-2026 |
| **Gumtree** | UK-focused classifieds | Apify actors | Varies | Smaller dataset but UK-heavy |
| **Etsy** | Handmade/vintage goods | Official API (free, limited) | Free | Good for vintage/collectible pricing |
| **Reverb** | Musical equipment | Official API | Free | Excellent for instruments/amps/synths |
| **Amazon UK** | Retail reference prices | Keepa API, CamelCamelCamel | Keepa ~€19/mo | Retail replacement value reference |

### Starter Datasets (Kaggle/HuggingFace)

| Dataset | What | Size | Link |
|---------|------|------|------|
| **UK Used Cars** | 100K scraped listings with price, mileage, year, fuel, transmission | 100K rows | Kaggle: adityadesai13/used-car-dataset |
| **Mercari Price** | Product listings with brand, category, condition, description | 1.4M rows | Kaggle: Mercari competition |
| **Clothing Second-Hand** | 31K clothing items with resale prices | 31K rows | NIAID Zenodo |
| **UCI Online Retail** | UK transactions 2010-2011, product/quantity/price | 541K rows | UCI ML Repository |

### GitHub Tools

| Tool | What | Link |
|------|------|------|
| **ebay-sold-prices-api** | Apify Actor for eBay sold prices + comp analytics | github.com/wwwlehyru-web/ebay-sold-prices-api |
| **VintedScraper** | Python scraper for Vinted via ScrapingAnt | github.com/kami4ka/VintedScraper |
| **facebook-marketplace-scraper** | Free FB Marketplace scraper (Playwright) | github.com/danyk20/facebook-marketplace-scraper |
| **ChocoData FB scraper** | Free FB Marketplace scraper (HTTP, no browser) | github.com/ChocoData-com/facebook-marketplace-scraper |

---

## UKGRAPH — UK Business/Local Economy

### Live/Daily APIs

| Source | What | Access | Cost | Notes |
|--------|------|--------|------|-------|
| **Companies House** | Live company info, officers, filings, status, SIC codes | REST API + Streaming API | Free (API key required) | Real-time company births/deaths. Streaming pushes data as it changes. |
| **ONS API** | Business demography, job adverts by occupation/local authority, economic indicators | REST API (beta) | Free (no key) | Job advert volumes by SOC code + local authority, back to 2017 |
| **Planning Data** | 100+ planning/housing datasets, planning applications | REST API | Free | England planning applications geographically |
| **GOV.UK** | Legislation, regulations, statutory instruments | Various APIs | Free | Regulatory change tracking |
| **Land Registry** | Property prices, title data | Price Paid Data | Free | Property market signals |
| **Ordnance Survey** | Postcodes, boundaries, geography | API | Free for some | Geographic joins |

### Starter Datasets (HuggingFace)

| Dataset | What | Size | Link |
|---------|------|------|------|
| **UK Company Financials** | 3.73M filings across 3.49M Companies House companies, normalized XBRL | ~10M rows | HuggingFace: dacheah/uk-company-financials |
| **UK SME Business** | Business data for UK SMEs | 612 rows | HuggingFace: mindweave/uk-sme-business-dataset |
| **Accounting Ledger UK** | UK accounting ledger data | 18.4K rows | HuggingFace: mindweave/accounting-ledger-uk |

### Key ONS Datasets

| Dataset | What | Frequency |
|---------|------|-----------|
| **Business Demography** | Births, deaths, survival by geography + SIC | Annual + Quarterly |
| **Labour Demand Volumes** | Job advert volumes by SOC + local authority | Monthly |
| **UK Business Activity/Size/Location** | Enterprise counts by region/industry/size | Annual |
| **Annual Business Survey** | Turnover, GVA, employment costs by industry/region | Annual |

---

## The Priority Stack

### Breadup — Start collecting NOW

1. **eBay UK sold prices** (Apify actor) — daily, by category
2. **Vinted UK listings** (Scrappa API) — daily, fashion/electronics
3. **Facebook Marketplace UK** (Apify actor) — daily, local
4. **Amazon UK prices** (Keepa) — hourly, retail reference

### UKGraph — Start collecting NOW

1. **Companies House streaming** — real-time company births/deaths
2. **ONS job adverts** — monthly, by occupation + local authority
3. **Planning applications** — daily, by council
4. **ONS business demography** — quarterly, births/deaths/survival

---

## Cost Estimate

| Source | Monthly Volume | Monthly Cost |
|--------|---------------|-------------|
| eBay sold (Apify) | 50K listings | ~$100 |
| Vinted (Scrappa) | 50K listings | Free (500 credits) → $50 |
| Facebook Marketplace | 20K listings | ~$25 |
| Companies House | Unlimited | Free |
| ONS API | Unlimited | Free |
| Planning Data | Unlimited | Free |
| **Total** | | **~$175/mo** |

Or start with just Companies House + ONS (free) + eBay Apify ($100) = ~$100/mo.
