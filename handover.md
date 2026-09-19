# Handover — What to do first

## Where we are

We have built the theory. Now we plant.

Everything we've designed decomposes into **reusable functions** that compose into products. The architecture is:

```
OBSERVE → DECIDE → CREATE → DISTRIBUTE → ENGAGE → LEARN → OBSERVE
```

---

## What exists

### Code (functional)
- **powpowpow/** — Full Seesaw infrastructure: warehouse, schema, entities, backtests, collectors, content system. 15+ Python modules. Core is working.

### Theory (complete)
- **datagarden/** — 16 documents: thesis, ideology, moat, formula, filters, OS, content strategy, content map, seed data, frontier analysis, unified architecture

### Products (designed)
- **influence/** — Agentic business stack: cmail, stevejobless, 16 products designed. roast.pet pipeline proven end-to-end. Graph + dash + receipts live.

### Missing (not built yet)
- **Breadup collectors** — no live data
- **UKGraph collectors** — no live data
- **Shared infrastructure** — entities, warehouse, manifest not extracted from powpowpow
- **Content pipeline** — no Shorts produced
- **Analytics feedback loop** — not wired

---

## The first loop (do this now)

One tree per forest. One Short each. Nine probes total.

### Week 1: Set up shared infrastructure

**Extract from powpowpow:**
```
entities.py    → datagarden/shared/entities.py
warehouse.py   → datagarden/shared/warehouse.py
schema.py      → datagarden/shared/schema.py
manifest.py    → datagarden/shared/manifest.py
```

**Create directory structure:**
```
datagarden/
├── shared/
├── forests/
│   ├── breadup/gardens/
│   ├── room/gardens/
│   ├── me/gardens/
│   └── powpowpow/
├── experiments/
└── content/
```

### Week 1: Start Breadup data collection

**Cheapest path:**
- Sign up for Apify ($100/mo)
- Deploy eBay UK sold listings actor
- Collect daily: 50 categories, sold price + condition + date
- Store in `datagarden/forests/breadup/data/`
- First metric: `median_sold_price` by category × platform

**Second collector (free):**
- Companies House streaming API (free, no key needed)
- Start logging: company births/deaths by SIC + region
- Store in `datagarden/forests/room/data/`

### Week 1: Make 3 test Shorts

Use existing data or public data. Just test the format.

**Short 1 (Breadup):**
Title: "What should you flip with £100?"
Format: Answer in first 3 seconds, prove with data
Length: 30-60 seconds

**Short 2 (UKGraph):**
Title: "The UK jobs getting crowded fastest"
Format: Ranking in first 3 seconds, evidence after
Length: 30-60 seconds

**Short 3 (PowPowPow):**
Title: "The most profitable compute hardware right now"
Format: Answer first, data second
Length: 30-60 seconds

### Week 2: Publish and measure

- Post all 3 Shorts
- Record: CTR, retention, comments, saves
- For each: was the hypothesis correct?
- Decision: prune / keep / deepen

### Week 2-3: Grow what works

- If Breadup Short performs → add Vinted collector
- If UKGraph Short performs → add ONS job adverts API
- If PowPowPow Short performs → add more networks

### Week 4: First content tree

Pick the best-performing forest. Make 3 more Shorts in that branch. Start building the experiment log.

---

## The experiment log

Every tree logs:

```text
tree_id: breadup-mispricing-001
forest: breadup
child: mispricing
audience: resellers, side-hustlers

title: "Things people are selling too cheaply right now"
hypothesis: People want arbitrage opportunities. Mispricing is actionable.
expected: high CTR, high saves

metric: sold_price / asking_price by category
data: eBay UK sold (Apify)
collected: 2026-09-19
categories: 50

published: 2026-09-22
platform: YouTube Shorts

results:
  impressions: TBD
  ctr: TBD
  retention_3s: TBD
  completion: TBD
  comments: TBD
  saves: TBD

decision: TBD
next_hypothesis: TBD
```

---

## Rules

1. **No collector without a title.** Every data pipeline powers a specific piece of content.

2. **No video without a measurement.** Every piece of content is backed by a metric we keep collecting.

3. **Answer in first 3 seconds.** No suspense farming. Give the answer, then prove it.

4. **Hypothesis before publish.** Predict performance. Learn from the gap.

5. **Nine trees max.** 3 per forest. Don't overbuild.

6. **Analytics drive growth.** Let YouTube tell us where to deepen.

7. **Higher-order moats emerge later.** Don't design them now. Plant and grow.

---

## Budget

| Item | Cost |
|------|------|
| Apify (eBay sold) | $100/mo |
| Companies House API | Free |
| ONS API | Free |
| YouTube (free to post) | Free |
| Arrow 2 (charts) | Free tier |
| **Total** | **~$100/mo** |

---

## Success criteria (30 days)

- [ ] 9 Shorts published
- [ ] Experiment log with 9 entries
- [ ] At least 1 Short with >5% CTR
- [ ] At least 1 Short with >50% retention
- [ ] Breadup: daily sold prices for 50 categories
- [ UKGraph: Companies House streaming active
- [ ] Decision on which forest to deepen

---

## The one-page summary

```
WHAT: Plant 9 trees (3 per forest), publish 9 Shorts, measure what works.

WHY: The loop is the moat. Analytics tell us where to grow.

HOW:
  1. Extract shared code from powpowpow
  2. Set up eBay + Companies House collectors
  3. Make 3 test Shorts (one per forest)
  4. Publish and measure
  5. Grow what works, prune what doesn't

RULES:
  - No collector without a title
  - No video without a measurement
  - Answer in first 3 seconds
  - Hypothesis before publish
  - Nine trees max

BUDGET: $100/mo
TIMELINE: 30 days to first data
```

---

## What we know

- The theory is sufficient
- The architecture is clean
- roast.pet proves the composition works
- powpowpow proves the data pipeline works
- influence proves the distribution + receipt system works
- We don't need more theory
- We need to plant

## What we don't know

- Which titles will perform
- Which audiences will respond
- Which forests deserve deeper collection
- What higher-order products will emerge
- What the audience will teach us

**That's why we plant. YouTube is the experiment. The audience grows the schema.**

---

$$
\boxed{\text{Plant now. Measure. Grow what works. Let the loop compound.}}
$$
