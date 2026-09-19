# UK Admin (Boring UK) — Canonical Resources (Updated)

## Government APIs (free, most need no key)

| API | URL | What it unlocks |
|-----|-----|-----------------|
| GOV.UK Content API | [content-api.publishing.service.gov.uk](https://content-api.publishing.service.gov.uk/) | Full structured GOV.UK content, JSON, no auth |
| GOV.UK Search API | GOV.UK | Full-text search across 700K+ pages, no auth |
| Companies House API | [developer.company-information.service.gov.uk](https://developer.company-information.service.gov.uk/) | Company register, officers, filings (free key) |
| DVLA Vehicle Enquiry API | [developer-portal.driver-vehicle-licensing.api.gov.uk](https://developer-portal.driver-vehicle-licensing.api.gov.uk/) | Vehicle details by registration |
| postcodes.io | [postcodes.io](https://postcodes.io) | Postcode → coordinates, council, constituency |
| Police Data API | [data.police.uk](https://data.police.uk/) | Street-level crime, outcomes, stop & search |
| Food Standards Agency API | FSA | Food hygiene ratings |
| Environment Agency Flood API | EA | Live flood warnings |
| NHS Service Search | NHS | GP, hospital, pharmacy finder |

## Council APIs (free, game-changing for Boring UK)

| API | URL | What it unlocks |
|-----|-----|-----------------|
| UK Bin Collection API | [ukbinday.co.uk/api/v1](https://ukbinday.co.uk/api/v1/docs) | Bin collection schedules by postcode/UPRN |
| UK Bin Collection Data (GitHub) | [robbrad/UKBinCollectionData](https://github.com/robbrad/UKBinCollectionData) | 348 stars, parsers for 100+ UK councils |
| UK Planning API | [ukplanningapi.co.uk](https://ukplanningapi.co.uk/) | Planning applications as JSON/MCP, 500 req/month free |
| Council Listener API | [council-api.arrakis.house](https://council-api.arrakis.house/api) | Council spending data, 39 councils, free |
| DemocracyClub/LGSF | [GitHub](https://github.com/DemocracyClub/LGSF) | Local Government Scraper Framework for council data |
| Gankdat UK Planning | [gankdat.com/stats/uk-planning](https://gankdat.com/stats/uk-planning) | 2K planning applications, normalized schema |
| PlanIt | [planit.org.uk](https://www.planit.org.uk/) | 420 authorities, 20.6M applications, free API |
| data.gov.uk Planning | [data.gov.uk](https://ckan.publishing.service.gov.uk/dataset/planning_applications) | National planning statistics |

## MCP Servers

| MCP Server | URL | Tools |
|------------|-----|-------|
| paulieb89/govuk-mcp | [GitHub](https://github.com/paulieb89/govuk-mcp) | 7: search, content, grep, orgs, postcode |
| Stealth-Labs-LTD/GovUK-MCP | [GitHub](https://github.com/Stealth-Labs-LTD/GovUK-MCP) | 33: Companies House, TfL, NHS, Parliament, Police |
| HappyMonkeyAI/OpenUKPublicDataMCP | [GitHub](https://github.com/HappyMonkeyAI/OpenUKPublicDataMCP) | Postcodes, GOV.UK, bank holidays, carbon, flood |
| matematicsolutions/gb-eli-mcp | [GitHub](https://github.com/matematicsolutions/gb-eli-mcp) | legislation.gov.uk + Find Case Law |

## Government Open Data

| Dataset | URL | What it unlocks |
|---------|-----|-----------------|
| GB Driving Licence Data | [data.gov.uk](https://data.gov.uk/dataset/d0be1ed2-9907-4ec4-b552-c048f6aec16a/gb-driving-licence-data) | Driving licences by DVLA, quarterly |
| Government Contract Awards | [github.com/webtruffle](https://github.com/webtruffle/government-contract-awards) | UK + EU contract awards, daily CSV |
| UK Rates & Thresholds | [github.com/Neonswitched](https://github.com/Neonswitched/uk-rates-thresholds) | Income Tax, NI, benefits + MCP server |
| CouncilData.co.uk | [councildata.co.uk](https://councildata.co.uk/datasets/) | Council tax bands for 350 councils |

## GitHub Repos

| Repo | URL | What it unlocks |
|------|-----|-----------------|
| i-dot-ai/awesome-gov-datasets | [GitHub](https://github.com/i-dot-ai/awesome-gov-datasets) | 141 stars, curated UK gov datasets |
| rithwikshetty/gov-opportunity-scraper | [GitHub](https://github.com/rithwikshetty/gov-opportunity-scraper) | UK tender opportunities scraper |

## HuggingFace Datasets

| Dataset | URL | What it unlocks |
|---------|-----|-----------------|
| AndreasThinks/ukgov-policy-docs | [HF](https://huggingface.co/datasets/AndreasThinks/ukgov-policy-docs) | GOV.UK policy papers + QA pairs |
| BSVGK/Text_to_KG_Construction_Dataset | [HF](https://huggingface.co/datasets/BSVGK/Text_to_KG_Construction_Dataset) | UK procurement contracts → knowledge graph |

## Verified Workflows (from live GOV.UK checks)

| Task | Cost | Agent Doable | Source URL | Verified |
|------|------|--------------|------------|----------|
| Renew driving licence | £14 online | YES (online) | https://www.gov.uk/renew-driving-licence | ✅ |
| Register to vote | Free | YES | https://www.gov.uk/register-to-vote | ✅ |
| Check MOT history | Free | YES | https://www.gov.uk/check-mot-history | ✅ |
| Vehicle tax | Varies | PARTIAL | https://www.gov.uk/vehicle-tax | ✅ |
| Council Tax bands | Free | YES (lookup) | https://www.gov.uk/council-tax-bands | ✅ |

## Human Tasks

| Task | Priority | Unlocks |
|------|----------|---------|
| Get MOT History API credentials (free) | High | Vehicle MOT history back to 2005 |
| Get Companies House API key (free) | High | Company data for business workflows |
| Integrate UK Bin Collection API | High | Real bin collection data for 100+ councils |
| Integrate UK Planning API | Medium | Real planning application data |
