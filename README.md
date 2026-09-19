# Datagarden

> Gardens that transform fragmented reality into continuously replenishing economic opportunities.

Three forests. One loop. Reusable functions.

---

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run daily collection
python -m collectors.run_daily
```

---

## Structure

```
datagarden/
├── collectors/           — data collectors (eBay, Companies House, ONS)
├── shared/               — infrastructure (entities, warehouse, schema, manifest)
├── forests/
│   ├── breadup/          — THINGS (physical goods value)
│   ├── room/             — MARKETS (where is there room?)
│   ├── me/               — PRODUCTION (where are the margins?)
│   └── powpowpow/        — RESOURCES (compute economics)
├── experiments/          — tree logs (hypotheses, outcomes)
├── content/              — generated content
├── thesis/               — theory layer
└── os/                   — operating system
```

---

## The loop

```
OBSERVE → DECIDE → CREATE → DISTRIBUTE → ENGAGE → LEARN → OBSERVE
```

---

## Getting started

See [handover.md](handover.md) for the first 30-day plan.
