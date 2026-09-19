# UKGraph — Canonical Resources

## Live Data (collectors built)

| Source | Records | API | Status |
|--------|---------|-----|--------|
| ons_jobs.py | ONS bulletins + datasets | ONS API | ✅ 68 records collected |
| companies_house.py | Company births/deaths | WebSocket streaming | ⚠️ Needs API key |
| ukgraph_historical.py | Nomis + ASHE + bulk | Multiple APIs | ✅ Built |

## Historical Datasets (collectors built)

| Source | Records | Access | What it unlocks |
|--------|---------|--------|-----------------|
| Nomis API | Employment/unemployment by occupation × region | Free REST API | Labour market intelligence |
| ASHE | Earnings by occupation × region (annual) | Free CSV | Wage scarcity/change |
| Companies House bulk | ~469MB monthly snapshot | Free download | All UK registered companies |
| Land Registry Price Paid | Every sale since 1995 | Free CSV (5.3GB) | Property transaction economics |
| Business Demography | Enterprise births/deaths | Free CSV | Business lifecycle |
| Contracts Finder | Government procurement OCDS | Free API | What government buys |
| Business Counts | Enterprise counts by SIC/region | Free CSV | Market structure |

## ONS Official Datasets (free, direct download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| Labour Market Statistics Time Series | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourmarketstatistics/current) | 11.7 MB CSV/XLS | THE core UK labour dataset |
| UK Business: Activity, Size and Location | [ONS](https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/datasets/ukbusinessactivitysizeandlocation) | Multiple XLS | 2.7M+ businesses by SIC, region, size |
| Average Weekly Earnings (EARN01) | ONS (within LMS) | Part of LMS | Pay by industry and region |
| Workforce Jobs (JOBS01/02) | ONS | Part of LMS | Jobs by industry, public/private |
| Claimant Count | NOMIS | Monthly | Most timely local labour signal |
| Annual Population Survey | NOMIS | Large | Qualifications, earnings, benefits |

## HuggingFace Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| `fabsssss/uk-local-labour-market` | [HF](https://huggingface.co/datasets/fabsssss/uk-local-labour-market) | 374 rows | Claimant count per local authority |
| `jhumbl/uk-open-data` | [HF](https://huggingface.co/datasets/jhumbl/uk-open-data) | Multiple parquet | Weekly: transport, policing, food safety, vehicle licensing |
| `theodi/ndl-core-corpus` | [HF](https://huggingface.co/datasets/theodi/ndl-core-corpus) | 156K+ records | GOV.UK, Hansard, ONS, Defra, legislation |
| `dacheah/uk-company-financials` | [HF](https://huggingface.co/datasets/dacheah/uk-company-financials) | 3.73M filings, 3.49M companies | Companies House financials, normalized |
| `fabsssss/uk-consultation-corpus` | [HF](https://huggingface.co/datasets/fabsssss/uk-consultation-corpus) | 6,260 consultations | Government consultations with policy coding |
| `othertales/uklegislation` | [HF](https://huggingface.co/datasets/othertales/uklegislation) | 175,515 documents | Full UK legislation corpus |

## Kaggle Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| UK Housing Prices Paid | [Kaggle](https://www.kaggle.com/datasets/hm-land-registry/uk-housing-prices-paid) | 22M+ rows, 2.41 GB | Every property sale since 1995 |
| UK Property Sales Geo-enriched | [Kaggle](https://www.kaggle.com/datasets/mansiaggarwal88/uk-property-sale-prices-20152026-geo-enriched) | 11M+ rows, 2.22 GB | Land Registry + lat/long |
| UK Housing Cleaned | [Kaggle](https://www.kaggle.com/datasets/burhanimtengwa/uk-housing-cleaned) | 1.6M+ rows | Cleaned, region-enriched, ML-ready |
| UK Inflation Data 1989-2022 | [Kaggle](https://www.kaggle.com/datasets/scarfsman/uk-inflation-data-1989-2022) | 3 CSVs | CPIH breakdown |

## Other Sources

| Source | URL | What it unlocks |
|--------|-----|-----------------|
| HM Land Registry PPD | [GOV.UK](https://www.gov.uk/government/statistical-data-sets/price-paid-data-single-file) | 5.3 GB CSV, 24M+ records from 1995 |
| UK House Price Index | [Land Registry](http://landregistry.data.gov.uk/app/ukhpi/) | SPARQL/CSV, monthly from 1995 |
| data.gov.uk API Catalogue | [api.gov.uk](https://www.api.gov.uk/) | 1000s of UK government APIs |
| open-data.org.uk | [open-data.org.uk](https://open-data.org.uk) | 104,000+ datasets, 193 portals |
| A Millennium of Macroeconomic Data | [datahub.io](https://datahub.io/economic-history/millennium-macroeconomic-data-uk) | GDP, wages, prices from 1086! |
| Planning Data Platform | [planning.data.gov.uk](https://www.planning.data.gov.uk/) | Planning and housing data |
| DfT Road Traffic | [roadtraffic.dft.gov.uk](https://roadtraffic.dft.gov.uk/downloads) | Traffic 1993-2025 |
| DESNZ Electricity | GOV.UK | Consumption 2005-2024 |
| EPC Data | [get-energy-performance-data](https://get-energy-performance-data.communities.gov.uk/) | Building certificates from 2012 |

## MCP Servers for UK Data

| MCP Server | URL | Tools |
|------------|-----|-------|
| `paulieb89/govuk-mcp` | [GitHub](https://github.com/paulieb89/govuk-mcp) | 7: search, content, grep, orgs, postcode |
| `Stealth-Labs-LTD/GovUK-MCP` | [GitHub](https://github.com/Stealth-Labs-LTD/GovUK-MCP) | 33: Companies House, TfL, NHS, Parliament, Police, Courts |
| `HappyMonkeyAI/OpenUKPublicDataMCP` | [GitHub](https://github.com/HappyMonkeyAI/OpenUKPublicDataMCP) | Postcodes, GOV.UK, bank holidays, carbon, flood, Parliament |

## Human Tasks Required

| Task | Priority | Unlocks |
|------|----------|---------|
| Download ONS Labour Market Statistics (11.7MB) | Critical | Core UK labour data |
| Download Land Registry PPD (5.3GB) | Critical | 24M+ property sales |
| Download HuggingFace UK datasets | High | 6 datasets, 4M+ records |
| Download Kaggle UK housing datasets | High | 24M+ property records |
| Get Companies House API key (free) | High | Live company data |
| Download ASHE earnings data | Medium | Wage data by occupation |
| Download Business Demography | Medium | Enterprise births/deaths |
