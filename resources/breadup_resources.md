# Breadup — Canonical Resources (Updated)

## Live Data

| Source | Records | API | Status |
|--------|---------|-----|--------|
| ebay_free.py | eBay UK public search | HTTP scraping (VPS-blocked) | ⚠️ Needs local execution |
| ebay_sold.py | eBay UK via Apify | Apify API ($5/mo free) | ⚠️ Needs API key |

## Kaggle Datasets

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| promptcloud/ebay-product-listing | [Kaggle](https://www.kaggle.com/datasets/promptcloud/ebay-product-listing) | 74MB | Product listings with prices |
| promptcloud/product-listing-dataset-ebay | [Kaggle](https://www.kaggle.com/datasets/promptcloud/product-listing-dataset-ebay) | Multi-MB | Full product data |
| promptcloud/ebay-product-dataset | [Kaggle](https://www.kaggle.com/datasets/promptcloud/ebay-product-dataset) | 30K records | Product data Jan 2021+ |
| e-commerece-sales-data-2024 | [Kaggle](https://www.kaggle.com/datasets/datascientist97/e-commerece-sales-data-2024) | 188MB | Sales data with user profiles |

## HuggingFace Datasets

| Dataset | URL | What it unlocks |
|---------|-----|-----------------|
| Jelonman/marketplace-fee-data | [HF](https://huggingface.co/datasets/Jelonman/marketplace-fee-data) | Platform fee data: eBay, Vinted, Depop, Etsy, Poshmark, Mercari fees |

## Apify Actors (cheapest eBay data)

| Actor | URL | Cost | What it unlocks |
|-------|-----|------|-----------------|
| sync-network/ebay-sold-listings-scraper | [Apify](https://apify.com/sync-network/ebay-sold-listings-scraper) | $5/mo free | 8 marketplaces, fast/detailed modes |
| caffein.dev/ebay-sold-listings | [Apify](https://apify.com/caffein.dev/ebay-sold-listings) | ~$0.001/listing | 8 marketplaces, Best Offer detection |
| midwest_united/ebay-sold-comps | [Apify](https://apify.com/midwest_united/ebay-sold-comps) | $0.02/record | Lot normalization, IQR fencing, A-D confidence |
| omao/ebay-sold-scraper | [Apify](https://apify.com/omao/ebay-sold-scraper) | Pay per result | Real sold prices & dates |
| apt_marble/ebay-sold-items-scraper | [Apify](https://apify.com/apt_marble/ebay-sold-items-scraper) | $1.20/1K | Clean sold data, 8 marketplaces |

## GitHub MCP Servers

| Tool | URL | What it unlocks |
|------|-----|-----------------|
| cunicopia-dev/ebay-mcp | [GitHub](https://github.com/cunicopia-dev/ebay-mcp) | MCP: ebay_price_check, ebay_search, ebay_get_item |
| BlackFalconData-org/ebay-sold-listings-scraper | [GitHub](https://github.com/BlackFalconData-org/ebay-sold-listings-scraper) | Structured eBay sold data at scale |

## Other Sources

| Source | URL | What it unlocks |
|--------|-----|-----------------|
| ING eBay Sold Listings | [inglisting.com](https://inglisting.com/ebay-sold-listings-data/) | 897K aggregate stats (not raw) |
| SoldComps API | [sold-comps.com](https://sold-comps.com/) | 40 sold comps per request, free tier |
| PlottData eBay Intelligence | [plottdata.com](https://plottdata.com/marketplaces/ebay) | Resale pricing & seller analytics |
| itemstoflip.com | [itemstoflip.com](https://itemstoflip.com/blog/ebay-flipping-profit-calculator) | Flipping profit calculator workflow |

## Human Tasks

| Task | Priority | Unlocks |
|------|----------|---------|
| Set up Apify account ($5/mo free) | High | Live eBay sold scraping from any machine |
| Download Kaggle eBay datasets | High | 2.8M+ product listings for normalization |
| Install kaggle CLI | High | Programmatic dataset access |
