# UKGraph — Canonical Resources (Updated)

## ONS Official Datasets (free, direct download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| Labour Market Statistics Time Series | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourmarketstatistics/current) | 11.7 MB CSV/XLS | Core UK labour data: employment, unemployment, earnings, vacancies |
| Average Weekly Earnings (EARN01) | ONS | Part of LMS | Pay by industry and region |
| Workforce Jobs (JOBS01/02) | ONS | Part of LMS | Jobs by industry, public/private |
| Vacancies by Industry | ONS | Part of LMS | Job vacancies by sector |
| ASHE Table 15 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) | Multiple ZIP (83MB each) | Earnings by SOC × Region (downloaded 2021-2024) |
| ASHE Table 14 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupationbyregion4digitsoc2010ashetable14) | Multiple ZIP | Earnings by Occupation × Region |
| ASHE Table 2 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupationby2digitsocashetable2) | Multiple ZIP | Earnings by 2-digit SOC |
| ASHE Table 3 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation2digitsocashetable3) | Multiple ZIP | Earnings by Region × 2-digit SOC |
| ASHE Table 5 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ukregionbyindustry2digitsicashetable5) | Multiple ZIP | Earnings by Region × Industry |
| ASHE Table 29 | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/earningsandhoursworkedbyindustryandoccupationashetable29) | Multiple ZIP (13.6MB) | Earnings by Industry × Occupation |
| EARN06: Gross weekly earnings by occupation | [ONS](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/grossweeklyearningsbyoccupationearn06) | 150KB XLS | Quarterly earnings by occupation |
| UK Business: Activity, Size and Location | [ONS](https://www.ons.gov.uk/businessindustryandtrade/business/activitysizeandlocation/datasets/ukbusinessactivitysizeandlocation) | Multiple XLS | 2.7M+ businesses by SIC, region, size |
| Claimant Count | [NOMIS](https://www.nomisweb.co.uk/) | Monthly API | Most timely local labour signal |

## HuggingFace Datasets

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| fabsssss/uk-local-labour-market | [HF](https://huggingface.co/datasets/fabsssss/uk-local-labour-market) | 374 rows | Claimant count per LA, monthly |
| jhumbl/uk-open-data | [HF](https://huggingface.co/datasets/jhumbl/uk-open-data) | Multiple parquet | Weekly: transport, policing, food safety, vehicle |
| dacheah/uk-company-financials | [HF](https://huggingface.co/datasets/dacheah/uk-company-financials) | 3.73M filings | Companies House financials, normalized |
| theodi/ndl-core-corpus | [HF](https://huggingface.co/datasets/theodi/ndl-core-corpus) | 156K records | GOV.UK, Hansard, ONS, Defra, legislation |
| othertales/uklegislation | [HF](https://huggingface.co/datasets/othertales/uklegislation) | 175K docs | Full UK legislation corpus |

## Kaggle Datasets

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| UK Housing Prices Paid | [Kaggle](https://www.kaggle.com/datasets/hm-land-registry/uk-housing-prices-paid) | 22M+ rows, 2.41 GB | Every property sale since 1995 |
| UK Property Transactions 2025 | [Kaggle](https://www.kaggle.com/datasets/uradkr/uk-property-transactions-2025) | 898K rows | Full year 2025 with engineered features |
| UK Housing (Cleaned) | [Kaggle](https://www.kaggle.com/datasets/burhanimtengwa/uk-housing-cleaned) | 262MB | Cleaned, region-enriched, ML-ready 2000-2023 |
| UK Property Prices with Sale History | [Kaggle](https://www.kaggle.com/datasets/isaacoresanya/uk-property-prices-with-sale-history) | Multi-MB | Rightmove + Land Registry combined |
| UK Property Price data 1995-2023 | [Kaggle](https://www.kaggle.com/datasets/willianoliveiragibin/uk-property-price-data-1995-2023-04) | Multi-MB | Full Land Registry history |
| GOV.UK Job Listing Data | [Kaggle](https://www.kaggle.com/datasets/mohammedderouiche/gov-uk-job-listing-data) | Multi-MB | UK government job portal listings |
| Employee Salary Dataset | [Kaggle](https://www.kaggle.com/datasets/anninasimon/employee-salary-dataset) | CSV | Employee salary with demographics |
| UK House Price Prediction 2015-2024 | [Kaggle](https://www.kaggle.com/datasets/swarupsudulaganti/uk-house-price-prediction-dataset-2015-to-2024) | 3MB | ML-ready house price data |

## Other Sources

| Source | URL | What it unlocks |
|--------|-----|-----------------|
| HM Land Registry PPD | [GOV.UK](https://www.gov.uk/government/statistical-data-sets/price-paid-data-single-file) | 5.3 GB CSV, 24M+ records from 1995 |
| UK House Price Index | [Land Registry](http://landregistry.data.gov.uk/app/ukhpi/) | SPARQL/CSV, monthly from 1995 |
| UK House Prices | [ukhouseprices.uk](https://ukhouseprices.uk/) | 31M+ records, free access |
| data.gov.uk CKAN API | [data.gov.uk/api/3/action](https://www.data.gov.uk/api/3/action/package_search) | 57,791 datasets, free API |
| open-data.org.uk | [open-data.org.uk](https://open-data.org.uk) | 104K+ datasets, 193 portals |
| A Millennium of Macroeconomic Data | [datahub.io](https://datahub.io/economic-history/millennium-macroeconomic-data-uk) | GDP, wages, prices from 1086! |
| Anthropic EconomicIndex | [HF](https://huggingface.co/datasets/Anthropic/EconomicIndex) | AI labour market impacts |
| Dallas Fed AI Wage Study | [dallasfed.org](http://dallasfed.org/research/economics/2026/0224) | AI impact on wages by sector |

## GitHub Repos

| Repo | URL | What it unlocks |
|------|-----|-----------------|
| i-dot-ai/awesome-gov-datasets | [GitHub](https://github.com/i-dot-ai/awesome-gov-datasets) | Curated UK gov datasets with metadata files |
| api-evangelist/data-gov-uk | [GitHub](https://github.com/api-evangelist/data-gov-uk) | UK gov open data API profiles |
| ONSdigital/sdg-data | [GitHub](https://github.com/ONSdigital/sdg-data) | UK SDG reporting data |
| ONSdigital/uk-topojson | [GitHub](https://github.com/ONSdigital/uk-topojson) | UK geography boundaries 2014-2025 |

## Human Tasks

| Task | Priority | Unlocks |
|------|----------|---------|
| Download ONS LMS (11.7MB) | Critical | Core UK labour data |
| Download Land Registry PPD (5.3GB) | Critical | 24M+ property sales |
| Download Kaggle UK housing (262MB) | High | Cleaned property data |
| Download HuggingFace UK datasets | High | Company financials, legislation |
| Get Companies House API key (free) | High | Live company data |
