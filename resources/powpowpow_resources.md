# PowPowPow — Canonical Resources

## Live Data (already integrated)

| Source | Records | API | Status |
|--------|---------|-----|--------|
| powpowpow chain collectors | 17 chains × 24 collectors | Multiple free APIs | ✅ Live |
| v1_live_cards.py | Real-time profitability | Computed from chain data | ✅ Live |
| v1_registry.py | Chain metadata | Static | ✅ Live |

## Historical Datasets (collectors built)

| Source | Records | Access | What it unlocks |
|--------|---------|--------|-----------------|
| CoinGecko API | 18 coins × 365 days | Free, 10-30 calls/min | Price/market history |
| Minerstat benchmarks | 10,730 hardware/algorithm pairs | Free API | Hardware capability database |
| WhatToMine | Network difficulty/hashrate | Free (scraping) | Network economics history |

## HuggingFace Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| `ismailtasdelen/bitcoin-historical-dataset` | [HF](https://huggingface.co/datasets/ismailtasdelen/bitcoin-historical-dataset) | 6,457 daily rows, 100+ features | Genesis-to-2026 Bitcoin: market + on-chain + mining + macro |
| `KEDevO/crypto-market-datasets` | [HF](https://huggingface.co/datasets/KEDevO/crypto-market-datasets) | 25GB+, 10 symbols | Binance tick-level from genesis, institutional-grade |
| `linxy/CryptoCoin` | [HF](https://huggingface.co/datasets/linxy/CryptoCoin) | 530+ pairs, 1m-1d | Binance spot OHLCV, auto-updated daily |
| `johnahn/mdk-mining-controller-data` | [HF](https://huggingface.co/datasets/johnahn/mdk-mining-controller-data) | 5.2M rows, 3.6GB | ASIC mining telemetry: hashrate, power, voltage, temp, failures |
| `COINjecture/NP_Solutions_v2` | [HF](https://huggingface.co/datasets/COINjecture/NP_Solutions_v2) | JSONL, 54+ fields | Blockchain PoUW consensus metrics |
| `COINjecture/MiningEmissions` | [HF](https://huggingface.co/datasets/COINjecture/MiningEmissions) | JSONL | Token emissions across 8 dimensional pools |
| `dataforge-labs/bitcoin-mining-pool-templates` | [HF](https://huggingface.co/datasets/dataforge-labs/bitcoin-mining-pool-templates) | Parquet | Stratum mining.notify jobs from 6 major pools |

## Kaggle Datasets (to download)

| Dataset | URL | Size | What it unlocks |
|---------|-----|------|-----------------|
| Bitcoin Network On-Chain Blockchain Data | [Kaggle](https://www.kaggle.com/datasets/aleexharris/bitcoin-network-on-chain-blockchain-data) | Daily + 30-min | Hashrate, difficulty, miner revenue, mempool |
| Cryptocurrency Mining Data | [Kaggle](https://www.kaggle.com/datasets/amritpal333/crypto-mining-data) | 9+ cryptos | Difficulty, coins, fees, active addresses per coin |
| Bitcoin Time Series All Time | [Kaggle](https://www.kaggle.com/datasets/bhaskartripathi/bitcoin-time-series-all-time) | 3,500 rows 2009-2025 | Price, volume, block size, tx/block |
| Crypto Market Intelligence Dataset | [Kaggle](https://www.kaggle.com/datasets/aminasalamt/crypto-market-intelligence-dataset) | 2018-2026 daily | Prices + sentiment + on-chain + technical indicators |
| GPU Benchmarks Compilation | [Kaggle](https://www.kaggle.com/datasets/alanjo/gpu-benchmarks) | 160+ GPUs, 40+ algos | Hashrate per GPU per algorithm |
| GPU Performance Prediction | [Kaggle](https://www.kaggle.com/competitions/gpu-performance-prediction-challenge) | 12,000+ GPUs | Cores, clock, memory → performance index |

## Other Sources

| Source | URL | What it unlocks |
|--------|-----|-----------------|
| Bitcoin Difficulty History | [d-central.tech](https://d-central.tech/bitcoin-difficulty-history/) | Every difficulty adjustment since 2009 |
| Hashrate.no | [hashrate.no](https://hashrate.no/gpus) | Real-time GPU profitability |
| WhatToMine | [whattomine.com](https://whattomine.com/gpus) | Break-even, efficiency per GPU |
| MinerCompare | [minercompare.com](https://minercompare.com/gpus) | Multi-currency profit calculator |
| MineROI-Net (GitHub) | [github.com/AMAAI-Lab/MineROI-Net](https://github.com/AMAAI-Lab/MineROI-Net) | Scripts to reconstruct ASIC ROI dataset |

## Human Tasks Required

| Task | Priority | Unlocks |
|------|----------|---------|
| Download HuggingFace datasets | High | 7 datasets, 50GB+ |
| Download Kaggle datasets | High | 6 datasets |
| Scrape Hashrate.no GPU data | Medium | 500+ GPU benchmarks |
| Scrape WhatToMine GPU rankings | Medium | 75+ GPU profitability |
| Run Minerstat benchmark seed | Medium | 10,730 hardware/algorithm pairs |
