# UK Admin (Boring UK) — Canonical Resources

## Live Data (collectors built)

| Source | Records | API | Status |
|--------|---------|-----|--------|
| uk_admin_collectors.py | 36 curated tasks + GOV.UK API | GOV.UK Content API | ✅ 36 tasks seeded |
| mot_history.py | DVSA MOT History | OAuth2 + API key | ⚠️ Needs credentials |
| council_mcp.py | 8 councils × 10 services | Internal database | ✅ Built |

## HuggingFace Datasets

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| `BSVGK/Text_to_KG_Construction_Dataset` | [HF](https://huggingface.co/datasets/BSVGK/Text_to_KG_Construction_Dataset) | 9,244 records | UK government procurement contracts → knowledge graph |
| `AndreasThinks/ukgov-policy-docs` | [HF](https://huggingface.co/datasets/AndreasThinks/ukgov-policy-docs) | Policy papers + QA | GOV.UK policy papers for LLM fine-tuning |
| `fabsssss/uk-algorithmic-transparency` | [HF](https://huggingface.co/datasets/fabsssss/uk-algorithmic-transparency) | 136 records | UK government AI/algorithmic tool disclosures |

## Government APIs (free, most need no key)

| API | URL | What it unlocks |
|-----|-----|-----------------|
| GOV.UK Content API | [content-api.publishing.service.gov.uk](https://content-api.publishing.service.gov.uk/) | Full structured GOV.UK content, JSON, no auth |
| GOV.UK Search API | GOV.UK | Full-text search across 700K+ pages, no auth |
| Companies House API | [developer.company-information.service.gov.uk](https://developer.company-information.service.gov.uk/) | Company register, officers, filings (free key) |
| DVLA Vehicle Enquiry API | [developer-portal.driver-vehicle-licensing.api.gov.uk](https://developer-portal.driver-vehicle-licensing.api.gov.uk/) | Vehicle details by registration |
| DVLA Driver Image API | [api.gov.uk](https://www.api.gov.uk/dvla/driver-image-api/) | Photo/signature from licence records |
| HMRC VAT Check API | [developer.service.hmrc.gov.uk](https://developer.service.hmrc.gov.uk/) | Check UK VAT numbers |
| postcodes.io | [postcodes.io](https://postcodes.io) | Postcode → coordinates, council, constituency |
| Food Standards Agency API | FSA | Food hygiene ratings |
| Environment Agency Flood API | EA | Live flood warnings |
| Police Data API | [data.police.uk](https://data.police.uk/) | Street-level crime, outcomes, stop & search |
| Charity Commission API | Charity Commission | Charity register data |
| NHS Service Search | NHS | GP, hospital, pharmacy finder |

## Government Open Data Downloads

| Dataset | URL | What it unlocks |
|---------|-----|-----------------|
| GB Driving Licence Data | [data.gov.uk](https://data.gov.uk/dataset/d0be1ed2-9907-4ec4-b552-c048f6aec16a/gb-driving-licence-data) | Driving licences by DVLA, quarterly |
| Government Contract Awards | [github.com/webtruffle](https://github.com/webtruffle/government-contract-awards) | UK + EU contract awards, daily CSV/JSON |
| UK Rates & Thresholds | [github.com/Neonswitched](https://github.com/Neonswitched/uk-rates-thresholds) | Income Tax, NI, benefits, wages, pensions + MCP server |

## Council Open Data

| Source | URL | What it unlocks |
|--------|-----|-----------------|
| CouncilData.co.uk | [councildata.co.uk](https://councildata.co.uk/datasets/) | Council tax bands for all 350 UK councils |
| mySociety Data | [data.mysociety.org](https://data.mysociety.org/) | Aggregated council and government data |
| Barnet Open Data | [open.barnet.gov.uk](https://open.barnet.gov.uk/datasets) | 300+ datasets across 10+ councils |

## MCP Servers for UK Government

| MCP Server | URL | Tools |
|------------|-----|-------|
| `paulieb89/govuk-mcp` | [GitHub](https://github.com/paulieb89/govuk-mcp) | 7: search, content, grep, orgs, postcode |
| `Stealth-Labs-LTD/GovUK-MCP` | [GitHub](https://github.com/Stealth-Labs-LTD/GovUK-MCP) | 33: Companies House, TfL, NHS, Parliament, Police, Courts, Charity, Legislation |
| `SimesD/govuk-mcp` | [GitHub](https://github.com/SimesD/govuk-mcp) | 33 UK government APIs, TypeScript |
| `HappyMonkeyAI/OpenUKPublicDataMCP` | [GitHub](https://github.com/HappyMonkeyAI/OpenUKPublicDataMCP) | Postcodes, GOV.UK, bank holidays, carbon, flood, Parliament, legislation, data.gov.uk |
| `matematicsolutions/gb-eli-mcp` | [GitHub](https://github.com/matematicsolutions/gb-eli-mcp) | legislation.gov.uk + Find Case Law + GOV.UK tribunal |

## GitHub Repos

| Repo | URL | What it unlocks |
|------|-----|-----------------|
| `ONSdigital/sdg-data` | [GitHub](https://github.com/ONSdigital/sdg-data) | UK SDG reporting data |
| `ONSdigital/uk-topojson` | [GitHub](https://github.com/ONSdigital/uk-topojson) | UK geography boundaries 2014-2025 |
| `dfe-analytical-services/mp-lookup` | [GitHub](https://github.com/dfe-analytical-services/mp-lookup) | MP constituencies lookup CSV |
| `dominicm2023/open-data-uk` | [GitHub](https://github.com/dominicm2023/open-data-uk) | 104K+ datasets from 193 portals |

## Human Tasks Required

| Task | Priority | Unlocks |
|------|----------|---------|
| Get MOT History API credentials (free) | High | Vehicle MOT history back to 2005 |
| Get Companies House API key (free) | High | Company data for business workflows |
| Integrate Stealth-Labs-LTD/GovUK-MCP (33 tools) | High | Instant access to 33 UK government APIs |
| Download CouncilData.co.uk data | Medium | Council tax bands for 350 councils |
| Download UK Rates & Thresholds | Medium | Tax/benefit rates + MCP server |
| Download Government Contract Awards | Medium | UK + EU procurement data |
| Submit Muse connector | Medium | Consumer distribution |
