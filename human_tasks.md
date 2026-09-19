# Human Tasks — Unlock the Full Data Garden System

Every API key, download, account, and action a human must take before the system runs autonomously.

---

## 1. CRITICAL — Must Have for Basic Functionality

Without these the garden cannot collect data, generate content, or publish.

### 1.1 Software Installations

| # | Item | What It Is | How to Get | Cost | What It Unlocks | Source File |
|---|------|-----------|------------|------|-----------------|-------------|
| 1 | **Python 3.10+** | Runtime for all collectors and content pipeline | `python3 --version` | FREE | Everything | All `*.py` |
| 2 | **FFmpeg** | Video assembly for Shorts | `sudo apt install ffmpeg` | FREE | All video generation | `content/pipeline.py` |
| 3 | **pip dependencies** | Python packages for collectors, voice, thumbnails | `cd /home/box/datagarden && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` | FREE | All Python modules | `requirements.txt` |
| 4 | **openpyxl** | XLSX parsing for ASHE earnings + Business Demography | `pip install openpyxl` | FREE | ASHE earnings collector | `collectors/ukgraph_historical.py` |

### 1.2 API Keys

| # | Service | What It Is | Where to Get | Cost | What It Unlocks | Env Var |
|---|---------|-----------|--------------|------|-----------------|---------|
| 5 | **Companies House API Key** | Real-time UK company births/deaths stream + bulk data | https://developer.company-information.service.gov.uk/ | FREE | `companies_house.py` live streaming, 5M company bulk, UKAdmin tasks | `COMPANIES_HOUSE_API_KEY` |
| 6 | **YouTube Data API Key** | Upload videos, read analytics, manage channel | https://console.cloud.google.com | FREE (10k units/day) | Shorts publishing loop, analytics feedback, experiments | `YOUTUBE_API_KEY` |
| 7 | **TypeSafe API Key (Jev)** | Typed observation classification, hypothesis scoring, audience analysis | https://console.typesafe.ai/keys | FREE ($0.042/Mtok in, out free) | `shared/jev.py` classification across all three forests | `TYPESAFE_API_KEY` |

### 1.3 Account Registrations and Manual Actions

| # | Action | URL | What It Unlocks | Notes |
|---|--------|-----|-----------------|-------|
| 8 | **Create YouTube channel** | https://studio.youtube.com | All Shorts publishing | Required before any content goes live |
| 9 | **Upload first 3 probe Shorts** | YouTube Studio -> Upload -> Set as Short (vertical, <60s) | First attention signals, experiment data | Use `content/shorts/short_*.mp4` |
| 10 | **Add thumbnails** | YouTube Studio upload flow | Click-through rate measurement | Use `content/shorts/thumb_*.png` |
| 11 | **Record analytics after 24-48h** | YouTube Studio -> Analytics | Update experiment JSONs | Without this Jev cannot score audience response |

### 1.4 Configuration Steps

| # | Step | Command | What It Unlocks |
|---|------|---------|-----------------|
| 12 | **Copy .env.example to .env** | `cp .env.example .env` | All collectors read keys from here |
| 13 | **Add Companies House key** | Edit `.env`: `COMPANIES_HOUSE_API_KEY=your_key` | Live company data |
| 14 | **Add YouTube API key** | Edit `.env`: `YOUTUBE_API_KEY=your_key` | Video upload + analytics |
| 15 | **Add TypeSafe key** | Edit `.env`: `TYPESAFE_API_KEY=your_key` | Jev classification pipeline |
| 16 | **Set up daily cron** | `python -m collectors.run_daily` via crontab | Automated daily collection |

---

## 2. HIGH — Significantly Improves Data Quality

Without these the garden works but has gaps in data coverage and historical depth.

### 2.1 API Keys and Accounts

| # | Service | What It Is | Where to Get | Cost | What It Unlocks | Env Var |
|---|---------|-----------|--------------|------|-----------------|---------|
| 17 | **Apify Token** | Structured eBay scraping (no HTML parsing) | https://apify.com | FREE ($5/mo credit, no card) | `collectors/ebay_sold.py`, ~2500 listings/mo | `APIFY_TOKEN` |
| 18 | **Kaggle Account + API Key** | 2.8M eBay product listings + batch GPU | https://www.kaggle.com | FREE | `breadup_historical.py --download-kaggle` | `~/.kaggle/kaggle.json` |
| 19 | **MOT History API Credentials** | UK vehicle MOT history lookup | https://register-mot-history.api.gov.uk/ | FREE | `collectors/mot_history.py`, vehicle admin | `MOT_CLIENT_ID`, `MOT_CLIENT_SECRET`, `MOT_TENANT_ID`, `MOT_API_KEY` |

### 2.2 Data Downloads

| # | Dataset | Records | Where | Size | What It Unlocks |
|---|---------|---------|-------|------|-----------------|
| 20 | **NBER Best Offer Bargaining Data** | 98M records (2012-13) | https://www.nber.org/research/data/best-offer-sequential-bargaining | Large | Negotiation models, seller acceptance behavior |
| 21 | **Kaggle eBay Product Listings** | ~980K + 1.8M | https://www.kaggle.com/datasets/promptcloud/ebay-product-listing-dataset | ~200MB | Product normalization, title-to-entity mapping |
| 22 | **Companies House Bulk Snapshot** | ~5M companies | https://download.companieshouse.gov.uk/ | ~469MB | Full UK company database for UKGraph joins |

### 2.3 Configuration Steps

| # | Step | Command | What It Unlocks |
|---|------|---------|-----------------|
| 23 | **Install apify-client** | `pip install apify-client` | Apify eBay scraping |
| 24 | **Install kaggle CLI** | `pip install kaggle` | Kaggle dataset downloads |
| 25 | **Add MOT credentials to .env** | Edit `.env` with all 4 MOT vars | Vehicle MOT history collector |

---

## 3. MEDIUM — Nice to Have

These improve workflow, discoverability, or add optional capabilities.

| # | Item | What It Is | Where | Cost | What It Unlocks | Env Var |
|---|------|-----------|-------|------|-----------------|---------|
| 26 | **Muse Connector Submission** | DataGarden as a Muse capability | https://muse.ai/platform | FREE | Agents can ask "Is this a bargain?" etc. | N/A |
| 27 | **Groq API Key** | Ultra-fast free inference for scripts | https://console.groq.com/keys | FREE (30 RPM, 1000 RPD) | Optional script generation | `GROQ_API_KEY` |
| 28 | **OpenRouter API Key** | Hub for 300+ models, many free | https://openrouter.ai/keys | FREE | Alternative inference routing | `OPENROUTER_API_KEY` |
| 29 | **Docker** | Isolated containers for federated services | `sudo apt install docker.io docker-compose` | FREE | GitGoblin/Dell/QDW in containers | N/A |
| 30 | **PostgreSQL** | Production database for OpenPatala | `sudo apt install postgresql` | FREE | Entity/assertion/event storage | `DATABASE_URL` |

---

## 4. LOW — Future Features

These are for expanding the system beyond its current scope.

### 4.1 Future Data Sources

| # | Service | What It Is | Where to Get | Cost | What It Unlocks |
|---|---------|-----------|--------------|------|-----------------|
| 31 | **OpenAlex API Key** | Academic research graph | https://docs.openalex.org/ | FREE (works without key) | GitGoblin research collection |
| 32 | **GitHub Token** | Higher API rate limits | https://github.com/settings/tokens | FREE | GitGoblin GitHub scanning |
| 33 | **Petals (pip)** | Distributed volunteer LLM swarm | `pip install petals` | FREE (slow, ~4-6 tok/s) | Free pool compute for batch research |
| 34 | **Oracle Always Free ARM VM** | 24/7 self-hosted small-model inference | https://cloud.oracle.com | FREE (2 OCPU, 12GB RAM) | Private llama.cpp endpoint |

### 4.2 Future API Keys (Dell / LLM Router)

| # | Service | Where to Get | Cost | Env Var |
|---|---------|--------------|------|---------|
| 35 | **Anthropic** (Claude) | https://console.anthropic.com/settings/keys | PAID ($5 free credit) | `ANTHROPIC_API_KEY` |
| 36 | **OpenAI** (GPT) | https://platform.openai.com/api-keys | PAID ($5 free credit) | `OPENAI_API_KEY` |
| 37 | **Google AI** (Gemini, 1M context) | https://aistudio.google.com/apikey | FREE | `GOOGLE_AI_API_KEY` |
| 38 | **HuggingFace** (hundreds of models) | https://huggingface.co/settings/tokens | FREE ($0.10/mo free) | `HUGGINGFACE_TOKEN` |
| 39 | **DeepSeek** (best price-to-quality) | https://platform.deepseek.com/api_keys | PAID (10 yuan free) | `DEEPSEEK_API_KEY` |
| 40 | **Groq** (fastest inference) | https://console.groq.com/keys | FREE (30 RPM) | `GROQ_API_KEY` |
| 41 | **Cerebras** (ultra-fast) | https://cloud.cerebras.ai | FREE | `CEREBRAS_API_KEY` |
| 42 | **Together AI** | https://api.together.xyz/settings/api-keys | FREE ($1 credit) | `TOGETHER_API_KEY` |
| 43 | **Fireworks** | https://fireworks.ai/account/api-keys | FREE ($1 credit) | `FIREWORKS_API_KEY` |
| 44 | **DeepInfra** (cheapest per-token) | https://deepinfra.com/dash/api_keys | FREE ($1 credit) | `DEEPINFRA_API_KEY` |
| 45 | **Mistral** (EU provider) | https://console.mistral.ai/api-keys/ | FREE | `MISTRAL_API_KEY` |
| 46 | **Cloudflare AI** (10K free neurons/day) | https://dash.cloudflare.com | FREE | `CLOUDFLARE_AI_API_KEY`, `CLOUDFLARE_AI_ACCOUNT_ID` |
| 47 | **Artificial Analysis** (benchmarks) | https://artificialanalysis.ai/api-key-management-redirect | FREE (100 req/24h) | `AA_API_KEY` |
| 48 | **OpenCode Go** | https://dev.opencode.ai/go | FREE | `OPENCODE_GO_API_KEY` |

### 4.3 Future Config (GitGoblin)

| # | Env Var | What It Does | Where to Get |
|---|---------|-------------|--------------|
| 49 | `GITGOBLIN_LLM_BASE_URL` | OpenAI-compatible endpoint for architecture enrichment | Any compatible endpoint |
| 50 | `GITGOBLIN_LLM_API_KEY` | Key for above | Same source as base URL |
| 51 | `GITGOBLIN_LLM_MODEL` | Model name for above | Same source |

### 4.4 Future Config (QDW Federation)

| # | Env Var | What It Does |
|---|---------|-------------|
| 52 | `QDW_GITGOBLIN_URL` | Connect QDW to GitGoblin |
| 53 | `QDW_DELL_URL` | Connect QDW to Dell |
| 54 | `QDW_FORGE_URL` | Connect QDW to Forge |
| 55 | `QDW_FORGE_ADMIN_TOKEN` | Authenticate to Forge |
| 56 | `QDW_FORGE_LEASE_SECRET` | Sign Forge lease tokens (min 32 bytes) |
| 57 | `QDW_FORGE_CLIENT_KEYS_JSON` | Client auth map for Forge API |
| 58 | `QDW_FEDERATION_TIMEOUT_SECONDS` | Federation request timeout (default 20) |
| 59 | `QDW_FEDERATION_LAB_MODE` | Set to "1" for lab/testing mode |

### 4.5 Future Config (OpenPatala)

| # | Env Var | What It Does | Default |
|---|---------|-------------|---------|
| 60 | `DATABASE_URL` | PostgreSQL connection for entity storage | `postgresql://patala:patala@127.0.0.1:5432/openpatala` |

---

## 5. Environment Variables Summary

```bash
# CRITICAL — Garden won't function without these
COMPANIES_HOUSE_API_KEY=        # https://developer.company-information.service.gov.uk/
YOUTUBE_API_KEY=                # https://console.cloud.google.com
TYPESAFE_API_KEY=               # https://console.typesafe.ai/keys

# HIGH — Improves data quality
APIFY_TOKEN=                    # https://apify.com ($5/mo free)
MOT_CLIENT_ID=                  # https://register-mot-history.api.gov.uk/
MOT_CLIENT_SECRET=
MOT_TENANT_ID=
MOT_API_KEY=

# MEDIUM — Nice to have
GROQ_API_KEY=                   # https://console.groq.com/keys
OPENROUTER_API_KEY=             # https://openrouter.ai/keys

# LOW — Future: Dell/LLM Router
AA_API_KEY=                     # https://artificialanalysis.ai
OPENCODE_GO_API_KEY=            # https://dev.opencode.ai/go
CLOUDFLARE_AI_API_KEY=          # https://dash.cloudflare.com
CLOUDFLARE_AI_ACCOUNT_ID=
ANTHROPIC_API_KEY=              # https://console.anthropic.com
OPENAI_API_KEY=                 # https://platform.openai.com
GOOGLE_AI_API_KEY=              # https://aistudio.google.com
HUGGINGFACE_TOKEN=              # https://huggingface.co/settings/tokens
DEEPSEEK_API_KEY=               # https://platform.deepseek.com
CEREBRAS_API_KEY=               # https://cloud.cerebras.ai
TOGETHER_API_KEY=               # https://api.together.xyz
FIREWORKS_API_KEY=              # https://fireworks.ai
DEEPINFRA_API_KEY=              # https://deepinfra.com
MISTRAL_API_KEY=                # https://console.mistral.ai

# LOW — Future: GitGoblin
OPENALEX_API_KEY=               # https://docs.openalex.org
GITHUB_TOKEN=                   # https://github.com/settings/tokens
GITGOBLIN_LLM_BASE_URL=
GITGOBLIN_LLM_API_KEY=
GITGOBLIN_LLM_MODEL=

# LOW — Future: QDW Federation
QDW_GITGOBLIN_URL=
QDW_DELL_URL=
QDW_FORGE_URL=
QDW_FORGE_ADMIN_TOKEN=
QDW_FORGE_LEASE_SECRET=
QDW_FORGE_CLIENT_KEYS_JSON=
DATABASE_URL=postgresql://patala:patala@127.0.0.1:5432/openpatala
```

---

## 6. Quick Start Checklist

```
[ ] sudo apt install ffmpeg
[ ] cd /home/box/datagarden && python3 -m venv venv && source venv/bin/activate
[ ] pip install -r requirements.txt && pip install openpyxl
[ ] cp .env.example .env
[ ] Get Companies House key -> add to .env
[ ] Get YouTube API key -> add to .env
[ ] Get TypeSafe key -> add to .env
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
