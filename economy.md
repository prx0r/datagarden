# Economy — The Operating Manual

## The pattern from powpowpow

> **If you cannot repeatedly observe the thing required for the transformation, it is not a core crop.**

```text
OBSERVE → NORMALIZE → TRANSFORM → SNAPSHOT → ANSWER A QUESTION → PUBLISH → MEASURE AUDIENCE → DECIDE WHAT TO DEEPEN
```

---

## Plant three minimal trees immediately

### Tree 1: UKGraph — job_demand

**Question:** Which UK jobs are gaining demand fastest?

**Source:** ONS job adverts by SOC 2020 × local authority (free, back to 2017)

**Schema:**
```text
occupation, soc_code, local_authority, period,
job_ads, change_1m, change_3m, change_12m,
national_relative_change, local_relative_change,
source_version, observed_at
```

**Content:**
- "The UK jobs where demand is rising fastest"
- "The jobs exploding in demand in Manchester"
- "Where electrician demand is increasing"

### Tree 2: Breadup — used_market_pressure

**Question:** Which used products are getting cheaper / more supplied fastest?

**Source:** eBay Browse API (free tier) + 100 manually curated music-gear SKUs

**Schema:**
```text
object_id, canonical_name, category,
listing_count, new_count, ended_count,
median_ask, p25, p75,
price_cut_rate, median_price_cut,
inventory_growth_7d, inventory_growth_30d,
observed_at
```

**Content:**
- "The used synths getting cheaper fastest"
- "The music gear with supply exploding right now"
- "Used gear sellers are cutting prices fastest on these products"

### Tree 3: PowPowPow — resource_flow

**Question:** Where are machine resources moving and getting paid?

**Source:** Already live in existing collectors

**Content:**
- "The networks miners are leaving fastest"
- "Which network is paying the most per unit of compute"

---

## First milestone

> Three forests each autonomously produce one truthful candidate Short from live data, and the system ingests YouTube's response back into the experiment record.

---

## Concrete order

1. UKGraph: import ONS dataset, normalize, generate job_demand.json
2. Breadup: define 100 SKUs, activate eBay Browse collector
3. PPP: one content_candidates() adapter over existing metrics
4. Shared: PublicationExperiment object
5. YouTube: OAuth + upload + Analytics ingestion
6. Publish one Short from each forest
7. Store audience outcome
8. Choose next trees from evidence
