# Breadup — Canonical Resources

## Live Data (collectors built)

| Source | Records | API | Status |
|--------|---------|-----|--------|
| ebay_free.py | eBay UK public search | HTTP scraping (VPS-blocked) | ⚠️ Needs local execution |
| ebay_sold.py | eBay UK via Apify | Apify API ($5/mo free) | ⚠️ Needs API key |
| run_daily.py | Daily orchestrator | Composite | ✅ Built |

## Historical Datasets (collectors built)

| Source | Records | Access | What it unlocks |
|--------|---------|--------|-----------------|
| SoldComps API | 40/request, free tier | REST API | Real eBay sold prices |
| CoinGecko API | 365 days × 18 coins | Free, 10-30 calls/min | Reference prices |
| Kaggle eBay datasets | ~980K (2020) + 1.8M (2021) | Download | Product normalization |
| NBER bargaining data | 98M Best Offer records | Download | Negotiation models |

## HuggingFace Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| `ismailtasdelen/bitcoin-historical-dataset` | [HF](https://huggingface.co/datasets/ismailtasdelen/bitcoin-historical-dataset) | 6,457 rows | Reference for crypto-related product pricing |

## Kaggle Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| promptcloud/ebay-product-listing-dataset | [Kaggle](https://www.kaggle.com/datasets/promptcloud/ebay-product-listing-dataset) | 2.8M records | Product normalization, title → entity mapping |
| United Kingdom House Price Index | [Kaggle](https://www.kaggle.com/datasets/shahidaka/united-kingdom-house-price-index) | Monthly 1995+ | Property pricing reference |

## Curated Datasets (free, direct download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| ING eBay Sold Listings | [inglisting.com](https://inglisting.com/ebay-sold-listings-data/) | 897,135 sold listings | Real eBay sales Jul-Aug 2026. Price, condition, seller, date |

## Apify Actors (pay-per-use, cheapest eBay data)

| Actor | URL | Cost | What it unlocks |
|-------|-----|------|-----------------|
| `caffein.dev/ebay-sold-listings` | [Apify](https://apify.com/caffein.dev/ebay-sold-listings) | ~$0.001/listing | 8 marketplaces, Best Offer detection |
| `midwest_united/ebay-sold-comps` | [Apify](https://apify.com/midwest_united/ebay-sold-comps) | $0.02/record | Lot normalization, IQR fencing, confidence score |
| `apt_marble/ebay-sold-items-scraper` | [Apify](https://apify.com/apt_marble/ebay-sold-items-scraper) | $1.20/1K listings | Clean sold data, 8 marketplaces |
| `khadinakbar/ebay-sold-comps-analytics` | [Apify](https://apify.com/khadinakbar/ebay-sold-comps-analytics-scraper) | $0.005/item | Analytics report: percentiles, velocity, trend |

## MCP Servers & GitHub

| Tool | URL | What it unlocks |
|------|-----|-----------------|
| `cunicopia-dev/ebay-mcp` | [GitHub](https://github.com/cunicopia-dev/ebay-mcp) | MCP: ebay_price_check, ebay_search, ebay_get_item |
| `wwwlehyru-web/ebay-sold-prices-api` | [GitHub](https://github.com/wwwlehyru-web/ebay-sold-prices-api) | Sold prices with free analytics |
| Resellbot | [resellbot.com](https://resellbot.com/ebay-sold-listings/) | Free eBay + Poshmark + Mercari sold comps |

## Human Tasks Required

| Task | Priority | Unlocks |
|------|----------|---------|
| Download ING eBay Sold Listings (897K records) | Critical | Instant Breadup dataset |
| Download Kaggle eBay datasets (2.8M records) | High | Product normalization |
| Install kaggle CLI + download | High | 2.8M product listings |
| Download NBER bargaining data | Medium | 98M negotiation records |
| Set up Apify account ($5/mo free) | Medium | Live eBay sold scraping |
| Run Breadup seed collector locally | Medium | Historical seed data |
