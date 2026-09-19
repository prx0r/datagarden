# Setup Guide — Get running in 15 minutes

## Prerequisites

```bash
# Python 3.10+
python3 --version

# FFmpeg (for video assembly)
sudo apt install ffmpeg
# or: brew install ffmpeg (macOS)
```

## Install

```bash
cd /home/box/datagarden
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Free API keys (optional, improves data)

### Apify (eBay data, $5/mo free credit, no card)
1. Go to https://apify.com
2. Sign up (GitHub/Google/email)
3. Go to Settings → API & Integrations → Create token
4. Add to `.env`:
```
APIFY_TOKEN=your_token_here
```

### Companies House (UK business data, free)
1. Go to https://developer.company-information.service.gov.uk/
2. Register for an account
3. Create an application
4. Copy the API key
5. Add to `.env`:
```
COMPANIES_HOUSE_API_KEY=your_key_here
```

### YouTube Data API (analytics, free)
1. Go to https://console.cloud.google.com
2. Create project → Enable YouTube Data API v3
3. Create OAuth credentials
4. Add to `.env`:
```
YOUTUBE_API_KEY=your_key_here
```

## Generate first three Shorts

```bash
source venv/bin/activate
python content/generate_first_three.py
```

Output:
```
content/shorts/
├── short_*.mp4      ← Videos (ready to upload)
├── thumb_*.png      ← Thumbnails
└── audio_*.mp3      ← Voiceovers

experiments/
├── breadup-market-pressure-001.json
├── ukgraph-job-demand-001.json
└── powpowpow-resource-flow-001.json
```

## Upload to YouTube

1. Go to https://studio.youtube.com
2. Upload each `short_*.mp4`
3. Add title from experiment JSON
4. Add thumbnail from `thumb_*.png`
5. Set as Short (vertical, <60s)

## Record analytics

After 24-48 hours, update experiment JSON with:
```json
{
  "impressions": 1234,
  "ctr": 0.08,
  "views": 456,
  "avg_view_duration": 18.5,
  "avg_view_percentage": 0.72,
  "likes": 23,
  "comments": 5,
  "decision": "deepen"
}
```

## Daily data collection

```bash
# Run all collectors
python -m collectors.run_daily

# Or individual collectors
python -m collectors.ebay_sold --query "technics turntable" --count 50
python -m collectors.ons_jobs
```

## What's free vs paid

| Tool | Cost | What it does |
|------|------|--------------|
| Edge-TTS | Free | Voiceover (Microsoft voices) |
| Pillow | Free | Thumbnails and text frames |
| FFmpeg | Free | Video assembly |
| ONS API | Free | UK job adverts by SOC/region |
| Companies House API | Free | UK company births/deaths |
| Apify free tier | $5/mo credit | eBay sold listings |
| YouTube Data API | Free (10k units/day) | Upload and analytics |
| Groq API | Free | Script generation (optional) |

**Total: $0/mo** (or $0 with Apify free credit)

## Files created

```
datagarden/
├── collectors/
│   ├── ebay_sold.py           ← eBay sold (Apify free tier)
│   ├── companies_house.py     ← Companies House streaming
│   ├── ons_jobs.py            ← ONS job adverts
│   └── run_daily.py           ← Daily runner
├── content/
│   ├── pipeline.py            ← Script → voice → frame → video
│   ├── shorts_generator.py    ← Full Shorts generator
│   └── generate_first_three.py ← First three probes
├── shared/
│   ├── entities.py            ← Permanent IDs
│   ├── warehouse.py           ← Storage layer
│   ├── schema.py              ← Dataclasses
│   ├── manifest.py            ← Daily manifests
│   └── experiment.py          ← PublicationExperiment
├── forests/
│   ├── breadup/
│   │   ├── skus.py            ← 100 music-gear SKUs
│   │   └── data/              ← eBay data
│   ├── room/
│   │   └── data/              ← Companies House data
│   └── powpowpow/             ← Compute economics
└── experiments/                ← Experiment logs
```
